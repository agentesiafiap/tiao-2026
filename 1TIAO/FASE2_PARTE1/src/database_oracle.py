import oracledb

USER = "rm566848"
PASSWORD = "270506"
DSN = "oracle.fiap.com.br:1521/ORCL"

def conectar_oracle():
    try:
        return oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
    except Exception as e:
        print(f"Erro Oracle: {e}")
        return None

def criar_tabela_oracle():
    conn = conectar_oracle()
    if not conn: return
    cur = conn.cursor()
    try:
        cur.execute("""
        BEGIN
            EXECUTE IMMEDIATE '
            CREATE TABLE resultados_colheita (
                id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                brix_base NUMBER(7,2),
                brix_meio NUMBER(7,2),
                brix_ponta NUMBER(7,2),
                brix_medio NUMBER(7,2),
                indice_maturacao NUMBER(7,2)
            )';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -955 THEN RAISE; END IF;
        END;
        """)
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")
    finally:
        cur.close()
        conn.close()

def inserir_resultados_oracle(lista):
    conn = conectar_oracle()
    if not conn: return
    cur = conn.cursor()
    try:
        for r in lista:
            cur.execute("""
            INSERT INTO resultados_colheita
            (brix_base, brix_meio, brix_ponta, brix_medio, indice_maturacao)
            VALUES (:1,:2,:3,:4,:5)
            """, (r["Brix Base"], r["Brix Meio"], r["Brix Ponta"], r["Brix Médio"], r["Índice de Maturação"]))
        conn.commit()
        print(f"{len(lista)} resultado(s) inserido(s) no Oracle.")
    except Exception as e:
        print(f"Erro ao inserir: {e}")
    finally:
        cur.close()
        conn.close()

def obter_resultados_oracle():
    conn = conectar_oracle()
    if not conn: return []
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, brix_base, brix_meio, brix_ponta, brix_medio, indice_maturacao FROM resultados_colheita ORDER BY id")
        return cur.fetchall()
    except Exception as e:
        print(f"Erro ao obter resultados: {e}")
        return []
    finally:
        cur.close()
        conn.close()
