from pathlib import Path

import pandas as pd
import pytest

from projeto_final.validacao import (
    carregar_instalacoes,
    obter_instalacoes_com_coordenadas,
)

CAMINHO_CSV = Path("referencia/instalacoes.csv")


def criar_catalogo() -> pd.DataFrame:
    """Cria dados fictícios para os testes."""
    return pd.DataFrame(
        {
            "id": [1, 2],
            "nome": ["Porto A", "Centro B"],
            "tipo": ["porto", "centro_logistico"],
            "cidade": ["Curitiba", "Joinville"],
            "estado": ["PR", "SC"],
            "latitude": [-25.4, None],
            "longitude": [-49.2, None],
            "fonte": ["fonte_a", "fonte_b"],
        }
    )


def test_carregar_catalogo_real():
    df = carregar_instalacoes(CAMINHO_CSV)

    assert len(df) == 9
    assert set(df["estado"]) == {"PR", "SC", "RS"}


def test_obter_instalacoes_com_coordenadas():
    df = criar_catalogo()

    resultado = obter_instalacoes_com_coordenadas(df)

    assert len(resultado) == 1
    assert resultado.iloc[0]["nome"] == "Porto A"


def test_rejeitar_ids_duplicados(tmp_path):
    df = criar_catalogo()
    df.loc[1, "id"] = 1

    caminho = tmp_path / "catalogo.csv"
    df.to_csv(caminho, index=False)

    with pytest.raises(ValueError, match="IDs"):
        carregar_instalacoes(caminho)


def test_rejeitar_estado_invalido(tmp_path):
    df = criar_catalogo()
    df.loc[0, "estado"] = "SP"

    caminho = tmp_path / "catalogo.csv"
    df.to_csv(caminho, index=False)

    with pytest.raises(ValueError, match="Estado inválido"):
        carregar_instalacoes(caminho)


def test_rejeitar_latitude_fora_do_limite(tmp_path):
    df = criar_catalogo()
    df.loc[0, "latitude"] = 95

    caminho = tmp_path / "catalogo.csv"
    df.to_csv(caminho, index=False)

    with pytest.raises(ValueError, match="Latitude"):
        carregar_instalacoes(caminho)


def test_rejeitar_coordenada_incompleta(tmp_path):
    df = criar_catalogo()
    df.loc[0, "longitude"] = None

    caminho = tmp_path / "catalogo.csv"
    df.to_csv(caminho, index=False)

    with pytest.raises(ValueError, match="preenchidas juntas"):
        carregar_instalacoes(caminho)
