# RouteOps — Logistics Intelligence

Plataforma de Engenharia de Dados desenvolvida para ingestão, processamento e análise de rotas rodoviárias entre instalações logísticas da Região Sul do Brasil.

O projeto utiliza a API OSRM para consultar estimativas de trajetos rodoviários, organiza os dados em uma arquitetura Bronze, Silver e Gold e disponibiliza indicadores analíticos por meio de um dashboard interativo.

## Objetivo do projeto

Aplicar conceitos e boas práticas de Engenharia de Dados em um cenário de logística, contemplando:

- Consumo de API externa.
- Ingestão e armazenamento de dados.
- Arquitetura Medallion (Bronze, Silver e Gold).
- Transformação e modelagem de dados.
- Desenvolvimento de indicadores analíticos utilizando SQL.
- Testes automatizados.
- Visualização de dados.

## Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python 3.13 | Linguagem principal |
| uv | Gerenciamento de ambiente e dependências |
| OSRM API | Consulta de rotas rodoviárias |
| Pandas | Manipulação de dados |
| DuckDB | Banco de dados analítico |
| SQL | Transformações e indicadores |
| Streamlit | Desenvolvimento do dashboard |
| Plotly | Visualizações interativas |
| Pytest | Testes automatizados |
| Ruff | Análise e formatação de código |

## Arquitetura de dados

O processamento segue a arquitetura Medallion, dividido em três camadas.

### Bronze — Dados brutos

Responsável pela ingestão dos dados disponibilizados pela API OSRM.

- Consulta de rotas entre instalações logísticas com coordenadas válidas.
- Solicitação de rotas principais e alternativas.
- Armazenamento das respostas originais em JSONL.
- Persistência dos dados no DuckDB.

### Silver — Dados tratados

Responsável pela transformação e organização dos dados brutos.

- Extração das informações de cada rota.
- Separação das rotas alternativas em registros individuais.
- Validação de distância e duração.
- Padronização dos dados para análise.
- Persistência dos dados tratados.

### Gold — Dados analíticos

Responsável pela modelagem analítica e geração dos indicadores.

- Construção da dimensão de instalações.
- Construção da tabela fato de rotas.
- Relacionamento entre origem e destino utilizando JOIN.
- Conversão de distância e duração para unidades analíticas.
- Cálculo de velocidade média estimada.
- Execução de consultas SQL para geração dos indicadores.

## Fonte de dados

### API OSRM

O projeto utiliza o serviço público de rotas OSRM:

https://router.project-osrm.org/

Documentação oficial:

https://project-osrm.org/docs/v26.5.0/

A API recebe coordenadas geográficas de origem e destino e retorna estimativas de trajetos rodoviários.

Parâmetros utilizados:

- Perfil de transporte: `driving`.
- Rotas alternativas: habilitadas.
- Coordenadas: longitude e latitude.
- Distância retornada em metros.
- Duração retornada em segundos.

### Catálogo de instalações

O arquivo `referencia/instalacoes.csv` contém nove instalações logísticas distribuídas entre Paraná, Santa Catarina e Rio Grande do Sul.

As referências utilizadas incluem:

- Portos do Paraná: https://www.portosdoparana.pr.gov.br/
- Cargolift: https://www.cargolift.com.br/
- Porto de Itajaí: https://www.portoitajai.com.br/
- Porto de São Francisco do Sul: https://www.apsfs.sc.gov.br/
- Porto de Imbituba: https://portodeimbituba.com.br/
- Portos RS: https://www.portosrs.com.br/

**Granularidade:** cada registro da camada Silver representa uma rota retornada pela API para um par ordenado de instalações, identificando origem, destino e alternativa.

**Observação:** as coordenadas são referências geográficas e não necessariamente representam os portões de acesso das instalações. Uma instalação não possui coordenadas cadastradas e não participa das consultas à API.

## Indicadores analíticos

Os indicadores são implementados em arquivos SQL individuais.

| Arquivo | Indicador |
|---|---|
| `01_distancia_media.sql` | Análise de distância média, mínima e máxima |
| `02_duracao_media.sql` | Análise de duração média, mínima e máxima |
| `03_velocidade_media.sql` | Análise de velocidade média |
| `04_melhores_rotas.sql` | Ranking das rotas mais rápidas |
| `05_comparacao_alternativas.sql` | Comparação entre rotas alternativas |
| `06_resumo_geral.sql` | Resumo geral das rotas |

## Dashboard

O projeto conta com um dashboard interativo desenvolvido com Streamlit e Plotly.

A interface permite visualizar indicadores consolidados, analisar rotas, comparar alternativas e explorar informações por estado de origem e destino.

Os dados são consultados diretamente na camada Gold do DuckDB.

## Como executar o projeto

### Pré-requisitos

- Python 3.13.
- uv instalado.
- Acesso à internet para consulta à API OSRM.

Documentação de instalação do uv:

https://docs.astral.sh/uv/getting-started/installation/

### 1. Clonar o repositório

```bash
git clone https://github.com/fferrarini-hub/desafio_engenharia_dados_Jr.git
cd desafio_engenharia_dados_Jr
```

### 2. Instalar as dependências

```bash
uv sync --group dev
```

### 3. Executar o pipeline

```bash
uv run python -m projeto_final.orquestrador
```

O pipeline executa as etapas de ingestão, transformação e geração da camada analítica.

### 4. Executar o dashboard

```bash
uv run streamlit run src/projeto_final/dashboard.py
```

Após a inicialização, acesse o endereço local apresentado pelo Streamlit.

### 5. Executar os testes

```bash
uv run pytest
```

Para verificar a cobertura:

```bash
uv run pytest --cov=projeto_final --cov-report=term-missing
```

### 6. Verificar a qualidade do código

Lint:

```bash
uv run ruff check .
```

Formatação:

```bash
uv run ruff format .
```

## Limitações e considerações

- Distâncias e durações representam estimativas calculadas pelo OSRM, não registros reais de entregas.
- Os resultados não representam histórico de transportadoras ou atrasos operacionais efetivos.
- As rotas dependem da malha viária e dos dados cartográficos disponíveis.
- O servidor público de demonstração do OSRM possui limitações de uso e não deve ser considerado infraestrutura de produção.
- A precisão depende da qualidade das coordenadas de origem e destino.
- A disponibilidade de rotas alternativas depende da resposta da API.

## Testes e qualidade

O projeto utiliza Pytest para validar componentes de extração, transformação, validação e orquestração.

Os testes utilizam dados simulados e mecanismos de isolamento, como `monkeypatch`, para reduzir a dependência de serviços externos durante a execução.

O Ruff é utilizado para padronização, formatação e análise estática do código.

## Utilização de Inteligência Artificial

Ferramentas de Inteligência Artificial foram utilizadas como apoio durante o desenvolvimento, na investigação de problemas técnicos, revisão de código e organização de documentação.

As implementações e decisões técnicas foram acompanhadas e validadas durante o desenvolvimento.

## Autor

**Fabi Ferrarini**

Projeto desenvolvido como parte dos estudos em Engenharia de Dados.

Repositório: https://github.com/fferrarini-hub/desafio_engenharia_dados_Jr
