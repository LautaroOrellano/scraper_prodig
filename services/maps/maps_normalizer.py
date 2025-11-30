# maps_scraper.py
from typing import Dict

def normalize_maps_data(raw_data: Dict) -> Dict:
    """
    Normaliza y prepara la data de Maps para el pipeline.
    Convierte nombres, direcciones, categorías y teléfono a formato uniforme.
    """
    normalized = {}

    # Nombre: quitar espacios extras y pasar a minúscula
    normalized["nombre"] = raw_data.get("nombre", "").strip()

    # Dirección completa
    normalized["direccion"] = raw_data.get("direccion", "").strip()

    # País y ciudad extraídos de la dirección
    # Por ahora simple split, podemos mejorarlo más tarde
    direccion_parts = normalized["direccion"].split(",")
    normalized["ciudad"] = direccion_parts[-2].strip() if len(direccion_parts) >= 2 else ""
    normalized["pais"] = direccion_parts[-1].strip() if len(direccion_parts) >= 1 else ""

    # Categoría
    normalized["categoria"] = raw_data.get("categoria", "").strip().lower()

    # Teléfono y sitio web
    normalized["telefono"] = raw_data.get("telefono", "").strip()
    normalized["sitio_web"] = raw_data.get("sitio_web", "").strip()

    return normalized
