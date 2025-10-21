
import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Get the absolute path to the index.html file
        index_path = os.path.abspath('index.html')

        await page.goto(f'file://{index_path}#wide-area-analysis')

        # Scope the locator to the correct section
        wide_area_analysis_section = page.locator('#wide-area-analysis')

        # Wait for the file input to be available and upload the file
        async with page.expect_file_chooser() as fc_info:
            await wide_area_analysis_section.locator('text="ファイルを追加"').click()
        file_chooser = await fc_info.value
        await file_chooser.set_files('verifications/sample.csv')

        # Wait for the rigid body selection UI to appear
        await page.wait_for_selector('#rigidbody-selection-area-wide')

        # Check if the "RigidBody" text is visible
        await page.wait_for_selector('text="RigidBody"')

        print("Rigid body selection UI is visible.")

        await page.screenshot(path='verifications/screenshot.png')
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
