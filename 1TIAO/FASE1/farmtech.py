#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FarmTech CLI — Agricultura Digital (Bahia)
Culturas: Milho (área retangular) e Soja (área circular — pivô central)
- Vetores: armazenam talhões/áreas e manejos de insumos
- Menu com: inserir, listar, atualizar, deletar, cálculos de área e insumo, sair
"""

import pandas as pd
from math import pi
import os

# Listas (vetores) para armazenar os dados
tipo_culturas: list[str] = []
areas: list[float]  = []
larguras: list[float]  = []
comprimentos: list[float]  = []

def menu() -> int:
    """"
        Exibir o menu de opções e captura a escolha di usuário.
    """
    print("\n--- FarmTech Solutions - Agricultura Digital ---")
    print("1. Adicionar nova cultura")
    print("2. Listar todas as culturas")
    print("3. Atualizar dados de uma cultura")
    print("4. Deletar uma cultura")
    print("5. Calcular insumos necessários")
    print("6. Salvar dados em arquivo CSV")
    print("7. Sair do programa\n")

    try:
        opcao: int = int(input("Escolha uma opção: "))
        return opcao
    except ValueError:
        print("Entrada inválida. Por favor , digite um número.")
        return 0
    
def adicionar_dados() -> None:
    """Permite ao usuário adicionar dados de uma nova cultura."""
    print("\n--- Adicionar Cultura ---")
    cultura = input("Digite o tipo de cultura (Milho/Soja): ").lower()
    
    if cultura == "milho":
        try:
            largura: float = float(input("Digite a largura da área em metros: "))
            comprimento: float = float(input("Digite o comprimento da área em metros: "))
            area: float = largura * comprimento
            tipo_culturas.append(cultura)
            areas.append(area)
            larguras.append(largura)
            comprimentos.append(comprimento)
            print(f"\nÁrea de milho de {area:.2f} m² adicionada com sucesso!\n")
        except ValueError:
            print("\nEntrada inválida. Por favor, digite valores numéricos.\n")
    
    elif cultura == "soja":
        try:
            raio: float = float(input("Digite o raio da área em metros: "))
            area: float = pi * (raio ** 2)
            tipo_culturas.append(cultura)
            areas.append(area)
            larguras.append(raio) # Armazenamos o lado na largura
            comprimentos.append(raio) # E também no comprimento para manter a estrutura
            print(f"\nÁrea de soja de {area:.2f} m² adicionada com sucesso!\n")
        except ValueError:
            print("\nEntrada inválida. Por favor, digite um valor numérico.\n")
    else:
        print("\nCultura inválida. Por favor, digite 'Milho' ou 'Soja'.\n")
    

def listar_dados() -> None:
    """Exibe todos os dados armazenados nas listas."""
    if not tipo_culturas:
        print("\nNenhum dado de cultura cadastrado.")
        return

    print("\n--- Dados das Culturas ---")
    for i in range(len(tipo_culturas)):
        print(f"Índice: {i}")
        print(f"  Tipo: {tipo_culturas[i].capitalize()}")
        print(f"  Área: {areas[i]:.2f} m²")
        print("-" * 20)

def atualizar_dados() -> None:
    """Atualiza um dado específico com base no índice."""
    listar_dados()
    if not tipo_culturas:
        return

    try:
        indice: int = int(input("Digite o índice da cultura que deseja atualizar: "))
        if 0 <= indice < len(tipo_culturas):
            nova_cultura: str = input("Digite o novo tipo de cultura (Milho/Soja): ").lower()
            if nova_cultura in ["milho", "soja"]:
                tipo_culturas[indice] = nova_cultura
                if nova_cultura == "milho":
                    largura: float = float(input("Digite a nova largura em metros: "))
                    comprimento: float = float(input("Digite o novo comprimento em metros: "))
                    areas[indice] = largura * comprimento
                    larguras[indice] = largura
                    comprimentos[indice] = comprimento
                else: # Soja
                    raio: float = float(input("Digite o novo raio em metros: "))
                    areas[indice] = pi * (raio ** 2)
                    larguras[indice] = raio
                    comprimentos[indice] = raio
                print("Dados atualizados com sucesso!\n")
            else:
                print("Cultura inválida.\n")
        else:
            print("Índice inválido.\n")
    except ValueError:
        print("Entrada inválida. Por favor, digite um número.\n")

def deletar_dados() -> None:
    """Deleta um dado com base no índice."""
    listar_dados()
    if not tipo_culturas:
        return
    
    try:
        indice: int = int(input("Digite o índice da cultura que deseja deletar: "))
        if 0 <= indice < len(tipo_culturas):
            tipo_culturas.pop(indice)
            areas.pop(indice)
            larguras.pop(indice)
            comprimentos.pop(indice)
            print("Cultura deletada com sucesso!\n")
        else:
            print("Índice inválido.\n")
    except ValueError:
        print("Entrada inválida. Por favor, digite um número.\n")

def calcular_insumos() -> None:
    """Calcula a quantidade de insumos com base na área e dose."""
    listar_dados()
    if not tipo_culturas:
        return
        
    try:
        indice = int(input("Digite o índice da cultura para o cálculo de insumos: "))
        if 0 <= indice < len(tipo_culturas):
            dose_por_m2: float = float(input("Digite a dose do insumo por m² (ex: 0.5 para 0.5L/m²): "))
            area_total: float = areas[indice]
            total_insumo: float = area_total * dose_por_m2
            print(f"\n--- Cálculo de Insumos ---")
            print(f"Para a cultura de {tipo_culturas[indice]} com área de {area_total:.2f} m²,")
            print(f"serão necessários {total_insumo:.2f} litros de insumo.\n")
        else:
            print("Índice inválido.\n")
    except ValueError:
        print("Entrada inválida. Por favor, digite um número.\n")

def salvar_dados() -> None:
    """Salva todos os dados em um arquivo CSV."""
    if not tipo_culturas:
        print("Não há dados para salvar.\n")
        return
    
    dados = {
        'Cultura': tipo_culturas,
        'Area_m2': areas,
    }
    df = pd.DataFrame(dados)
    df.to_csv('dados_farmtech.csv', index=False)
    print("Dados salvos com sucesso em 'dados_farmtech.csv'.")

def main() -> None: 
    # Loop principal do programa
    while True:
        opcao = menu()
        
        match opcao:
            case 1:
                adicionar_dados()
            case 2:
                listar_dados()
            case 3:
                atualizar_dados()
            case 4:
                deletar_dados()
            case 5:
                calcular_insumos()
            case 6:
                salvar_dados()
            case 7:
                salvar_dados()
                print("Saindo do programa. Até mais!")
                break
            case _:
                print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()