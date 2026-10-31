"""RouteOps — painel de inteligência logística."""

from pathlib import Path

import duckdb
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "database" / "projeto_final.duckdb"

# Imagem ilustrativa; não representa um veículo real da operação.
TRUCK_IMAGE_URL = (
    "https://images.unsplash.com/photo-1601584115197-04ecc0da31d7"
    "?auto=format&fit=crop&w=900&q=85"
)

st.set_page_config(
    page_title="RouteOps | Logistics Intelligence",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------
# Identidade visual
# ---------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #080e18;
        --panel: #111b29;
        --panel-2: #152235;
        --border: #26384c;
        --muted: #91a3b8;
        --text: #edf4fb;
        --cyan: #35d5e8;
        --orange: #ff8a24;
        --green: #8bdc74;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 52% 40%, rgba(20, 73, 100, .18), transparent 46%),
            linear-gradient(135deg, #080e18 0%, #0a1320 55%, #09111d 100%);
        color: var(--text);
    }

    .block-container {
        max-width: 1600px;
        padding: 1.1rem 1.4rem 2rem;
    }

    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stToolbar"] { right: 1rem; }

    h1, h2, h3, p, label { color: var(--text); }

    .topbar {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(90deg, rgba(5, 15, 28, .98) 0%, rgba(5, 15, 28, .90) 48%, rgba(5, 15, 28, .52) 100%),
            url("https://images.unsplash.com/photo-1601584115197-04ecc0da31d7?auto=format&fit=crop&w=1600&q=85") center 48% / cover;
        border: 1px solid rgba(53, 213, 232, .18);
        border-radius: 14px;
        min-height: 104px;
        padding: 20px 22px;
        box-shadow: 0 12px 36px rgba(0,0,0,.22);
    }

    .brand-mark {
        width: 42px;
        height: 42px;
        font-size: 22px;
    }

    .top-meta {
        padding: 8px 12px;
        border: 1px solid rgba(111, 165, 200, .22);
        border-radius: 8px;
        background: rgba(5, 16, 29, .62);
    }

    .route-card {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 9px;
        min-height: 82px;
        transition: border-color .18s ease, transform .18s ease;
    }

    .route-card:hover {
        border-color: rgba(53, 213, 232, .65);
        transform: translateY(-1px);
    }

    .route-thumb {
        width: 76px;
        height: 62px;
        flex: 0 0 76px;
        object-fit: cover;
        border-radius: 7px;
        border: 1px solid rgba(130, 170, 200, .28);
        filter: saturate(.88);
    }

    .route-card-content {
        min-width: 0;
        flex: 1;
    }

    .truck-hero {
        width: 100%;
        height: 142px;
        object-fit: cover;
        border-radius: 10px;
        border: 1px solid rgba(53, 213, 232, .20);
        margin: 5px 0 12px;
        filter: saturate(.88) contrast(1.04);
    }

    .panel {
        box-shadow: 0 10px 30px rgba(0,0,0,.16);
    }

    .kpi-card {
        position: relative;
        overflow: hidden;
    }

    .kpi-card:after {
        content: "";
        position: absolute;
        right: -22px;
        top: -28px;
        width: 86px;
        height: 86px;
        border-radius: 50%;
        background: rgba(53, 213, 232, .055);
    }

        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        padding: 8px 2px 16px;
        border-bottom: 1px solid rgba(125, 157, 188, .18);
        margin-bottom: 16px;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 11px;
        font-size: 23px;
        font-weight: 800;
        letter-spacing: -.7px;
        color: #f4f8fc;
    }

    .brand-mark {
        width: 34px;
        height: 34px;
        display: grid;
        place-items: center;
        border-radius: 10px;
        color: #07111d;
        font-size: 19px;
        font-weight: 900;
        background: linear-gradient(135deg, #ff9b35, #ff6c19);
        box-shadow: 0 0 22px rgba(255, 130, 35, .24);
    }

    .brand small {
        color: var(--orange);
        font-size: 12px;
        margin-left: 3px;
        letter-spacing: .2px;
    }

    .top-meta {
        color: #8fa2b8;
        font-size: 11px;
        letter-spacing: 1.4px;
        font-weight: 700;
    }

    .section-kicker {
        color: var(--cyan);
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.8px;
        margin: 4px 0 5px;
    }

    .section-heading {
        color: #edf4fb;
        font-size: 18px;
        font-weight: 700;
        margin: 0 0 12px;
    }

    .kpi-card {
        background: linear-gradient(145deg, rgba(23, 39, 58, .96), rgba(15, 27, 42, .96));
        border: 1px solid #293b50;
        border-radius: 12px;
        padding: 13px 15px;
        min-height: 92px;
        box-shadow: 0 8px 24px rgba(0,0,0,.14);
    }

    .kpi-label {
        color: #9aadc1;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    .kpi-value {
        color: #f4f8fc;
        font-size: 25px;
        line-height: 1.35;
        font-weight: 800;
        margin-top: 5px;
    }

    .kpi-foot {
        color: #7890a9;
        font-size: 10px;
        margin-top: 1px;
    }

    .panel {
        background: rgba(16, 27, 42, .88);
        border: 1px solid #26394e;
        border-radius: 13px;
        padding: 13px;
    }

    .route-card {
        border: 1px solid #2b4056;
        border-left: 3px solid var(--orange);
        border-radius: 9px;
        background: linear-gradient(120deg, #17263a, #111d2d);
        padding: 11px 12px;
        margin-bottom: 9px;
    }

    .route-card.selected {
        border-color: rgba(255, 138, 36, .75);
        box-shadow: 0 0 0 1px rgba(255, 138, 36, .12);
    }

    .route-card-title {
        color: #f0f5fa;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .route-card-sub {
        color: #94a8bd;
        font-size: 10px;
        line-height: 1.5;
    }

    .route-card-metrics {
        display: flex;
        justify-content: space-between;
        gap: 5px;
        border-top: 1px solid #2a3b50;
        margin-top: 9px;
        padding-top: 8px;
        color: #c5d3e0;
        font-size: 10px;
    }

    .detail-label {
        color: #8fa5bb;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }

    .detail-value {
        color: #f2f6fa;
        font-size: 21px;
        font-weight: 800;
        margin: 3px 0 10px;
    }

    .detail-row {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        padding: 8px 0;
        border-bottom: 1px solid rgba(130, 157, 184, .13);
        color: #aebed0;
        font-size: 11px;
    }

    .detail-row strong { color: #eef4fa; font-weight: 700; }

    .notice {
        color: #9aadc1;
        background: rgba(35, 54, 74, .55);
        border: 1px solid #2b4055;
        border-radius: 8px;
        padding: 9px 11px;
        font-size: 10px;
        line-height: 1.5;
        margin-top: 9px;
    }

    div[data-testid="stSelectbox"] label,
    div[data-testid="stMultiSelect"] label {
        color: #a8bacd !important;
        font-size: 11px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stMultiSelect"] > div > div {
        background: #111e2e;
        border-color: #2b4055;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #2a3b50;
    }

    .stTabs [data-baseweb="tab"] {
        color: #9aadc1;
        font-size: 11px;
    }

    .stTabs [aria-selected="true"] {
        color: #35d5e8 !important;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #293d52;
        border-radius: 9px;
        overflow: hidden;
    }

    .footer {
        color: #667f98;
        text-align: center;
        font-size: 9px;
        letter-spacing: 1.5px;
        padding-top: 22px;
    }

    @media (max-width: 900px) {
        .block-container { padding-left: .7rem; padding-right: .7rem; }
        .brand { font-size: 19px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Dados
# ---------------------------------------------------------------------

@st.cache_data(ttl=60)
def consultar(sql: str, parametros: tuple = ()) -> pd.DataFrame:
    """Consulta o DuckDB em modo somente leitura."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            "Banco não encontrado. Execute primeiro o pipeline Bronze, Silver e Gold."
        )
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        return con.execute(sql, list(parametros)).fetchdf()
    finally:
        con.close()


@st.cache_data(ttl=60)
def carregar_dados():
    """Carrega fatos e instalações para a experiência do dashboard."""
    rotas = consultar(
        """
        SELECT
            rota_id, origem_id, destino_id, origem, destino,
            cidade_origem, cidade_destino, estado_origem, estado_destino,
            numero_rota, distancia_km, duracao_horas,
            duracao_segundos, velocidade_media_kmh
        FROM gold.fato_rotas
        ORDER BY origem, destino, numero_rota
        """
    )
    instalacoes = consultar(
        """
        SELECT
            instalacao_id, nome_instalacao, cidade, estado,
            latitude, longitude, tipo_instalacao
        FROM gold.dim_instalacoes
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY estado, nome_instalacao
        """
    )
    return rotas, instalacoes


# ---------------------------------------------------------------------
# Componentes de apresentação
# ---------------------------------------------------------------------

def render_kpi(label: str, value: str, foot: str):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def formatar_duracao(horas) -> str:
    if pd.isna(horas):
        return "—"
    total_minutos = round(float(horas) * 60)
    h, m = divmod(total_minutos, 60)
    return f"{h}h {m:02d}min"


def criar_mapa(rotas: pd.DataFrame, instalacoes: pd.DataFrame, rota_selecionada):
    """Cria mapa geográfico com pontos e conexões aproximadas."""
    fig = go.Figure()

    coords = instalacoes.set_index("instalacao_id").to_dict("index")
    rotas_principais = rotas[rotas["numero_rota"] == 1].copy()

    # Conexões entre todos os pares no contexto, em baixa opacidade.
    for row in rotas_principais.itertuples():
        origem = coords.get(row.origem_id)
        destino = coords.get(row.destino_id)
        if origem is None or destino is None:
            continue

        fig.add_trace(
            go.Scattergeo(
                lat=[origem["latitude"], destino["latitude"]],
                lon=[origem["longitude"], destino["longitude"]],
                mode="lines",
                line=dict(width=1, color="rgba(53, 213, 232, 0.22)"),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # Conexão selecionada em destaque.
    selecionada = rotas[rotas["rota_id"] == rota_selecionada]
    if not selecionada.empty:
        row = selecionada.iloc[0]
        origem = coords.get(int(row["origem_id"]))
        destino = coords.get(int(row["destino_id"]))
        if origem is not None and destino is not None:
            fig.add_trace(
                go.Scattergeo(
                    lat=[origem["latitude"], destino["latitude"]],
                    lon=[origem["longitude"], destino["longitude"]],
                    mode="lines",
                    line=dict(width=4, color="#ff8a24"),
                    name="Conexão selecionada",
                    hovertemplate="Conexão geográfica selecionada<extra></extra>",
                )
            )

    # Pontos das instalações.
    fig.add_trace(
        go.Scattergeo(
            lat=instalacoes["latitude"],
            lon=instalacoes["longitude"],
            mode="markers+text",
            text=instalacoes["nome_instalacao"],
            textposition="top right",
            textfont=dict(size=10, color="#dce8f3"),
            marker=dict(
                size=9,
                color="#35d5e8",
                line=dict(width=1, color="#d8faff"),
            ),
            customdata=instalacoes[["cidade", "estado"]],
            hovertemplate=(
                "<b>%{text}</b><br>%{customdata[0]} - %{customdata[1]}"
                "<extra></extra>"
            ),
            name="Instalações",
        )
    )

    if instalacoes.empty:
        lat_range = [-34, -24]
        lon_range = [-54, -46]
    else:
        lat_min = float(instalacoes["latitude"].min())
        lat_max = float(instalacoes["latitude"].max())
        lon_min = float(instalacoes["longitude"].min())
        lon_max = float(instalacoes["longitude"].max())
        lat_pad = max((lat_max - lat_min) * 0.25, 0.8)
        lon_pad = max((lon_max - lon_min) * 0.25, 0.8)
        lat_range = [lat_min - lat_pad, lat_max + lat_pad]
        lon_range = [lon_min - lon_pad, lon_max + lon_pad]

    fig.update_layout(
        geo=dict(
            scope="south america",
            projection_type="mercator",
            showland=True,
            landcolor="#172536",
            showocean=True,
            oceancolor="#0b1726",
            showlakes=True,
            lakecolor="#0b1726",
            showcountries=True,
            countrycolor="#53677b",
            showsubunits=True,
            subunitcolor="#34495e",
            showcoastlines=True,
            coastlinecolor="#60758a",
            bgcolor="rgba(0,0,0,0)",
            lataxis=dict(range=lat_range, showgrid=True, gridcolor="rgba(110,150,180,.12)"),
            lonaxis=dict(range=lon_range, showgrid=True, gridcolor="rgba(110,150,180,.12)"),
        ),
        height=520,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#eaf2fa"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.015,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(8,14,24,.75)",
        ),
    )
    return fig


def main():
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">
                <div class="brand-mark">R</div>
                <div>RouteOps <small>LOGISTICS INTELLIGENCE</small></div>
            </div>
            <div class="top-meta">NETWORK ANALYTICS&nbsp;&nbsp; / &nbsp;&nbsp;SOUTHERN BRAZIL</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        rotas, instalacoes = carregar_dados()
    except Exception as erro:
        st.error(f"Não foi possível carregar os dados: {erro}")
        st.info("Execute `uv run python -m projeto_final.orquestrador` para gerar as camadas analíticas.")
        return

    if rotas.empty:
        st.warning("A tabela gold.fato_rotas não possui registros.")
        return

    estados = sorted(
        set(rotas["estado_origem"].dropna().tolist())
        | set(rotas["estado_destino"].dropna().tolist())
    )

    # Filtros no topo.
    st.markdown('<div class="section-kicker">CONTROL CENTER</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1.2, 1.2, 1.6])
    with f1:
        estados_origem = st.multiselect(
            "Estados de origem",
            estados,
            default=estados,
            key="filtro_origem",
        )
    with f2:
        estados_destino = st.multiselect(
            "Estados de destino",
            estados,
            default=estados,
            key="filtro_destino",
        )
    with f3:
        st.markdown(
            '<div class="notice">Dados estimados pelo OSRM · rotas principais e alternativas · '
            'instalações do catálogo RouteOps</div>',
            unsafe_allow_html=True,
        )

    filtradas = rotas[
        rotas["estado_origem"].isin(estados_origem)
        & rotas["estado_destino"].isin(estados_destino)
    ].copy()
    principais = filtradas[filtradas["numero_rota"] == 1].copy()

    if principais.empty:
        st.warning("Nenhuma rota encontrada para a combinação de filtros.")
        return

    total_rotas = len(principais)
    distancia_media = principais["distancia_km"].mean()
    duracao_media = principais["duracao_horas"].mean()
    velocidade_media = principais["velocidade_media_kmh"].mean()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi("Rotas principais", f"{total_rotas}", "Combinações origem-destino")
    with k2:
        render_kpi("Distância média", f"{distancia_media:,.1f} km", "Estimativa de percurso")
    with k3:
        render_kpi("Duração média", formatar_duracao(duracao_media), "Tempo estimado pelo OSRM")
    with k4:
        render_kpi("Velocidade média", f"{velocidade_media:,.1f} km/h", "Distância ÷ duração")

    st.markdown("<br>", unsafe_allow_html=True)

    # Seleção da rota.
    principais = principais.sort_values("duracao_segundos")
    opcoes = {
        int(row.rota_id): f"{row.origem}  →  {row.destino}"
        for row in principais.itertuples()
    }
    rota_ids = list(opcoes)
    if "rota_selecionada" not in st.session_state or st.session_state["rota_selecionada"] not in rota_ids:
        st.session_state["rota_selecionada"] = rota_ids[0]

    st.markdown('<div class="section-kicker">LIVE ROUTE EXPLORER</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Central de controle logístico</div>', unsafe_allow_html=True)

    esquerda, centro, direita = st.columns([1.05, 2.35, 1.15], gap="medium")

    with esquerda:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("**Rotas em análise**")
        st.caption(f"{len(principais)} rotas principais no filtro atual")
        rota_escolhida = st.selectbox(
            "Selecionar rota",
            options=rota_ids,
            format_func=lambda rota_id: opcoes[rota_id],
            key="rota_selecionada",
            label_visibility="collapsed",
        )

        lista = principais.head(8)
        for row in lista.itertuples():
            selecionada = int(row.rota_id) == int(rota_escolhida)
            classe = "route-card selected" if selecionada else "route-card"
            st.markdown(
                f"""
                <div class="{classe}">
                    <img class="route-thumb" src="{TRUCK_IMAGE_URL}" alt="Imagem ilustrativa de caminhão">
                    <div class="route-card-content">
                        <div class="route-card-title">{row.origem} → {row.destino}</div>
                        <div class="route-card-sub">{row.estado_origem} → {row.estado_destino}</div>
                        <div class="route-card-metrics">
                            <span>{row.distancia_km:.1f} km</span>
                            <span>{formatar_duracao(row.duracao_horas)}</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with centro:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("**Mapa de conexões**")
        st.caption("Instalações cadastradas e conexões entre pares de origem e destino")
        mapa_instalacoes = instalacoes[
            instalacoes["estado"].isin(set(estados_origem + estados_destino))
        ].copy()
        mapa_rotas = filtradas[
            filtradas["origem_id"].isin(mapa_instalacoes["instalacao_id"])
            & filtradas["destino_id"].isin(mapa_instalacoes["instalacao_id"])
        ]
        fig = criar_mapa(mapa_rotas, mapa_instalacoes, rota_escolhida)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            '<div class="notice">As linhas representam conexões geográficas aproximadas entre as coordenadas '
            'das instalações. Não são geometrias reais das estradas.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with direita:
        detalhe = filtradas[filtradas["rota_id"] == rota_escolhida]
        if detalhe.empty:
            detalhe = principais[principais["rota_id"] == rota_escolhida]
        row = detalhe.iloc[0]

        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown("**Detalhes da rota**")
        st.markdown(
            f'<img class="truck-hero" src="{TRUCK_IMAGE_URL}" alt="Foto ilustrativa de caminhão em rodovia">',
            unsafe_allow_html=True,
        )
        st.caption(f"{row.origem} → {row.destino}")
        st.markdown('<div class="detail-label">Distância estimada</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-value">{row.distancia_km:,.2f} km</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="detail-row"><span>Duração estimada</span><strong>{formatar_duracao(row.duracao_horas)}</strong></div>
            <div class="detail-row"><span>Velocidade média</span><strong>{row.velocidade_media_kmh:.1f} km/h</strong></div>
            <div class="detail-row"><span>Origem</span><strong>{row.cidade_origem} / {row.estado_origem}</strong></div>
            <div class="detail-row"><span>Destino</span><strong>{row.cidade_destino} / {row.estado_destino}</strong></div>
            """,
            unsafe_allow_html=True,
        )

        alternativas = filtradas[
            (filtradas["origem_id"] == row.origem_id)
            & (filtradas["destino_id"] == row.destino_id)
            & (filtradas["numero_rota"] > 1)
        ].sort_values("numero_rota")

        st.markdown("<br>**Rotas alternativas**", unsafe_allow_html=True)
        if alternativas.empty:
            st.caption("Nenhuma alternativa retornada para este par.")
        else:
            for alt in alternativas.itertuples():
                st.markdown(
                    f"""
                    <div class="detail-row">
                        <span>Alternativa {alt.numero_rota}</span>
                        <strong>{alt.distancia_km:.1f} km · {formatar_duracao(alt.duracao_horas)}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)

    # Área analítica complementar.
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-kicker">PERFORMANCE ANALYTICS</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Desempenho e comparação</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Desempenho por estado", "Ranking de rotas", "Alternativas"])

    with tab1:
        desempenho = (
            principais.groupby("estado_origem", as_index=False)
            .agg(
                quantidade_rotas=("rota_id", "count"),
                distancia_media=("distancia_km", "mean"),
                duracao_media=("duracao_horas", "mean"),
                velocidade_media=("velocidade_media_kmh", "mean"),
            )
        )
        col_a, col_b = st.columns(2)
        with col_a:
            fig = go.Figure(
                go.Bar(
                    x=desempenho["estado_origem"],
                    y=desempenho["distancia_media"],
                    marker_color="#35d5e8",
                    text=desempenho["distancia_media"].round(1),
                    textposition="outside",
                    name="Distância média",
                )
            )
            fig.update_layout(title="Distância média por estado (km)", height=330)
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig = go.Figure(
                go.Bar(
                    x=desempenho["estado_origem"],
                    y=desempenho["duracao_media"],
                    marker_color="#ff8a24",
                    text=desempenho["duracao_media"].round(1),
                    textposition="outside",
                    name="Duração média",
                )
            )
            fig.update_layout(title="Duração média por estado (h)", height=330)
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        ranking = principais.sort_values("duracao_horas").head(10).copy()
        ranking["trajeto"] = ranking["origem"] + " → " + ranking["destino"]
        fig = go.Figure(
            go.Bar(
                x=ranking["duracao_horas"],
                y=ranking["trajeto"],
                orientation="h",
                marker_color="#35d5e8",
                text=ranking["duracao_horas"].round(2),
                textposition="outside",
            )
        )
        fig.update_layout(
            title="10 rotas com menor duração estimada",
            height=430,
            yaxis=dict(autorange="reversed"),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        if alternativas.empty:
            st.info("Não há rotas alternativas para os filtros selecionados.")
        else:
            comparacao = alternativas.copy()
            comparacao["trajeto"] = comparacao["origem"] + " → " + comparacao["destino"]
            st.dataframe(
                comparacao[
                    [
                        "trajeto", "numero_rota", "distancia_km",
                        "duracao_horas", "velocidade_media_kmh",
                    ]
                ].rename(
                    columns={
                        "trajeto": "Trajeto",
                        "numero_rota": "Alternativa",
                        "distancia_km": "Distância (km)",
                        "duracao_horas": "Duração (h)",
                        "velocidade_media_kmh": "Velocidade média (km/h)",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

    st.markdown(
        '<div class="footer">ROUTEOPS · LOGISTICS INTELLIGENCE · OSRM · DUCKDB · PYTHON</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
