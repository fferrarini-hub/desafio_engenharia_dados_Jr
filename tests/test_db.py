import duckdb
import pandas as pd

from projeto_final.db import criar_schema, gravar


def test_criar_schema():
    con = duckdb.connect(":memory:")

    criar_schema(con, "bronze")

    resultado = con.execute(
        "SELECT schema_name FROM information_schema.schemata "
        "WHERE schema_name = 'bronze'"
    ).fetchone()

    assert resultado is not None
    con.close()


def test_gravar_dataframe():
    con = duckdb.connect(":memory:")
    criar_schema(con, "bronze")

    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "nome": ["A", "B", "C"],
        }
    )

    total = gravar(con, df, "bronze", "teste")

    resultado = con.execute("SELECT COUNT(*) FROM bronze.teste").fetchone()[0]

    assert total == 3
    assert resultado == 3
    con.close()
