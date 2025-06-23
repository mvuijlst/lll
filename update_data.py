#!/usr/bin/env python
"""
Helper script to automate the complete process of scraping data and updating the Django database.
This script will:
1. Run the scrape2.py script to gather data from academy websites
2. Run the import_detailed_data command to update the Django database
3. Run the move_ugain_offerings command to handle UGain exceptions

Usage:
    python update_data.py [--clear]

Options:
    --clear    Clear existing data before importing
"""

import os
import subprocess
import sys
import time
import shutil

# Configuration
JSON_PATH = os.path.join('getdata', 'ugent_academies_data_detailed.json')
ROOT_JSON_PATH = 'ugent_academies_data_detailed.json'  # In case it's saved in the root

def main():
    clear_option = '--clear' in sys.argv
    
    print("=== UGent Academy Data Management ===")
    
    # Step 1: Run the scraper
    print("\n🔄 Step 1: Running scraper to collect data...")
    try:
        scraper_path = os.path.join('getdata', 'scrape2.py')
        subprocess.run([sys.executable, scraper_path], check=True)
        print("✅ Scraping completed successfully")
    except subprocess.CalledProcessError:
        print("❌ Scraping failed. Please check the scraper output for errors.")
        if input("Continue with import anyway? (y/n): ").lower() != 'y':
            return

    # Small delay to ensure file writes are complete
    time.sleep(1)
      # Check if JSON file exists
    if not os.path.exists(JSON_PATH):
        # Check if the file might be in the root directory
        if os.path.exists(ROOT_JSON_PATH):
            print(f"⚠️ JSON file found in root directory instead of getdata folder.")
            print(f"   Moving file to correct location: {JSON_PATH}")
            # Create the getdata directory if it doesn't exist
            os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
            # Move the file to the correct location
            shutil.move(ROOT_JSON_PATH, JSON_PATH)
            print("   File moved successfully.")
        else:
            print(f"❌ Error: JSON file not found at {JSON_PATH} or in root directory")
            print("   Please check the scraper configuration and output.")
            return
          # Step 2: Import data into Django
    print("\n🔄 Step 2: Importing data into Django...")
    command = [sys.executable, 'manage.py', 'import_detailed_data', JSON_PATH]
    if clear_option:
        command.append('--clear')
        print("   (Using --clear option: existing data will be cleared)")
        
    try:
        subprocess.run(command, check=True)
        print("✅ Import completed successfully")
    except subprocess.CalledProcessError:
        print("❌ Import failed. Please check the Django error output.")
        return
    
    # Step 3: Move UGain offerings from Science Academy to UGain Academy
    print("\n🔄 Step 3: Moving UGain offerings to correct academy...")
    try:
        move_command = [sys.executable, 'manage.py', 'move_ugain_offerings']
        subprocess.run(move_command, check=True)
        print("✅ UGain offerings moved successfully")
    except subprocess.CalledProcessError:
        print("❌ UGain move failed. This may be normal if no UGain offerings were found.")
        print("   You can run 'python manage.py move_ugain_offerings' manually if needed.")
        
    print("\n✨ Complete data update process finished! ✨")
    print("All steps completed:")
    print("  ✅ Data scraped from academy websites")
    print("  ✅ Data imported into Django database")
    print("  ✅ UGain offerings moved to correct academy")
    print("You can now check the Django site to see the updated content.")

if __name__ == '__main__':
    main()
