# services/google/google_query_builder.py
from dataclasses import dataclass
from typing import List


@dataclass
class MapsBusinessData:
    """Representa los datos normalizados que vienen del MapsReader."""
    nombre: str
    ciudad: str
    pais: str
    categoria: str
    telefono: str
    sitio_web: str
    direccion: str


class GoogleQueryBuilder:
    """
    Construye queries inteligentes para Google basadas en los datos de la empresa.
    Genera múltiples estrategias de búsqueda para encontrar redes sociales.
    """

    def __init__(self):
        # Keywords de redes para priorizar
        self.social_keywords = ["instagram", "facebook", "tiktok"]

    def clean_name(self, name: str) -> str:
        """Limpia caracteres innecesarios para evitar ruido en las búsquedas."""
        bad_chars = ["·", "|", "•", "-", "_"]
        for bad in bad_chars:
            name = name.replace(bad, " ")
        return " ".join(name.split()).strip()

    def build_queries(self, data: MapsBusinessData) -> List[str]:
        """
        Construye varias consultas para Google partiendo del nombre, ciudad y país.
        Se devuelven las más enfocadas primero, y las genéricas después.
        """

        nombre_clean = self.clean_name(data.nombre)
        ciudad = data.ciudad
        pais = data.pais
        categoria = data.categoria

        queries = []

        # 1️⃣ Query principal → más directa
        if ciudad:
            queries.append(f"{nombre_clean} {ciudad} instagram")
        if ciudad:
            queries.append(f"{nombre_clean} {ciudad} {categoria} instagram")

        # 2️⃣ Query con país (por si la ciudad no aparece bien en Maps)
        if pais:
            queries.append(f"{nombre_clean} {pais} instagram")
            queries.append(f"{nombre_clean} {categoria} {pais} instagram")

        # 3️⃣ Query muy amplia (solo nombre + palabra red social)
        for kw in self.social_keywords:
            queries.append(f"{nombre_clean} {kw}")

        # 4️⃣ Query con comillas → maximiza exactitud en resultados difíciles
        queries.append(f"\"{nombre_clean}\" instagram")
        queries.append(f"\"{nombre_clean}\" \"{ciudad}\" instagram")

        # 5️⃣ Query por teléfono si existe
        if data.telefono:
            queries.append(f"{data.telefono} instagram")

        # 6️⃣ Query por sitio web si existe
        if data.sitio_web:
            queries.append(f"{data.sitio_web} instagram")

        # Remover duplicados manteniendo el orden
        final_queries = list(dict.fromkeys(queries))

        return final_queries
