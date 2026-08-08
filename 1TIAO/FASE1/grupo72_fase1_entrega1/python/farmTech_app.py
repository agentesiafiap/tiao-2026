import sys
import csv

# Dados organizados em vetores (listas)
culturas = ["Café", "Cana"]  # Suporte explícito para Café e Cana
areas = []
manejos = []

def menu():
    print("\n--- FarmTech Solutions ---")
    print("1. Cálculo de área e manejo")
    print("2. Exibir dados")
    print("3. Atualizar dados")
    print("4. Remover dados")
    print("5. Exportar dados para CSV")  # Novo item no menu
    print("6. Sair do programa")  # Atualizado para refletir a nova opção
    opcao = input("Escolha uma opção: ")
    return opcao

def entrada_dados():
    print("\nTipos de cultura disponíveis:")
    for i, cultura in enumerate(culturas):
        print(f"{i+1}. {cultura}")
    tipo = int(input("Escolha o tipo de cultura (número): ")) - 1
    cultura = culturas[tipo]

    # Área de plantio (Retângulo para ambas as culturas)
    print(f"\nÁrea de {cultura} será calculada como Retângulo.")
    largura = float(input("\nDigite a largura do terreno (m): "))
    comprimento = float(input("\nDigite o comprimento do terreno (m): "))
    area = largura * comprimento
    print(f"\n\nÁrea calculada: {area:.2f} m²")
    areas.append((cultura, area))

    # Manejo de insumos
    produto = input("\nNome do produto a aplicar: ")
    quantidade_por_metro = float(input("\nQuantidade do produto por metro quadrado (mL/m²): "))
    total_produto = quantidade_por_metro * area
    print(f"\n\nTotal de produto necessário: {total_produto:.2f} mL")

    manejos.append((cultura, produto, quantidade_por_metro, total_produto))

def saida_dados():
    print("\n--- Dados de Áreas ---\n")
    for i, (cultura, area) in enumerate(areas):
        print(f"{i}: Cultura: {cultura}, Área: {area:.2f} m²\n")
    print("--- Dados de Manejo ---\n")
    for i, dado in enumerate(manejos):
        print(f"{i}: Cultura: {dado[0]}, Produto: {dado[1]}, Qtde/m: {dado[2]} mL/m, Total: {dado[3]:.2f} mL\n")

def atualizar_dados():
    print("\nDeseja atualizar área ou manejo? (1-Área, 2-Manejo)\n")
    tipo = input("Escolha: ")
    if tipo == "1":
        saida_dados()
        idx = int(input("Digite o índice da área a atualizar: "))
        nova_area = float(input("Digite o novo valor da área: "))
        areas[idx] = (areas[idx][0], nova_area)
        print("\nÁrea atualizada com sucesso.\n")
    elif tipo == "2":
        saida_dados()
        idx = int(input("Digite o índice do manejo a atualizar: "))
        novo_total = float(input("Digite o novo total de produto necessário: "))
        cultura, prod, qtde_m, _ = manejos[idx]
        manejos[idx] = (cultura, prod, qtde_m, novo_total)
        print("\nManejo atualizado com sucesso.\n")

def deletar_dados():
    print("\nDeseja deletar área ou manejo? (1-Área, 2-Manejo)\n")
    tipo = input("Escolha: ")
    if tipo == "1":
        saida_dados()
        idx = int(input("Digite o índice da área a deletar: "))
        del areas[idx]
        print("\nÁrea deletada com sucesso.\n")
    elif tipo == "2":
        saida_dados()
        idx = int(input("Digite o índice do manejo a deletar: "))
        del manejos[idx]
        print("\nManejo deletado com sucesso.\n")

def exportar_dados():
    """Exportar dados de áreas e manejos para arquivos CSV."""
    # Exportar áreas
    with open("areas_export.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Cultura", "Area"])  # Cabeçalhos
        writer.writerows(areas)  # Dados
    print("Dados de áreas exportados para 'areas_export.csv'.")

    # Exportar manejos
    with open("manejos_export.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Cultura", "Produto", "Qtde", "Total"])  # Cabeçalhos
        writer.writerows(manejos)  # Dados
    print("Dados de manejos exportados para 'manejos_export.csv'.")

def main():
    while True:
        opcao = menu()
        if opcao == "1":
            entrada_dados()
        elif opcao == "2":
            saida_dados()
        elif opcao == "3":
            atualizar_dados()
        elif opcao == "4":
            deletar_dados()
        elif opcao == "5":
            exportar_dados()
        elif opcao == "6":
            print("Saindo do programa...")
            sys.exit()
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()