# utils/human_typing.py
import time
import random

def human_type(page, text, min_delay=0.08, max_delay=0.28):
    """
    Escribe texto en la página con retraso variable, simulando humano.
    """
    for char in text:
        page.keyboard.type(char)
        time.sleep(random.uniform(min_delay, max_delay))
