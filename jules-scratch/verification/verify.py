
import asyncio
from playwright.async_api import async_playwright, expect
import csv
import random

async def main():
    # Generate a large sample CSV file
    num_points = 6000
    header = "Motive:Take 2025-10-29.csv,,,,,,\\n"
    header += "Format Version,1.23,,,,,,\\n"
    header += "Take Name,SampleTake,,,,,,\\n"
    header += "Capture Frame Rate,120,,,,,,\\n"
    header += "Export Frame Rate,120,,,,,,\\n"
    header += f"Total Frames,{num_points},,,,,,\\n"
    header += ",,Type,Rigid Body,Rigid Body,Rigid Body\\n"
    header += ",,Name,TestRigidBody,TestRigidBody,TestRigidBody\\n"
    header += ",,Property,Position,Position,Position\\n"
    header += "Frame,Time (Seconds),,X,Y,Z\\n"

    with open("jules-scratch/verification/large_sample.csv", "w") as f:
        f.write(header)
        for i in range(num_points):
            time = i * 0.01
            x = 10 * random.random()
            y = 10 * random.random()
            z = 10 * random.random()
            f.write(f"{i+1},{time:.6f},,{x:.6f},{y:.6f},{z:.6f}\\n")


    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.goto("http://localhost:8000")

        # Navigate to Wide Area Analysis Tool
        await page.click('a[href="#wide-area-analysis"]')
        await expect(page.get_by_role("heading", name="広域解析ツール")).to_be_visible()

        # Upload CSV file
        async with page.expect_file_chooser() as fc_info:
            await page.locator('label[for="csv-files-wide"].cursor-pointer').click()
        file_chooser = await fc_info.value
        await file_chooser.set_files("jules-scratch/verification/large_sample.csv")
        await expect(page.locator('.rigidbody-checkbox-wide')).to_be_visible()

        # Check no downsampling
        await page.check("#no-downsampling-checkbox-wide")

        await page.click("#analyze-btn-wide")
        await expect(page.locator("#results-card-wide")).to_be_visible()

        # Verify that the simplification notice is displayed
        await expect(page.locator("#simplification-notice-wide")).to_be_visible()

        await page.screenshot(path="jules-scratch/verification/verification.png")
        await browser.close()

asyncio.run(main())
