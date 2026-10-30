"""Validação do catálogo de instalações logísticas."""

from pathlib import Path

import pandas as pd

COLUNAS_OBRIGATORIAS = {
    "id",
    "nome",
    "tipo",
    "cidade",
    "estado",
    "latitude",
    "longitude",
    "fonte",
}

ESTADOS_VALIDOS = {"PR", "SC", "RS"}


def carregar_instalacoes(caminho: Path) -> pd.DataFrame:
    """Carrega e valida o catálogo de instalações."""
    df = pd.read_csv(caminho)

    colunas_ausentes = COLUNAS_OBRIGATORIAS - set(df.columns)
    if colunas_ausentes:
        raise ValueError(f"Colunas ausentes: {sorted(colunas_ausentes)}")

    if df.empty:
        raise ValueError("O catálogo não possui instalações.")

    if df["id"].isna().any() or df["id"].duplicated().any():
        raise ValueError("Os IDs devem estar preenchidos e ser únicos.")

    if df["nome"].isna().any() or df["nome"].str.strip().eq("").any():
        raise ValueError("Todas as instalações devem possuir nome.")

    if not df["estado"].isin(ESTADOS_VALIDOS).all():
        raise ValueError("Estado inválido. Utilize PR, SC ou RS.")

    latitude = pd.to_numeric(df["latitude"], errors="coerce")
    longitude = pd.to_numeric(df["longitude"], errors="coerce")

    if latitude.isna().ne(longitude.isna()).any():
        raise ValueError("Latitude e longitude devem ser preenchidas juntas.")

    coordenadas_preenchidas = latitude.notna()

    if not latitude[coordenadas_preenchidas].between(-90, 90).all():
        raise ValueError("Latitude fora dos limites geográficos.")

    if not longitude[coordenadas_preenchidas].between(-180, 180).all():
        raise ValueError("Longitude fora dos limites geográficos.")

    df["latitude"] = latitude
    df["longitude"] = longitude

    return df


def obter_instalacoes_com_coordenadas(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna somente instalações aptas para consulta ao OSRM."""
    return df.dropna(subset=["latitude", "longitude"]).copy()
