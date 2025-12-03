import openpyxl


class ExcelReader:
    """
    Lee y valida archivos XLSX con datos exportados de Google Maps.
    Devuelve filas listas para usar en la automatización.
    """

    def __init__(self, required_columns=None):
        # Columnas esperadas en el Excel de Google Maps
        self.required_columns = required_columns or [
            "name",
            "formatted_address",
            "formatted_phone_number",
            "website"
        ]

    def read(self, path: str) -> list:
        """
        Lee un archivo .xlsx y devuelve una lista de diccionarios.
        Cada dict = una empresa.
        """
        wb = openpyxl.load_workbook(path)
        sheet = wb.active

        headers = []
        for cell in sheet[1]:
            headers.append(cell.value.strip().lower() if cell.value else "")

        self._validate_headers(headers)

        data = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            item = {headers[i]: (row[i] if row[i] is not None else "") for i in range(len(headers))}
            data.append(self._clean_row(item))

        return data

    def _validate_headers(self, headers):
        """
        Verifica que el Excel tenga todas las columnas necesarias.
        """
        missing = [col for col in self.required_columns if col not in headers]
        if missing:
            raise ValueError(f"Faltan columnas obligatorias en el Excel: {missing}")

    def _clean_row(self, row: dict) -> dict:
        """
        Limpia textos y normaliza valores.
        """
        clean = {}

        for k, v in row.items():
            if isinstance(v, str):
                clean[k] = v.strip()
            else:
                clean[k] = v

        return clean
