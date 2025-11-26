import time
import random
import numpy as np
from playwright.sync_api import sync_playwright

# 🔥 ACTUALIZACIÓN: Forzamos tamaño Full HD (1920x1080)
# Esto asegura que el área de dibujo interna de Playwright sea grande
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080


# --- 1. FÍSICA (BEZIER) ---
def get_bezier_curve(start, end, num_points=50):
    points = []
    t_values = np.linspace(0, 1, num_points)

    ctrl1_x = start[0] + random.uniform(-200, 200)
    ctrl1_y = start[1] + random.uniform(-200, 200)
    ctrl2_x = end[0] + random.uniform(-200, 200)
    ctrl2_y = end[1] + random.uniform(-200, 200)

    for t in t_values:
        x = (1 - t) ** 3 * start[0] + 3 * (1 - t) ** 2 * t * ctrl1_x + 3 * (1 - t) * t ** 2 * ctrl2_x + t ** 3 * end[0]
        y = (1 - t) ** 3 * start[1] + 3 * (1 - t) ** 2 * t * ctrl1_y + 3 * (1 - t) * t ** 2 * ctrl2_y + t ** 3 * end[1]
        points.append({'x': x, 'y': y})
    return points


# --- 2. COMPORTAMIENTO HUMANO ---
def human_move_to_element(page, selector, current_x, current_y):
    try:
        # Esperamos a que aparezca el elemento
        page.wait_for_selector(selector, state="visible", timeout=8000)
        element = page.locator(selector).first
        box = element.bounding_box()

        if box:
            target_x = box['x'] + random.uniform(10, box['width'] - 10)
            target_y = box['y'] + random.uniform(5, box['height'] - 5)

            path = get_bezier_curve((current_x, current_y), (target_x, target_y), num_points=random.randint(40, 70))

            for point in path:
                page.mouse.move(point['x'], point['y'])
                # Intentamos mover la bolita (si existe en esta página)
                try:
                    page.evaluate(f"if(window.moveDot) window.moveDot({point['x']}, {point['y']})")
                except:
                    pass  # Si cambiamos de página y no hay bolita, no pasa nada
                time.sleep(random.uniform(0.001, 0.01))

            time.sleep(random.uniform(0.3, 0.7))
            return target_x, target_y
    except Exception as e:
        print(f"⚠️ No pude moverme al elemento {selector}: {e}")
        return current_x, current_y


def human_type(page, text):
    for char in text:
        page.keyboard.type(char)
        time.sleep(random.uniform(0.10, 0.35))


def inject_visual_cursor(page):
    """Inyecta la bolita roja en la página actual"""
    try:
        page.evaluate("""
            const dot = document.createElement('div');
            dot.id = 'mouse-helper';
            dot.style.position = 'absolute';
            dot.style.width = '15px';
            dot.style.height = '15px';
            dot.style.backgroundColor = 'rgba(255, 0, 0, 0.7)'; 
            dot.style.borderRadius = '50%';
            dot.style.zIndex = '99999';
            dot.style.pointerEvents = 'none';
            document.body.appendChild(dot);
            window.moveDot = (x, y) => {
                const dot = document.getElementById('mouse-helper');
                if(dot) {
                    dot.style.left = x + 'px';
                    dot.style.top = y + 'px';
                }
            }
        """)
    except:
        pass


