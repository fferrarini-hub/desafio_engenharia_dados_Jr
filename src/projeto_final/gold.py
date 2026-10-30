
"""Processamento e persistência da camada Gold."""

from pathlib import Path

from projeto_final.db import conectar, criar_schema

RAIZ_PROJETO = Path(__file__).resolve().parents[2]

DIRETORIO_DIMENSOES = (
    RAIZ_PROJETO / "sql" / "gold" / "dimensoes"
)

DIRETORIO_INDICADORES = (
    RAIZ_PROJETO / "sql" / "gold" / "indicadores"
)


def executar_sql(con, caminho: Path) -> None:
    """Executa um arquivo SQL."""
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo SQL não encontrado: {caminho}"
        )

    sql = caminho.read_text(encoding="utf-8")
    con.execute(sql).fetchall()

    print(f"Executado: {caminho.name}")


def executar_gold() -> None:
    """Cria as tabelas Gold e executa os indicadores."""
    con = conectar()

    try:
        # Verifica se a camada Silver está disponível.
        tabelas_silver = con.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_schema = 'silver'
              AND table_name = 'rotas'
            """
        ).fetchone()[0]

        if not tabelas_silver:
            raise ValueError(
                "Tabela silver.rotas não encontrada. "
                "Execute a camada Silver primeiro."
            )

        # Cria o schema Gold.
        criar_schema(con, "gold")

        # Cria dimensão e fato.
        arquivos_dimensoes = [
            "dim_instalacoes.sql",
            "fato_rotas.sql",
        ]

        for nome in arquivos_dimensoes:
            caminho = DIRETORIO_DIMENSOES / nome
            executar_sql(con, caminho)

        # Executa os cinco indicadores.
        arquivos_indicadores = sorted(
            DIRETORIO_INDICADORES.glob("*.sql")
        )

        if not arquivos_indicadores:
            raise FileNotFoundError(
                "Nenhum arquivo SQL de indicador foi encontrado."
            )

        for caminho in arquivos_indicadores:
            resultado = con.execute(
                caminho.read_text(encoding="utf-8")
            ).fetchdf()

            print(f"\nIndicador: {caminho.stem}")
            print(resultado.to_string(index=False))

        # Apresenta o resumo da camada Gold.
        total_instalacoes = con.execute(
            "SELECT COUNT(*) FROM gold.dim_instalacoes"
        ).fetchone()[0]

        total_rotas = con.execute(
            "SELECT COUNT(*) FROM gold.fato_rotas"
        ).fetchone()[0]

        print("\nCamada Gold criada com sucesso.")
        print(f"Instalações: {total_instalacoes}")
        print(f"Rotas: {total_rotas}")
        print(f"Indicadores executados: {len(arquivos_indicadores)}")

    finally:
        con.close()


if __name__ == "__main__":
    executar_gold()
