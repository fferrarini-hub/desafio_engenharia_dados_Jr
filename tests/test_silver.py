import pandas as pd
import pytest

from projeto_final import silver


class ResultadoFake:
    def __init__(self, dataframe):
        self.dataframe = dataframe

    def fetchdf(self):
        return self.dataframe


class ConexaoFake:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.fechada = False

    def execute(self, query):
        return ResultadoFake(self.dataframe)

    def close(self):
        self.fechada = True


def test_executar_silver_com_sucesso(monkeypatch):
    bronze = pd.DataFrame(
        [
            {
                "origem_id": 1,
                "destino_id": 2,
                "coletado_em": "2026-10-30T10:00:00+00:00",
                "resposta_json": (
                    '{"code": "Ok", "routes": '
                    '[{"distance": 10000, "duration": 1200}]}'
                ),
            }
        ]
    )

    conexao = ConexaoFake(bronze)
    gravacao = {}

    monkeypatch.setattr(silver, "conectar", lambda: conexao)
    monkeypatch.setattr(
        silver,
        "criar_schema",
        lambda con, schema: gravacao.update(schema=schema),
    )

    def gravar_fake(con, dataframe, schema, tabela):
        gravacao.update(
            registros=len(dataframe),
            tabela=tabela,
            distancia=dataframe.iloc[0]["distancia_metros"],
        )
        return len(dataframe)

    monkeypatch.setattr(silver, "gravar", gravar_fake)

    silver.executar_silver()

    assert gravacao["schema"] == "silver"
    assert gravacao["tabela"] == "rotas"
    assert gravacao["registros"] == 1
    assert gravacao["distancia"] == 10000
    assert conexao.fechada


def test_executar_silver_com_bronze_vazia(monkeypatch):
    conexao = ConexaoFake(pd.DataFrame())

    monkeypatch.setattr(silver, "conectar", lambda: conexao)

    with pytest.raises(
        ValueError,
        match="A camada Bronze não possui registros",
    ):
        silver.executar_silver()

    assert conexao.fechada
