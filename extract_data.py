import json
import re
import sys
from pathlib import Path
import time
import argparse
from datetime import datetime

# Configuration
BASE_DIR = Path(__file__).resolve().parent
SQL_FILE = BASE_DIR / "getdata" / "drupal" / "ipv_prd.sql"
OUTPUT_FILE = BASE_DIR / "getdata" / "20260108_diergeneeskunde.json"

# Desired tables and their key mappings
DESIRED_TABLES = [
    "commerce_product_field_data",
    "commerce_product_variation_field_data",
    "taxonomy_term_field_data",
    "file_managed",
    "commerce_product__field_course_desc",
    "commerce_product__field_course_program",
    "commerce_product__field_course_img",
    "commerce_product__field_course_category",
    "commerce_product_variation__field_lesson_dates", 
    "commerce_product_variation__field_location_ref",
    "commerce_product_variation__field_optional_prices",
    "commerce_product_variation__field_teachers",
    "users_field_data",
    "user__roles",
    "user__user_picture",
    "commerce_order",
    "commerce_order_item"
]

# Simple regex for SQL parsing
CREATE_TABLE_REGEX = re.compile(r"CREATE TABLE `(\w+)` \((.*?)\) ENGINE", re.DOTALL)
INSERT_INTO_REGEX = re.compile(r"INSERT INTO `(\w+)` \((.*?)\) VALUES")

def parse_sql_value(val_str):
    """
    Parses a single SQL value string into a Python type.
    Handles 'string', NULL, numbers, hex.
    """
    val_str = val_str.strip()
    if val_str.upper() == "NULL":
        return None
    if val_str.startswith("'") and val_str.endswith("'"):
        # Basic unescaping for SQL strings
        # Replace '' with '
        inner = val_str[1:-1]
        return inner.replace(r"\'", "'").replace(r"\\", "\\").replace("''", "'") # standard SQL escape is '' typically
    if val_str.startswith("0x"):
        # Hex string / binary
        return val_str
    try:
        if "." in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        return val_str

def parse_insert_values(values_str):
    """
    Parses the VALUES part of an INSERT statement: (1, 'a'), (2, 'b')
    Returns a list of lists.
    This is the tricky part usually done by a lexer.
    We will implement a simple state machine.
    """
    rows = []
    current_row = []
    current_val = []
    in_string = False
    escaped = False
    
    # Iterate through chars
    # We expect the string to start with '(' and end with ')' (for the last row)
    
    # Quick hack: If the file is extremely consistent, we might be able to split by "), ("
    # But usually text fields ruin that.
    
    # Let's try a scan
    vals = []
    
    idx = 0
    length = len(values_str)
    
    # Values represent a list of rows
    # Format: (val1, val2), (val3, val4)
    
    # We will split into row strings first if possible, but simplest is to parse char by char
    
    row_start = False
    val_start = False
    quote_char = None
    
    # Optimization: processing 50MB by char in Python is slow.
    # PHP/Drupal dumps are usually: INSERT INTO x VALUES (row1), (row2);
    # Regex split might be safer if we assume standard formatting.
    # Split by `), (` is risky if content has it.
    
    # Let's try to interpret the structure.
    # state: OUTSIDE_ROW, IN_ROW, IN_VAL, IN_STRING
    
    state = "OUTSIDE_ROW"
    current_token = []
    
    for i, char in enumerate(values_str):
        if state == "OUTSIDE_ROW":
            if char == '(':
                state = "IN_ROW"
                current_row = []
        elif state == "IN_ROW":
            if char == ')':
                # End of row
                # Flush last token
                if current_token:
                    val = "".join(current_token).strip()
                    if val.endswith(","): val = val[:-1] # Should not happen if logic is correct
                    current_row.append(parse_sql_value(val))
                    current_token = []
                
                rows.append(current_row)
                state = "OUTSIDE_ROW"
            elif char == "'":
                state = "IN_STRING"
                current_token.append(char)
            elif char == ',':
                # End of value
                val = "".join(current_token).strip()
                current_row.append(parse_sql_value(val))
                current_token = []
            else:
                current_token.append(char)
        elif state == "IN_STRING":
            current_token.append(char)
            if char == "'" and not escaped:
                state = "IN_ROW" # Back to row
            
            if char == '\\':
                escaped = not escaped
            else:
                escaped = False

    return rows

