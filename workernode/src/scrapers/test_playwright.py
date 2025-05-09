# test_playwright_no_proxy.py (Modified for no proxy, headless)
import asyncio
from playwright.async_api import async_playwright, Frame

async def main():
    # Proxy details removed as we are not using a proxy
    # proxy_details = { ... }

    target_url = "https://ww19.0123movie.net/movie/alien-romulus-1630857469.html"

    print(f"--- Testing URL (NO PROXY): {target_url} ---")

    async with async_playwright() as p:
        # Updated print statement
        print(f"Launching browser (Headless: True, No Proxy)...")
        browser = None
        try:
            browser = await p.chromium.launch(
                headless=True,  # Set explicitly to True
                proxy=None,     # Set explicitly to None to disable proxy
                args=['--no-sandbox']
            )
            print("Browser launched.")

            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                ignore_https_errors=True
            )
            print("Context created.")

            page = await context.new_page()
            print(f"Page created. Navigating to: {target_url}")

            # Listeners (Corrected typo)
            page.on("request", lambda request: print(f">> Request: {request.method} {request.url}"))
            page.on("response", lambda response: print(f"<< Response: {response.status} {response.url}"))
            page.on("framenavigated", lambda frame: print(f"NAVIGATED to frame URL: {frame.url} (Main: {frame.is_main_frame()})"))

            await page.goto(target_url, timeout=60000, wait_until="domcontentloaded")

            print(f"--- Navigation Complete ---")
            print(f"Final Page URL: {page.url}")
            print(f"Page title: {await page.title()}")

            print("Page content snapshot (first 500 chars):")
            content = await page.content()
            print(content[:500])

            # No need for sleep in headless mode

        except Exception as e:
            print(f"An error occurred: {type(e).__name__} - {e}")
            import traceback
            traceback.print_exc()
        finally:
            if browser and browser.is_connected():
                await browser.close()
                print("Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())