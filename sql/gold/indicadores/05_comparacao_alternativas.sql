
WITH rota_principal AS (
    SELECT
        origem_id,
        destino_id,
        distancia_km AS distancia_principal_km,
        duracao_horas AS duracao_principal_horas
    FROM gold.fato_rotas
    WHERE numero_rota = 1
),

rotas_alternativas AS (
    SELECT
        origem,
        destino,
        origem_id,
        destino_id,
        numero_rota,
        distancia_km,
        duracao_horas
    FROM gold.fato_rotas
    WHERE numero_rota > 1
)

SELECT
    a.origem,
    a.destino,
    a.numero_rota,
    ROUND(p.distancia_principal_km, 2) AS distancia_principal_km,
    ROUND(a.distancia_km, 2) AS distancia_alternativa_km,
    ROUND(
        a.distancia_km - p.distancia_principal_km, 2
    ) AS diferenca_distancia_km,
    ROUND(p.duracao_principal_horas, 2) AS duracao_principal_horas,
    ROUND(a.duracao_horas, 2) AS duracao_alternativa_horas,
    ROUND(
        a.duracao_horas - p.duracao_principal_horas, 2
    ) AS diferenca_duracao_horas,
    CASE
        WHEN a.duracao_horas < p.duracao_principal_horas
            THEN 'Mais rapida'
        WHEN a.duracao_horas > p.duracao_principal_horas
            THEN 'Mais lenta'
        ELSE 'Mesmo tempo'
    END AS classificacao_tempo
FROM rotas_alternativas AS a
INNER JOIN rota_principal AS p
    ON a.origem_id = p.origem_id
    AND a.destino_id = p.destino_id
ORDER BY diferenca_duracao_horas;
