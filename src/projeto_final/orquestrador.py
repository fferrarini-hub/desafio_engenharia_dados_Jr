"""Orquestra a execução das camadas do projeto."""

from projeto_final.gold import executar_gold
from projeto_final.pipeline import executar_ingestao
from projeto_final.silver import executar_silver


def executar_pipeline_completo() -> None:
    """Executa a ingestão e todas as camadas analíticas."""
    print("\n=== INICIANDO PIPELINE COMPLETO ===")

    print("\n[1/3] Executando camada Bronze...")
    executar_ingestao()

    print("\n[2/3] Executando camada Silver...")
    executar_silver()

    print("\n[3/3] Executando camada Gold...")
    executar_gold()

    print("\n=== PIPELINE CONCLUÍDO COM SUCESSO ===")


def atualizar_camadas_analiticas() -> None:
    """Atualiza Silver e Gold usando os dados Bronze existentes."""
    print("\n=== ATUALIZANDO CAMADAS ANALÍTICAS ===")

    print("\n[1/2] Executando camada Silver...")
    executar_silver()

    print("\n[2/2] Executando camada Gold...")
    executar_gold()

    print("\n=== ATUALIZAÇÃO CONCLUÍDA ===")


if __name__ == "__main__":
    executar_pipeline_completo()
