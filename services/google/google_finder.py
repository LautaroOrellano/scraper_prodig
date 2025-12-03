import time
import random
from playwright.sync_api import Page
from scraper_services.core.instagram_scraper import find_instagram_profile
from scraper_services.core.facebook_scraper import find_facebook_page


class GoogleProfileSearcher:

    def __init__(self, delay=(1.2, 2.3)):
        self.dmin, self.dmax = delay

    def wait(self):
        time.sleep(random.uniform(self.dmin, self.dmax))

    # ---------------------------
    def google_search(self, page: Page, query: str):
        print(f"🔍 Buscando en Google: {query}")
        page.goto("https://www.google.com/?hl=es")

        try:
            btn = page.locator("button:has-text('Aceptar todo')")
            if btn.is_visible():
                btn.click()
        except:
            pass

        page.wait_for_selector("textarea[name='q']")
        page.click("textarea[name='q']")
        page.keyboard.type(query, delay=80)
        page.keyboard.press("Enter")

        page.wait_for_selector("#search")
        self.wait()

    # ---------------------------
    def find_first_result(self, page: Page, domain: str):
        links = page.locator("#search a")
        total = links.count()

        for i in range(min(40, total)):
            href = links.nth(i).get_attribute("href") or ""
            if domain in href and "maps" not in href and "google" not in href:
                return href

        return None

    # ---------------------------
    def open_tab(self, page: Page, url: str):
        print(f"➡️ Abriendo: {url}")
        tab = page.context.new_page()
        tab.goto(url, timeout=30000)
        return tab

    # ---------------------------
    def scrape_instagram(self, page: Page, empresa, ciudad):

        queries = [
            f"{empresa} {ciudad} instagram",
            f"{empresa} instagram",
            f"{empresa} {ciudad} ig"
        ]

        for q in queries:
            self.google_search(page, q)
            url = self.find_first_result(page, "instagram.com")
            if not url:
                continue

            tab = self.open_tab(page, url)
            try:
                data = find_instagram_profile(tab)
            finally:
                tab.close()

            if data and data.get("username"):
                return {"success": True, "data": data, "url": url}

        return {"success": False}

    # ---------------------------
    def scrape_facebook(self, page: Page, empresa, ciudad):

        queries = [
            f"{empresa} {ciudad} facebook",
            f"{empresa} facebook",
            f"{empresa} {ciudad} fb"
        ]

        for q in queries:
            self.google_search(page, q)
            url = self.find_first_result(page, "facebook.com")
            if not url:
                continue

            tab = self.open_tab(page, url)
            try:
                data = find_facebook_page(tab)
            finally:
                tab.close()

            if data and data.get("page_name"):
                return {"success": True, "data": data, "url": url}

        return {"success": False}
