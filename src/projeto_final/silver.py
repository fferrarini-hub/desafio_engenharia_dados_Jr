"""Processamento e persistência da camada Silver."""

from projeto_final.db import conectar, criar_schema, gravar
from projeto_final.transformacao import transformar_rotas


def executar_silver() -> None:
    """Transforma os dados Bronze e grava a camada Silver."""
    con = conectar()

    try:
        df_bronze = con.execute("SELECT * FROM bronze.rotas_raw").fetchdf()

        if df_bronze.empty:
            raise ValueError("A camada Bronze não possui registros.")

        df_silver = transformar_rotas(df_bronze)

        criar_schema(con, "silver")
        total = gravar(con, df_silver, "silver", "rotas")

        print(f"Registros Bronze: {len(df_bronze)}")
        print(f"Registros Silver: {total}")
        print("Camada Silver criada com sucesso.")

    finally:
        con.close()


if __name__ == "__main__":
    executar_silver()
