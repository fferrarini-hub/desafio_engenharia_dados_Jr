"""Transformação dos dados brutos OSRM para a camada Silver."""

import json

import pandas as pd

COLUNAS_SILVER = [
    "origem_id",
    "destino_id",
    "numero_rota",
    "distancia_metros",
    "duracao_segundos",
    "coletado_em",
]


def transformar_rotas(df_bronze: pd.DataFrame) -> pd.DataFrame:
    """Extrai e estrutura todas as rotas das respostas brutas OSRM."""
    registros = []

    for registro in df_bronze.to_dict("records"):
        resposta = json.loads(registro["resposta_json"])

        if resposta.get("code") != "Ok":
            raise ValueError(f"Resposta OSRM inválida: {resposta.get('code')}")

        rotas = resposta.get("routes")

        if not isinstance(rotas, list) or not rotas:
            raise ValueError("Resposta OSRM sem rotas.")

        for numero_rota, rota in enumerate(rotas, start=1):
            distancia = rota.get("distance")
            duracao = rota.get("duration")

            if (
                isinstance(distancia, bool)
                or not isinstance(distancia, (int, float))
                or distancia < 0
            ):
                raise ValueError("Distância inválida na resposta OSRM.")

            if (
                isinstance(duracao, bool)
                or not isinstance(duracao, (int, float))
                or duracao <= 0
            ):
                raise ValueError("Duração inválida na resposta OSRM.")

            registros.append(
                {
                    "origem_id": registro["origem_id"],
                    "destino_id": registro["destino_id"],
                    "numero_rota": numero_rota,
                    "distancia_metros": distancia,
                    "duracao_segundos": duracao,
                    "coletado_em": registro["coletado_em"],
                }
            )

    return pd.DataFrame(registros, columns=COLUNAS_SILVER)
