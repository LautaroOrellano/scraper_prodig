from playwright.sync_api import Page
from browser.humanizer.human_mouse import human_move_to_element
from browser.humanizer.human_typing import human_type
import time

def scrape_facebook_page(page: Page):
    """
    Extrae datos públicos de un perfil/página de Facebook.
    No requiere login y funciona sobre páginas business estándar.
    """

    data = {
        "fb_nombre": None,
        "fb_categoria": None,
        "fb_sitio_web": None,
        "fb_direccion": None,
        "fb_telefono": None,
        "fb_seguidores": None,
        "fb_bio": None,
    }

    try:
        page.wait_for_selector("body", timeout=8000)
    except:
        return {"status": "error", "reason": "no_body_loaded"}

    # Nombre
    try:
        data["fb_nombre"] = page.locator("h1").first.inner_text().strip()
    except:
        pass

    # Categoría (suele aparecer debajo del nombre)
    try:
        data["fb_categoria"] = page.locator("div:below(h1)").nth(1).inner_text().strip()
    except:
        pass

    # Seguidores
    try:
        seguidores = page.locator("div:has-text('seguidores')").first.inner_text()
        data["fb_seguidores"] = seguidores.replace("seguidores", "").strip()
    except:
        pass

    # Información
    about_selectors = [
        "div[role='main'] div:has-text('Información')",
        "div[role='main'] section div"
    ]

    for sel in about_selectors:
        try:
            info_section = page.locator(sel).all()
            for block in info_section:
                text = block.inner_text()

                if "www." in text or "http" in text:
                    data["fb_sitio_web"] = text.strip()

                if "Tel" in text or "+" in text:
                    data["fb_telefono"] = text.strip()

                if "Dirección" in text or "Address" in text:
                    data["fb_direccion"] = text.strip()

                if len(text.split()) > 6 and not data["fb_bio"]:
                    data["fb_bio"] = text.strip()

        except:
            pass

    return {"status": "ok", "data": data}



def find_facebook_page(page: Page, maps_data: dict):
    """
    Busca una página de Facebook en Google usando los datos del Excel.
    Luego delega el scraping al método `scrape_facebook_page`.
    """

    query = f"{maps_data['nombre']} {maps_data['ciudad']} facebook"
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
        if href and "facebook.com" in href and "pages" in href and "google" not in href:
            print(f"🎯 Link candidato: {href}")
            target = link
            break

    if not target:
        print("❌ No se encontró página de Facebook.")
        return {"status": "error", "reason": "no_facebook_found"}

    # Movimiento humano
    box = target.bounding_box()
    if box:
        human_move_to_element(page, box, 100, 100)
        time.sleep(0.3)

        print("👆 Entrando a Facebook...")
        with page.expect_navigation(timeout=30000):
            page.mouse.click(box["x"] + 10, box["y"] + 10)

    time.sleep(3)

    # Si Facebook lo redirige al login → podemos seguir igual si muestra preview.
    if "login" in page.url:
        print("⛔ Redireccionado a login. Intentando scrap limitado...")

    # Scraper principal
    return scrape_facebook_page(page)
