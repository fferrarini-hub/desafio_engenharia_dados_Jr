
SELECT
    estado_origem,
    COUNT(*) AS quantidade_rotas,
    ROUND(AVG(velocidade_media_kmh), 2) AS velocidade_media_kmh,
    ROUND(MIN(velocidade_media_kmh), 2) AS menor_velocidade_kmh,
    ROUND(MAX(velocidade_media_kmh), 2) AS maior_velocidade_kmh
FROM gold.fato_rotas
WHERE numero_rota = 1
    AND velocidade_media_kmh IS NOT NULL
GROUP BY estado_origem
ORDER BY estado_origem;