# --- 3. SCRIPT PRINCIPAL ---
def run():
    with sync_playwright() as p:
        # Iniciamos navegador
        # 🔥 MODIFICACIÓN CLAVE: Mantenemos start-maximized para la ventana física
        browser = p.chromium.launch(
            headless=False,
            args=['--start-maximized']
        )

        # 🔥 MODIFICACIÓN CLAVE: Re-introducimos el viewport, pero usando el tamaño grande (1920x1080)
        # Esto fuerza que el contenido se dibuje correctamente.
        context = browser.new_context(
            viewport={'width': VIEWPORT_WIDTH, 'height': VIEWPORT_HEIGHT},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # 1. Ir a Maps
        print("📍 Entrando a Google Maps...")
        page.goto("https://www.google.com/maps?hl=es")  # Forzamos español para que los selectores funcionen
        inject_visual_cursor(page)

        # Spawn random (usando las nuevas y grandes constantes)
        mouse_x = random.randint(50, VIEWPORT_WIDTH - 50)
        mouse_y = random.randint(50, VIEWPORT_HEIGHT - 50)
        page.mouse.move(mouse_x, mouse_y)
        page.evaluate(f"window.moveDot({mouse_x}, {mouse_y})")
        time.sleep(1)

        # 2. Buscar
        print("🔍 Buscando Pizzería...")
        mouse_x, mouse_y = human_move_to_element(page, "input#searchboxinput", mouse_x, mouse_y)
        page.mouse.click(mouse_x, mouse_y)

        human_type(page, "Panda, mar del plata")
        page.keyboard.press("Enter")

        print("⏳ Esperando que cargue la ficha del lugar...")
        try:
            page.wait_for_selector("h1", timeout=10000)
            time.sleep(2)
        except:
            print("❌ No cargaron los resultados.")
            browser.close()
            return

        # 3. Buscar el botón de Sitio Web
        website_selector = "[data-item-id='authority']"

        if page.locator(website_selector).count() > 0:
            print("🌐 ¡Botón de Sitio Web encontrado! Preparando click...")

            popup_abierto = False
            intentos = 0

            while intentos < 2 and not popup_abierto:
                intentos += 1
                print(f"👆 Intento de click #{intentos}...")

                mouse_x, mouse_y = human_move_to_element(page, website_selector, mouse_x, mouse_y)

                try:
                    with page.expect_popup(
                            timeout=5000) as popup_info:
                        page.mouse.click(mouse_x, mouse_y)

                    new_page = popup_info.value
                    new_page.wait_for_load_state()
                    popup_abierto = True

                    print(f"🚀 ¡ÉXITO! Aterrizamos en: {new_page.title()}")

                    # Inyectamos bolita en la nueva web
                    inject_visual_cursor(new_page)

                    # Scroll y lectura en la nueva web
                    print("👀 Simulando lectura en la web del cliente...")
                    # Usamos el tamaño forzado para centrar el mouse
                    new_mouse_x = VIEWPORT_WIDTH / 2
                    new_mouse_y = VIEWPORT_HEIGHT / 2

                    for _ in range(3):
                        new_page.mouse.wheel(0, random.randint(100, 300))
                        time.sleep(random.uniform(1, 2))

                        # Mover mouse suavemente
                        new_mouse_x += random.randint(-50, 50)
                        new_mouse_y += random.randint(-50, 50)

                        # Usamos las constantes VIEWPORT para asegurar que no se salga del área de 1920x1080
                        new_mouse_x = max(0, min(new_mouse_x, VIEWPORT_WIDTH))
                        new_mouse_y = max(0, min(new_mouse_y, VIEWPORT_HEIGHT))

                        try:
                            new_page.mouse.move(new_mouse_x, new_mouse_y)
                            new_page.evaluate(f"if(window.moveDot) window.moveDot({new_mouse_x}, {new_mouse_y})")
                        except:
                            pass

                    print("✅ Lectura finalizada.")
                    new_page.close()

                except Exception as e:
                    print(f"⚠️ El click #{intentos} falló o no abrió pestaña. Reintentando...")
                    mouse_x += random.randint(-10, 10)
                    mouse_y += random.randint(-10, 10)
                    page.mouse.move(mouse_x, mouse_y)
                    time.sleep(1)

            if not popup_abierto:
                print("❌ No se pudo abrir la web después de 2 intentos.")

        else:
            print("❌ Este local no tiene botón de Sitio Web visible.")

        print("✅ Misión cumplida. Cerrando.")
        time.sleep(3)
        browser.close()


if __name__ == "__main__":
    run()