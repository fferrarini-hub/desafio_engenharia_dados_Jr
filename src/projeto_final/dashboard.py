"""RouteOps - Logistics Intelligence Platform."""

from pathlib import Path

import duckdb
import plotly.express as px
import streamlit as st

# ============================================================
# CONFIGURACAO
# ============================================================

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "projeto_final.duckdb"

st.set_page_config(
    page_title="RouteOps | Logistics Intelligence",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# IDENTIDADE VISUAL
# ============================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    * {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #08111F;
        background-image:
            radial-gradient(
                ellipse at 10% 5%,
                rgba(0, 205, 190, 0.13),
                transparent 32%
            ),
            radial-gradient(
                ellipse at 90% 20%,
                rgba(38, 100, 180, 0.17),
                transparent 35%
            ),
            radial-gradient(
                ellipse at 50% 100%,
                rgba(0, 150, 130, 0.09),
                transparent 40%
            ),
            linear-gradient(
                rgba(80, 140, 170, 0.035) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(80, 140, 170, 0.035) 1px,
                transparent 1px
            );

        background-size:
            auto,
            auto,
            auto,
            40px 40px,
            40px 40px;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #101E32,
            #0A1423
        );
        border-right: 1px solid #253B52;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #F2F7FC !important;
    }

    p, label {
        color: #A9BCD0;
    }

    .brand {
        font-size: 34px;
        font-weight: 800;
        letter-spacing: 4px;
        color: #43DDC7;
    }

    .brand-subtitle {
        font-size: 11px;
        color: #9CB4CB;
        letter-spacing: 4px;
        margin-top: 4px;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(
                circle at 85% 50%,
                rgba(46, 218, 198, 0.17),
                transparent 30%
            ),
            linear-gradient(
                120deg,
                #152B43,
                #102238,
                #102C39
            );
        border: 1px solid #31536A;
        border-radius: 18px;
        padding: 30px;
        margin-bottom: 28px;
        box-shadow: 0 15px 40px rgba(0,0,0,.25);
    }

    .hero:after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: 30px;
        top: -110px;
        border: 1px solid rgba(67,221,199,.2);
        border-radius: 50%;
        box-shadow:
            0 0 0 30px rgba(67,221,199,.025),
            0 0 0 65px rgba(67,221,199,.025),
            0 0 0 100px rgba(67,221,199,.02);
    }

    .hero-description {
        color: #B5C9DB;
        font-size: 13px;
        margin-top: 18px;
        max-width: 650px;
    }

    .hero-status {
        color: #43DDC7;
        font-size: 10px;
        letter-spacing: 2px;
        font-weight: 700;
        margin-top: 20px;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(
            145deg,
            #172B42,
            #102035
        );
        border: 1px solid #29445C;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,.16);
    }

    [data-testid="stMetricLabel"] {
        color: #91AFC6 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
    }

    [data-testid="stMetricValue"] {
        color: #F2F7FC !important;
        font-weight: 800;
    }

    .section-title {
        color: #43DDC7;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 5px;
    }

    .section-description {
        color: #91A9C0;
        font-size: 12px;
        margin-bottom: 18px;
    }

    .panel {
        background: rgba(18, 35, 55, 0.88);
        border: 1px solid #29445C;
        border-radius: 14px;
        padding: 18px;
    }

    [data-testid="stTabs"] button {
        color: #A9BCD0;
    }

    [data-testid="stTabs"] button[aria-selected="true"] {
        color: #43DDC7;
    }

    hr {
        border-color: #263B50;
    }

    .footer {
        text-align: center;
        color: #718BA4;
        font-size: 10px;
        letter-spacing: 2px;
        padding: 30px 0 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# BANCO DE DADOS
# ============================================================


def consultar(sql, parametros=None):
    """Consulta o DuckDB em modo somente leitura."""
    if not DB_PATH.exists():
        raise FileNotFoundError("Banco não encontrado. Execute as camadas do projeto.")

    con = duckdb.connect(str(DB_PATH), read_only=True)

    try:
        return con.execute(sql, parametros or []).fetchdf()
    finally:
        con.close()


# ============================================================
# FILTROS E CONSULTAS
# ============================================================


def carregar_estados():
    """Retorna os estados cadastrados na dimensão."""
    return consultar(
        """
        SELECT DISTINCT estado
        FROM gold.dim_instalacoes
        ORDER BY estado
        """
    )["estado"].tolist()


def carregar_resumo(origens, destinos):
    """Calcula os indicadores das rotas principais."""
    if not origens or not destinos:
        return consultar(
            """
            SELECT
                0 AS total_rotas,
                NULL AS distancia_media,
                NULL AS duracao_media,
                NULL AS velocidade_media
            WHERE FALSE
            """
        )

    origem_placeholders = ", ".join(["?"] * len(origens))
    destino_placeholders = ", ".join(["?"] * len(destinos))

    return consultar(
        f"""
        SELECT
            COUNT(*) AS total_rotas,
            ROUND(AVG(distancia_km), 2) AS distancia_media,
            ROUND(AVG(duracao_horas), 2) AS duracao_media,
            ROUND(AVG(velocidade_media_kmh), 2) AS velocidade_media
        FROM gold.fato_rotas
        WHERE numero_rota = 1
          AND estado_origem IN ({origem_placeholders})
          AND estado_destino IN ({destino_placeholders})
        """,
        list(origens) + list(destinos),
    )


def carregar_desempenho(origens, destinos):
    """Consulta o desempenho por estado de origem."""
    if not origens or not destinos:
        return consultar("SELECT * FROM gold.fato_rotas WHERE FALSE")

    po = ", ".join(["?"] * len(origens))
    pd = ", ".join(["?"] * len(destinos))

    return consultar(
        f"""
        SELECT
            estado_origem,
            COUNT(*) AS quantidade_rotas,
            ROUND(AVG(distancia_km), 2) AS distancia_media,
            ROUND(AVG(duracao_horas), 2) AS duracao_media,
            ROUND(AVG(velocidade_media_kmh), 2) AS velocidade_media
        FROM gold.fato_rotas
        WHERE numero_rota = 1
          AND estado_origem IN ({po})
          AND estado_destino IN ({pd})
        GROUP BY estado_origem
        ORDER BY estado_origem
        """,
        list(origens) + list(destinos),
    )


def carregar_ranking(origens, destinos):
    """Consulta as dez rotas principais mais rápidas."""
    if not origens or not destinos:
        return consultar("SELECT * FROM gold.fato_rotas WHERE FALSE")

    po = ", ".join(["?"] * len(origens))
    pd = ", ".join(["?"] * len(destinos))

    return consultar(
        f"""
        SELECT
            origem,
            destino,
            estado_origem,
            estado_destino,
            ROUND(distancia_km, 2) AS distancia_km,
            ROUND(duracao_horas, 2) AS duracao_horas,
            ROUND(velocidade_media_kmh, 2) AS velocidade_media
        FROM gold.fato_rotas
        WHERE numero_rota = 1
          AND estado_origem IN ({po})
          AND estado_destino IN ({pd})
        ORDER BY duracao_segundos
        LIMIT 10
        """,
        list(origens) + list(destinos),
    )


def carregar_alternativas(origens, destinos):
    """Consulta a comparação entre rotas principais e alternativas."""
    if not origens or not destinos:
        return consultar("SELECT * FROM gold.fato_rotas WHERE FALSE")

    po = ", ".join(["?"] * len(origens))
    pd = ", ".join(["?"] * len(destinos))

    return consultar(
        f"""
        WITH principais AS (
            SELECT
                origem_id,
                destino_id,
                duracao_segundos AS duracao_principal,
                distancia_km AS distancia_principal
            FROM gold.fato_rotas
            WHERE numero_rota = 1
              AND estado_origem IN ({po})
              AND estado_destino IN ({pd})
        )
        SELECT
            r.origem,
            r.destino,
            r.numero_rota,
            ROUND(r.distancia_km, 2) AS distancia_alternativa,
            ROUND(r.duracao_segundos / 3600.0, 2)
                AS duracao_alternativa,
            ROUND(
                (r.duracao_segundos - p.duracao_principal) / 3600.0,
                2
            ) AS diferenca_horas,
            ROUND(
                r.distancia_km - p.distancia_principal,
                2
            ) AS diferenca_km
        FROM gold.fato_rotas r
        INNER JOIN principais p
            ON r.origem_id = p.origem_id
            AND r.destino_id = p.destino_id
        WHERE r.numero_rota > 1
        ORDER BY diferenca_horas
        """,
        list(origens) + list(destinos),
    )


def carregar_instalacoes():
    """Carrega as instalações com coordenadas válidas."""
    return consultar(
        """
        SELECT
            nome_instalacao,
            cidade,
            estado,
            latitude,
            longitude,
            tipo_instalacao
        FROM gold.dim_instalacoes
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
        ORDER BY estado, nome_instalacao
        """
    )


# ============================================================
# GRAFICOS
# ============================================================


def tema_grafico(fig, altura=350):
    """Aplica o tema visual aos gráficos Plotly."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(18,35,55,0)",
        plot_bgcolor="rgba(18,35,55,0)",
        font=dict(
            family="Inter",
            color="#DCE8F3",
        ),
        height=altura,
        margin=dict(l=15, r=15, t=55, b=20),
        legend=dict(
            orientation="h",
            y=1.12,
            x=0,
        ),
    )

    fig.update_xaxes(
        gridcolor="rgba(110,150,180,.12)",
        zerolinecolor="rgba(110,150,180,.15)",
    )

    fig.update_yaxes(
        gridcolor="rgba(110,150,180,.12)",
        zerolinecolor="rgba(110,150,180,.15)",
    )

    return fig


def secao(titulo, descricao):
    """Apresenta o título de uma seção."""
    st.markdown(
        f"""
        <div class="section-title">{titulo.upper()}</div>
        <div class="section-description">{descricao}</div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# APLICACAO
# ============================================================


def main():
    """Executa o dashboard RouteOps."""

    # CABECALHO
    st.markdown(
        """
        <div class="hero">
            <div class="brand">ROUTEOPS</div>
            <div class="brand-subtitle">
                LOGISTICS INTELLIGENCE PLATFORM
            </div>
            <div class="hero-description">
                Inteligência de dados para análise de conectividade,
                desempenho e alternativas de rotas logísticas.
            </div>
            <div class="hero-status">
                ● ANALYTICS ENVIRONMENT &nbsp; | &nbsp;
                SOUTHERN BRAZIL
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # SIDEBAR
    with st.sidebar:
        st.markdown(
            '<div class="brand">ROUTEOPS</div>',
            unsafe_allow_html=True,
        )
        st.caption("LOGISTICS INTELLIGENCE")
        st.divider()

        st.markdown("### FILTROS DE ANÁLISE")

        try:
            estados = carregar_estados()
        except Exception as erro:
            st.error(f"Erro ao carregar estados: {erro}")
            return

        origens = st.multiselect(
            "Estado de origem",
            estados,
            default=estados,
        )

        destinos = st.multiselect(
            "Estado de destino",
            estados,
            default=estados,
        )

        st.divider()

        st.markdown("### DATA SOURCES")
        st.caption("OSRM Routing API")
        st.caption("DuckDB Analytics")
        st.caption("Python + Streamlit")

        st.divider()
        st.caption(
            "As durações representam estimativas de roteamento, "
            "não tempos reais de entrega."
        )

    # CONSULTAS
    try:
        resumo = carregar_resumo(origens, destinos)

        desempenho = carregar_desempenho(origens, destinos)

        ranking = carregar_ranking(origens, destinos)

        alternativas = carregar_alternativas(origens, destinos)

        instalacoes = carregar_instalacoes()

    except Exception as erro:
        st.error(f"Erro ao consultar a camada Gold: {erro}")
        return

    if resumo.empty or int(resumo.iloc[0]["total_rotas"]) == 0:
        st.warning("Nenhuma rota encontrada para os filtros selecionados.")
        return

    dados = resumo.iloc[0]

    # ========================================================
    # KPI
    # ========================================================

    secao(
        "01 / Overview",
        "Visão consolidada das rotas principais.",
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "ROTAS ANALISADAS",
        f"{int(dados['total_rotas'])}",
    )

    c2.metric(
        "DISTÂNCIA MÉDIA",
        f"{dados['distancia_media']:,.1f} km",
    )

    c3.metric(
        "DURAÇÃO MÉDIA",
        f"{dados['duracao_media']:,.1f} h",
    )

    c4.metric(
        "VELOCIDADE MÉDIA",
        f"{dados['velocidade_media']:,.1f} km/h",
    )

    st.divider()

    # ========================================================
    # MAPA
    # ========================================================

    secao(
        "02 / Logistics Network",
        "Distribuição geográfica das instalações cadastradas.",
    )

    mapa = instalacoes.copy()

    estados_mapa = set(origens + destinos)

    mapa = mapa[mapa["estado"].isin(estados_mapa)]

    if not mapa.empty:
        # O st.map evita dependência de tokens de mapas.
        mapa_visual = mapa.rename(
            columns={
                "latitude": "lat",
                "longitude": "lon",
            }
        )

        st.map(
            mapa_visual,
            latitude="lat",
            longitude="lon",
            size=180,
            color="#28CDBB",
            zoom=4,
            use_container_width=True,
        )

        st.caption(
            "Pontos de referência das instalações. "
            "As coordenadas não representam necessariamente "
            "os portões de acesso."
        )

        with st.expander("Ver instalações no mapa"):
            st.dataframe(
                mapa[
                    [
                        "nome_instalacao",
                        "cidade",
                        "estado",
                        "tipo_instalacao",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

    else:
        st.info("Não há instalações nos estados selecionados.")

    st.divider()

    # ========================================================
    # DESEMPENHO
    # ========================================================

    secao(
        "03 / Performance Analytics",
        "Comparação dos indicadores por estado de origem.",
    )

    tab1, tab2, tab3 = st.tabs(["DISTÂNCIA", "DURAÇÃO", "VELOCIDADE"])

    with tab1:
        fig = px.bar(
            desempenho,
            x="estado_origem",
            y="distancia_media",
            color="estado_origem",
            text="distancia_media",
            title="Distância média por estado (km)",
            labels={
                "estado_origem": "Estado",
                "distancia_media": "Distância média (km)",
            },
        )
        tema_grafico(fig)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = px.bar(
            desempenho,
            x="estado_origem",
            y="duracao_media",
            color="estado_origem",
            text="duracao_media",
            title="Duração média estimada por estado (h)",
            labels={
                "estado_origem": "Estado",
                "duracao_media": "Duração média (h)",
            },
        )
        tema_grafico(fig)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        fig = px.bar(
            desempenho,
            x="estado_origem",
            y="velocidade_media",
            color="estado_origem",
            text="velocidade_media",
            title="Velocidade média estimada por estado (km/h)",
            labels={
                "estado_origem": "Estado",
                "velocidade_media": "Velocidade média (km/h)",
            },
        )
        tema_grafico(fig)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ========================================================
    # RANKING
    # ========================================================

    secao(
        "04 / Route Ranking",
        "Rotas principais ordenadas pela menor duração estimada.",
    )

    if not ranking.empty:
        ranking = ranking.copy()

        ranking["trajeto"] = ranking["origem"] + " → " + ranking["destino"]

        ranking_plot = ranking.sort_values(
            "duracao_horas",
            ascending=True,
        )

        fig = px.bar(
            ranking_plot,
            x="duracao_horas",
            y="trajeto",
            orientation="h",
            color="estado_origem",
            text="duracao_horas",
            hover_data=[
                "distancia_km",
                "velocidade_media",
            ],
            labels={
                "duracao_horas": "Duração estimada (h)",
                "trajeto": "Trajeto",
                "estado_origem": "Estado",
            },
            title="TOP 10 ROTAS COM MENOR DURAÇÃO",
        )

        fig.update_layout(yaxis=dict(autorange="reversed"))

        tema_grafico(fig, 430)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            ranking.drop(columns=["trajeto"]),
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("Nenhuma rota encontrada.")

    st.divider()

    # ========================================================
    # ALTERNATIVAS
    # ========================================================

    secao(
        "05 / Alternative Routes",
        "Comparação entre a rota principal e as alternativas retornadas pelo OSRM.",
    )

    if not alternativas.empty:
        alternativas = alternativas.copy()

        alternativas["trajeto"] = (
            alternativas["origem"] + " → " + alternativas["destino"]
        )

        fig = px.bar(
            alternativas,
            x="trajeto",
            y="diferenca_horas",
            color="diferenca_horas",
            color_continuous_scale="RdYlGn_r",
            hover_data=[
                "numero_rota",
                "diferenca_km",
                "duracao_alternativa",
            ],
            title="DIFERENÇA DE DURAÇÃO DAS ALTERNATIVAS",
            labels={
                "trajeto": "Trajeto",
                "diferenca_horas": "Diferença de duração (h)",
            },
        )

        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="#FFFFFF",
        )

        tema_grafico(fig, 400)

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            alternativas.drop(columns=["trajeto"]),
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("Nenhuma alternativa encontrada.")

    st.divider()

    # ========================================================
    # RODAPE
    # ========================================================

    st.markdown(
        """
        <div class="footer">
            ROUTEOPS · LOGISTICS INTELLIGENCE PLATFORM
            <br><br>
            DATA ENGINEERING · OSRM · DUCKDB · PYTHON
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
