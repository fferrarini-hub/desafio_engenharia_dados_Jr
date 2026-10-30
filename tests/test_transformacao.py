import pandas as pd
import pytest

from projeto_final.transformacao import transformar_rotas


def criar_bronze(resposta):
    """Cria um registro Bronze fictício."""
    return pd.DataFrame(
        [
            {
                "origem_id": 1,
                "destino_id": 2,
                "resposta_json": resposta,
                "coletado_em": "2026-10-30T12:00:00+00:00",
            }
        ]
    )


def test_transformar_rota_principal():
    resposta = '{"code": "Ok", "routes": [{"distance": 1000.5, "duration": 120.5}]}'

    resultado = transformar_rotas(criar_bronze(resposta))

    assert len(resultado) == 1
    assert resultado.iloc[0]["numero_rota"] == 1
    assert resultado.iloc[0]["distancia_metros"] == 1000.5
    assert resultado.iloc[0]["duracao_segundos"] == 120.5


def test_transformar_rota_e_alternativa():
    resposta = (
        '{"code": "Ok", "routes": ['
        '{"distance": 1000, "duration": 120},'
        '{"distance": 1200, "duration": 150}'
        "]}"
    )

    resultado = transformar_rotas(criar_bronze(resposta))

    assert len(resultado) == 2
    assert resultado["numero_rota"].tolist() == [1, 2]


def test_rejeitar_codigo_osrm_invalido():
    resposta = '{"code": "NoRoute", "routes": []}'

    with pytest.raises(ValueError, match="Resposta OSRM inválida"):
        transformar_rotas(criar_bronze(resposta))


def test_rejeitar_resposta_sem_rotas():
    resposta = '{"code": "Ok", "routes": []}'

    with pytest.raises(ValueError, match="sem rotas"):
        transformar_rotas(criar_bronze(resposta))


def test_rejeitar_distancia_negativa():
    resposta = '{"code": "Ok", "routes": [{"distance": -100, "duration": 120}]}'

    with pytest.raises(ValueError, match="Distância inválida"):
        transformar_rotas(criar_bronze(resposta))


def test_rejeitar_duracao_zero():
    resposta = '{"code": "Ok", "routes": [{"distance": 100, "duration": 0}]}'

    with pytest.raises(ValueError, match="Duração inválida"):
        transformar_rotas(criar_bronze(resposta))
