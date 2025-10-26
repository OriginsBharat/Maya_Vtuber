from playwright.sync_api import sync_playwright, expect

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            # 1. Navigate to the Gradio app
            # The default Gradio URL is 7860
            page.goto("http://127.0.0.1:7860")

            # 2. Find the input textbox and fill it
            # We use get_by_label for a robust, user-facing locator
            chat_input = page.get_by_label("Simulated Input")
            expect(chat_input).to_be_visible()
            chat_input.fill("Hello Maya, what are your thoughts on AI consciousness?")

            # 3. Click the submit button
            submit_button = page.get_by_role("button", name="Run Manual Interaction")
            submit_button.click()

            # 4. Wait for the responses to appear
            # We will wait for Sarjana's output to be filled.
            # We expect it to contain text, not be empty.
            sarjana_output = page.get_by_label("Sarjana's Response")
            expect(sarjana_output).not_to_be_empty(timeout=60000) # Increased timeout for the LLM

            durjana_output = page.get_by_label("Durjana's Response")
            expect(durjana_output).not_to_be_empty(timeout=60000)

            # 5. Take a screenshot
            page.screenshot(path="jules-scratch/verification/verification.png")
            print("Screenshot taken successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")
            # Take a screenshot anyway for debugging
            page.screenshot(path="jules-scratch/verification/error.png")

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
