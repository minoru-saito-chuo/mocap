from playwright.sync_api import sync_playwright
import os

def run(playwright):
    browser = playwright.chromium.launch()
    context = browser.new_context()
    page = context.new_page()

    # Get the absolute path to the index.html file
    file_path = "file://" + os.path.abspath("index.html")
    page.goto(file_path)

    # Wait for the page to be ready
    page.wait_for_load_state("networkidle")

    # Light mode screenshot
    page.screenshot(path="jules-scratch/verification/light-mode.png")

    # Switch to dark mode by executing JavaScript
    page.evaluate("""
        localStorage.setItem('theme', 'dark');
        document.documentElement.classList.add('dark');
    """)

    # Wait for styles to apply
    page.wait_for_timeout(500)

    # Dark mode screenshot
    page.screenshot(path="jules-scratch/verification/dark-mode.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
