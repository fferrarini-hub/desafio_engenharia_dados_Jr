"""Testes do módulo de orquestração."""

from projeto_final import orquestrador


def test_executar_pipeline_completo(monkeypatch):
    chamadas = []

    monkeypatch.setattr(
        orquestrador,
        "executar_ingestao",
        lambda: chamadas.append("bronze"),
    )
    monkeypatch.setattr(
        orquestrador,
        "executar_silver",
        lambda: chamadas.append("silver"),
    )
    monkeypatch.setattr(
        orquestrador,
        "executar_gold",
        lambda: chamadas.append("gold"),
    )

    orquestrador.executar_pipeline_completo()

    assert chamadas == ["bronze", "silver", "gold"]


def test_atualizar_camadas_analiticas(monkeypatch):
    chamadas = []

    monkeypatch.setattr(
        orquestrador,
        "executar_silver",
        lambda: chamadas.append("silver"),
    )
    monkeypatch.setattr(
        orquestrador,
        "executar_gold",
        lambda: chamadas.append("gold"),
    )

    orquestrador.atualizar_camadas_analiticas()

    assert chamadas == ["silver", "gold"]
