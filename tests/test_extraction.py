import pytest
import requests

from projeto_final.extraction import ErroOSRM, obter_rota


class RespostaSimulada:
    def raise_for_status(self):
        pass

    def json(self):
        return {
            "code": "Ok",
            "routes": [
                {
                    "distance": 10000,
                    "duration": 900,
                }
            ],
        }


def test_obter_rota_com_sucesso(monkeypatch):
    def requisicao_simulada(*args, **kwargs):
        return RespostaSimulada()

    monkeypatch.setattr(requests, "get", requisicao_simulada)

    resultado = obter_rota(
        (-49.27, -25.43),
        (-48.50, -25.52),
    )

    assert resultado["code"] == "Ok"
    assert resultado["routes"][0]["distance"] == 10000


def test_obter_rota_com_erro_osrm(monkeypatch):
    class RespostaErro(RespostaSimulada):
        def json(self):
            return {"code": "NoRoute", "routes": []}

    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: RespostaErro(),
    )

    with pytest.raises(ErroOSRM):
        obter_rota(
            (-49.27, -25.43),
            (-48.50, -25.52),
        )


def test_obter_rota_com_coordenada_invalida():
    with pytest.raises(ValueError):
        obter_rota(
            (200, -25.43),
            (-48.50, -25.52),
        )