def parse_insert_values_simple(values_str):
    """
    A simpler parser that assumes standard mysqldump format.
    It splits by `),(`.
    WARNING: usage of `),(` in text content will break this.
    """
    # Remove leading ( and trailing ); or )
    s = values_str.strip()
    if s.endswith(";"): s = s[:-1].strip()
    if s.endswith(","): s = s[:-1].strip()
    
    if s.startswith("("): s = s[1:]
    if s.endswith(")"): s = s[:-1]
    
    # Split by "), (" or "),("
    # Regex for split
    row_strings = re.split(r"\),\s*\(", s)
    
    rows = []
    for rs in row_strings:
        # Now parse a single row: val1, 'val2', ...
        # csv module might handle this if we treat ' as quote char
        # But CSV doesn't handle NULL or Numbers mixed well without custom dialect
        
        # Simple scan for comma, respecting quotes
        vals = []
        curr = []
        in_quote = False
        escape = False
        
        for char in rs:
            if in_quote:
                curr.append(char)
                if char == "'" and not escape:
                    in_quote = False # potential end
                    # Check if next char is ' (sql escape)
                    # Use a lookahead assumption or fix later
                if char == "\\" and not escape:
                    escape = True
                else:
                    escape = False
            else:
                if char == "'":
                    in_quote = True
                    curr.append(char)
                elif char == ",":
                    vals.append("".join(curr))
                    curr = []
                else:
                    curr.append(char)
        
        if curr:
            vals.append("".join(curr))
            
        # Post-process values
        parsed_vals = [parse_sql_value(v) for v in vals]
        rows.append(parsed_vals)
        
    return rows


# Better approach for large file: State-based scan of the whole VALUES section is too slow?
# No, let's just use the python `csv` library logic but custom?
# Actually, the file is 50MB. Reading it line by line and regex matching is OK.

