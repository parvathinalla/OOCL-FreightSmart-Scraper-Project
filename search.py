import re
from playwright.sync_api import sync_playwright

def perform_search(token, origin, destination, cargo_ready_date, container_type):
    """
    Perform the freight quote search on FreightSmart using the provided parameters.
    Requires a valid session token for authentication.
    Returns the raw HTML content of the results section (or page) for parsing.
    """
    search_url = "https://freightsmart.oocl.com/en/quote/e-spot/"   
    content = ""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        context = browser.new_context()
        context.add_cookies([{
            "name": "token",
            "value": token,
            "domain": "freightsmart.oocl.com",
            "path": "/",
            "httpOnly": True,
            "secure": True
        }])
        page = context.new_page()
        page.goto(search_url, timeout=60000)
        try:
            page.wait_for_selector("input", timeout=10000)
        except Exception:
            pass

        filled = False
        for selector in ['input[name="origin"]', 'input#origin', 'input[placeholder*="Origin"]']:
            if not filled:
                try:
                    page.fill(selector, origin)
                    filled = True
                except Exception:
                    continue
        if not filled:
            raise Exception("Origin input field not found or could not be filled")
        try:
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
        except Exception:
            pass

        filled = False
        for selector in ['input[name="destination"]', 'input#destination', 'input[placeholder*="Destination"]']:
            if not filled:
                try:
                    page.fill(selector, destination)
                    filled = True
                except Exception:
                    continue
        if not filled:
            raise Exception("Destination input field not found or could not be filled")
        try:
            page.keyboard.press("ArrowDown")
            page.keyboard.press("Enter")
        except Exception:
            pass

        try:
            page.select_option('select[name="containerType"]', value=container_type)
        except Exception:
            try:
                page.click(f"text={container_type}")
            except Exception:
                try:
                    page.fill('input[name="containerType"]', container_type)
                except Exception:
                    pass

        filled = False
        for selector in ['input[name="date"]', 'input[name="cargoReadyDate"]', 'input[type="date"]']:
            if not filled:
                try:
                    page.fill(selector, cargo_ready_date)
                    filled = True
                except Exception:
                    continue
        try:
            page.keyboard.press("Enter")
        except Exception:
            pass

        search_clicked = False
        try:
            page.click("button:has-text(\"Search\")")
            search_clicked = True
        except Exception:
            try:
                page.get_by_role("button", name="Search").click()
                search_clicked = True
            except Exception:
                pass
        if not search_clicked:
            try:
                page.keyboard.press("Enter")
            except Exception:
                pass

        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        try:
            page.wait_for_selector("text=USD", timeout=10000)
        except Exception:
            pass

        content = page.content()
        browser.close()

    return content
