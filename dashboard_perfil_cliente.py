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

# Configuração da página
st.set_page_config(
    page_title="Perfil de Cliente - Almeida Junior",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado - Simples e funcional
st.markdown("""
<style>
    /* Header principal */
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1E3A5F;
        text-align: center;
        margin-bottom: 1rem;
        padding: 0.5rem;
        background-color: #f0f2f6;
        border-radius: 10px;
    }

    /* Cards de métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E3A5F;
    }

    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #333333;
        font-weight: 600;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.85rem;
    }

    /* Container das métricas */
    [data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1E3A5F;
    }

    section[data-testid="stSidebar"] * {
        color: #FFFFFF;
    }

    section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #FFFFFF;
    }

    section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #B0C4DE;
    }

    /* Títulos na área principal */
    .main h1, .main h2, .main h3, .main .stMarkdown h1, .main .stMarkdown h2, .main .stMarkdown h3 {
        color: #1E3A5F;
    }

    /* Subheaders */
    .main [data-testid="stSubheader"] {
        color: #1E3A5F;
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        background-color: #2C3E50;
        color: #FFFFFF;
        border-radius: 8px;
        margin-right: 5px;
        padding: 10px 20px;
        font-weight: 500;
        border: none;
    }

    button[data-baseweb="tab"]:hover {
        background-color: #34495E;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #3498DB;
        color: #FFFFFF;
    }

    button[data-baseweb="tab"] div {
        color: #FFFFFF;
    }

    /* Labels de selectbox */
    .stSelectbox label, .stMultiSelect label {
        color: #1E3A5F;
        font-weight: 600;
    }

    /* Radio buttons no sidebar */
    section[data-testid="stSidebar"] .stRadio label {
        color: #FFFFFF;
    }

    /* Dataframe */
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
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

    # Dados de Perfil (novos)
    dados['personas'] = pd.read_csv(f'{base_path}/personas_clientes.csv')
    dados['comparacao_hs'] = pd.read_csv(f'{base_path}/comparacao_high_spenders.csv')
    dados['hs_por_genero'] = pd.read_csv(f'{base_path}/high_spenders_por_genero.csv')
    dados['hs_por_faixa'] = pd.read_csv(f'{base_path}/high_spenders_por_faixa.csv')
    dados['matriz_clientes'] = pd.read_csv(f'{base_path}/matriz_clientes_genero_idade.csv')
    dados['matriz_valor'] = pd.read_csv(f'{base_path}/matriz_valor_genero_idade.csv')
    dados['matriz_ticket'] = pd.read_csv(f'{base_path}/matriz_ticket_genero_idade.csv')
    dados['segmentos_por_genero'] = pd.read_csv(f'{base_path}/top_segmentos_por_genero.csv')
    dados['segmentos_por_faixa'] = pd.read_csv(f'{base_path}/top_segmentos_por_faixa.csv')
    dados['comportamento_periodo'] = pd.read_csv(f'{base_path}/comportamento_periodo_dia.csv')
    dados['comportamento_dia'] = pd.read_csv(f'{base_path}/comportamento_dia_semana.csv')

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
# Logo - carrega GIF
logo_file = "AJ-AJFANS V2 - GIF.gif"
if os.path.exists(logo_file):
    st.sidebar.image(logo_file, use_container_width=True)

st.sidebar.title("🛍️ Almeida Junior")
st.sidebar.markdown("**Dashboard Perfil de Cliente**")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Selecione a visão:",
    ["📊 Visão Geral", "🎭 Personas", "🏬 Por Shopping", "👥 Perfil Demográfico", "⭐ High Spenders", "🛒 Segmentos", "⏰ Comportamento", "📈 Comparativo"]
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
# PÁGINA: PERSONAS
# ============================================================================
elif pagina == "🎭 Personas":
    st.markdown('<p class="main-header">🎭 Personas de Clientes</p>', unsafe_allow_html=True)

    st.markdown("""
    As **Personas** representam perfis comportamentais de clientes, agrupados por características
    similares de consumo, frequência e valor gasto.
    """)

    # Métricas das principais personas
    col1, col2, col3 = st.columns(3)
    top3 = dados['personas'].head(3)

    with col1:
        st.metric(
            top3.iloc[0]['persona'],
            f"{top3.iloc[0]['pct_clientes']:.1f}% dos clientes",
            delta=f"R$ {top3.iloc[0]['ticket_medio']:,.0f} ticket médio"
        )
    with col2:
        st.metric(
            top3.iloc[1]['persona'],
            f"{top3.iloc[1]['pct_clientes']:.1f}% dos clientes",
            delta=f"R$ {top3.iloc[1]['ticket_medio']:,.0f} ticket médio"
        )
    with col3:
        st.metric(
            top3.iloc[2]['persona'],
            f"{top3.iloc[2]['pct_clientes']:.1f}% dos clientes",
            delta=f"R$ {top3.iloc[2]['ticket_medio']:,.0f} ticket médio"
        )

    st.markdown("---")

    # Gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Distribuição de Clientes por Persona")
        fig = px.pie(
            dados['personas'],
            values='qtd_clientes',
            names='persona',
            hole=0.4
        )
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("💰 Valor Total por Persona")
        fig = px.bar(
            dados['personas'].sort_values('valor_total', ascending=True),
            x='valor_total',
            y='persona',
            orientation='h',
            color='valor_total',
            color_continuous_scale='Blues',
            text=dados['personas'].sort_values('valor_total', ascending=True)['valor_total'].apply(lambda x: f'R$ {x/1e6:.1f}M')
        )
        fig.update_layout(height=450, showlegend=False)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Comparativo de métricas por persona
    st.subheader("📈 Comparativo de Métricas por Persona")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Ticket Médio por Persona**")
        fig = px.bar(
            dados['personas'].sort_values('ticket_medio', ascending=True),
            x='ticket_medio',
            y='persona',
            orientation='h',
            color='ticket_medio',
            color_continuous_scale='Greens',
            text=dados['personas'].sort_values('ticket_medio', ascending=True)['ticket_medio'].apply(lambda x: f'R$ {x:,.0f}')
        )
        fig.update_layout(height=400, showlegend=False)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("**Frequência Média de Compras**")
        fig = px.bar(
            dados['personas'].sort_values('freq_media', ascending=True),
            x='freq_media',
            y='persona',
            orientation='h',
            color='freq_media',
            color_continuous_scale='Oranges',
            text=dados['personas'].sort_values('freq_media', ascending=True)['freq_media'].apply(lambda x: f'{x:.1f}x')
        )
        fig.update_layout(height=400, showlegend=False)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    # Tabela detalhada
    st.subheader("📋 Detalhes das Personas")
    df_personas = dados['personas'].copy()
    df_personas['valor_total'] = df_personas['valor_total'].apply(lambda x: f'R$ {x:,.2f}')
    df_personas['ticket_medio'] = df_personas['ticket_medio'].apply(lambda x: f'R$ {x:,.2f}')
    df_personas['freq_media'] = df_personas['freq_media'].apply(lambda x: f'{x:.1f}')
    df_personas['idade_media'] = df_personas['idade_media'].apply(lambda x: f'{x:.0f} anos')
    df_personas['pct_clientes'] = df_personas['pct_clientes'].apply(lambda x: f'{x:.1f}%')
    df_personas['pct_valor'] = df_personas['pct_valor'].apply(lambda x: f'{x:.1f}%')
    df_personas.columns = ['Persona', 'Clientes', 'Valor Total', 'Ticket Médio', 'Freq. Média', 'Idade Média', '% Clientes', '% Valor']
    st.dataframe(df_personas, use_container_width=True, hide_index=True)

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

    st.markdown("---")

    # Tabs para análises detalhadas
    tab1, tab2, tab3 = st.tabs(["👥 Por Gênero", "📊 Por Faixa Etária", "🔄 HS vs Demais"])

    with tab1:
        st.subheader("High Spenders por Gênero")
        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                dados['hs_por_genero'],
                values='qtd_hs',
                names='genero',
                color='genero',
                color_discrete_map={'Feminino': '#E91E63', 'Masculino': '#2196F3', 'Nao Informado': '#9E9E9E', 'Outro': '#4CAF50'},
                title='Distribuição por Gênero'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                dados['hs_por_genero'].sort_values('valor_total', ascending=True),
                x='valor_total',
                y='genero',
                orientation='h',
                color='genero',
                color_discrete_map={'Feminino': '#E91E63', 'Masculino': '#2196F3', 'Nao Informado': '#9E9E9E', 'Outro': '#4CAF50'},
                title='Valor Total por Gênero',
                text=dados['hs_por_genero'].sort_values('valor_total', ascending=True)['valor_total'].apply(lambda x: f'R$ {x/1e6:.1f}M')
            )
            fig.update_layout(showlegend=False)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        # Tabela
        df_hs_gen = dados['hs_por_genero'].copy()
        df_hs_gen['valor_total'] = df_hs_gen['valor_total'].apply(lambda x: f'R$ {x:,.2f}')
        df_hs_gen['ticket_medio'] = df_hs_gen['ticket_medio'].apply(lambda x: f'R$ {x:,.2f}')
        df_hs_gen['pct_hs'] = df_hs_gen['pct_hs'].apply(lambda x: f'{x:.2f}%')
        df_hs_gen.columns = ['Gênero', 'Qtd HS', 'Valor Total', 'Ticket Médio', '% do Total']
        st.dataframe(df_hs_gen, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("High Spenders por Faixa Etária")
        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                dados['hs_por_faixa'],
                values='qtd_hs',
                names='faixa_etaria',
                title='Distribuição por Faixa Etária'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                dados['hs_por_faixa'],
                x='faixa_etaria',
                y='ticket_medio',
                color='ticket_medio',
                color_continuous_scale='Greens',
                title='Ticket Médio por Faixa Etária',
                text=dados['hs_por_faixa']['ticket_medio'].apply(lambda x: f'R$ {x:,.0f}')
            )
            fig.update_layout(showlegend=False, xaxis_tickangle=-45)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        # Tabela
        df_hs_faixa = dados['hs_por_faixa'].copy()
        df_hs_faixa['valor_total'] = df_hs_faixa['valor_total'].apply(lambda x: f'R$ {x:,.2f}')
        df_hs_faixa['ticket_medio'] = df_hs_faixa['ticket_medio'].apply(lambda x: f'R$ {x:,.2f}')
        df_hs_faixa['pct_hs'] = df_hs_faixa['pct_hs'].apply(lambda x: f'{x:.2f}%')
        df_hs_faixa.columns = ['Faixa Etária', 'Qtd HS', 'Valor Total', 'Ticket Médio', '% do Total']
        st.dataframe(df_hs_faixa, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Comparação: High Spenders vs Demais Clientes")

        # Preparar dados para comparação
        comp = dados['comparacao_hs'].set_index('Metrica')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**High Spenders**")
            st.metric("Quantidade", f"{comp.loc['Qtd Clientes', 'High Spenders']:,.0f}")
            st.metric("Valor Total", f"R$ {comp.loc['Valor Total (R$)', 'High Spenders']/1e6:.1f}M")
            st.metric("Ticket Médio", f"R$ {comp.loc['Ticket Medio (R$)', 'High Spenders']:,.0f}")
            st.metric("Freq. Média", f"{comp.loc['Freq Media Compras', 'High Spenders']:.1f} compras")
            st.metric("% Feminino", f"{comp.loc['% Feminino', 'High Spenders']:.1f}%")

        with col2:
            st.markdown("**Demais Clientes**")
            st.metric("Quantidade", f"{comp.loc['Qtd Clientes', 'Demais Clientes']:,.0f}")
            st.metric("Valor Total", f"R$ {comp.loc['Valor Total (R$)', 'Demais Clientes']/1e6:.1f}M")
            st.metric("Ticket Médio", f"R$ {comp.loc['Ticket Medio (R$)', 'Demais Clientes']:,.0f}")
            st.metric("Freq. Média", f"{comp.loc['Freq Media Compras', 'Demais Clientes']:.1f} compras")
            st.metric("% Feminino", f"{comp.loc['% Feminino', 'Demais Clientes']:.1f}%")

        st.markdown("---")

        # Gráfico comparativo
        st.subheader("Comparativo Visual")
        metricas_comp = ['Ticket Medio (R$)', 'Freq Media Compras', 'Idade Media']
        df_comp_chart = dados['comparacao_hs'][dados['comparacao_hs']['Metrica'].isin(metricas_comp)].melt(
            id_vars='Metrica', var_name='Grupo', value_name='Valor'
        )

        fig = px.bar(
            df_comp_chart,
            x='Metrica',
            y='Valor',
            color='Grupo',
            barmode='group',
            color_discrete_map={'High Spenders': '#E74C3C', 'Demais Clientes': '#3498DB'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PÁGINA: SEGMENTOS
# ============================================================================
elif pagina == "🛒 Segmentos":
    st.markdown('<p class="main-header">🛒 Análise por Segmentos</p>', unsafe_allow_html=True)

    st.markdown("""
    Análise detalhada dos **segmentos de consumo** por gênero e faixa etária,
    mostrando as preferências de compra de cada grupo demográfico.
    """)

    tab1, tab2, tab3 = st.tabs(["👫 Por Gênero", "📊 Por Faixa Etária", "🔥 Matrizes Cruzadas"])

    with tab1:
        st.subheader("Top 5 Segmentos por Gênero")

        # Filtrar apenas os principais gêneros
        generos_principais = ['Feminino', 'Masculino']

        for genero in generos_principais:
            df_gen = dados['segmentos_por_genero'][dados['segmentos_por_genero']['genero'] == genero]

            st.markdown(f"**{genero}**")
            fig = px.bar(
                df_gen,
                x='valor',
                y='segmento',
                orientation='h',
                color='valor',
                color_continuous_scale='Blues' if genero == 'Masculino' else 'RdPu',
                text=df_gen['valor'].apply(lambda x: f'R$ {x/1e6:.1f}M')
            )
            fig.update_layout(height=250, showlegend=False, yaxis={'categoryorder': 'total ascending'})
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        # Tabela completa
        st.subheader("📋 Detalhes por Gênero")
        df_seg_gen = dados['segmentos_por_genero'].copy()
        df_seg_gen['valor'] = df_seg_gen['valor'].apply(lambda x: f'R$ {x:,.2f}')
        df_seg_gen.columns = ['Gênero', 'Segmento', 'Valor', 'Clientes', 'Ranking']
        st.dataframe(df_seg_gen, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Top Segmentos por Faixa Etária")

        # Ler dados de segmentos por faixa
        try:
            df_seg_faixa = pd.read_csv('Resultados/top_segmentos_por_faixa.csv')

            ordem_faixas = ['16-24 (Gen Z)', '25-39 (Millennials)', '40-54 (Gen X)', '55-69 (Boomers)', '70+ (Silent)']

            for faixa in ordem_faixas:
                df_f = df_seg_faixa[df_seg_faixa['faixa_etaria'] == faixa].head(5)
                if len(df_f) > 0:
                    st.markdown(f"**{faixa}**")
                    fig = px.bar(
                        df_f,
                        x='valor',
                        y='segmento',
                        orientation='h',
                        color='valor',
                        color_continuous_scale='Oranges',
                        text=df_f['valor'].apply(lambda x: f'R$ {x/1e6:.1f}M')
                    )
                    fig.update_layout(height=200, showlegend=False, yaxis={'categoryorder': 'total ascending'})
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Dados de segmentos por faixa etária não disponíveis.")

    with tab3:
        st.subheader("Matrizes Cruzadas: Gênero x Faixa Etária")

        st.markdown("**Quantidade de Clientes**")
        df_matriz_cli = dados['matriz_clientes'].set_index('faixa_etaria')
        fig = px.imshow(
            df_matriz_cli,
            color_continuous_scale='Blues',
            aspect='auto',
            text_auto=True
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Valor Total (R$)**")
            df_matriz_val = dados['matriz_valor'].set_index('faixa_etaria')
            fig = px.imshow(
                df_matriz_val,
                color_continuous_scale='Greens',
                aspect='auto',
                text_auto='.2s'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**Ticket Médio (R$)**")
            df_matriz_tick = dados['matriz_ticket'].set_index('faixa_etaria')
            fig = px.imshow(
                df_matriz_tick,
                color_continuous_scale='Oranges',
                aspect='auto',
                text_auto='.0f'
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PÁGINA: COMPORTAMENTO
# ============================================================================
elif pagina == "⏰ Comportamento":
    st.markdown('<p class="main-header">⏰ Comportamento de Compra</p>', unsafe_allow_html=True)

    st.markdown("""
    Análise do **comportamento de compra** dos clientes por período do dia e dia da semana,
    segmentado por faixa etária.
    """)

    tab1, tab2 = st.tabs(["🌅 Período do Dia", "📅 Dia da Semana"])

    with tab1:
        st.subheader("Comportamento por Período do Dia")

        # Agrupar por período
        df_periodo_total = dados['comportamento_periodo'].groupby('periodo_dia').agg({
            'valor': 'sum',
            'transacoes': 'sum'
        }).reset_index()

        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                df_periodo_total,
                values='valor',
                names='periodo_dia',
                title='Valor por Período',
                color='periodo_dia',
                color_discrete_map={
                    'Manha (6h-12h)': '#FFC107',
                    'Tarde (12h-18h)': '#FF9800',
                    'Noite (18h-22h)': '#673AB7'
                }
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(
                df_periodo_total,
                values='transacoes',
                names='periodo_dia',
                title='Transações por Período',
                color='periodo_dia',
                color_discrete_map={
                    'Manha (6h-12h)': '#FFC107',
                    'Tarde (12h-18h)': '#FF9800',
                    'Noite (18h-22h)': '#673AB7'
                }
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Período por Faixa Etária")

        # Heatmap período x faixa
        df_periodo_pivot = dados['comportamento_periodo'].pivot_table(
            values='valor',
            index='faixa_etaria',
            columns='periodo_dia',
            fill_value=0
        )
        ordem_faixas = ['16-24 (Gen Z)', '25-39 (Millennials)', '40-54 (Gen X)', '55-69 (Boomers)', '70+ (Silent)', 'Nao Informado']
        df_periodo_pivot = df_periodo_pivot.reindex([f for f in ordem_faixas if f in df_periodo_pivot.index])

        fig = px.imshow(
            df_periodo_pivot,
            color_continuous_scale='YlOrRd',
            aspect='auto',
            text_auto='.2s',
            title='Valor por Faixa Etária e Período'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Comportamento por Dia da Semana")

        # Agrupar por dia
        df_dia_total = dados['comportamento_dia'].groupby('dia_semana').agg({
            'valor': 'sum',
            'transacoes': 'sum'
        }).reset_index()

        ordem_dias = ['Segunda', 'Terca', 'Quarta', 'Quinta', 'Sexta', 'Sabado', 'Domingo']
        df_dia_total['ordem'] = df_dia_total['dia_semana'].map({d: i for i, d in enumerate(ordem_dias)})
        df_dia_total = df_dia_total.sort_values('ordem')

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                df_dia_total,
                x='dia_semana',
                y='valor',
                color='valor',
                color_continuous_scale='Blues',
                title='Valor por Dia da Semana',
                text=df_dia_total['valor'].apply(lambda x: f'R$ {x/1e6:.1f}M')
            )
            fig.update_layout(showlegend=False)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                df_dia_total,
                x='dia_semana',
                y='transacoes',
                color='transacoes',
                color_continuous_scale='Greens',
                title='Transações por Dia da Semana',
                text='transacoes'
            )
            fig.update_layout(showlegend=False)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Dia da Semana por Faixa Etária")

        # Heatmap dia x faixa
        df_dia_pivot = dados['comportamento_dia'].pivot_table(
            values='valor',
            index='faixa_etaria',
            columns='dia_semana',
            fill_value=0
        )
        df_dia_pivot = df_dia_pivot.reindex([f for f in ordem_faixas if f in df_dia_pivot.index])
        df_dia_pivot = df_dia_pivot[[d for d in ordem_dias if d in df_dia_pivot.columns]]

        fig = px.imshow(
            df_dia_pivot,
            color_continuous_scale='Purples',
            aspect='auto',
            text_auto='.2s',
            title='Valor por Faixa Etária e Dia da Semana'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

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
