import json
from config.settings import BANCO_PATH

def carregar_banco():
    try:
        with open(BANCO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def salvar_banco(banco):
    with open(BANCO_PATH, "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=2)
