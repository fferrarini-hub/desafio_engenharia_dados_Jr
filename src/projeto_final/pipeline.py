"""Orquestra a ingestão de rotas OSRM na camada Bronze."""

import json
import time
from datetime import UTC, datetime
from itertools import permutations
from pathlib import Path

import pandas as pd

from projeto_final.db import conectar, criar_schema, gravar
from projeto_final.extraction import obter_rota
from projeto_final.validacao import (
    carregar_instalacoes,
    obter_instalacoes_com_coordenadas,
)

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
CAMINHO_CATALOGO = RAIZ_PROJETO / "dados" / "referencia" / "instalacoes.csv"
CAMINHO_BRONZE = RAIZ_PROJETO / "raw" / "osrm_rotas.jsonl"
INTERVALO_SEGUNDOS = 1


def executar_ingestao() -> None:
    """Consulta os pares de instalações e salva as respostas brutas."""
    instalacoes = carregar_instalacoes(CAMINHO_CATALOGO)
    instalacoes = obter_instalacoes_com_coordenadas(instalacoes)

    pares = list(permutations(instalacoes.to_dict("records"), 2))
    registros = []

    CAMINHO_BRONZE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Iniciando ingestão de {len(pares)} combinações.")

    with CAMINHO_BRONZE.open("w", encoding="utf-8") as arquivo:
        for indice, (origem, destino) in enumerate(pares, start=1):
            resposta = obter_rota(
                (origem["longitude"], origem["latitude"]),
                (destino["longitude"], destino["latitude"]),
            )

            registro = {
                "origem_id": int(origem["id"]),
                "destino_id": int(destino["id"]),
                "origem_nome": origem["nome"],
                "destino_nome": destino["nome"],
                "coletado_em": datetime.now(UTC).isoformat(),
                "resposta_json": json.dumps(resposta, ensure_ascii=False),
            }

            registros.append(registro)
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")

            print(f"[{indice}/{len(pares)}] {origem['nome']} -> {destino['nome']}")

            if indice < len(pares):
                time.sleep(INTERVALO_SEGUNDOS)

    df = pd.DataFrame(registros)

    con = conectar()
    try:
        criar_schema(con, "bronze")
        total = gravar(con, df, "bronze", "rotas_raw")
    finally:
        con.close()

    print(f"Ingestão concluída: {total} registros gravados no DuckDB.")
    print(f"Arquivo Bronze: {CAMINHO_BRONZE}")


if __name__ == "__main__":
    executar_ingestao()
