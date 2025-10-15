#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import datetime
import os
import requests
import subprocess
import argparse

def parse_day_arg(arg):
    """Parse the day argument and return the corresponding weekday index (0=Monday, 4=Friday)."""

    arg = arg.strip().lower()
    day_map_en = {"monday":0, "tuesday":1, "wednesday":2, "thursday":3, "friday":4}
    day_map_da = {"mandag":0, "tirsdag":1, "onsdag":2, "torsdag":3, "fredag":4}

    today_idx = datetime.datetime.today().weekday()

    if arg == "today":
        return today_idx
    elif arg == "tomorrow":
        return today_idx + 1
    elif arg in day_map_en:
        return day_map_en[arg]
    elif arg in day_map_da:
        return day_map_da[arg]
    else:
        print("Unknown day argument. Defaulting to today.")
        return today_idx

def open_pdf_and_cleanup(pdf_path):
    """Open the PDF file in Preview and delete it after closing (macOS)."""
    # AppleScript to open PDF in Preview and wait until closed
    apple_script = f'''
        tell application "Preview"
            open POSIX file "{pdf_path}"
            activate
            set startTime to current date
            repeat while ((current date) - startTime) < 30
                if (count of windows) = 0 then
                    quit
                    return
                end if
                delay 1
            end repeat
            if (count of windows) > 0 then quit
        end tell
    '''
    subprocess.run(['osascript', '-e', apple_script])
    
    # Delete the PDF after the viewer closes
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

def main():
    """Main function to fetch and display the menu PDF."""
    # --- Use argparse instead of sys.argv ---
    parser = argparse.ArgumentParser(description="Download and open Noon CPH menu PDF for a specific day.")
    parser.add_argument("day", nargs="?", default="today",
                        help="Day to fetch menu for (today, tomorrow, or weekday name in English or Danish)")
    args = parser.parse_args()

    # --- Parse the target day ---
    target_idx = parse_day_arg(args.day)
    # Only allow weekdays (0-4), no weekends
    if target_idx > 4:
        print("No menu PDF for weekends")
        return

    # --- Configuration ---
    URL = "https://www.nooncph.dk/ugens-menuer"
    DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
    CHROME_DRIVER_PATH = "/opt/homebrew/bin/chromedriver"  # replace with your path

    # Ensure download directory exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # --- Set up Selenium WebDriver with headless Chrome ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # fetch the page
    driver.get(URL)

    # --- Map weekday index to Danish day names ---
    # NOTE the site is in Danish, why we need the Danish names for matching
    weekday_map_da = {0: "mandag", 1: "tirsdag", 2: "onsdag", 3: "torsdag", 4: "fredag"}
    target_day_da = weekday_map_da[target_idx]

    # --- Find the link for the target day ---
    buttons = driver.find_elements(By.CSS_SELECTOR, "div.div-block-23.bred a")
    pdf_url = None
    for btn in buttons:
        if btn.text.strip().lower() == target_day_da:
            pdf_url = btn.get_attribute("href")
            break
    # Clean up the driver
    driver.quit()

    # If no PDF link found, exit
    if not pdf_url:
        print(f"Could not find PDF for {target_day_da}")
        return

    # --- Download the PDF ---
    pdf_path = os.path.join(DOWNLOAD_DIR, os.path.basename(pdf_url))
    with requests.get(pdf_url, stream=True) as r:
        r.raise_for_status()
        with open(pdf_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    # --- Invoke the function to open and clean up the PDF ---
    open_pdf_and_cleanup(pdf_path)

if __name__ == "__main__":
    main()
