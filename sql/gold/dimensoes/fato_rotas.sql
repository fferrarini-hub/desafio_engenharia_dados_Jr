
CREATE OR REPLACE TABLE gold.fato_rotas AS
SELECT
    ROW_NUMBER() OVER (
        ORDER BY
            r.origem_id,
            r.destino_id,
            r.numero_rota
    ) AS rota_id,

    r.origem_id,
    origem.nome_instalacao AS origem,
    origem.cidade AS cidade_origem,
    origem.estado AS estado_origem,

    r.destino_id,
    destino.nome_instalacao AS destino,
    destino.cidade AS cidade_destino,
    destino.estado AS estado_destino,

    r.numero_rota,
    r.distancia_metros,
    r.duracao_segundos,

    r.distancia_metros / 1000.0 AS distancia_km,
    r.duracao_segundos / 3600.0 AS duracao_horas,

    CASE
        WHEN r.duracao_segundos > 0
        THEN (r.distancia_metros / 1000.0)
             / (r.duracao_segundos / 3600.0)
        ELSE NULL
    END AS velocidade_media_kmh,

    r.coletado_em

FROM silver.rotas AS r

INNER JOIN gold.dim_instalacoes AS origem
    ON r.origem_id = origem.instalacao_id

INNER JOIN gold.dim_instalacoes AS destino
    ON r.destino_id = destino.instalacao_id;
