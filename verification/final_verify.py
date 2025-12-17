import time
from playwright.sync_api import sync_playwright
import os

def run_verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("http://localhost:8000")

        # Upload
        page.locator("#csv-file-trimming").set_input_files("testData/Take 2025-06-06 Normal Pad.csv")
        page.locator("nav a[href='#data-trimming']").first.click()

        # Wait for chart
        page.locator("#trim-chart-x").wait_for(state="visible", timeout=10000)
        time.sleep(2)

        # Check options
        options = page.locator("#trimming-rigidbody-select option").all_inner_texts()
        print(f"Options: {options}")

        # Screenshot
        page.screenshot(path="verification/trimming_final.png")
        print("Screenshot saved to verification/trimming_final.png")

        browser.close()

if __name__ == "__main__":
    run_verify()
