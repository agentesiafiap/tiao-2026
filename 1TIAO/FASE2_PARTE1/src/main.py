from analytics import procedimento_calculo, gerar_grafico, prever_momento_colheita
from database_oracle import criar_tabela_oracle, inserir_resultados_oracle
from file_manager import salvar_json, salvar_txt
from utils import contar_resultados, exibir_resultados_submenu, remover_resultado, carregar_dados

def menu():
    criar_tabela_oracle()
    memoria = []

    while True:
        contar_resultados(memoria)
        print("""
==============================
SISTEMA AGRÍCOLA INTEGRADO
==============================
1. Adicionar Novo Resultado do Dia
2. Exibir Resultados
3. Remover Resultado
4. Salvar Resultados
5. Carregar Dados
6. Prever Momento Ideal de Colheita
7. Gerar Gráfico de Evolução
0. Sair
==============================
""")
        opc = input("Escolha: ").strip()
        if opc == "1":
            r = procedimento_calculo()
            if r:
                memoria.append(r)
                print("Resultado adicionado à memória.")
        elif opc == "2":
            exibir_resultados_submenu(memoria)
        elif opc == "3":
            remover_resultado(memoria)
        elif opc == "4":
            if memoria:
                salvar_json(memoria)
                salvar_txt(memoria)
                inserir_resultados_oracle(memoria)
            else:
                print("Memória vazia. Nada para salvar.")
        elif opc == "5":
            carregar_dados(memoria)
        elif opc == "6":
            prever_momento_colheita(memoria)
        elif opc == "7":
            gerar_grafico(memoria)
        elif opc == "0":
            print("Encerrando o sistema...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()
