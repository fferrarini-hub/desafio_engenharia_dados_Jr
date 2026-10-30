# RouteOps — Logistics Intelligence

Plataforma de Engenharia de Dados desenvolvida para ingestão, processamento e análise de rotas rodoviárias entre instalações logísticas da Região Sul do Brasil.

O projeto utiliza a API OSRM (Open Source Routing Machine) para consultar estimativas de trajetos rodoviários, organiza os dados em uma arquitetura Medallion (Bronze, Silver e Gold), constrói indicadores analíticos com SQL e disponibiliza os resultados por meio de um dashboard interativo.

---

## 1. Objetivo do projeto

Aplicar conceitos e boas práticas de Engenharia de Dados em um cenário de logística, contemplando:

- Consumo de API externa.
- Ingestão e armazenamento de dados.
- Arquitetura Medallion (Bronze, Silver e Gold).
- Transformação e validação de dados.
- Modelagem analítica.
- Desenvolvimento de indicadores utilizando SQL.
- Testes automatizados.
- Visualização de dados.

## 2. Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| Python 3.13 | Linguagem principal |
| uv | Gerenciamento de ambiente e dependências |
| OSRM API | Consulta de rotas rodoviárias |
| Pandas | Manipulação e transformação de dados |
| DuckDB | Armazenamento e consultas analíticas |
| SQL | Modelagem e indicadores |
| Streamlit | Desenvolvimento do dashboard |
| Plotly | Visualizações interativas |
| Pytest | Testes automatizados |
| Ruff | Análise estática e formatação de código |

## 3. Arquitetura de dados

O processamento segue a arquitetura Medallion, dividido em três camadas.

### 3.1 Bronze — Dados brutos

Responsável pela ingestão dos dados disponibilizados pela API OSRM.

Principais responsabilidades:

- Consulta de rotas entre instalações logísticas com coordenadas válidas.
- Solicitação de rotas principais e alternativas.
- Armazenamento das respostas originais em formato JSONL.
- Persistência dos dados brutos no DuckDB.

### 3.2 Silver — Dados tratados

Responsável pela transformação e organização dos dados brutos.

Principais responsabilidades:

- Extração das informações das respostas da API.
- Separação das rotas alternativas em registros individuais.
- Validação dos valores de distância e duração.
- Padronização dos dados para análise.
- Persistência dos dados tratados.

### 3.3 Gold — Dados analíticos

Responsável pela modelagem analítica e geração dos indicadores.

Principais responsabilidades:

- Construção da dimensão de instalações.
- Construção da tabela fato de rotas.
- Relacionamento entre origem e destino utilizando JOIN.
- Conversão de distância e duração para unidades analíticas.
- Cálculo da velocidade média estimada.
- Execução de consultas SQL individuais para geração dos indicadores.

## 4. Fontes de dados e procedência

### 4.1 API OSRM

O projeto utiliza o serviço público de rotas OSRM:

https://router.project-osrm.org/

Documentação oficial:

https://project-osrm.org/docs/v26.5.0/

A API recebe coordenadas geográficas de origem e destino e retorna estimativas de trajetos rodoviários.

Parâmetros utilizados:

| Parâmetro | Configuração |
|---|---|
| Perfil de transporte | `driving` |
| Rotas alternativas | Habilitadas |
| Coordenadas | Longitude e latitude |
| Distância retornada | Metros |
| Duração retornada | Segundos |

O serviço calcula trajetos com base na rede viária disponível em sua base cartográfica. Os resultados representam estimativas de roteamento, não registros reais de operações de transporte.

### 4.2 Dados cartográficos — OpenStreetMap

O OSRM pode utilizar dados do OpenStreetMap (OSM) para construir sua rede viária.

Site oficial:

https://www.openstreetmap.org/

Informações sobre direitos autorais e licença:

https://www.openstreetmap.org/copyright

