from playwright.sync_api import sync_playwright
from scraper_service import find_instagram_profile
from scraper_service import  create_stealth_persistent_context, STEALTH_JS


def run_scraper():
    business = {
        "nombre": "mar de salina",
        "ciudad": "Mar del Plata",
        "pais": "Argentina",
        "categoria": "Rebosado"
    }

    with sync_playwright() as p:
        print("🔵 Iniciando navegador...")
        context = create_stealth_persistent_context(
            p,
            user_data_dir=r"C:\Users\NoxiePC\AppData\Local\Microsoft\Edge\User Data",
            channel="msedge",
            headless=False
        )

        context.add_init_script(STEALTH_JS)
        page = context.new_page()

        print("\n🔎 Scrapeando Instagram...")
        instagram_data = find_instagram_profile(page, business, tipo="instagram")

        print("\n📌 DATOS FINALES:")
        print(instagram_data)

        # page.pause() # Descomenta si quieres dejarlo abierto para ver
        context.close()
        print("\n✔ Listo.")


if __name__ == "__main__":
    run_scraper()