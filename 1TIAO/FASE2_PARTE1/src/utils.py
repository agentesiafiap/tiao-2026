from file_manager import carregar_json
from database_oracle import obter_resultados_oracle, conectar_oracle
import json

def contar_resultados(memoria):
    memoria_count = len(memoria)
    json_count = len(carregar_json())
    oracle_count = len(obter_resultados_oracle())
    print(f"\nMemória: {memoria_count} | JSON: {json_count} | Oracle: {oracle_count}\n")

def exibir_resultados_submenu(memoria):
    while True:
        print("1. Memória\n2. JSON\n3. Oracle\n4. Voltar")
        opc = input("Escolha: ")
        if opc == "1":
            for i, r in enumerate(memoria, start=1):
                print(f"\nResultado {i}: {r}")
        elif opc == "2":
            lista = carregar_json()
            for i, r in enumerate(lista, start=1):
                print(f"\nResultado {i}: {r}")
        elif opc == "3":
            rows = obter_resultados_oracle()
            for row in rows:
                print(f"ID {row[0]}: Base={row[1]}, Meio={row[2]}, Ponta={row[3]}, Médio={row[4]}, IM={row[5]}")
        elif opc == "4":
            break
        else:
            print("Opção inválida.")

def remover_resultado(memoria):
    print("1.Memória 2.JSON 3.Oracle 4.Cancelar")
    opc = input("Escolha: ")
    if opc == "1":
        for i, r in enumerate(memoria, start=1): print(f"{i}: {r}")
        idx = int(input("ID: "))
        if 1 <= idx <= len(memoria): memoria.pop(idx-1)
    elif opc == "2":
        lista = carregar_json()
        for i, r in enumerate(lista, start=1): print(f"{i}: {r}")
        idx = int(input("ID: "))
        if 1 <= idx <= len(lista):
            lista.pop(idx-1)
            with open("resultados_colheita.json", "w", encoding="utf-8") as f:
                json.dump(lista, f, ensure_ascii=False, indent=4)
    elif opc == "3":
        rows = obter_resultados_oracle()
        for row in rows: print(f"ID {row[0]}: {row[1:]}")
        idx = int(input("Digite ID Oracle: "))
        conn = conectar_oracle()
        cur = conn.cursor()
        cur.execute("DELETE FROM resultados_colheita WHERE id=:id", {"id": idx})
        conn.commit()
        cur.close(); conn.close()
    elif opc == "4":
        return
    else:
        print("Opção inválida.")

def carregar_dados(memoria):
    print("1.JSON 2.Oracle")
    opc = input("Escolha: ")
    if opc=="1":
        dados = carregar_json()
        memoria.clear(); memoria.extend(dados)
    elif opc=="2":
        from database_oracle import obter_resultados_oracle
        rows = obter_resultados_oracle()
        memoria.clear()
        for r in rows:
            memoria.append({
                "Brix Base": r[1], "Brix Meio": r[2], "Brix Ponta": r[3],
                "Brix Médio": r[4], "Índice de Maturação": r[5]
            })
