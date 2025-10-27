from playwright.sync_api import sync_playwright, expect

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        try:
            page.goto("http://127.0.0.1:7860")

            # Verify the main interaction tab
            expect(page.get_by_label("Simulated Input")).to_be_visible()
            page.screenshot(path="jules-scratch/verification/01_manual_interaction.png")

            # In Gradio, tabs are buttons. Use get_by_role to click them.
            # Verify the Reddit tab
            page.get_by_role("button", name="Reddit Content").click()
            expect(page.get_by_label("Subreddit")).to_be_visible()
            page.screenshot(path="jules-scratch/verification/02_reddit_tab.png")

            # Verify the Twitter tab
            page.get_by_role("button", name="X (Twitter) Content").click()
            expect(page.get_by_label("Twitter Username")).to_be_visible()
            page.screenshot(path="jules-scratch/verification/03_twitter_tab.png")

            # Verify the Memory tab
            page.get_by_role("button", name="Memory Management").click()
            expect(page.get_by_text("Sarjana's Memory")).to_be_visible()
            page.screenshot(path="jules-scratch/verification/04_memory_tab.png")

            print("All screenshots taken successfully.")

        except Exception as e:
            print(f"An error occurred: {e}")
            page.screenshot(path="jules-scratch/verification/error.png")

        finally:
            browser.close()

if __name__ == "__main__":
    run_verification()
