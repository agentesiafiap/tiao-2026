import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

def calcular_brix_medio(leituras):
    return sum(leituras) / len(leituras)

def calcular_indice_maturacao(brix_base, brix_ponta):
    if brix_base == 0: return 0
    return brix_ponta / brix_base

def procedimento_calculo():
    try:
        brix_base = float(input("Brix Base: "))
        brix_meio = float(input("Brix Meio: "))
        brix_ponta = float(input("Brix Ponta: "))
    except ValueError:
        print("Entrada inválida.")
        return None
    brix_medio = calcular_brix_medio((brix_base, brix_meio, brix_ponta))
    im = calcular_indice_maturacao(brix_base, brix_ponta)
    return {
        "Brix Base": round(brix_base, 2),
        "Brix Meio": round(brix_meio, 2),
        "Brix Ponta": round(brix_ponta, 2),
        "Brix Médio": round(brix_medio, 2),
        "Índice de Maturação": round(im, 2)
    }

def gerar_grafico(memoria):
    print("\n--- GRÁFICO DE EVOLUÇÃO DO BRIX E IM ---")

    if not memoria:
        print("Nenhum dado disponível para gerar gráfico.")
        return

    # Dias reais da amostragem
    dias = np.arange(1, len(memoria) + 1)
    brix_values = [r.get("Brix Médio", r.get("brix", 0)) for r in memoria]
    im_values = [r.get("Índice de Maturação", r.get("IM", 0)) for r in memoria]

    # Ajuste linear para previsão
    coef_brix = np.polyfit(dias, brix_values, 1)
    coef_im = np.polyfit(dias, im_values, 1)
    poly_brix = np.poly1d(coef_brix)
    poly_im = np.poly1d(coef_im)

    # Dias futuros (365 dias à frente)
    dias_futuros = np.arange(1, len(memoria) + 366)
    previsao_brix = poly_brix(dias_futuros)
    previsao_im = poly_im(dias_futuros)

    plt.figure(figsize=(12, 6))
    # Valores históricos
    plt.plot(dias, brix_values, marker='o', linestyle='-', label="Brix histórico")
    plt.plot(dias, im_values, marker='x', linestyle='-', label="IM histórico")
    # Projeção futura
    plt.plot(dias_futuros, previsao_brix, linestyle='--', color='green', label="Brix projetado")
    plt.plot(dias_futuros, previsao_im, linestyle='--', color='orange', label="IM projetado")

    # Linhas ideais
    plt.axhline(18, color='green', linestyle=':', label="Brix ideal (18°)")
    plt.axhline(1.0, color='orange', linestyle=':', label="IM ideal (1.0)")

    plt.title("Evolução e Projeção do Brix e Índice de Maturação da Cana")
    plt.xlabel("Dias de amostragem")
    plt.ylabel("Valor medido")
    plt.legend()
    plt.grid(True)
    plt.show()
def prever_momento_colheita(memoria):
    print("\n--- PREVISÃO DE MOMENTO IDEAL DE COLHEITA ---")

    if not memoria:
        print("Nenhum dado disponível para previsão.")
        return

    dias = np.arange(len(memoria))
    brix_values = [r.get("Brix Médio", r.get("brix", 0)) for r in memoria]
    im_values = [r.get("Índice de Maturação", r.get("IM", 0)) for r in memoria]

    # Verifica se existem pelo menos 2 valores distintos
    if len(set(brix_values)) < 2 or len(set(im_values)) < 2:
        print("Dados insuficientes ou valores constantes. Não é possível prever com regressão linear.")
        return

    # Ajuste linear (grau 1) para maior estabilidade
    coef_brix = np.polyfit(dias, brix_values, 1)
    coef_im = np.polyfit(dias, im_values, 1)

    poly_brix = np.poly1d(coef_brix)
    poly_im = np.poly1d(coef_im)

    # Previsão para os próximos 365 dias
    dias_futuros = np.arange(len(memoria), len(memoria) + 365)
    previsao_brix = poly_brix(dias_futuros)
    previsao_im = poly_im(dias_futuros)

    for i, (b, im) in enumerate(zip(previsao_brix, previsao_im), start=1):
        # Critério de maturação ideal: Brix >= 18 e IM entre 0.95 e 1.05
        if b >= 18 and 0.95 <= im <= 1.05:
            dias_para_colheita = i
            data_prevista = datetime.now() + timedelta(days=dias_para_colheita)
            print(f"\n📅 Previsão: A cana deve atingir o ponto ideal em aproximadamente {dias_para_colheita} dias.")
            print(f"Data estimada da colheita: {data_prevista.strftime('%d/%m/%Y')}")
            break
    else:
        print("\n⚠️ Nenhum ponto ideal previsto nos próximos 365 dias.")