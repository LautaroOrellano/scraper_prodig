# maps_scraper.py
from typing import Dict

def normalize_maps_data(raw_data: Dict) -> Dict:
    """
    Normaliza y prepara la data de Maps para el pipeline.
    Adaptado a las columnas reales del Excel:
    name, formatted_address, formatted_phone, website
    """

    normalized = {}

    # Nombre tal cual viene
    normalized["nombre"] = raw_data.get("name", "").strip()

    # Dirección completa
    direccion = raw_data.get("formatted_address", "").strip()
    normalized["direccion"] = direccion

    # Extraemos ciudad y país desde la dirección
    parts = [p.strip() for p in direccion.split(",")]

    normalized["ciudad"] = parts[-2] if len(parts) >= 2 else ""
    normalized["pais"] = parts[-1] if len(parts) >= 1 else ""

    # Teléfono
    normalized["telefono"] = raw_data.get("formatted_phone", "").strip()

    # Sitio web
    normalized["sitio_web"] = raw_data.get("website", "").strip()

    return normalized
