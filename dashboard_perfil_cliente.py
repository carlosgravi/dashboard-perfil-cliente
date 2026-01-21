"""
DASHBOARD - PERFIL DE CLIENTE POR SHOPPING
Visualização interativa dos dados de perfil de cliente
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import base64

# Configuração da página
st.set_page_config(
    page_title="Perfil de Cliente - Almeida Junior",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para converter imagem para base64
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Carregar imagem de fundo
bg_image = get_base64_image("AJ.jpg")
bg_style = ""
if bg_image:
    bg_style = f"""
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpeg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(255, 255, 255, 0.85);
        z-index: -1;
    }}
    """

# CSS customizado - Compatível com Streamlit Cloud
st.markdown(f"""
<style>
    {bg_style}
    /* Header principal */
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1E3A5F !important;
        text-align: center;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background-color: rgba(240, 242, 246, 0.95);
        border-radius: 10px;
        backdrop-filter: blur(5px);
    }

    /* Main content area */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
    }

    /* Cards de métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: bold !important;
        color: #1E3A5F !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        color: #333333 !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.85rem !important;
        color: #28a745 !important;
    }

    /* Container das métricas */
    [data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15) !important;
        backdrop-filter: blur(5px) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E3A5F 0%, #2C3E50 100%) !important;
    }

    section[data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }

    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #B0C4DE !important;
    }

    /* Títulos */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #1E3A5F !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        background-color: #2C3E50 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
        margin-right: 5px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        border: none !important;
    }

    button[data-baseweb="tab"]:hover {
        background-color: #34495E !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #3498DB !important;
        color: #FFFFFF !important;
    }

    /* Texto das tabs */
    button[data-baseweb="tab"] div {
        color: #FFFFFF !important;
    }

    /* Selectbox e Multiselect */
    .stSelectbox label, .stMultiSelect label {
        color: #1E3A5F !important;
        font-weight: 600 !important;
    }

    /* Radio buttons no sidebar */
    section[data-testid="stSidebar"] .stRadio label {
        color: #FFFFFF !important;
    }

    /* Dataframe */
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }

    /* Subheader */
    .stMarkdown h2, .stMarkdown h3 {
        border-bottom: 2px solid #3498DB;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Cores para os shoppings
CORES_SHOPPING = {
    'BS': '#E74C3C',
    'CS': '#3498DB',
    'GS': '#2ECC71',
    'NK': '#9B59B6',
    'NR': '#F39C12',
    'NS': '#1ABC9C'
}

NOMES_SHOPPING = {
    'BS': 'Balneário Shopping',
    'CS': 'Continente Shopping',
    'GS': 'Garten Shopping',
    'NK': 'Neumarkt Shopping',
    'NR': 'Norte Shopping',
    'NS': 'Nações Shopping'
}

# Função para carregar dados
@st.cache_data
def carregar_dados():
    base_path = 'Resultados'

    dados = {}

    # Resumo por shopping
    dados['resumo'] = pd.read_csv(f'{base_path}/resumo_por_shopping.csv')

    # Consolidados
    dados['genero'] = pd.read_csv(f'{base_path}/consolidado_genero_por_shopping.csv')
    dados['faixa'] = pd.read_csv(f'{base_path}/consolidado_faixa_etaria_por_shopping.csv')
    dados['segmentos'] = pd.read_csv(f'{base_path}/consolidado_segmentos_por_shopping.csv')

    # Por shopping
    dados['por_shopping'] = {}
    for sigla in ['BS', 'CS', 'GS', 'NK', 'NR', 'NS']:
        shop_path = f'{base_path}/Por_Shopping/{sigla}'
        if os.path.exists(shop_path):
            dados['por_shopping'][sigla] = {
                'genero': pd.read_csv(f'{shop_path}/perfil_genero.csv'),
                'faixa': pd.read_csv(f'{shop_path}/perfil_faixa_etaria.csv'),
                'segmentos': pd.read_csv(f'{shop_path}/top_segmentos.csv'),
                'lojas': pd.read_csv(f'{shop_path}/top_lojas.csv'),
                'periodo': pd.read_csv(f'{shop_path}/comportamento_periodo.csv'),
                'dia_semana': pd.read_csv(f'{shop_path}/comportamento_dia_semana.csv')
            }
            # High spenders (pode não existir)
            hs_path = f'{shop_path}/high_spenders_stats.csv'
            if os.path.exists(hs_path):
                dados['por_shopping'][sigla]['hs_stats'] = pd.read_csv(hs_path)

    return dados

# Carregar dados
try:
    dados = carregar_dados()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Sidebar
# Logo - carrega se existir arquivo PNG ou SVG
logo_path = None
for ext in ['png', 'svg', 'jpg']:
    if os.path.exists(f"AJFans-logo.{ext}"):
        logo_path = f"AJFans-logo.{ext}"
        break
    if os.path.exists(f"logo.{ext}"):
        logo_path = f"logo.{ext}"
        break

if logo_path:
    st.sidebar.image(logo_path, use_container_width=True)
else:
    # Placeholder com estilo para o logo
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 1rem;">
        <h2 style="color: white; margin: 0; font-size: 1.5rem;">AJ FANS</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 0.8rem;">Almeida Junior</p>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.title("🛍️ Almeida Junior")
st.sidebar.markdown("**Dashboard Perfil de Cliente**")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Selecione a visão:",
    ["📊 Visão Geral", "🏬 Por Shopping", "👥 Perfil Demográfico", "⭐ High Spenders", "📈 Comparativo"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Período da Base")
st.sidebar.markdown("**11/12/2022 a 19/01/2026**")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Total Geral")
st.sidebar.metric("Clientes", f"{dados['resumo']['clientes'].sum():,}")
st.sidebar.metric("Valor Total", f"R$ {dados['resumo']['valor_total'].sum()/1e6:.1f}M")

# ============================================================================
# PÁGINA: VISÃO GERAL
# ============================================================================
if pagina == "📊 Visão Geral":
    st.markdown('<p class="main-header">📊 Visão Geral - Perfil de Cliente</p>', unsafe_allow_html=True)

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total de Clientes",
            f"{dados['resumo']['clientes'].sum():,}",
            delta="6 shoppings"
        )

    with col2:
        st.metric(
            "Valor Total",
            f"R$ {dados['resumo']['valor_total'].sum()/1e6:.1f}M",
            delta=f"Ticket: R$ {dados['resumo']['valor_total'].sum()/dados['resumo']['clientes'].sum():,.0f}"
        )

    with col3:
        st.metric(
            "High Spenders",
            f"{dados['resumo']['qtd_high_spenders'].sum():,}",
            delta=f"{dados['resumo']['qtd_high_spenders'].sum()/dados['resumo']['clientes'].sum()*100:.1f}% do total"
        )

    with col4:
        ticket_medio_geral = dados['resumo']['valor_total'].sum() / dados['resumo']['clientes'].sum()
        st.metric(
            "Ticket Médio",
            f"R$ {ticket_medio_geral:,.0f}",
            delta="valor total / clientes"
        )

    st.markdown("---")

    # Gráficos lado a lado
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Valor Total por Shopping")
        fig = px.bar(
            dados['resumo'].sort_values('valor_total', ascending=True),
            x='valor_total',
            y='sigla',
            orientation='h',
            color='sigla',
            color_discrete_map=CORES_SHOPPING,
            text=dados['resumo'].sort_values('valor_total', ascending=True)['valor_total'].apply(lambda x: f'R$ {x/1e6:.1f}M')
        )
        fig.update_layout(showlegend=False, height=400)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("👥 Clientes por Shopping")
        fig = px.pie(
            dados['resumo'],
            values='clientes',
            names='sigla',
            color='sigla',
            color_discrete_map=CORES_SHOPPING,
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Tabela resumo
    st.subheader("📋 Resumo por Shopping")
    df_display = dados['resumo'][['shopping', 'sigla', 'clientes', 'valor_total', 'ticket_medio', 'qtd_high_spenders']].copy()
    df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f'R$ {x:,.2f}')
    df_display['ticket_medio'] = df_display['ticket_medio'].apply(lambda x: f'R$ {x:,.2f}')
    df_display.columns = ['Shopping', 'Sigla', 'Clientes', 'Valor Total', 'Ticket Médio', 'High Spenders']
    st.dataframe(df_display, use_container_width=True, hide_index=True)

# ============================================================================
# PÁGINA: POR SHOPPING
# ============================================================================
elif pagina == "🏬 Por Shopping":
    st.markdown('<p class="main-header">🏬 Análise por Shopping</p>', unsafe_allow_html=True)

    # Seletor de shopping
    shopping_selecionado = st.selectbox(
        "Selecione o Shopping:",
        options=list(NOMES_SHOPPING.keys()),
        format_func=lambda x: f"{x} - {NOMES_SHOPPING[x]}"
    )

    if shopping_selecionado in dados['por_shopping']:
        shop_data = dados['por_shopping'][shopping_selecionado]
        resumo_shop = dados['resumo'][dados['resumo']['sigla'] == shopping_selecionado].iloc[0]

        st.markdown(f"### {NOMES_SHOPPING[shopping_selecionado]}")

        # Métricas do shopping
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Clientes", f"{resumo_shop['clientes']:,}")
        with col2:
            st.metric("Valor Total", f"R$ {resumo_shop['valor_total']/1e6:.1f}M")
        with col3:
            st.metric("Ticket Médio", f"R$ {resumo_shop['ticket_medio']:,.0f}")
        with col4:
            st.metric("High Spenders", f"{resumo_shop['qtd_high_spenders']:,}")

        st.markdown("---")

        # Tabs para diferentes análises
        tab1, tab2, tab3, tab4 = st.tabs(["👥 Demografia", "🏪 Lojas & Segmentos", "⏰ Comportamento", "📊 Detalhes"])

        with tab1:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Por Gênero")
                fig = px.pie(
                    shop_data['genero'],
                    values='qtd_clientes',
                    names='genero',
                    color='genero',
                    color_discrete_map={'Feminino': '#E91E63', 'Masculino': '#2196F3', 'Nao Informado': '#9E9E9E'}
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Por Faixa Etária")
                fig = px.bar(
                    shop_data['faixa'],
                    x='faixa_etaria',
                    y='qtd_clientes',
                    color='faixa_etaria',
                    text='qtd_clientes'
                )
                fig.update_layout(showlegend=False, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Top 10 Segmentos")
                fig = px.bar(
                    shop_data['segmentos'].head(10),
                    x='valor',
                    y='segmento',
                    orientation='h',
                    color='valor',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Top 10 Lojas")
                fig = px.bar(
                    shop_data['lojas'].head(10),
                    x='valor',
                    y='loja',
                    orientation='h',
                    color='valor',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Por Período do Dia")
                fig = px.pie(
                    shop_data['periodo'],
                    values='valor',
                    names='periodo_dia',
                    color='periodo_dia',
                    color_discrete_map={
                        'Manha (6h-12h)': '#FFC107',
                        'Tarde (12h-18h)': '#FF9800',
                        'Noite (18h-22h)': '#673AB7'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Por Dia da Semana")
                ordem_dias = ['Segunda', 'Terca', 'Quarta', 'Quinta', 'Sexta', 'Sabado', 'Domingo']
                df_dia = shop_data['dia_semana'].copy()
                df_dia['ordem'] = df_dia['dia_semana'].map({d: i for i, d in enumerate(ordem_dias)})
                df_dia = df_dia.sort_values('ordem')

                fig = px.bar(
                    df_dia,
                    x='dia_semana',
                    y='valor',
                    color='valor',
                    color_continuous_scale='Oranges'
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)

        with tab4:
            st.subheader("Dados Detalhados")

            st.markdown("**Perfil por Gênero**")
            st.dataframe(shop_data['genero'], use_container_width=True, hide_index=True)

            st.markdown("**Perfil por Faixa Etária**")
            st.dataframe(shop_data['faixa'], use_container_width=True, hide_index=True)

# ============================================================================
# PÁGINA: PERFIL DEMOGRÁFICO
# ============================================================================
elif pagina == "👥 Perfil Demográfico":
    st.markdown('<p class="main-header">👥 Perfil Demográfico</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Por Gênero", "Por Faixa Etária"])

    with tab1:
        st.subheader("Distribuição por Gênero - Todos os Shoppings")

        # Pivot para comparação
        df_genero_pivot = dados['genero'].pivot_table(
            values='qtd_clientes',
            index='genero',
            columns='sigla',
            fill_value=0
        )

        fig = px.bar(
            dados['genero'],
            x='sigla',
            y='qtd_clientes',
            color='genero',
            barmode='group',
            color_discrete_map={'Feminino': '#E91E63', 'Masculino': '#2196F3', 'Nao Informado': '#9E9E9E', 'Outro': '#4CAF50'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Percentual por shopping
        st.subheader("Percentual por Gênero")
        df_pct = dados['genero'].pivot_table(
            values='pct_clientes',
            index='sigla',
            columns='genero',
            fill_value=0
        ).round(1)
        st.dataframe(df_pct, use_container_width=True)

    with tab2:
        st.subheader("Distribuição por Faixa Etária - Todos os Shoppings")

        ordem_faixas = ['16-24 (Gen Z)', '25-39 (Millennials)', '40-54 (Gen X)', '55-69 (Boomers)', '70+ (Silent)', 'Nao Informado']
        dados['faixa']['ordem'] = dados['faixa']['faixa_etaria'].map({f: i for i, f in enumerate(ordem_faixas)})
        df_faixa_sorted = dados['faixa'].sort_values(['sigla', 'ordem'])

        fig = px.bar(
            df_faixa_sorted,
            x='sigla',
            y='qtd_clientes',
            color='faixa_etaria',
            barmode='stack',
            category_orders={'faixa_etaria': ordem_faixas}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        # Heatmap
        st.subheader("Mapa de Calor - Clientes por Faixa Etária")
        df_heatmap = dados['faixa'].pivot_table(
            values='qtd_clientes',
            index='faixa_etaria',
            columns='sigla',
            fill_value=0
        )
        df_heatmap = df_heatmap.reindex([f for f in ordem_faixas if f in df_heatmap.index])

        fig = px.imshow(
            df_heatmap,
            color_continuous_scale='Blues',
            aspect='auto',
            text_auto=True
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PÁGINA: HIGH SPENDERS
# ============================================================================
elif pagina == "⭐ High Spenders":
    st.markdown('<p class="main-header">⭐ High Spenders</p>', unsafe_allow_html=True)

    st.markdown("""
    **High Spenders** são os clientes no **Top 10%** em valor de compras de cada shopping.
    Eles representam aproximadamente **40% do faturamento total**.
    """)

    # Métricas gerais
    col1, col2, col3 = st.columns(3)

    total_hs = dados['resumo']['qtd_high_spenders'].sum()
    total_clientes = dados['resumo']['clientes'].sum()

    with col1:
        st.metric("Total High Spenders", f"{total_hs:,}")
    with col2:
        st.metric("% dos Clientes", f"{total_hs/total_clientes*100:.1f}%")
    with col3:
        st.metric("Média por Shopping", f"{total_hs//6:,}")

    st.markdown("---")

    # Gráfico de HS por shopping
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("High Spenders por Shopping")
        fig = px.bar(
            dados['resumo'].sort_values('qtd_high_spenders', ascending=True),
            x='qtd_high_spenders',
            y='sigla',
            orientation='h',
            color='sigla',
            color_discrete_map=CORES_SHOPPING,
            text='qtd_high_spenders'
        )
        fig.update_layout(showlegend=False, height=400)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Threshold High Spender (R$)")
        fig = px.bar(
            dados['resumo'].sort_values('threshold_hs', ascending=True),
            x='threshold_hs',
            y='sigla',
            orientation='h',
            color='sigla',
            color_discrete_map=CORES_SHOPPING,
            text=dados['resumo'].sort_values('threshold_hs', ascending=True)['threshold_hs'].apply(lambda x: f'R$ {x:,.0f}')
        )
        fig.update_layout(showlegend=False, height=400)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # Tabela comparativa
    st.subheader("📋 Resumo High Spenders por Shopping")
    df_hs = dados['resumo'][['sigla', 'shopping', 'clientes', 'qtd_high_spenders', 'threshold_hs']].copy()
    df_hs['pct_hs'] = (df_hs['qtd_high_spenders'] / df_hs['clientes'] * 100).round(1)
    df_hs['threshold_hs'] = df_hs['threshold_hs'].apply(lambda x: f'R$ {x:,.2f}')
    df_hs.columns = ['Sigla', 'Shopping', 'Total Clientes', 'High Spenders', 'Threshold', '% HS']
    st.dataframe(df_hs, use_container_width=True, hide_index=True)

# ============================================================================
# PÁGINA: COMPARATIVO
# ============================================================================
elif pagina == "📈 Comparativo":
    st.markdown('<p class="main-header">📈 Comparativo entre Shoppings</p>', unsafe_allow_html=True)

    # Seletor de shoppings para comparar
    shoppings_comparar = st.multiselect(
        "Selecione os shoppings para comparar:",
        options=list(NOMES_SHOPPING.keys()),
        default=['BS', 'CS', 'NK'],
        format_func=lambda x: f"{x} - {NOMES_SHOPPING[x]}"
    )

    if len(shoppings_comparar) >= 2:
        df_comp = dados['resumo'][dados['resumo']['sigla'].isin(shoppings_comparar)]

        # Radar chart
        st.subheader("Comparativo de Métricas (Normalizado)")

        # Normalizar métricas para radar
        df_radar = df_comp[['sigla', 'clientes', 'valor_total', 'ticket_medio', 'qtd_high_spenders']].copy()
        for col in ['clientes', 'valor_total', 'ticket_medio', 'qtd_high_spenders']:
            max_val = df_radar[col].max()
            df_radar[col] = (df_radar[col] / max_val * 100).round(1)

        fig = go.Figure()

        categories = ['Clientes', 'Valor Total', 'Ticket Médio', 'High Spenders']

        for _, row in df_radar.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row['clientes'], row['valor_total'], row['ticket_medio'], row['qtd_high_spenders']],
                theta=categories,
                fill='toself',
                name=row['sigla'],
                line_color=CORES_SHOPPING[row['sigla']]
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=True,
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)

        # Comparativo de barras
        st.subheader("Comparativo de Valores Absolutos")

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                df_comp,
                x='sigla',
                y='valor_total',
                color='sigla',
                color_discrete_map=CORES_SHOPPING,
                title='Valor Total',
                text=df_comp['valor_total'].apply(lambda x: f'R$ {x/1e6:.1f}M')
            )
            fig.update_layout(showlegend=False)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                df_comp,
                x='sigla',
                y='ticket_medio',
                color='sigla',
                color_discrete_map=CORES_SHOPPING,
                title='Ticket Médio',
                text=df_comp['ticket_medio'].apply(lambda x: f'R$ {x:,.0f}')
            )
            fig.update_layout(showlegend=False)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Selecione pelo menos 2 shoppings para comparar.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Dashboard de Perfil de Cliente - Almeida Junior Shoppings</p>
    <p>Dados atualizados em Janeiro/2026</p>
</div>
""", unsafe_allow_html=True)