Os dados do OpenStreetMap são disponibilizados sob a licença Open Database License (ODbL), com exigências de atribuição aos colaboradores e demais condições aplicáveis.

A atribuição cartográfica correspondente deve ser considerada na utilização e distribuição dos dados derivados do OpenStreetMap.

**Atribuição:** © OpenStreetMap contributors.

### 4.3 Catálogo de instalações logísticas

O arquivo `referencia/instalacoes.csv` contém nove instalações logísticas distribuídas entre os estados do Paraná, Santa Catarina e Rio Grande do Sul.

O catálogo possui os seguintes campos:

| Campo | Descrição |
|---|---|
| `id` | Identificador único da instalação |
| `nome` | Nome da instalação |
| `tipo` | Classificação da instalação |
| `cidade` | Município |
| `estado` | Unidade federativa |
| `latitude` | Coordenada geográfica de latitude |
| `longitude` | Coordenada geográfica de longitude |
| `fonte` | Endereço da fonte institucional de referência |

As fontes institucionais utilizadas incluem:

| Instituição | Fonte |
|---|---|
| Portos do Paraná | https://www.portosdoparana.pr.gov.br/ |
| Cargolift | https://www.cargolift.com.br/ |
| Porto de Itajaí | https://www.portoitajai.com.br/ |
| Porto de São Francisco do Sul | https://www.apsfs.sc.gov.br/ |
| Porto de Imbituba | https://portodeimbituba.com.br/ |
| Portos RS | https://www.portosrs.com.br/ |

### 4.4 Procedência das coordenadas

As coordenadas geográficas foram levantadas por meio de consulta cartográfica ao Google Maps, utilizando pontos de referência aproximados das instalações logísticas.

Essas coordenadas foram utilizadas como referências para alimentar as consultas de roteamento da API OSRM.

**Limitações das coordenadas:**

- Representam pontos geográficos aproximados das instalações.
- Não necessariamente correspondem aos portões de entrada ou áreas operacionais.
- Não foram validadas como pontos oficiais de acesso para veículos pesados.
- A precisão dos trajetos depende da qualidade dessas referências geográficas.

Uma das nove instalações cadastradas, a Cargolift de São José dos Pinhais, não possui coordenadas preenchidas e, por isso, não participa das consultas à API.

### 4.5 Licenciamento e atribuição

As fontes institucionais registradas no catálogo servem como referências de procedência das instalações e não representam, por si só, uma declaração de licença de redistribuição dos dados.

O projeto não atribui automaticamente ao catálogo `instalacoes.csv` a licença ODbL do OpenStreetMap.

Da mesma forma, a licença do software OSRM não deve ser confundida com a licença dos dados cartográficos utilizados pelo serviço.

A utilização do servidor público de demonstração OSRM está sujeita às condições e limitações estabelecidas pelo respectivo serviço.

## 5. Granularidade dos dados

A granularidade varia conforme a camada de processamento.

| Camada | Granularidade |
|---|---|
| Bronze | Resposta bruta da API para cada consulta de origem e destino |
| Silver | Um registro para cada rota retornada pela API, incluindo alternativas |
| Gold | Registro analítico de rota relacionado às dimensões de origem e destino |

Cada registro da camada Silver representa uma rota retornada pela API para um par ordenado de instalações, identificando origem, destino e alternativa.

A existência de rotas alternativas significa que um mesmo par de origem e destino pode possuir múltiplos registros.

## 6. Indicadores analíticos

Os indicadores são implementados em arquivos SQL individuais, localizados em `sql/gold/indicadores/`.

| Arquivo | Indicador |
|---|---|
| `01_distancia_media.sql` | Análise de distância média, mínima e máxima |
| `02_duracao_media.sql` | Análise de duração média, mínima e máxima |
| `03_velocidade_media.sql` | Análise de velocidade média |
| `04_melhores_rotas.sql` | Ranking das rotas mais rápidas |
| `05_comparacao_alternativas.sql` | Comparação entre rotas alternativas |
| `06_resumo_geral.sql` | Resumo geral das rotas |

