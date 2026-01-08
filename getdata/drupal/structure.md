<head></head>
# System Architecture & Database Schema Documentation

Subject: Academic Course Management System (Drupal Commerce Implementation)

Context: This system utilizes a Drupal Commerce structure to manage academic curricula. "Products" are mapped to Courses, and "Variations" are mapped to Lessons.

* * *

## 1. High-Level Architectural Mapping

The system relies on a specific mapping of academic concepts to e-commerce entities. The developer must understand this translation to navigate the database relationships.

- **Cursus (Course) $\rightarrow$ Product Display (Entity):** The container node that holds general description and program info. It implies the marketing page.
- **Les (Lesson) $\rightarrow$ Product Variation:** The actual sellable SKU. A course can have multiple lessons (e.g., different dates or locations). This entity holds the price, stock (seats), and schedule.
- **Order $\rightarrow$ Transaction:** The financial record linking a payer (Billing Profile) to the items purchased.
- **Inschrijving (Registration) $\rightarrow$ Line Item Reference:** The registration data acts as the "ticket" inside an order. It links a specific student (Cursist) to a specific Lesson.

* * *

## 2. Entity Detail & Data Dictionary

### A. Cursus (The "Entity" / Container)

**Role:** Stores static, high-level program information shared across all lessons.

- **Identity:** Title, Cursusnummer, ODB-nummer.
- **Categorization:** Cursus Type, Academiejaar (Taxonomy), Categorie, Interessegebied.
- **Content:** Beschrijving, Programma, Programma-overzicht, Infobrochure, Afbeelding.
- **Settings:** Published (y/n), Micro-credentials (y/n), Voertaal (Language), Streamed (y/n), Sort order.
- **Relations:**

    - **Organiserende instelling**
    - **Coördinatoren:** (One-to-many user reference)
    - **Partners:** (One-to-many reference)
    - **Gerelateerde cursussen:** (Entity reference)

### B. Les (The "Variation" / Sellable Unit)

**Role:** The specific instance of a course occurring at a specific time/place. This is what the user adds to the cart.

- **Core Data:** Title, Published (y/n), Description, Remarks.
- **Logistics:**

    - **Dates:** Datum van/tot (Multiple date ranges allowed).
    - **Location:** Locatie (Taxonomy).
    - **Stock/Capacity:** Type (Online/Onsite), Max # deelnemers ter plaatse, Datum automatisch afsluiten.
    - **Status:** Geannuleerd (y/n), On demand (y/n).
- **Pricing:** Basisinfo, Basisprijs, Uitzonderingsprijzen (Taxonomy based), Met waardebon (y/n).
- **Access Control:** Toelatingsvoorwaarden, 3de master toegelaten (y/n), Voorafgaande les nodig (y/n).
- **Education Logic:**

    - **Teachers:** Lesgevers (User reference).
    - **Certificates:** Type (Attest/Getuigschrift/None), Info for certificate, Name of training on certificate, VOV (Flemish leave) eligible (y/n), Bijscholingspunten.
    - **Media:** Media-items (Video/Live feed), Moderator user.

### C. Inschrijving (The Registration)

**Role:** Represents the attendee's ticket. It sits between the Order and the Lesson.

- **Attendee Data:** Voornaam, Familienaam, Emailadres, Phone, RRN/INSZ (National ID).
- **Context:** Type (Onsite vs Online), Internal notes.
- **Validation:** Attest voor VOV requested (y/n), Aangepaste aanwezigheid info (y/n).

### D. Order & Facturatie (The Transaction)

**Role:** Handles the financial state.

- **Order Header:**

    - **Status:** Order activity/State (Draft, Completed, etc.).
    - **Sync:** SAP sync status, SAP Order ID, SAP Invoice ID, SAP Payment status.
- **Line Items:** Contains "Product variation" and "Quantity".
- **Discounts:** Coupon, Voucher codes, Adjustments, Exception group.
- **Facturatieprofiel (Billing Profile):**

    - **Identity:** Type (VAT liable/not), Organization, First Name, Last Name.
    - **Contact:** Address, Country, Postal code, Email, City.
    - **System:** SAP reference, Linked User.

### E. User

**Role:** Represents all actors (Students, Teachers, Coordinators).

- **Role/Status:** Status (Blocked/Active), Role (Teacher/Coordinator/Secretariat/Debtors).
- **Details:** Name, Address, Phone, Mobile, Graduated year.
- **System:** SAP customer numbers, Internal remarks.

### F. Budget Record

**Role:** Financial tracking per lesson.

- **Fields:** Income/Expense, Budget category, Price.
- **Relations:** Links to Lesson, Teacher.
- **Status:** Payment status (Unknown/Not paid/Paid/Accredited/Settlement).

* * *

## 3. Key Relationships & Logic Flows

### 1. The Purchase Flow

1. **Selection:** User selects a `Cursus` (Entity).
2. **Variation:** User chooses a specific `Les` (Variation).
3. **Cart:** User enters `Inschrijving` details (Attendee Name/Email).
4. **Checkout:** User (or a separate Payer) provides a `Facturatieprofiel`.
5. **Completion:** `Order` is generated.

    - **Trigger:** Order moves from Draft to "Klaar" (Done).
    - **Output:** An email is sent.
    - **Sync:** Data is pushed to SAP (Sales Header/Items).

### 2. The Teacher/Budget Flow

- **Linkage:** A `User` with role "Lesgever" is linked to a `Les`.
- **Financials:** A `Budget Record` is created for the lesson.

    - This tracks Income/Expenses per lesson.
    - It links the Price, Lesson, and Teacher together.
    - Tracks Payment Status (e.g., "Geaccrediteerd" or "Betaald").

### 3. Credit Note / Refund Logic

- A `Credit Note` is not just a financial document; it has a functional impact on the course logic.
- **Effect:** It sets the budget record of the lesson to 0 euro.
- **Link:** Explicitly links back to `Van toepassing op les(sen)` (Applicable to lessons).

* * *

## 4. External Integrations (SAP)

The system has a rigid dependency on SAP for financial records.

- **Data Fields:** The system stores `SAP klantennummers` on the User and `SAP reference` on the Billing Profile.
- **Logging:** The system logs specific SAP messages (e.g., `SALES_HEADER_IN succesvol verwerkt`).
- **Direction:** The sync appears to be bidirectional or at least verified (Sync count, Sync finished fields).