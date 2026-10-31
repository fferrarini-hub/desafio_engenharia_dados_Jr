**# RouteOps — Logistics Intelligence**



Plataforma de Engenharia de Dados desenvolvida para ingestão, processamento e análise de rotas rodoviárias entre instalações logísticas da Região Sul do Brasil.



O projeto utiliza a API OSRM (Open Source Routing Machine) para consultar estimativas de trajetos rodoviários, organiza os dados em uma arquitetura Medallion (Bronze, Silver e Gold), constrói indicadores analíticos com SQL e disponibiliza os resultados por meio de um dashboard interativo.



**---**



**## 1. Objetivo do projeto**



Aplicar conceitos e boas práticas de Engenharia de Dados em um cenário de logística, contemplando:



\- Consumo de API externa.

\- Ingestão e armazenamento de dados.

\- Arquitetura Medallion (Bronze, Silver e Gold).

\- Transformação e validação de dados.

\- Modelagem analítica.

\- Desenvolvimento de indicadores utilizando SQL.

\- Testes automatizados.

\- Visualização de dados.



**## 2. Tecnologias utilizadas**



\| Tecnologia | Aplicação |

\|---|---|

\| Python 3.13 | Linguagem principal |

\| uv | Gerenciamento de ambiente e dependências |

\| OSRM API | Consulta de rotas rodoviárias |

\| Pandas | Manipulação e transformação de dados |

\| DuckDB | Armazenamento e consultas analíticas |

\| SQL | Modelagem e indicadores |

\| Streamlit | Desenvolvimento do dashboard |

\| Plotly | Visualizações interativas |

\| Pytest | Testes automatizados |

\| Ruff | Análise estática e formatação de código |



**## 3. Arquitetura de dados**



O processamento segue a arquitetura Medallion, dividido em três camadas.



**### 3.1 Bronze — Dados brutos**



Responsável pela ingestão dos dados disponibilizados pela API OSRM.



Principais responsabilidades:



\- Consulta de rotas entre instalações logísticas com coordenadas válidas.

\- Solicitação de rotas principais e alternativas.

\- Armazenamento das respostas originais em formato JSONL.

\- Persistência dos dados brutos no DuckDB.



**### 3.2 Silver — Dados tratados**



Responsável pela transformação e organização dos dados brutos.



Principais responsabilidades:



\- Extração das informações das respostas da API.

\- Separação das rotas alternativas em registros individuais.

\- Validação dos valores de distância e duração.

\- Padronização dos dados para análise.

\- Persistência dos dados tratados.



**### 3.3 Gold — Dados analíticos**



Responsável pela modelagem analítica e geração dos indicadores.



Principais responsabilidades:



\- Construção da dimensão de instalações.

\- Construção da tabela fato de rotas.

\- Relacionamento entre origem e destino utilizando JOIN.

\- Conversão de distância e duração para unidades analíticas.

\- Cálculo da velocidade média estimada.

\- Execução de consultas SQL individuais para geração dos indicadores.



**## 4. Fontes de dados e procedência**



**### 4.1 API OSRM**



O projeto utiliza o serviço público de rotas OSRM:



https\://router.project-osrm.org/



Documentação oficial:



https\://project-osrm.org/docs/v26.5.0/



A API recebe coordenadas geográficas de origem e destino e retorna estimativas de trajetos rodoviários.



Parâmetros utilizados:



\| Parâmetro | Configuração |

\|---|---|

