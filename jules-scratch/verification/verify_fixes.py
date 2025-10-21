import os
import json
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Get the absolute path to the index.html file
    file_path = os.path.abspath('index.html')

    # Go to the local index.html file
    page.goto(f'file://{file_path}')

    # Navigate to the "Wide Area Analysis Tool"
    page.click('a[href="#wide-area-analysis"]')

    # Mock data to be injected
    mock_data = {
        "trajectory1": [
            {"t": 0, "x": 0, "y": 0, "z": 0},
            {"t": 1, "x": 1, "y": 1, "z": 1},
            {"t": 2, "x": 2, "y": 2, "z": 0},
            {"t": 3, "x": 3, "y": 1, "z": 1},
            {"t": 4, "x": 4, "y": 0, "z": 0}
        ]
    }

    # Inject mock data and trigger analysis and rendering
    page.evaluate(f"""
        window.lastSampledDataWide = {json.dumps(mock_data)};

        // Make the results section visible before analysis
        document.getElementById('results-card-wide').classList.remove('hidden');

        // Since analyzeDataWide is not globally accessible, we'll manually call the rendering functions
        // after setting the global data variables.
        const verticalAxis = document.getElementById('vertical-axis-wide').value;
        const axes = ['X', 'Y', 'Z'];
        const horizontalAxes = axes.filter(ax => ax !== verticalAxis);
        const hAxis1 = horizontalAxes[0];
        const hAxis2 = horizontalAxes[1];
        const gridSize = parseFloat(document.getElementById('heatmap-grid-size-wide').value) / 1000;

        window.lastHeatmapGridWide = calculateHeatmapGridWide(window.lastSampledDataWide, gridSize, hAxis1, hAxis2);
        drawTrajectoryWide(window.lastSampledDataWide, hAxis1, hAxis2);
        draw3DTrajectory(window.lastSampledDataWide);
    """)

    # Verify the 2D trajectory and heatmap view
    page.click('#show-heatmap-btn-wide')
    page.screenshot(path="jules-scratch/verification/verification_heatmap.png")

    # Verify the 3D trajectory view
    page.click('#show-3d-trajectory-btn-wide')
    page.screenshot(path="jules-scratch/verification/verification_3d.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
