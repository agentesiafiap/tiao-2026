"""Parte 1 da Fase 2 (CardioIA): extrai sintomas de frases de pacientes e sugere um diagnóstico.

Lê `assets/frases_sintomas.txt` e `assets/mapa_conhecimento.csv`, faz o matching de
sintomas por substring (após normalização de acentos/caixa) e agrega os resultados
por contagem de votos por doença.
"""

import csv
import re
import unicodedata
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FRASES_PATH = BASE_DIR / "assets" / "frases_sintomas.txt"
MAPA_PATH = BASE_DIR / "assets" / "mapa_conhecimento.csv"


def normalizar(texto: str) -> str:
    """Remove acentos e caixa para tornar o matching robusto."""
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def tokenizar(texto: str) -> set[str]:
    """Converte a frase em um conjunto de palavras normalizadas, ignorando pontuação."""
    return set(re.findall(r"\w+", normalizar(texto)))


def carregar_mapa_conhecimento(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8") as f:
        return [
            {
                "sintomas_tokens": [tokenizar(linha["sintoma_1"]), tokenizar(linha["sintoma_2"])],
                "sintomas_originais": [linha["sintoma_1"], linha["sintoma_2"]],
                "doenca": linha["doenca_associada"],
            }
            for linha in csv.DictReader(f)
        ]


def carregar_frases(caminho: Path) -> list[str]:
    with open(caminho, encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]


def identificar_sintomas(frase: str, mapa: list[dict]) -> tuple[list[str], Counter]:
    """Retorna os sintomas encontrados na frase e a contagem de votos por doença.

    Um sintoma é considerado presente se todas as suas palavras aparecem na frase,
    em qualquer ordem (matching por conjunto de palavras, não por substring exata).
    """
    tokens_frase = tokenizar(frase)
    sintomas_encontrados = []
    votos_por_doenca: Counter = Counter()
    for entrada in mapa:
        for tokens_sintoma, sintoma_original in zip(entrada["sintomas_tokens"], entrada["sintomas_originais"]):
            if tokens_sintoma <= tokens_frase:
                sintomas_encontrados.append(sintoma_original)
                votos_por_doenca[entrada["doenca"]] += 1
    return sintomas_encontrados, votos_por_doenca


def sugerir_diagnostico(votos_por_doenca: Counter) -> str:
    if not votos_por_doenca:
        return "Nenhum sintoma identificado"
    votos_max = max(votos_por_doenca.values())
    candidatas = sorted(d for d, v in votos_por_doenca.items() if v == votos_max)
    if len(candidatas) > 1:
        return f"Indefinido (empate: {', '.join(candidatas)})"
    return candidatas[0]


def main() -> None:
    mapa = carregar_mapa_conhecimento(MAPA_PATH)
    frases = carregar_frases(FRASES_PATH)

    print(f"{'#':<3} {'Sintomas identificados':<55} {'Diagnóstico sugerido'}")
    print("-" * 100)
    for i, frase in enumerate(frases, start=1):
        sintomas, votos = identificar_sintomas(frase, mapa)
        diagnostico = sugerir_diagnostico(votos)
        sintomas_str = "; ".join(sorted(set(sintomas))) or "-"
        print(f"{i:<3} {sintomas_str:<55} {diagnostico}")
        print(f"    Frase: {frase}\n")


if __name__ == "__main__":
    main()
