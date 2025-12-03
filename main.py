import time
from playwright.sync_api import sync_playwright

from services.excel.excel_reader import ExcelReader
from services.excel.excel_writer import ExcelWriter

from services.google.google_finder import GoogleProfileSearcher
from scraper_services.core.browser_manager import create_stealth_persistent_context, STEALTH_JS


def clean_value(value):
    """Devuelve siempre un string limpio, aunque el valor sea None."""
    if value is None:
        return ""
    return str(value).replace("\n", " ").strip()


def extract_city(full_address: str):
    """Extrae la ciudad desde la dirección completa."""
    if not full_address:
        return ""

    partes = full_address.split(",")
    if len(partes) >= 2:
        return partes[1].replace("B7600", "").strip()

    return full_address.strip()


def run_scraper(input_excel: str, output_excel: str):
    print("🚀 Iniciando scraper...")

    searcher = GoogleProfileSearcher()
    reader = ExcelReader()
    rows = reader.read(input_excel)
    print(f"📄 Registros a procesar: {len(rows)}")

    writer = ExcelWriter(output_excel)

    with sync_playwright() as p:
        print("🟢 Abriendo navegador con perfil persistente...")

        context = create_stealth_persistent_context(
            p,
            user_data_dir=r"C:\Users\NoxiePC\AppData\Local\Microsoft\Edge\User Data",
            channel="msedge",
            headless=False
        )

        context.add_init_script(STEALTH_JS)
        page = context.new_page()

        for idx, data in enumerate(rows, 1):

            print("\n" + "=" * 70)
            print(f"➡️ Procesando {idx}/{len(rows)} → {data['name']}")

            direccion = clean_value(data.get("formatted_address"))
            ciudad = extract_city(direccion)

            business = {
                "nombre": clean_value(data.get("name")),
                "ciudad": ciudad,
                "telefono": clean_value(data.get("formatted_phone_number")),
                "website": clean_value(data.get("website")),
                "pais": "Argentina"
            }

            result = {
                "name": business["nombre"],
                "formatted_address": direccion,
                "formatted_phone_number": business["telefono"],
                "website": business["website"],
                "instagram_usuario": "",
                "instagram_seguidores": "",
                "instagram_siguiendo": "",
                "instagram_posts": "",
                "instagram_url": "",
                "facebook_name": "",
                "facebook_likes": "",
                "facebook_followers": "",
                "facebook_url": ""
            }

            # ---------------------------------------
            # 📌 INSTAGRAM (PRIMERA BÚSQUEDA OBLIGADA)
            # ---------------------------------------
            try:
                insta = searcher.scrape_instagram(
                    page,
                    business["nombre"],
                    business["ciudad"]
                )

                if insta["success"]:
                    data_ig = insta["data"]
                    result["instagram_usuario"] = clean_value(data_ig.get("username"))
                    result["instagram_seguidores"] = clean_value(data_ig.get("followers"))
                    result["instagram_siguiendo"] = clean_value(data_ig.get("following"))
                    result["instagram_posts"] = clean_value(data_ig.get("posts"))
                    result["instagram_url"] = insta["url"]
                else:
                    result["instagram_url"] = "No encontrado"

            except Exception as e:
                result["instagram_url"] = f"ERROR: {str(e)}"

            time.sleep(1)

            # ---------------------------------------
            # 📌 FACEBOOK (SEGUNDA BÚSQUEDA OBLIGADA)
            # ---------------------------------------
            try:
                fb = searcher.scrape_facebook(
                    page,
                    business["nombre"],
                    business["ciudad"]
                )

                if fb["success"]:
                    data_fb = fb["data"]
                    result["facebook_name"] = clean_value(data_fb.get("page_name"))
                    result["facebook_likes"] = clean_value(data_fb.get("likes"))
                    result["facebook_followers"] = clean_value(data_fb.get("followers"))
                    result["facebook_url"] = fb["url"]
                else:
                    result["facebook_url"] = "No encontrado"

            except Exception as e:
                result["facebook_url"] = f"ERROR: {str(e)}"

            time.sleep(1)

            # ---------------------------------------
            # 📁 GUARDAR EN EXCEL
            # ---------------------------------------
            writer.append_row(result)

        context.close()

    print("📁 Datos guardados en:", output_excel)
    print("🎉 Scraping finalizado correctamente.")


if __name__ == "__main__":
    run_scraper(
        input_excel="maps_input.xlsx",
        output_excel="resultados_scraping.xlsx"
    )
