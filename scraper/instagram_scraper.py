import time
import random
from playwright.sync_api import Page
# Asegúrate de que esta importación apunte a tu archivo correcto
from  scraper.utils.human_mouse import human_move_to_element


def scrape_instagram_profile(page: Page):
    """
    Versión HÍBRIDA FINAL:
    - Meta Tags para contadores (Seguidores/Seguidos).
    - DOM Filtrado para Links de Bio (Sin historias).
    - DOM Feed para el primer post real (Sin historias).
    - Movimiento de mouse visual incluido.
    """
    print("📸 Analizando perfil (Modo Híbrido + Visual)...")

    # 1. Scroll inicial humano para cargar el feed y activar imágenes
    time.sleep(1)
    try:
        page.mouse.wheel(0, 400)
        time.sleep(1.5)  # Espera a que cargue el contenido tras el scroll
    except:
        pass

    # -------------------------
    # 1. EXTRAER CONTADORES (Estrategia Meta Tags - La más fiable)
    # -------------------------
    meta_desc = ""
    try:
        meta_el = page.locator('meta[property="og:description"]').first
        if meta_el.count() > 0:
            meta_desc = meta_el.get_attribute("content")
    except:
        pass

    # -------------------------
    # FIX: PARSEO MULTILENGUAJE (Funciona en ESP / ENG / PT / FR / DE)
    # -------------------------

    followers = "No detectado"
    following = "No detectado"
    posts = "No detectado"

    if meta_desc:
        try:
            # Ejemplo ES: "1.204 seguidores, 481 seguidos, 108 publicaciones - ..."
            # Ejemplo EN: "1,204 Followers, 481 Following, 108 Posts - ..."
            # Tomamos SOLO la primera parte antes del guion.
            parts = meta_desc.split(" - ")[0]
            stats = parts.split(", ")

            for stat in stats:

                s = stat.lower()

                # --- FOLLOWERS ---
                if any(k in s for k in ["followers", "follower", "seguidores", "abonnés", "abonnenten", "seguidores"]):
                    followers = (
                        s.replace("followers", "")
                        .replace("follower", "")
                        .replace("seguidores", "")
                        .replace("abonnés", "")
                        .replace("abonnenten", "")
                        .strip()
                    )

                # --- FOLLOWING ---
                elif any(k in s for k in ["following", "seguidos", "abonnements", "abonniert"]):
                    following = (
                        s.replace("following", "")
                        .replace("seguidos", "")
                        .replace("abonnements", "")
                        .replace("abonniert", "")
                        .strip()
                    )

                # --- POSTS ---
                elif any(k in s for k in ["posts", "post", "publicaciones", "beiträge", "publications"]):
                    posts = (
                        s.replace("posts", "")
                        .replace("post", "")
                        .replace("publicaciones", "")
                        .replace("publicación", "")
                        .replace("beiträge", "")
                        .replace("publications", "")
                        .strip()
                    )

        except Exception as e:
            print(f"⚠️ Error parseando meta description: {e}")

    # -------------------------
    # 2. EXTRAER DATOS DEL HEADER (Nombre, Bio, Links)
    # -------------------------

    # Username desde la URL para asegurar
    username = page.url.split("instagram.com/")[-1].replace("/", "").split("?")[0]

    # Nombre completo
    full_name = ""
    try:
        header_section = page.locator("header section").first
        if header_section.count() > 0:
            # Busca el primer span con texto que no sea un botón
            full_name = header_section.locator("h2").first.inner_text()
            # Fallback si h2 está vacío (a veces es span)
            if not full_name:
                full_name = header_section.locator("span").first.inner_text()
    except:
        pass

    # Biografía
    bio = ""
    try:
        bio = page.locator("header section div._aacl").first.inner_text()
    except:
        try:
            # Fallback genérico: todo el texto del header menos el nombre
            bio = page.locator("header section").inner_text()
        except:
            bio = "No detectada"

    # LINKS DE LA BIO (Filtrando Historias)
    bio_links = []
    try:
        # Buscamos enlaces SOLAMENTE dentro del header
        links_elements = page.locator("header section a").all()
        for link in links_elements:
            href = link.get_attribute("href")

            # FILTRO AGRESIVO:
            # 1. Debe tener href
            # 2. NO puede ser historias (/stories/)
            # 3. NO puede ser followers/following/reels/tagged
            if href and "/stories/" not in href and "followers" not in href \
                    and "following" not in href and "reels" not in href and "tagged" not in href:
                # Si es un link externo (ej: linktr.ee) o interno válido
                bio_links.append(href)
    except:
        pass

    # -------------------------
    # 3. PRIMER POST DEL FEED (Con Mouse Visual)
    # -------------------------
    first_post = {
        "url": None,
        "is_video": False
    }

    print("🖼️ Buscando post en el Feed...")

    try:
        # SCROLL REAL OBLIGATORIO
        for _ in range(3):
            page.mouse.wheel(0, random.randint(600, 900))
            time.sleep(random.uniform(1.2, 1.7))

        # NUEVOS SELECTORES DEL FEED (2024–2025)
        feed_selector = (
            "a[href^='/p/'], a[href^='/reel/'], "
            "div.x9f619 a[href^='/p/'], div.x9f619 a[href^='/reel/']"
        )

        # 1. Esperar a que exista en el DOM
        page.wait_for_selector(feed_selector, state="attached", timeout=15000)
        time.sleep(2)  # retraso real de Instagram

        first_post_el = page.locator(feed_selector).first

        if first_post_el.count() == 0:
            print("⚠️ No se encontraron posts (grid no cargado).")
        else:
            href = first_post_el.get_attribute("href")
            first_post["url"] = f"https://www.instagram.com{href}"
            first_post["is_video"] = "/reel/" in href

            box = first_post_el.bounding_box()

            if box:
                print(f"🖱️ Moviendo cursor hacia el post: {first_post['url']}")
                human_move_to_element(page, box, 400, 300)
                time.sleep(0.5)

    except Exception as e:
        print(f"⚠️ No se pudo obtener el primer post: {e}")

    # -------------------------
    # RETORNO FINAL
    # -------------------------
    return {
        "username": username,
        "full_name": full_name,
        "followers": followers,
        "following": following,
        "posts_count": posts,
        "bio": bio.replace("\n", " ")[:150],  # Limpieza básica
        "bio_links": bio_links,
        "first_post": first_post
    }