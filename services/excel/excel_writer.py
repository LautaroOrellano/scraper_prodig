import pandas as pd
import os

class ExcelWriter:
    def __init__(self, output_path="output/results.xlsx"):
        self.output_path = output_path

        if not os.path.exists(output_path):
            df = pd.DataFrame(columns=[
                # Datos Google Maps
                "name",
                "formatted_address",
                "formatted_phone",
                "website",

                # Instagram
                "instagram_username",
                "instagram_followers",
                "instagram_following",
                "instagram_posts",
                "instagram_url",

                # Facebook
                "facebook_page_name",
                "facebook_likes",
                "facebook_followers",
                "facebook_url",
            ])
            df.to_excel(output_path, index=False)

    def append_row(self, row_data: dict):
        df = pd.read_excel(self.output_path)
        df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
        df.to_excel(self.output_path, index=False)

        print(f"✅ Datos guardados en {self.output_path}")
