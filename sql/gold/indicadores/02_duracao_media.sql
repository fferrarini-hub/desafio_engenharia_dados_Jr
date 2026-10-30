
SELECT
    estado_origem,
    COUNT(*) AS quantidade_rotas,
    ROUND(AVG(duracao_horas), 2) AS duracao_media_horas,
    ROUND(MIN(duracao_horas), 2) AS menor_duracao_horas,
    ROUND(MAX(duracao_horas), 2) AS maior_duracao_horas
FROM gold.fato_rotas
WHERE numero_rota = 1
GROUP BY estado_origem
ORDER BY estado_origem;
