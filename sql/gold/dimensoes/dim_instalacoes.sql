
CREATE OR REPLACE TABLE gold.dim_instalacoes AS
SELECT
    CAST(id AS INTEGER) AS instalacao_id,
    TRIM(nome) AS nome_instalacao,
    TRIM(tipo) AS tipo_instalacao,
    TRIM(cidade) AS cidade,
    UPPER(TRIM(estado)) AS estado,
    TRY_CAST(latitude AS DOUBLE) AS latitude,
    TRY_CAST(longitude AS DOUBLE) AS longitude,
    TRIM(fonte) AS fonte
FROM read_csv(
    'referencia/instalacoes.csv',
    header = true,
    nullstr = ''
);
