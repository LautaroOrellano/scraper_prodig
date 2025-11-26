import time
import random
import numpy as np

VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

# Script JS para el cursor visual
VISUAL_CURSOR_JS = """
    if(!document.getElementById('mouse-helper')){
        const dot = document.createElement('div');
        dot.id = 'mouse-helper';
        dot.style.position = 'fixed';
        dot.style.width = '15px';
        dot.style.height = '15px';
        dot.style.backgroundColor = 'rgba(255,0,0,0.6)';
        dot.style.border = '2px solid white';
        dot.style.borderRadius = '50%';
        dot.style.zIndex = '999999';
        dot.style.pointerEvents = 'none';
        dot.style.transform = 'translate(-50%, -50%)';
        dot.style.transition = 'left 0.005s linear, top 0.005s linear'; // Más suave
        document.body.appendChild(dot);

        window.moveDot = (x, y) => {
            const dot = document.getElementById('mouse-helper');
            if(dot){
                dot.style.left = x + 'px';
                dot.style.top = y + 'px';
            }
        }
    }
"""


def get_bezier_curve(start, end, num_points=50):
    points = []
    t_values = np.linspace(0, 1, num_points)

    # Puntos de control aleatorios para la curvatura
    ctrl1_x = start[0] + random.uniform(-200, 200)
    ctrl1_y = start[1] + random.uniform(-200, 200)
    ctrl2_x = end[0] + random.uniform(-200, 200)
    ctrl2_y = end[1] + random.uniform(-200, 200)

    for t in t_values:
        x = (1 - t) ** 3 * start[0] + 3 * (1 - t) ** 2 * t * ctrl1_x + 3 * (1 - t) * t ** 2 * ctrl2_x + t ** 3 * end[0]
        y = (1 - t) ** 3 * start[1] + 3 * (1 - t) ** 2 * t * ctrl1_y + 3 * (1 - t) * t ** 2 * ctrl2_y + t ** 3 * end[1]
        points.append({'x': x, 'y': y})
    return points


def human_move_to_element(page, selector_or_box, current_x, current_y, wait_time=0.8):
    """
    Mueve el mouse hacia un selector O una bounding box directamente.
    """
    target_x = current_x
    target_y = current_y

    # Si pasamos un selector (string)
    if isinstance(selector_or_box, str):
        try:
            page.wait_for_selector(selector_or_box, state="visible", timeout=5000)
            element = page.locator(selector_or_box).first
            box = element.bounding_box()
        except:
            print(f"⚠️ No se encontró el elemento para mover el mouse: {selector_or_box}")
            return current_x, current_y
    else:
        # Si ya pasamos la caja (bounding box)
        box = selector_or_box

    if box:
        # Punto aleatorio dentro del elemento
        target_x = box['x'] + random.uniform(5, box['width'] - 5)
        target_y = box['y'] + random.uniform(5, box['height'] - 5)

        # Generar camino
        path = get_bezier_curve((current_x, current_y), (target_x, target_y),
                                num_points=random.randint(40, 70))

        for point in path:
            page.mouse.move(point['x'], point['y'])
            # Intentamos actualizar el punto rojo, ignoramos si falla (ej: cambio de página)
            try:
                page.evaluate(f"if(window.moveDot) window.moveDot({point['x']}, {point['y']})")
            except:
                pass
            time.sleep(random.uniform(0.005, 0.015))

        # Pausa antes de interactuar
        time.sleep(random.uniform(0.2, 0.5))

    return target_x, target_y

def human_move_to_box(page, box, current_x=500, current_y=300, wait_time=0.8):
    """
    Mueve el mouse hacia las coordenadas de un bounding box usando curvas Bézier.
    """
    try:
        end_x = box["x"] + random.uniform(5, box["width"] - 5)
        end_y = box["y"] + random.uniform(5, box["height"] - 5)

        # Overshoot natural
        overshoot_x = end_x + random.uniform(-20, 20)
        overshoot_y = end_y + random.uniform(-20, 20)

        path = get_bezier_curve((current_x, current_y), (overshoot_x, overshoot_y),
                                num_points=random.randint(50, 80))

        for p in path:
            page.mouse.move(p["x"], p["y"])
            try:
                page.evaluate(f"if(window.moveDot) window.moveDot({p['x']}, {p['y']})")
            except:
                pass
            time.sleep(random.uniform(0.003, 0.015))

        # Pequeños ajustes
        for _ in range(random.randint(3, 6)):
            adj_x = end_x + random.uniform(-5, 5)
            adj_y = end_y + random.uniform(-3, 3)
            page.mouse.move(adj_x, adj_y)
            try:
                page.evaluate(f"if(window.moveDot) window.moveDot({adj_x}, {adj_y})")
            except:
                pass
            time.sleep(random.uniform(0.05, 0.15))

        return end_x, end_y

    except Exception as e:
        print(f"⚠ Error en human_move_to_box: {e}")
        return current_x, current_y
