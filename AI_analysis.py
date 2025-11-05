from transformers import pipeline
import torch

# модели
classifier = pipeline("text2text-generation", model="facebook/bart-large-cnn", device=0)

class AI_Analysis_Links:
    def __init__(self, link):
        self.link = link

    # генерация обьяснения ссылок
    def links_analys(self):
        promt = f"Explain what this website or link is used for: {self.link}"
        explanation = classifier(promt, max_new_tokens=80, do_sample=False)[0]['generated_text']
        return explanation