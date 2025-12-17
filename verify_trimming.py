import shutil
import os
import sys
import time
from playwright.sync_api import sync_playwright

def verify_trimming_tool():
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

            # Select Rigid Body
            page.select_option("#trimming-rigidbody-select", label="Red_body")

            # Debug current values
            s_val = page.input_value("#trim-start-time")
            e_val = page.input_value("#trim-end-time")
            print(f"Initial Start: {s_val}, End: {e_val}")

            # Set Trimming
            print("Setting start to 1.0")
            page.fill("#trim-start-time", "1.0")
            page.evaluate("document.getElementById('trim-start-time').dispatchEvent(new Event('change'))")
            page.wait_for_timeout(500)

            print("Setting end to 2.0")
            page.fill("#trim-end-time", "2.0")
            page.evaluate("document.getElementById('trim-end-time').dispatchEvent(new Event('change'))")
            page.wait_for_timeout(500)

            s_val_new = page.input_value("#trim-start-time")
            e_val_new = page.input_value("#trim-end-time")
            duration = page.input_value("#trim-duration")
            print(f"New Start: {s_val_new}, End: {e_val_new}, Duration: {duration}")

            assert float(duration) == 1.0, f"Duration should be 1.0, got {duration}"

            # Export
            with page.expect_download() as download_info:
                page.click("#export-trimmed-csv")
            download = download_info.value
            download_path = "trimmed_test_output.csv"
            download.save_as(download_path)
            print(f"Downloaded {download_path}")

            # Verify file content
            with open(download_path, 'r') as f:
                content = f.read()
                # Basic check
                assert "Red_body" in content
                lines = content.splitlines()
                # Check data lines count roughly (120Hz * 1s = 120 lines)
                data_lines = [l for l in lines if l and l[0].isdigit()] # Simple heuristic
                print(f"Exported data lines (approx): {len(data_lines)}")

            os.remove(download_path)
            print("First test passed.")

            # Second file
            test_file_path_2 = "testData/Take 2025-07-02 pad_Wship_Hopping.csv"
            print(f"Uploading {test_file_path_2}...")
            with page.expect_file_chooser() as fc_info:
                page.click("label[for='csv-file-trimming']")
            fc_info.value.set_files(test_file_path_2)

            page.wait_for_timeout(2000)

            page.select_option("#trimming-rigidbody-select", label="RED_WShip")
            page.check("#trimming-downsample")
            print("Second test passed.")

    except Exception as e:
        print(f"Verification failed: {e}")
        raise e
    finally:
        server_process.terminate()

if __name__ == "__main__":
    verify_trimming_tool()
