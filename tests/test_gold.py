from pathlib import Path

import pytest

from projeto_final import gold


def test_executar_sql_com_sucesso(tmp_path):
    arquivo = tmp_path / "teste.sql"
    arquivo.write_text("SELECT 1", encoding="utf-8")

    class ConexaoFake:
        def __init__(self):
            self.sql_executado = None

        def execute(self, sql):
            self.sql_executado = sql
            return self

        def fetchall(self):
            return [(1,)]

    conexao = ConexaoFake()

    gold.executar_sql(conexao, arquivo)

    assert conexao.sql_executado == "SELECT 1"


def test_executar_sql_com_arquivo_inexistente(tmp_path):
    arquivo = tmp_path / "inexistente.sql"

    with pytest.raises(FileNotFoundError, match="Arquivo SQL não encontrado"):
        gold.executar_sql(None, arquivo)


def test_executar_gold_sem_tabela_silver(monkeypatch):
    class ResultadoFake:
        def fetchone(self):
            return (0,)

    class ConexaoFake:
        def __init__(self):
            self.fechada = False

        def execute(self, sql):
            return ResultadoFake()

        def close(self):
            self.fechada = True

    conexao = ConexaoFake()
    monkeypatch.setattr(gold, "conectar", lambda: conexao)

    with pytest.raises(
        ValueError,
        match="Tabela silver.rotas não encontrada",
    ):
        gold.executar_gold()

    assert conexao.fechada
