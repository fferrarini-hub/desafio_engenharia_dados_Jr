import pandas as pd

from projeto_final import pipeline


def test_executar_ingestao_com_sucesso(monkeypatch, tmp_path):
    instalacoes = pd.DataFrame(
        [
            {"id": 1, "nome": "Origem", "latitude": -25.0, "longitude": -49.0},
            {"id": 2, "nome": "Destino", "latitude": -26.0, "longitude": -48.0},
        ]
    )

    monkeypatch.setattr(
        pipeline,
        "CAMINHO_CATALOGO",
        tmp_path / "instalacoes.csv",
    )
    monkeypatch.setattr(
        pipeline,
        "CAMINHO_BRONZE",
        tmp_path / "raw" / "rotas.jsonl",
    )
    monkeypatch.setattr(
        pipeline,
        "carregar_instalacoes",
        lambda caminho: instalacoes,
    )
    monkeypatch.setattr(
        pipeline,
        "obter_instalacoes_com_coordenadas",
        lambda df: df,
    )
    monkeypatch.setattr(
        pipeline,
        "obter_rota",
        lambda origem, destino: {
            "code": "Ok",
            "routes": [{"distance": 10000, "duration": 1200}],
        },
    )

    class ConexaoFake:
        fechada = False

        def close(self):
            self.fechada = True

    conexao = ConexaoFake()
    gravacao = {}

    monkeypatch.setattr(pipeline, "conectar", lambda: conexao)
    monkeypatch.setattr(
        pipeline,
        "criar_schema",
        lambda con, schema: gravacao.update(schema=schema),
    )

    def gravar_fake(con, dataframe, schema, tabela):
        gravacao.update(
            quantidade=len(dataframe),
            tabela=tabela,
            schema_gravacao=schema,
        )
        return len(dataframe)

    monkeypatch.setattr(pipeline, "gravar", gravar_fake)
    monkeypatch.setattr(pipeline.time, "sleep", lambda segundos: None)

    pipeline.executar_ingestao()

    assert gravacao["schema"] == "bronze"
    assert gravacao["schema_gravacao"] == "bronze"
    assert gravacao["tabela"] == "rotas_raw"
    assert gravacao["quantidade"] == 2
    assert conexao.fechada

    arquivo = tmp_path / "raw" / "rotas.jsonl"
    assert arquivo.exists()
    assert len(arquivo.read_text(encoding="utf-8").splitlines()) == 2
