import shutil
import os
import sys
import time
from playwright.sync_api import sync_playwright

def verify_trimming_ux():
    port = 8000
    os.system(f"kill $(lsof -t -i:{port}) 2>/dev/null || true")

    import subprocess
    server_process = subprocess.Popen([sys.executable, "-m", "http.server", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Started HTTP server on port {port}")

    time.sleep(2)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(f"http://localhost:{port}/index.html")
            page.click("a[href='#data-trimming']")
            page.wait_for_selector("#data-trimming")

            test_file_path = "testData/Take 2025-06-06 Normal Pad.csv"
            if not os.path.exists(test_file_path):
                print("Test file not found")
                return

            print(f"Uploading {test_file_path}...")
            with page.expect_file_chooser() as fc_info:
                page.click("label[for='csv-file-trimming']")
            fc_info.value.set_files(test_file_path)

            page.wait_for_selector("#trimming-ui:not(.hidden)", timeout=10000)
            print("File processed.")

            # Check Rigid Body Selection
            options = page.locator("#trimming-rigidbody-select option")
            option_texts = options.all_text_contents()
            print("Options:", option_texts)

            # Check if duplicates are handled
            red_bodies = [t for t in option_texts if "Red_body" in t]
            print("Red_body entries:", red_bodies)

            if len(red_bodies) < 2:
                print("WARNING: Expected multiple Red_body entries if duplicates exist.")

            # Select first Red_body
            page.select_option("#trimming-rigidbody-select", label=red_bodies[0])

            # Take screenshot to verify data visualization
            page.wait_for_timeout(1000)
            page.screenshot(path="verification_trimming_ux.png")
            print("Screenshot saved to verification_trimming_ux.png")

            # Note: We can't easily verify drag interaction via headless script without complex mouse event simulation.
            # But the presence of options and successful chart rendering is a good sign.

    except Exception as e:
        print(f"Verification failed: {e}")
        raise e
    finally:
        server_process.terminate()

if __name__ == "__main__":
    verify_trimming_ux()