def extract_data(sql_file: Path, *, progress: bool = False, progress_interval_s: float = 2.0):
    schemas = {}
    data = {}
    
    print(f"Reading {sql_file}...")
    
    current_table = None
    current_insert_table = None
    current_insert_cols = []
    
    # Pre-initialize data lists
    for t in DESIRED_TABLES:
        data[t] = []

    rows_by_table = {t: 0 for t in DESIRED_TABLES}
    last_progress = time.monotonic()
    last_table = None

    def maybe_report_progress(force: bool = False):
        nonlocal last_progress
        if not progress:
            return
        now = time.monotonic()
        if not force and (now - last_progress) < progress_interval_s:
            return
        last_progress = now

        products = rows_by_table.get("commerce_product_field_data", 0)
        variations = rows_by_table.get("commerce_product_variation_field_data", 0)
        orders = rows_by_table.get("commerce_order", 0)
        order_items = rows_by_table.get("commerce_order_item", 0)
        users = rows_by_table.get("users_field_data", 0)
        files = rows_by_table.get("file_managed", 0)
        table_hint = f" (table: {last_table})" if last_table else ""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(
            f"[{ts}] ...parsed rows — courses:{products:,} lessons:{variations:,} "
            f"orders:{orders:,} items:{order_items:,} users:{users:,} files:{files:,}{table_hint}"
        )

    with open(sql_file, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # 1. Parse CREATE TABLE
            if line_stripped.startswith("CREATE TABLE"):
                match = re.search(r"CREATE TABLE `(\w+)`", line_stripped)
                if match:
                    current_table = match.group(1)
                    schemas[current_table] = []
                    current_insert_table = None # Reset insert state if new table creation starts
            
            # Detect columns inside create table (simplified)
            if current_table and line_stripped.startswith("`") and not line_stripped.startswith("CREATE"):
                # `col_name` type ...
                col_match = re.search(r"`(\w+)`", line_stripped)
                if col_match:
                    schemas[current_table].append(col_match.group(1))

            if line_stripped.startswith(") ENGINE"):
                current_table = None

            # 2. Parse INSERT INTO
            if line_stripped.startswith("INSERT INTO"):
                match = INSERT_INTO_REGEX.match(line_stripped)
                if match:
                    table_name = match.group(1)
                    if table_name in DESIRED_TABLES:
                        current_insert_table = table_name
                        cols_str = match.group(2)
                        current_insert_cols = [c.strip().strip('`') for c in cols_str.split(',')]

                        last_table = current_insert_table

                        values_part = line_stripped[match.end():].strip()
                        if values_part.startswith("VALUES"):
                            values_part = values_part[6:].strip()

                        if values_part:
                            # There is content on the first line
                            try:
                                rows = parse_insert_values_simple(values_part)
                                for row in rows:
                                    if len(row) == len(current_insert_cols):
                                        data[current_insert_table].append(dict(zip(current_insert_cols, row)))
                                        rows_by_table[current_insert_table] += 1
                                        maybe_report_progress()
                            except Exception as e:
                                # print(f"Error parsing line: {e}")
                                pass

                        if line_stripped.endswith(";"):
                            current_insert_table = None
                    else:
                        current_insert_table = None
                else:
                    current_insert_table = None

            elif current_insert_table:
                # Continuation of INSERT
                # line likely starts with (
                if line_stripped.startswith("(") or line_stripped.startswith("0x"): # Sometimes just hex? No, rows are always parens
                    try:
                        rows = parse_insert_values_simple(line_stripped)
                        for row in rows:
                            if len(row) == len(current_insert_cols):
                                data[current_insert_table].append(dict(zip(current_insert_cols, row)))
                                rows_by_table[current_insert_table] += 1
                                maybe_report_progress()
                    except Exception as e:
                         # print(f"Error parsing continuation line: {e}")
                         pass
                
                if line_stripped.endswith(";"):
                    current_insert_table = None

    maybe_report_progress(force=True)
    return schemas, data

def reconstruct_json(data, *, progress: bool = False, progress_interval_s: float = 2.0):
    last_progress = time.monotonic()

    def maybe_report(stage: str, *, force: bool = False, **counts):
        nonlocal last_progress
        if not progress:
            return
        now = time.monotonic()
        if not force and (now - last_progress) < progress_interval_s:
            return
        last_progress = now

        parts = [f"{k}:{v:,}" for k, v in counts.items()]
        counts_str = (" — " + " ".join(parts)) if parts else ""
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] ...building JSON ({stage}){counts_str}")

    # Dictionaries for lookup
    products = {}
    variations = {}
    taxonomies = {}
    files = {} 
    users = {}
    
    # 0. Index Files
    if "file_managed" in data:
        for idx, fbox in enumerate(data["file_managed"], start=1):
            # Standard Drupal field is 'uri' or sometimes 'filename' but usually 'uri' stores public://path
            files[fbox.get('fid')] = fbox.get('uri')
            maybe_report("files", files=idx)

    # 0.5. Index Users
    if "users_field_data" in data:
        for idx, u in enumerate(data["users_field_data"], start=1):
            uid = u.get('uid')
            users[uid] = {
                "id": uid,
                "name": u.get('name'),
                "mail": u.get('mail'),
                "status": u.get('status'),
                "roles": [],
                "picture": None
            }
            maybe_report("users", users=idx)

    if "user__roles" in data:
        for r in data["user__roles"]:
            uid = r.get('entity_id')
            if uid in users:
                users[uid]["roles"].append(r.get('roles_target_id'))

    if "user__user_picture" in data:
        for p in data["user__user_picture"]:
            uid = p.get('entity_id')
            fid = p.get('user_picture_target_id')
            if uid in users and fid in files:
                users[uid]["picture"] = files[fid]


    # 1. Index Taxonomies
    if "taxonomy_term_field_data" in data:
        for idx, term in enumerate(data["taxonomy_term_field_data"], start=1):
            taxonomies[term.get('tid')] = term.get('name')
            maybe_report("taxonomy", terms=idx)

    # 2. Index Variations
    # Map: SKU/ID -> Variation Object
    # Group by Product ID
    vars_by_product = {}
    
    if "commerce_product_variation_field_data" in data:
        for idx, v in enumerate(data["commerce_product_variation_field_data"], start=1):
            vid = v.get('variation_id')
            pid = v.get('product_id')
            
            v_obj = {
                "id": vid,
                "sku": v.get('sku'),
                "title": v.get('title'),
                "status": v.get('status'),
                # Attach fields later
            }
            
            # Initialize linkage
            if pid not in vars_by_product:
                vars_by_product[pid] = []
            vars_by_product[pid].append(v_obj)
            
            variations[vid] = v_obj
            maybe_report("lessons", lessons=idx)

    # 3. Attach Variation Fields
    # Dates
    if "commerce_product_variation__field_lesson_dates" in data:
        for row in data["commerce_product_variation__field_lesson_dates"]:
            vid = row.get('entity_id') # Usually entity_id for fields
            if vid in variations:
                if "dates" not in variations[vid]: variations[vid]["dates"] = []
                variations[vid]["dates"].append({
                    "start": row.get('field_lesson_dates_value'),
                    "end": row.get('field_lesson_dates_end_value')
                })
    
    # Location
    if "commerce_product_variation__field_location_ref" in data:
         for row in data["commerce_product_variation__field_location_ref"]:
            vid = row.get('entity_id')
            tid = row.get('field_location_ref_target_id')
            if vid in variations:
                variations[vid]["location"] = taxonomies.get(tid, tid)

    # Teachers
    if "commerce_product_variation__field_teachers" in data:
         for row in data["commerce_product_variation__field_teachers"]:
            vid = row.get('entity_id')
            uid = row.get('field_teachers_target_id')
            if vid in variations and uid in users:
                if "teachers" not in variations[vid]: variations[vid]["teachers"] = []
                variations[vid]["teachers"].append(users[uid])

    # 4. Process Products (Courses)
    result_courses = []
    
    if "commerce_product_field_data" in data:
        for idx, p in enumerate(data["commerce_product_field_data"], start=1):
            pid = p.get('product_id')
            
            course = {
                "id": pid,
                "title": p.get('title'),
                "type": p.get('type'),
                "status": p.get('status'),
                "created": p.get('created'),
                "description": None,
                "program": None,
                "image": None,
                "category": None,
                "lessons": vars_by_product.get(pid, [])
            }
            
            products[pid] = course
            result_courses.append(course)
            maybe_report("courses", courses=idx, lessons=len(variations))

    # 5. Attach Product Fields
    # Description
    if "commerce_product__field_course_desc" in data:
        for row in data["commerce_product__field_course_desc"]:
            pid = row.get('entity_id')
            if pid in products:
                products[pid]["description"] = row.get('field_course_desc_value')

    # Program
    if "commerce_product__field_course_program" in data:
        for row in data["commerce_product__field_course_program"]:
            pid = row.get('entity_id')
            if pid in products:
                products[pid]["program"] = row.get('field_course_program_value')

    # Image
    if "commerce_product__field_course_img" in data:
        for row in data["commerce_product__field_course_img"]:
            pid = row.get('entity_id')
            fid = row.get('field_course_img_target_id')
            # Look up file path if we had file_managed
            if pid in products:
                products[pid]["image_id"] = fid
                products[pid]["image"] = files.get(fid)

    # Category
    if "commerce_product__field_course_category" in data:
        for row in data["commerce_product__field_course_category"]:
            pid = row.get('entity_id')
            tid = row.get('field_course_category_target_id')
            if pid in products:
                products[pid]["category"] = taxonomies.get(tid, tid)

    # 6. Process Orders
    # Link Orders -> Items -> Variations -> Products
    # We want to attach students/orders to the Lessons (Variations) or to the output?
    # Let's add a top-level list of orders for now, or attach "attendees" to lessons.
    
    # Let's map orders
    all_orders = []
    orders_map = {}
    
    if "commerce_order" in data:
        for idx, o in enumerate(data["commerce_order"], start=1):
            oid = o.get('order_id')
            uid = o.get('uid')
            
            order_obj = {
                "id": oid,
                "order_number": o.get('order_number'),
                "mail": o.get('mail'),
                "state": o.get('state'),
                "total_price": o.get('total_price__number'),
                "currency": o.get('total_price__currency_code'),
                "owner": users.get(uid),
                "items": []
            }
            orders_map[oid] = order_obj
            all_orders.append(order_obj)
            maybe_report("orders", orders=idx, courses=len(result_courses), lessons=len(variations))

    # Map Items
    if "commerce_order_item" in data:
        attendees_count = 0
        for idx, item in enumerate(data["commerce_order_item"], start=1):
            oid = item.get('order_id')
            vid = item.get('purchased_entity') # Check if this column exists or if it is in another field table
            
            # If purchased_entity is missing in base table (Drupal Commerce 2 usually has it in commerce_order_item table for performnace, 
            # but stricly it might be in commerce_order_item_field_data? 
            # If the script fails we will know)
            
            if oid in orders_map:
                line_item = {
                    "id": item.get('order_item_id'),
                    "type": item.get('type'),
                    "quantity": item.get('quantity'),
                    "unit_price": item.get('unit_price__number'),
                    "total_price": item.get('total_price__number'),
                    "product_variation_id": vid,
                    # We can try to attach the variation title directly
                    "product_title": variations.get(vid, {}).get('title') if vid else "Unknown"
                }
                orders_map[oid]["items"].append(line_item)
                
                # Reverse link: Add student to lesson
                if vid in variations:
                   if "attendees" not in variations[vid]: variations[vid]["attendees"] = []
                   # The attendee is the owner of the order? Or separate registration entity?
                   # Assuming order owner for now.
                   if orders_map[oid]["owner"]:
                       variations[vid]["attendees"].append({
                           "name": orders_map[oid]["owner"]["name"],
                           "mail": orders_map[oid]["owner"]["mail"],
                           "order_id": oid
                       })
                       attendees_count += 1

            maybe_report(
                "participants",
                items=idx,
                participants=attendees_count,
                courses=len(result_courses),
                lessons=len(variations),
            )

        maybe_report(
            "done",
            force=True,
            courses=len(result_courses),
            lessons=len(variations),
            orders=len(all_orders),
            participants=attendees_count,
        )

    return {"courses": result_courses, "orders": all_orders, "teachers": [u for u in users.values() if "lesgever" in u["roles"] or u["id"] in [t["id"] for c in result_courses for l in c["lessons"] if "teachers" in l for t in l["teachers"]]]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract course/order data from a Drupal Commerce SQL dump")
    parser.add_argument("--sql-file", type=Path, default=SQL_FILE, help="Path to the SQL dump")
    parser.add_argument("--output-file", type=Path, default=OUTPUT_FILE, help="Path to write the extracted JSON")
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Print periodic progress updates while parsing and building JSON",
    )
    parser.add_argument(
        "--progress-interval",
        type=float,
        default=2.0,
        help="Minimum seconds between progress messages (default: 2.0)",
    )
    args = parser.parse_args()

    schemas, data = extract_data(args.sql_file, progress=args.progress, progress_interval_s=args.progress_interval)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] Extraction complete. Reconstructing JSON...")
    json_output = reconstruct_json(data, progress=args.progress, progress_interval_s=args.progress_interval)

    # Save
    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_file, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=2, default=str)

    courses_count = len(json_output.get("courses", []))
    lessons_count = sum(len(c.get("lessons", [])) for c in json_output.get("courses", []))
    participants_count = sum(
        len(l.get("attendees", []))
        for c in json_output.get("courses", [])
        for l in c.get("lessons", [])
        if isinstance(l, dict)
    )
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[{ts}] Saved {courses_count} courses, {lessons_count} lessons, {participants_count} participants to {args.output_file}"
    )
