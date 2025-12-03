import re
import time
from playwright.sync_api import Page


def find_facebook_page(page: Page):

    print("📘 Analizando página de Facebook...")

    # Esperar que cargue algo útil
    try:
        page.wait_for_selector("body", timeout=10000)
    except:
        return None

    result = {
        "fb_page_name": "",
        "fb_followers": "",
        "fb_likes": "",
        "fb_bio": "",
    }

    # -----------------------------
    # 🟦 NOMBRE DE LA PÁGINA
    # -----------------------------
    try:
        # Nueva UI → <h1> visible
        header_name = page.locator("h1").first.inner_text().strip()
        if header_name:
            result["fb_page_name"] = header_name
    except:
        pass

    # -----------------------------
    # 🟦 BIO / DESCRIPCIÓN
    # -----------------------------
    try:
        # Normalmente dentro de "About" pero Facebook cambia mucho
        about_div = page.locator("div[role='main'] div:has-text('Información')").first
        if about_div:
            result["fb_bio"] = about_div.inner_text().strip()
        else:
            # Alternativa más general
            bio_generic = page.locator("div[role='main'] div").nth(10).inner_text()
            if bio_generic:
                result["fb_bio"] = bio_generic.strip()
    except:
        pass

    # -----------------------------
    # 🟦 NÚMEROS: seguidores / me gusta
    # -----------------------------
    full_text = ""
    try:
        full_text = page.locator("body").inner_text()
    except:
        full_text = ""

    # Buscar "X seguidores" o "X personas siguen esto"
    followers_patterns = [
        r"(\d[\d\.\,]*)\s*seguidores",
        r"(\d[\d\.\,]*)\s*personas siguen esto"
    ]
    for pattern in followers_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            result["fb_followers"] = match.group(1)
            break

    # Buscar "X me gusta" o "X personas les gusta esto"
    likes_patterns = [
        r"(\d[\d\.\,]*)\s*me gusta",
        r"(\d[\d\.\,]*)\s*personas les gusta esto"
    ]
    for pattern in likes_patterns:
        match = re.search(pattern, full_text, re.IGNORECASE)
        if match:
            result["fb_likes"] = match.group(1)
            break

    return result
