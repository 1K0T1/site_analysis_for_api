from google import genai
from pathlib import Path
from dotenv import load_dotenv
import os

env_key = Path(__file__).parent / "key" / ".env"

load_dotenv(dotenv_path=env_key)

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))


class AiGenerate:
    def __init__(self, name, web_file, additionally):
        self.name = name
        self.web_file = web_file
        self.additionally = additionally

    # генерация
    def file_analys(self):
        path_code = Path(__file__).parent / "users_file" / self.name / self.web_file
        text_file = Path(__file__).parent / "users_file" / self.name / "response.txt"

        with open(path_code, "r+", encoding="utf-8") as f:
            code = f.read()

        if self.additionally != None:
            result = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=f"{self.additionally} Ответь на русском и подробно проаналезируй код: {code}",
            )
        else:
            result = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=f"Ответь на русском и подробно проаналезируй код: {code}",
            )

        with open(text_file, "w", encoding="utf-8") as f:
            f.write(result.text)

        return result.text
