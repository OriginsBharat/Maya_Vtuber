from playwright.sync_api import sync_playwright

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Navigate to the Gradio app
            page.goto("http://localhost:7861")

            # Wait for the UI to load and find the "Proactive Creator" tab button
            # Gradio uses button roles for tabs, we find it by its text content.
            proactive_tab_button = page.get_by_text("Proactive Creator")
            proactive_tab_button.click()

            # Take a screenshot of the entire page
            page.screenshot(path="jules-scratch/verification/proactive_creator_ui.png")

            print("Screenshot taken successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