## 7. Dashboard

O projeto conta com um dashboard interativo desenvolvido com Streamlit e Plotly.

A interface permite:

- Visualizar indicadores consolidados.
- Analisar rotas rodoviárias.
- Comparar alternativas de trajetos.
- Explorar informações por estado de origem e destino.
- Consultar métricas de distância, duração e velocidade estimada.

Os dados são consultados diretamente na camada Gold do DuckDB.

## 8. Como executar o projeto

### 8.1 Pré-requisitos

- Python 3.13.
- uv instalado.
- Acesso à internet para consulta à API OSRM.

Documentação de instalação do uv:

https://docs.astral.sh/uv/getting-started/installation/

### 8.2 Clonar o repositório

```bash
git clone https://github.com/fferrarini-hub/desafio_engenharia_dados_Jr.git
cd desafio_engenharia_dados_Jr
```

### 8.3 Instalar as dependências

```bash
uv sync --group dev
```

### 8.4 Executar o pipeline

```bash
uv run python -m projeto_final.orquestrador
```

O pipeline executa as etapas de ingestão, transformação e geração da camada analítica.

### 8.5 Executar o dashboard

```bash
uv run streamlit run src/projeto_final/dashboard.py
```

Após a inicialização, acesse o endereço local apresentado pelo Streamlit.

### 8.6 Executar os testes

```bash
uv run pytest
```

Para verificar a cobertura:

```bash
uv run pytest --cov=projeto_final --cov-report=term-missing
```

### 8.7 Verificar a qualidade do código

Lint:

```bash
uv run ruff check .
```

Formatação:

```bash
uv run ruff format .
```

## 9. Testes e qualidade

O projeto utiliza Pytest para validar componentes de extração, transformação, validação e orquestração.

Os testes utilizam dados simulados e mecanismos de isolamento, como `monkeypatch`, reduzindo a dependência de serviços externos durante sua execução.

O Ruff é utilizado para padronização, formatação e análise estática do código.

## 10. Limitações e considerações técnicas

- Distâncias e durações representam estimativas calculadas pelo OSRM, não registros reais de entregas.
- Os resultados não representam histórico de transportadoras, atrasos efetivos ou desempenho operacional observado.
- As rotas dependem da malha viária e dos dados cartográficos disponíveis.
- O servidor público de demonstração do OSRM possui limitações de uso e não deve ser considerado infraestrutura de produção.
- A precisão depende da qualidade das coordenadas de origem e destino.
- As coordenadas do catálogo são referências geográficas aproximadas, não necessariamente pontos de acesso operacional.
- A disponibilidade de rotas alternativas depende da resposta da API.
- Uma instalação sem coordenadas não participa das consultas de roteamento.
- Os resultados possuem finalidade analítica e demonstrativa.

## 11. Utilização de Inteligência Artificial

Ferramentas de Inteligência Artificial foram utilizadas como apoio durante o desenvolvimento do projeto, incluindo:

- Investigação e resolução de problemas técnicos.
- Apoio na revisão e organização do código.
- Auxílio na documentação técnica.
- Apoio na análise de resultados e validação de implementações.

As sugestões produzidas com auxílio de IA foram avaliadas durante o desenvolvimento, com acompanhamento das implementações, execução de testes e validações técnicas.

A utilização de IA não substituiu a necessidade de verificar o funcionamento do código, a consistência dos dados e os resultados produzidos.

## 12. Autor

**Fabi Ferrarini**

Projeto desenvolvido como parte dos estudos em Engenharia de Dados.

**Repositório:**
https://github.com/fferrarini-hub/desafio_engenharia_dados_Jr

---

© OpenStreetMap contributors. Dados cartográficos utilizados conforme os termos da Open Database License (ODbL).
