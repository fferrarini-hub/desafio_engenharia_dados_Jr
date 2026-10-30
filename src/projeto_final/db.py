"""Funções de conexão e persistência de dados no DuckDB."""

from pathlib import Path
from uuid import uuid4

import duckdb

DB_PATH = Path(__file__).resolve().parents[2] / "database" / "projeto_final.duckdb"


def conectar():
    """Cria o diretório do banco e retorna uma conexão DuckDB."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def criar_schema(con, nome):
    """Cria um schema no DuckDB caso ele ainda não exista."""
    nome_sql = nome.replace('"', '""')
    con.execute(f'CREATE SCHEMA IF NOT EXISTS "{nome_sql}"').fetchall()


def gravar(con, df, schema, tabela):
    """Grava um DataFrame como tabela no DuckDB e retorna a quantidade."""
    nome_relacao = f"df_{uuid4().hex}"
    schema_sql = schema.replace('"', '""')
    tabela_sql = tabela.replace('"', '""')

    con.register(nome_relacao, df)

    con.execute(
        f'CREATE OR REPLACE TABLE "{schema_sql}"."{tabela_sql}" '
        f"AS SELECT * FROM {nome_relacao}"
    ).fetchall()

    resultado = con.execute(
        f'SELECT COUNT(*) FROM "{schema_sql}"."{tabela_sql}"'
    ).fetchone()

    return resultado[0]
