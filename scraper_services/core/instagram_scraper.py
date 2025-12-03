import time
import random
from playwright.sync_api import Page
from browser.humanizer.human_mouse import human_move_to_element


def find_instagram_profile(page: Page):

    print("📸 Analizando perfil de Instagram...")

    # Scroll inicial
    try:
        page.mouse.wheel(0, 300)
    except:
        pass

    # -------------------------
    # META DESCRIPTION (followers, following, posts)
    # -------------------------
    meta_desc = ""
    try:
        meta_desc = page.locator('meta[property="og:description"]').get_attribute("content")
    except:
        pass

    followers, following, posts = "?", "?", "?"

    if meta_desc:
        try:
            stats = meta_desc.split(" - ")[0].split(", ")
            for s in stats:
                low = s.lower()
                if "followers" in low or "seguidores" in low:
                    followers = s.split(" ")[0]
                elif "following" in low or "seguidos" in low:
                    following = s.split(" ")[0]
                elif "posts" in low or "publicaciones" in low:
                    posts = s.split(" ")[0]
        except:
            pass

    # Username desde la URL
    username = page.url.split("instagram.com/")[-1].split("/")[0]

    # -------------------------
    # Nombre completo
    # -------------------------
    try:
        full_name = page.locator("header h2").first.inner_text()
    except:
        full_name = ""

    # -------------------------
    # BIO (texto)
    # -------------------------
    try:
        bio = page.locator("header section").first.inner_text().replace("\n", " ").strip()
    except:
        bio = ""

    # -------------------------
    # EXTRAER LINKS DE LA BIO
    # -------------------------
    bio_links = []

    try:
        # Contenedor de la bio (Instagram actual)
        bio_container = page.locator("header section").first

        link_elements = bio_container.locator("a").all()

        for link in link_elements:
            href = link.get_attribute("href")
            if href and href not in bio_links:
                # Normalizar links tipo "/link/" → transformarlos en absolutos
                if href.startswith("/"):
                    href = f"https://www.instagram.com{href}"
                bio_links.append(href)

    except Exception as e:
        print("⚠️ No se pudieron extraer los links de la bio:", str(e))

    # -------------------------
    # PRIMER POST
    # -------------------------
    first_post = None
    post_sel = "a[href^='/p/'], a[href^='/reel/']"

    try:
        page.wait_for_selector(post_sel, timeout=15000)
        link = page.locator(post_sel).first.get_attribute("href")
        if link:
            first_post = "https://www.instagram.com" + link
    except:
        pass

    # -------------------------
    # RESULTADO FINAL
    # -------------------------
    return {
        "username": username,
        "full_name": full_name,
        "followers": followers,
        "following": following,
        "posts": posts,
        "bio": bio,
        "bio_links": ", ".join(bio_links),  # <--- LOS LINKS IMPORTANTES
        "first_post": first_post
    }
