
SELECT
    COUNT(*) AS total_rotas,
    ROUND(AVG(distancia_km), 2) AS distancia_media_km,
    ROUND(AVG(duracao_horas), 2) AS duracao_media_horas,
    ROUND(AVG(velocidade_media_kmh), 2) AS velocidade_media_kmh
FROM gold.fato_rotas
WHERE numero_rota = 1;
