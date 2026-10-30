
SELECT
    estado_origem,
    COUNT(*) AS quantidade_rotas,
    ROUND(AVG(distancia_km), 2) AS distancia_media_km,
    ROUND(MIN(distancia_km), 2) AS menor_distancia_km,
    ROUND(MAX(distancia_km), 2) AS maior_distancia_km
FROM gold.fato_rotas
WHERE numero_rota = 1
GROUP BY estado_origem
ORDER BY estado_origem;
