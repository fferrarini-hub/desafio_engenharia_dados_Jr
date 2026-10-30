
SELECT
    origem,
    cidade_origem,
    estado_origem,
    destino,
    cidade_destino,
    estado_destino,
    numero_rota,
    ROUND(distancia_km, 2) AS distancia_km,
    ROUND(duracao_horas, 2) AS duracao_horas,
    ROUND(velocidade_media_kmh, 2) AS velocidade_media_kmh
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY origem_id, destino_id
            ORDER BY duracao_segundos ASC, numero_rota ASC
        ) AS classificacao
    FROM gold.fato_rotas
) AS rotas_classificadas
WHERE classificacao = 1
ORDER BY duracao_horas ASC;
