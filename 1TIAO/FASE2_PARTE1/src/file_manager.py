import json
import os

JSON_FILE = "resultados_colheita.json"
TXT_FILE = "resultados_colheita.txt"

def carregar_json(arquivo=JSON_FILE):
    if not os.path.exists(arquivo): return []
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar JSON: {e}")
        return []

def salvar_json(lista, arquivo=JSON_FILE):
    try:
        with open(arquivo, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=4)
        print(f"{len(lista)} resultado(s) salvo(s) em JSON.")
    except Exception as e:
        print(f"Erro ao salvar JSON: {e}")

def salvar_txt(lista, arquivo=TXT_FILE):
    try:
        with open(arquivo, "w", encoding="utf-8") as f:
            for r in lista:
                for k, v in r.items(): f.write(f"{k}: {v}\n")
                f.write("\n")
        print(f"{len(lista)} resultado(s) salvo(s) em TXT.")
    except Exception as e:
        print(f"Erro ao salvar TXT: {e}")
