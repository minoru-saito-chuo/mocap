import os
from playwright.sync_api import sync_playwright, Page, expect

def run_verification(page: Page):
    """
    This script verifies the 3D trajectory feature in the Wide Area Analysis Tool.
    """
    # 1. Navigate to the application's index.html file.
    file_path = os.path.abspath('index.html')
    page.goto(f'file://{file_path}')

    # 2. Navigate to the "Wide Area Analysis Tool" page.
    page.get_by_role("link", name="広域解析ツール").click()

    # 3. Upload the sample CSV file.
    wide_analysis_section = page.locator("#wide-area-analysis")
    with page.expect_file_chooser() as fc_info:
        wide_analysis_section.get_by_text("ファイルを追加", exact=True).click()
    file_chooser = fc_info.value
    file_chooser.set_files("jules-scratch/verification/sample_data.csv")

    # 4. Wait for the file to be processed by waiting for the rigidbody selection area to appear.
    expect(page.locator("#rigidbody-selection-area-wide")).to_be_visible(timeout=10000)

    # 5. Click the "Start Analysis" button.
    page.get_by_role("button", name="解析開始").click()

    # 6. Wait for analysis to complete by waiting for the results card to appear.
    expect(page.locator("#results-card-wide")).to_be_visible(timeout=10000)

    # 7. Switch to the "3D Trajectory" view.
    page.get_by_role("button", name="3D軌跡").click()

    # Give the 3D scene a moment to render
    page.wait_for_timeout(2000)

    # 8. Take a screenshot for visual verification.
    screenshot_path = "jules-scratch/verification/verification.png"
    page.locator("#3d-trajectory-container-wide").screenshot(path=screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        run_verification(page)
        browser.close()

if __name__ == "__main__":
    main()