\| Perfil de transporte | \`driving\` |

\| Rotas alternativas | Habilitadas |

\| Coordenadas | Longitude e latitude |

\| Distância retornada | Metros |

\| Duração retornada | Segundos |



O serviço calcula trajetos com base na rede viária disponível em sua base cartográfica. Os resultados representam estimativas de roteamento, não registros reais de operações de transporte.



**### 4.2 Dados cartográficos — OpenStreetMap**



O OSRM pode utilizar dados do OpenStreetMap (OSM) para construir sua rede viária.



Site oficial:



https\://www\.openstreetmap.org/



Informações sobre direitos autorais e licença:



https\://www\.openstreetmap.org/copyright



Os dados do OpenStreetMap são disponibilizados sob a licença Open Database License (ODbL), com exigências de atribuição aos colaboradores e demais condições aplicáveis.



**\*\*Atribuição:\*\*** © OpenStreetMap contributors.



A atribuição e os termos aplicáveis devem ser observados conforme a origem e a utilização dos dados cartográficos efetivamente empregados pelo serviço.



**### 4.3 Catálogo de instalações logísticas**



O arquivo \`referencia/instalacoes.csv\` contém nove instalações logísticas distribuídas entre os estados do Paraná, Santa Catarina e Rio Grande do Sul.



O catálogo possui os seguintes campos:



\| Campo | Descrição |

\|---|---|

\| \`id\` | Identificador único da instalação |

\| \`nome\` | Nome da instalação |

\| \`tipo\` | Classificação da instalação |

\| \`cidade\` | Município |

\| \`estado\` | Unidade federativa |

\| \`latitude\` | Coordenada geográfica de latitude |

\| \`longitude\` | Coordenada geográfica de longitude |

\| \`fonte\` | Endereço da fonte institucional de referência |



As fontes institucionais utilizadas incluem:



\| Instituição | Fonte |

\|---|---|

\| Portos do Paraná | https\://www\.portosdoparana.pr.gov.br/ |

\| Cargolift | https\://www\.cargolift.com.br/ |

\| Porto de Itajaí | https\://www\.portoitajai.com.br/ |

\| Porto de São Francisco do Sul | https\://www\.apsfs.sc.gov.br/ |

\| Porto de Imbituba | https\://portodeimbituba.com.br/ |

\| Portos RS | https\://www\.portosrs.com.br/ |



**### 4.4 Procedência das coordenadas**



O catálogo `referencia/instalacoes.csv` contém nove instalações logísticas. Oito registros possuem latitude e longitude preenchidas; um registro, referente à Cargolift de São José dos Pinhais, não possui coordenadas.

As coordenadas existentes são mantidas neste projeto como referências geográficas aproximadas para alimentar as consultas de roteamento da API OSRM. A origem individual de cada coordenada não foi registrada no catálogo e, portanto, não é possível atribuir documentalmente sua obtenção a uma fonte específica. A coluna `fonte` identifica referências institucionais das instalações, mas não comprova a origem das coordenadas.

**Limitações e rastreabilidade das coordenadas:**

- Representam pontos geográficos aproximados das instalações.
- A origem individual das coordenadas não está documentada no CSV.
- Não necessariamente correspondem aos portões de entrada ou áreas operacionais.
- Não foram validadas como pontos oficiais de acesso para veículos pesados.
- A precisão dos trajetos depende da qualidade dessas referências geográficas.

Uma das nove instalações cadastradas, a Cargolift de São José dos Pinhais, não possui coordenadas preenchidas e, por isso, não participa das consultas à API.



**### 4.5 Licenciamento e atribuição**



As fontes institucionais registradas no catálogo servem como referências de procedência das instalações e não representam, por si só, uma declaração de licença de redistribuição dos dados.



O projeto não atribui automaticamente ao catálogo \`instalacoes.csv\` a licença ODbL do OpenStreetMap.



Da mesma forma, a licença do software OSRM não deve ser confundida com a licença dos dados cartográficos utilizados pelo serviço.



A utilização do servidor público de demonstração OSRM está sujeita às condições e limitações estabelecidas pelo respectivo serviço.



**## 5. Granularidade dos dados**



A granularidade varia conforme a camada de processamento.



\| Camada | Granularidade |

\|---|---|

\| Bronze | Resposta bruta da API para cada consulta de origem e destino |

\| Silver | Um registro para cada rota retornada pela API, incluindo alternativas |

\| Gold | Registro analítico de rota relacionado às dimensões de origem e destino |



Cada registro da camada Silver representa uma rota retornada pela API para um par ordenado de instalações, identificando origem, destino e alternativa.



A existência de rotas alternativas significa que um mesmo par de origem e destino pode possuir múltiplos registros.



**## 6. Indicadores analíticos**



Os indicadores são implementados em arquivos SQL individuais, localizados em \`sql/gold/indicadores/\`.



\| Arquivo | Indicador |

\|---|---|

\| \`01_distancia_media.sql\` | Análise de distância média, mínima e máxima |

\| \`02_duracao_media.sql\` | Análise de duração média, mínima e máxima |

\| \`03_velocidade_media.sql\` | Análise de velocidade média |

\| \`04_melhores_rotas.sql\` | Ranking das rotas mais rápidas |

\| \`05_comparacao_alternativas.sql\` | Comparação entre rotas alternativas |

\| \`06_resumo_geral.sql\` | Resumo geral das rotas |



**## 7. Dashboard**



O projeto conta com um dashboard interativo desenvolvido com Streamlit e Plotly.



A interface permite:



\- Visualizar indicadores consolidados.

\- Analisar rotas rodoviárias.

\- Comparar alternativas de trajetos.

\- Explorar informações por estado de origem e destino.

\- Consultar métricas de distância, duração e velocidade estimada.



Os dados são consultados diretamente na camada Gold do DuckDB.



**## 8. Como executar o projeto**



**### 8.1 Pré-requisitos**



\- Python 3.13.

\- uv instalado.

\- Acesso à internet para consulta à API OSRM.



Documentação de instalação do uv:



https\://docs.astral.sh/uv/getting-started/installation/



**### 8.2 Clonar o repositório**



\`\`\`bash

git clone https\://github.com/fferrarini-hub/desafio_engenharia_dados_Jr.git

cd desafio_engenharia_dados_Jr

\`\`\`



**### 8.3 Instalar as dependências**



\`\`\`bash

uv sync --group dev

\`\`\`



**### 8.4 Executar o pipeline**



\`\`\`bash

uv run python -m projeto_final.orquestrador

\`\`\`



O pipeline executa as etapas de ingestão, transformação e geração da camada analítica.



**### 8.5 Executar o dashboard**



\`\`\`bash

uv run streamlit run src/projeto_final/dashboard.py

\`\`\`



Após a inicialização, acesse o endereço local apresentado pelo Streamlit.



**### 8.6 Executar os testes**



\`\`\`bash

uv run pytest

\`\`\`



Para verificar a cobertura:



\`\`\`bash

uv run pytest --cov=projeto_final --cov-report=term-missing

\`\`\`



**### 8.7 Verificar a qualidade do código**



Lint:



\`\`\`bash

uv run ruff check .

\`\`\`



Formatação:



\`\`\`bash

uv run ruff format .

\`\`\`



**## 9. Testes e qualidade**



O projeto utiliza Pytest para validar componentes de extração, transformação, validação e orquestração.



Os testes utilizam dados simulados e mecanismos de isolamento, como \`monkeypatch\`, reduzindo a dependência de serviços externos durante sua execução.



O Ruff é utilizado para padronização, formatação e análise estática do código.



**## 10. Limitações e considerações técnicas**



\- Distâncias e durações representam estimativas calculadas pelo OSRM, não registros reais de entregas.

\- Os resultados não representam histórico de transportadoras, atrasos efetivos ou desempenho operacional observado.

\- As rotas dependem da malha viária e dos dados cartográficos disponíveis.

\- O servidor público de demonstração do OSRM possui limitações de uso e não deve ser considerado infraestrutura de produção.

\- A precisão depende da qualidade das coordenadas de origem e destino.

\- As coordenadas do catálogo são referências geográficas aproximadas, não necessariamente pontos de acesso operacional.

\- A disponibilidade de rotas alternativas depende da resposta da API.

\- Uma instalação sem coordenadas não participa das consultas de roteamento.

\- Os resultados possuem finalidade analítica e demonstrativa.



**## 11. Utilização de Inteligência Artificial**



Durante o desenvolvimento do RouteOps, ferramentas de Inteligência Artificial foram utilizadas como apoio ao processo de Engenharia de Dados, contribuindo para a investigação de problemas técnicos, revisão de implementações, organização do código e documentação do projeto.



A utilização ocorreu de forma assistiva, mantendo a análise crítica e a responsabilidade técnica sobre as decisões e implementações.



**### 11.1 Aplicações da IA no desenvolvimento**



As ferramentas de IA foram utilizadas como apoio nas seguintes atividades:



\- **\*\*Arquitetura:\*\*** apoio na organização do projeto e na estruturação das camadas Bronze, Silver e Gold.

\- **\*\*Engenharia de Dados:\*\*** auxílio na análise das etapas de ingestão, transformação, validação e persistência dos dados.

\- **\*\*SQL:\*\*** apoio na elaboração e revisão das consultas analíticas utilizadas na camada Gold.

\- **\*\*Dashboard:\*\*** auxílio na estruturação da interface com Streamlit e Plotly, incluindo organização dos indicadores e filtros.

\- **\*\*Investigação técnica:\*\*** apoio na identificação de possíveis causas de erros e análise de alternativas de implementação.

\- **\*\*Documentação:\*\*** revisão da documentação técnica, descrição das fontes de dados e registro das limitações do projeto.



**### 11.2 Investigação de problemas técnicos**



A IA também foi utilizada como apoio na investigação de comportamentos inesperados durante o desenvolvimento.



O processo envolveu:



1\. Identificação e descrição do problema observado.

2\. Análise do contexto técnico e dos componentes envolvidos.

3\. Levantamento de possíveis causas.

4\. Avaliação de alternativas de correção.

5\. Aplicação e execução das alterações propostas.

6\. Verificação do comportamento após as modificações.



As sugestões foram avaliadas considerando a consistência dos dados, a arquitetura definida e o comportamento esperado das funcionalidades.



**### 11.3 Validações e qualidade**



A qualidade das implementações foi acompanhada por meio de ferramentas e procedimentos de validação:



\- **\*\*Pytest:\*\*** execução de testes automatizados para verificar o comportamento dos componentes do projeto.

\- **\*\*Dados simulados:\*\*** utilização de dados fictícios e mecanismos de isolamento, como \`monkeypatch\`, para reduzir a dependência de serviços externos durante os testes.

\- **\*\*Ruff:\*\*** análise estática, padronização e formatação do código.

\- **\*\*SQL:\*\*** conferência das consultas analíticas e dos resultados produzidos na camada Gold.

\- **\*\*Integração:\*\*** verificação do funcionamento conjunto do pipeline, DuckDB e dashboard.

\- **\*\*Documentação:\*\*** revisão das fontes, premissas e limitações utilizadas no processamento.



**### 11.4 Responsabilidade técnica**



A Inteligência Artificial foi utilizada como ferramenta de apoio, não como substituta do processo de desenvolvimento e validação.



As decisões técnicas, a revisão das sugestões, a execução dos testes e a avaliação dos resultados fazem parte do processo de desenvolvimento do projeto.



O objetivo foi utilizar IA para aumentar a produtividade, apoiar a resolução de problemas e aprimorar a qualidade das entregas, mantendo a rastreabilidade e a compreensão das soluções implementadas.



**## 12. Autor**



**\*\*Fabiane Ferrarini\*\***



A reprodução do projeto foi validada em um ambiente limpo, incluindo a execução completa do pipeline, a geração do banco DuckDB e o funcionamento do dashboard interativo. Também foram verificados a seleção de rotas, os filtros e as visualizações analíticas.

Projeto desenvolvido como parte dos estudos em Engenharia de Dados.



**\*\*Repositório:\*\***

https\://github.com/fferrarini-hub/desafio_engenharia_dados_Jr



**---**



© OpenStreetMap contributors. Dados cartográficos utilizados conforme os termos aplicáveis da Open Database License (ODbL).
