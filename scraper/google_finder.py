from playwright.sync_api import Page
from scraper.utils.human_mouse import human_move_to_element
from scraper.utils.human_typing import human_type
from scraper.instagram_scraper import scrape_instagram_profile
import time
import random


def google_search_social(page: Page, maps_data: dict, tipo: str):
    # Query optimizada: "site:instagram.com nombre ciudad" ayuda a filtrar basura
    query = f"{maps_data['nombre']} {maps_data['ciudad']} instagram"
    print(f"🔍 Buscando: {query}")

    page.goto("https://www.google.com/webhp?hl=es")

    try:
        # Aceptar cookies si aparecen (común en Europa/Latam a veces)
        if page.locator("button:has-text('Aceptar todo')").is_visible():
            page.locator("button:has-text('Aceptar todo')").click()
    except:
        pass

    # Buscar input
    try:
        input_sel = "textarea[name='q']"
        page.wait_for_selector(input_sel, timeout=5000)
        page.click(input_sel)
        human_type(page, query)
        page.keyboard.press("Enter")
    except Exception as e:
        print(f"⚠️ Error en búsqueda Google: {e}")
        return None

    print("⏳ Analizando resultados...")
    page.wait_for_selector("#search", timeout=10000)
    time.sleep(2)

    # Buscar links
    links = page.locator("#search a").all()
    target_link = None

    for link in links:
        href = link.get_attribute("href")
        if href and "instagram.com" in href and "/p/" not in href and "google" not in href:
            # Evitamos links directos a fotos (/p/), queremos el perfil
            target_link = link
            print(f"🎯 Link Candidato: {href}")
            break

    if target_link:
        # Movimiento visual y click
        box = target_link.bounding_box()
        if box:
            human_move_to_element(page, box, 100, 100)
            time.sleep(0.3)

            print("👆 Entrando a Instagram...")
            with page.expect_navigation(timeout=30000):
                # Click en coordenadas para ser más humano
                page.mouse.click(box["x"] + 10, box["y"] + 10)

            # Espera crítica para que cargue el perfil
            time.sleep(3)

            # Verificar si hubo Login Wall
            if "login" in page.url:
                print("⛔ Redireccionado a Login. Intentando scraping limitado...")

            return scrape_instagram_profile(page)

    print("❌ No se encontró el perfil en Google.")
    return None