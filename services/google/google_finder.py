from playwright.sync_api import Page
from browser.humanizer.human_mouse import human_move_to_element
from browser.humanizer.human_typing import human_type
from scraper_service.core.instagram_scraper import scrape_instagram_profile
import time


class GoogleProfileSearcher:

    def __init__(self, human_delay=(1.2, 2.6)):
        self.min_delay, self.max_delay = human_delay

    def _human_idle(self):
        """Pequeña pausa humana aleatoria."""
        import random
        time.sleep(random.uniform(self.min_delay, self.max_delay))

    def _google_search(self, page: Page, query: str) -> list:
        """
        Hace una búsqueda en Google y devuelve una lista de links candidatos.
        """

        print(f"🔍 Buscando en Google: {query}")

        page.goto("https://www.google.com/webhp?hl=es")

        # Aceptar cookies si aparecen
        try:
            cookie_btn = page.locator("button:has-text('Aceptar todo')")
            if cookie_btn.is_visible():
                cookie_btn.click()
        except:
            pass

        # Input de búsqueda
        try:
            page.wait_for_selector("textarea[name='q']", timeout=6000)
            page.click("textarea[name='q']")
            human_type(page, query)
            page.keyboard.press("Enter")
        except Exception as e:
            print(f"⚠️ Error en búsqueda Google: {e}")
            return []

        page.wait_for_selector("#search", timeout=15000)
        self._human_idle()

        links = page.locator("#search a").all()
        candidates = []

        for link in links:
            href = link.get_attribute("href")
            if not href:
                continue

            if ("instagram.com" in href and
                "/p/" not in href and
                "google" not in href):
                candidates.append(link)

        return candidates

    def find_instagram_profile(self, page: Page, queries: list):
        """
        Prueba múltiples queries hasta encontrar un perfil válido.
        """

        for query in queries:

            candidates = self._google_search(page, query)

            if not candidates:
                print(f"❌ No hubo candidatos con: {query}")
                continue

            for link in candidates:
                box = link.bounding_box()
                href = link.get_attribute("href")

                print(f"🎯 Candidato encontrado: {href}")

                if not box:
                    continue

                # Movimiento humano
                human_move_to_element(page, box, 100, 100)
                time.sleep(0.3)

                with page.expect_navigation(timeout=30000):
                    page.mouse.click(box["x"] + 10, box["y"] + 10)

                self._human_idle()

                # login wall
                if "login" in page.url:
                    print("⛔ Login wall detectado.")
                    # seguimos scrapeando igual

                # Scraper Instagram
                data = scrape_instagram_profile(page)

                if data and data.get("username"):
                    print("✅ Perfil válido encontrado")
                    return {
                        "success": True,
                        "selected_query": query,
                        "candidate_url": href,
                        "instagram_data": data
                    }

                print("❌ Este candidato no era un perfil válido.")

        return {
            "success": False,
            "error": "no_profile_found",
            "instagram_data": None
        }
