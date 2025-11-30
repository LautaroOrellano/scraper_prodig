from playwright.sync_api import Page
from browser.humanizer.human_mouse import human_move_to_element
from browser.humanizer.human_typing import human_type
from scraper_service.core.instagram_scraper import scrape_instagram_profile
import time

def find_instagram_profile(page: Page, maps_data: dict):
    """
    Busca un perfil de Instagram en Google basado en los datos de Maps
    y delega el scraping al módulo instagram_scraper.
    """

    query = f"{maps_data['nombre']} {maps_data['ciudad']} instagram"
    print(f"🔍 Buscando en Google: {query}")

    page.goto("https://www.google.com/webhp?hl=es")

    # Cookies
    try:
        if page.locator("button:has-text('Aceptar todo')").is_visible():
            page.locator("button:has-text('Aceptar todo')").click()
    except:
        pass

    # Input
    try:
        page.wait_for_selector("textarea[name='q']", timeout=5000)
        page.click("textarea[name='q']")
        human_type(page, query)
        page.keyboard.press("Enter")
    except Exception as e:
        print(f"⚠️ Error en búsqueda Google: {e}")
        return {"status": "error", "reason": "google_search_failed"}

    print("⏳ Analizando resultados...")
    page.wait_for_selector("#search", timeout=10000)
    time.sleep(2)

    links = page.locator("#search a").all()
    target = None

    for link in links:
        href = link.get_attribute("href")
        if href and "instagram.com" in href and "/p/" not in href and "google" not in href:
            print(f"🎯 Link candidato: {href}")
            target = link
            break

    if not target:
        print("❌ No se encontró perfil.")
        return {"status": "error", "reason": "no_profile_found"}

    # Movimiento humano
    box = target.bounding_box()
    if box:
        human_move_to_element(page, box, 100, 100)
        time.sleep(0.3)

        print("👆 Entrando a Instagram...")
        with page.expect_navigation(timeout=30000):
            page.mouse.click(box["x"] + 10, box["y"] + 10)

    time.sleep(3)

    # Detected login wall?
    if "login" in page.url:
        print("⛔ Redireccionado a login. Intentando scrape limitado...")

    # Delegamos scraping
    data = scrape_instagram_profile(page)
    return {"status": "ok", "data": data}
