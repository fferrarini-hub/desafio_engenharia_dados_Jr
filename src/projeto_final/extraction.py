"""Especificação e implementação do consumo da API pública OSRM.

Este módulo é responsável exclusivamente por solicitar rotas ao serviço
Route do OSRM e devolver o JSON recebido. Não calcula indicadores, não grava
dados no DuckDB e não faz transformações da camada Silver.

Decisões e critérios desta especificação:

* ``obter_rota(origem, destino)`` recebe cada coordenada como um par
  ``(longitude, latitude)``, na ordem exigida pelo OSRM. Os valores devem ser
  numéricos, finitos e estar nos intervalos geográficos válidos.
* A chamada usa HTTPS no endpoint público ``router.project-osrm.org`` e o
  perfil ``driving``. Esse perfil é necessário no caminho do endpoint e foi
  escolhido para representar deslocamentos rodoviários.
* O parâmetro ``alternatives=true`` solicita percursos alternativos. A API
  pode devolver apenas a rota principal quando não houver alternativas.
* O serviço Route inclui ``distance`` (metros) e ``duration`` (segundos) em
  cada rota retornada; esses campos e todo o restante do JSON são devolvidos
  sem alteração.
* A requisição tem limite de 30 segundos. Erros de comunicação e de status
  HTTP, JSON inválido, resposta incompatível com o contrato Route e código
  OSRM diferente de ``Ok`` são reportados como ``ErroOSRM``.
* O módulo não escolhe coordenadas ou instalações, não persiste dados e não
  executa qualquer regra analítica ou transformação de dados.
"""

from __future__ import annotations

from math import isfinite
from numbers import Real
from typing import Any

import requests

Coordenada = tuple[float, float]

_OSRM_BASE_URL = "https://router.project-osrm.org"
_PERFIL = "driving"
_TIMEOUT_SEGUNDOS = 30


class ErroOSRM(RuntimeError):
    """Indica falhas de comunicação ou respostas inválidas do serviço OSRM."""


def _formatar_coordenada(coordenada: Coordenada, nome: str) -> str:
    """Valida e serializa um par longitude/latitude para o endpoint Route."""
    try:
        longitude, latitude = coordenada
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"{nome} deve conter longitude e latitude, nessa ordem."
        ) from exc

    valores = (longitude, latitude)
    if any(
        isinstance(valor, bool) or not isinstance(valor, Real) or not isfinite(valor)
        for valor in valores
    ):
        raise ValueError(f"{nome} deve conter coordenadas numéricas e finitas.")

    if not -180 <= longitude <= 180:
        raise ValueError(f"A longitude de {nome} deve estar entre -180 e 180.")
    if not -90 <= latitude <= 90:
        raise ValueError(f"A latitude de {nome} deve estar entre -90 e 90.")

    return f"{longitude},{latitude}"


def _detalhe_erro_http(resposta: requests.Response) -> str:
    """Extrai código e mensagem OSRM para contextualizar um erro HTTP."""
    try:
        corpo = resposta.json()
    except ValueError:
        return ""

    if not isinstance(corpo, dict):
        return ""

    detalhes = []
    codigo = corpo.get("code")
    mensagem = corpo.get("message")
    if isinstance(codigo, str):
        detalhes.append(f"código OSRM {codigo}")
    if isinstance(mensagem, str):
        detalhes.append(mensagem)

    return f" ({'; '.join(detalhes)})" if detalhes else ""


def obter_rota(origem: Coordenada, destino: Coordenada) -> dict[str, Any]:
    """Solicita ao OSRM a rota entre duas coordenadas e devolve seu JSON.

    ``origem`` e ``destino`` são pares ``(longitude, latitude)``. A resposta
    mantém a estrutura original do OSRM, incluindo distâncias, durações e
    alternativas que o serviço encontrar.

    Raises:
        ValueError: Se uma coordenada não tiver dois valores numéricos válidos.
        ErroOSRM: Se houver falha de comunicação, erro HTTP, JSON inválido,
            código OSRM diferente de ``Ok`` ou resposta incompatível com o
            contrato do serviço Route.
    """
    origem_url = _formatar_coordenada(origem, "origem")
    destino_url = _formatar_coordenada(destino, "destino")
    url = f"{_OSRM_BASE_URL}/route/v1/{_PERFIL}/{origem_url};{destino_url}"

    try:
        resposta = requests.get(
            url,
            params={"alternatives": "true"},
            timeout=_TIMEOUT_SEGUNDOS,
        )
    except requests.RequestException as exc:
        raise ErroOSRM("Falha de comunicação ao consultar o OSRM.") from exc

    try:
        resposta.raise_for_status()
    except requests.HTTPError as exc:
        detalhe = _detalhe_erro_http(resposta)
        raise ErroOSRM(
            f"OSRM retornou status HTTP {resposta.status_code}{detalhe}."
        ) from exc

    try:
        dados = resposta.json()
    except ValueError as exc:
        raise ErroOSRM("OSRM retornou um corpo que não contém JSON válido.") from exc

    if not isinstance(dados, dict):
        raise ErroOSRM("A resposta JSON do OSRM deve ser um objeto.")

    codigo = dados.get("code")
    if not isinstance(codigo, str):
        raise ErroOSRM("A resposta JSON do OSRM não contém um código válido.")
    if codigo != "Ok":
        mensagem = dados.get("message")
        detalhe = f": {mensagem}" if isinstance(mensagem, str) else ""
        raise ErroOSRM(f"OSRM retornou o código {codigo!r}{detalhe}.")

    rotas = dados.get("routes")
    if not isinstance(rotas, list) or not rotas:
        raise ErroOSRM("A resposta OSRM não contém uma lista de rotas.")

    for indice, rota in enumerate(rotas):
        if not isinstance(rota, dict):
            raise ErroOSRM(f"A rota de índice {indice} não é um objeto JSON.")
        for campo in ("distance", "duration"):
            valor = rota.get(campo)
            if (
                isinstance(valor, bool)
                or not isinstance(valor, Real)
                or not isfinite(valor)
            ):
                raise ErroOSRM(
                    f"A rota de índice {indice} não contém {campo} numérico válido."
                )

    return dados
