"""
DASHBOARD - PERFIL DE CLIENTE POR SHOPPING
Visualização interativa dos dados de perfil de cliente
Atualizado em: 2026-01-23 - Correção de mapeamento de shoppings
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Função para enviar email via SMTP
def enviar_email(destinatario, assunto, corpo, remetente_nome, remetente_email):
    """
    Envia email usando SMTP do Gmail.
    Requer configuração dos secrets no Streamlit Cloud:
    - SMTP_EMAIL: email do remetente (Gmail)
    - SMTP_PASSWORD: senha de app do Gmail
    """
    try:
        # Verificar se os secrets estão configurados
        if "SMTP_EMAIL" not in st.secrets or "SMTP_PASSWORD" not in st.secrets:
            return False, "Configuração de email não encontrada. Entre em contato diretamente."

        smtp_email = st.secrets["SMTP_EMAIL"]
        smtp_password = st.secrets["SMTP_PASSWORD"]

        # Configurar mensagem
        msg = MIMEMultipart()
        msg['From'] = f"{remetente_nome} <{smtp_email}>"
        msg['To'] = destinatario
        msg['Subject'] = assunto
        msg['Reply-To'] = remetente_email

        # Corpo do email em HTML
        corpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1E3A5F; border-bottom: 2px solid #1E3A5F; padding-bottom: 10px;">
                    📊 Nova Mensagem do Dashboard
                </h2>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    {corpo.replace(chr(10), '<br>')}
                </div>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="color: #666; font-size: 12px;">
                    Esta mensagem foi enviada através do Dashboard de Perfil de Cliente - Almeida Junior Shoppings
                </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(corpo_html, 'html', 'utf-8'))

        # Conectar e enviar
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)

        return True, "Email enviado com sucesso!"

    except smtplib.SMTPAuthenticationError:
        return False, "Erro de autenticação. Verifique as credenciais de email."
    except Exception as e:
        return False, f"Erro ao enviar email: {str(e)}"

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

# Função para carregar índice de períodos
@st.cache_data
def carregar_indice_periodos():
    try:
        df = pd.read_csv('Resultados/indice_periodos.csv')
        return df
    except:
        return None

# Função para carregar dados
@st.cache_data
def carregar_dados(periodo_pasta='Completo'):
    base_path = f'Resultados/{periodo_pasta}'

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

    # Calcular clientes únicos (total real sem duplicação entre shoppings)
    # Um cliente que compra em múltiplos shoppings é contado apenas uma vez
    dados['clientes_unicos'] = int(dados['personas']['qtd_clientes'].sum())
    dados['clientes_por_shopping'] = int(dados['resumo']['clientes'].sum())  # soma com duplicação

    return dados

# Sidebar
# Logo - carrega GIF
logo_file = "AJ-AJFANS V2 - GIF.gif"
if os.path.exists(logo_file):
    st.sidebar.image(logo_file, use_container_width=True)

st.sidebar.title("🛍️ Almeida Junior")
st.sidebar.markdown("**Dashboard Perfil de Cliente**")
st.sidebar.markdown("---")

# Seletor de Período (Multiselect para comparação)
st.sidebar.markdown("### 📅 Período de Análise")
st.sidebar.caption("Selecione 1 período para análise ou 2+ para comparar")
indice_periodos = carregar_indice_periodos()

if indice_periodos is not None and len(indice_periodos) > 0:
    # Criar opções agrupadas por tipo
    opcoes_periodo = {}
    for _, row in indice_periodos.iterrows():
        tipo = row['tipo']
        codigo = row['codigo']
        nome = row['nome']
        pasta = row['pasta']

        if tipo not in opcoes_periodo:
            opcoes_periodo[tipo] = []
        opcoes_periodo[tipo].append({'codigo': codigo, 'nome': nome, 'pasta': pasta})

    # Criar lista de opções para multiselect
    lista_periodos = []
    mapa_periodos = {}

    # Adicionar na ordem: Completo, Ano, Trimestre, Mês
    ordem_tipos = ['Completo', 'Ano', 'Trimestre', 'Mes']
    for tipo in ordem_tipos:
        if tipo in opcoes_periodo:
            for p in opcoes_periodo[tipo]:
                label = f"{p['nome']}"
                lista_periodos.append(label)
                mapa_periodos[label] = p['pasta']

    periodos_selecionados = st.sidebar.multiselect(
        "Selecione período(s):",
        options=lista_periodos,
        default=["Período Completo"],  # Período Completo como padrão
        max_selections=4  # Limitar a 4 para não sobrecarregar
    )

    # Garantir que pelo menos um período esteja selecionado
    if not periodos_selecionados:
        periodos_selecionados = ["Período Completo"]
        st.sidebar.warning("Selecionando Período Completo como padrão")

    # Mapear períodos selecionados para pastas
    periodos_pasta = {p: mapa_periodos[p] for p in periodos_selecionados}

    # Modo de visualização
    modo_comparativo = len(periodos_selecionados) > 1

    # Para compatibilidade com código existente (quando 1 período)
    periodo_selecionado = periodos_selecionados[0]
    periodo_pasta = periodos_pasta[periodo_selecionado]
else:
    periodos_selecionados = ["Período Completo"]
    periodos_pasta = {"Período Completo": "Completo"}
    periodo_selecionado = "Período Completo"
    periodo_pasta = "Completo"
    modo_comparativo = False

st.sidebar.markdown("---")

# Carregar dados dos períodos selecionados
try:
    if modo_comparativo:
        # Carregar dados de múltiplos períodos
        dados_periodos = {}
        for nome_periodo, pasta in periodos_pasta.items():
            dados_periodos[nome_periodo] = carregar_dados(pasta)
        # Usar o primeiro período como referência para páginas não comparativas
        dados = dados_periodos[periodos_selecionados[0]]
    else:
        # Carregar dados de um único período
        dados = carregar_dados(periodo_pasta)
        dados_periodos = {periodo_selecionado: dados}
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

pagina = st.sidebar.radio(
    "Selecione a visão:",
    ["📊 Visão Geral", "🎭 Personas", "🏬 Por Shopping", "👥 Perfil Demográfico", "⭐ High Spenders", "🛒 Segmentos", "⏰ Comportamento", "📈 Comparativo", "📥 Exportar Dados", "🤖 Assistente", "📚 Documentação"]
)

st.sidebar.markdown("---")
if modo_comparativo:
    st.sidebar.markdown(f"### 📊 Comparando {len(periodos_selecionados)} períodos")
    for nome_p in periodos_selecionados:
        d = dados_periodos[nome_p]
        st.sidebar.markdown(f"**{nome_p}:**")
        st.sidebar.caption(f"Clientes: {d['clientes_unicos']:,} | Valor: R$ {d['resumo']['valor_total'].sum()/1e6:.1f}M")
else:
    st.sidebar.markdown("### 📊 Totais do Período")
    st.sidebar.metric("Clientes Únicos", f"{dados['clientes_unicos']:,}", delta=f"Por shopping: {dados['clientes_por_shopping']:,}")
    st.sidebar.metric("Valor Total", f"R$ {dados['resumo']['valor_total'].sum()/1e6:.1f}M")
    # HS únicos
    hs_unicos_sidebar = int(dados['comparacao_hs'].loc[dados['comparacao_hs']['Metrica'] == 'Qtd Clientes', 'High Spenders'].values[0])
    hs_por_shopping_sidebar = int(dados['resumo']['qtd_high_spenders'].sum())
    st.sidebar.metric("High Spenders", f"{hs_unicos_sidebar:,}", delta=f"Por shopping: {hs_por_shopping_sidebar:,}")
    # Diferença = clientes que frequentam mais de 1 shopping
    diff_clientes = dados['clientes_por_shopping'] - dados['clientes_unicos']
    st.sidebar.caption(f"🔄 {diff_clientes:,} clientes frequentam mais de 1 shopping")

# Cores para períodos (para comparação)
CORES_PERIODOS = ['#E74C3C', '#3498DB', '#2ECC71', '#9B59B6']

# ============================================================================
# PÁGINA: VISÃO GERAL
# ============================================================================
if pagina == "📊 Visão Geral":
    st.markdown('<p class="main-header">📊 Visão Geral - Perfil de Cliente</p>', unsafe_allow_html=True)

    if modo_comparativo:
        # === MODO COMPARATIVO ===
        st.markdown(f"**Comparando:** {' vs '.join(periodos_selecionados)}")

        # Preparar dados para comparação
        df_comparativo = []
        for nome_p in periodos_selecionados:
            d = dados_periodos[nome_p]
            df_comparativo.append({
                'Período': nome_p,
                'Clientes': d['clientes_unicos'],
                'Valor Total': d['resumo']['valor_total'].sum(),
                'Ticket Médio': d['resumo']['valor_total'].sum() / d['clientes_unicos'],
                'High Spenders': d['resumo']['qtd_high_spenders'].sum()
            })
        df_comp = pd.DataFrame(df_comparativo)

        # Métricas comparativas
        st.subheader("📊 Comparativo de Métricas")
        cols = st.columns(len(periodos_selecionados))
        for i, nome_p in enumerate(periodos_selecionados):
            with cols[i]:
                d = dados_periodos[nome_p]
                st.markdown(f"**{nome_p}**")
                st.metric("Clientes Únicos", f"{d['clientes_unicos']:,}")
                st.metric("Valor Total", f"R$ {d['resumo']['valor_total'].sum()/1e6:.1f}M")
                ticket = d['resumo']['valor_total'].sum() / d['clientes_unicos']
                st.metric("Ticket Médio", f"R$ {ticket:,.0f}")
                st.metric("High Spenders", f"{d['resumo']['qtd_high_spenders'].sum():,}")

        st.markdown("---")

        # Gráficos comparativos
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 Valor Total por Período")
            fig = px.bar(
                df_comp,
                x='Período',
                y='Valor Total',
                color='Período',
                color_discrete_sequence=CORES_PERIODOS[:len(periodos_selecionados)],
                text=df_comp['Valor Total'].apply(lambda x: f'R$ {x/1e6:.1f}M')
            )
            fig.update_layout(showlegend=False, height=400)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("👥 Clientes Únicos por Período")
            fig = px.bar(
                df_comp,
                x='Período',
                y='Clientes',
                color='Período',
                color_discrete_sequence=CORES_PERIODOS[:len(periodos_selecionados)],
                text=df_comp['Clientes'].apply(lambda x: f'{x:,}')
            )
            fig.update_layout(showlegend=False, height=400)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎫 Ticket Médio por Período")
            fig = px.bar(
                df_comp,
                x='Período',
                y='Ticket Médio',
                color='Período',
                color_discrete_sequence=CORES_PERIODOS[:len(periodos_selecionados)],
                text=df_comp['Ticket Médio'].apply(lambda x: f'R$ {x:,.0f}')
            )
            fig.update_layout(showlegend=False, height=400)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("⭐ High Spenders por Período")
            fig = px.bar(
                df_comp,
                x='Período',
                y='High Spenders',
                color='Período',
                color_discrete_sequence=CORES_PERIODOS[:len(periodos_selecionados)],
                text=df_comp['High Spenders'].apply(lambda x: f'{x:,}')
            )
            fig.update_layout(showlegend=False, height=400)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Comparativo por Shopping
        st.subheader("🏬 Valor por Shopping - Comparativo entre Períodos")
        df_shop_comp = []
        for nome_p in periodos_selecionados:
            d = dados_periodos[nome_p]
            for _, row in d['resumo'].iterrows():
                df_shop_comp.append({
                    'Período': nome_p,
                    'Shopping': row['sigla'],
                    'Valor': row['valor_total']
                })
        df_shop = pd.DataFrame(df_shop_comp)

        fig = px.bar(
            df_shop,
            x='Shopping',
            y='Valor',
            color='Período',
            barmode='group',
            color_discrete_sequence=CORES_PERIODOS[:len(periodos_selecionados)],
            text=df_shop['Valor'].apply(lambda x: f'R$ {x/1e6:.1f}M')
        )
        fig.update_layout(height=450)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

        # Tabela resumo
        st.subheader("📋 Tabela Comparativa")
        df_comp_display = df_comp.copy()
        df_comp_display['Valor Total'] = df_comp_display['Valor Total'].apply(lambda x: f'R$ {x:,.2f}')
        df_comp_display['Ticket Médio'] = df_comp_display['Ticket Médio'].apply(lambda x: f'R$ {x:,.2f}')
        df_comp_display['Clientes'] = df_comp_display['Clientes'].apply(lambda x: f'{x:,}')
        df_comp_display['High Spenders'] = df_comp_display['High Spenders'].apply(lambda x: f'{x:,}')
        df_comp_display = df_comp_display.rename(columns={'Clientes': 'Clientes Únicos'})
        st.dataframe(df_comp_display, use_container_width=True, hide_index=True)

    else:
        # === MODO NORMAL (1 período) ===
        st.markdown(f"**Período selecionado:** {periodo_selecionado}")

        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Clientes Únicos",
                f"{dados['clientes_unicos']:,}",
                delta=f"Por shopping: {dados['clientes_por_shopping']:,}",
                help="Clientes únicos: cada pessoa contada uma vez. Por shopping: soma dos clientes de cada shopping (inclui quem compra em múltiplos shoppings)"
            )

        with col2:
            st.metric(
                "Valor Total",
                f"R$ {dados['resumo']['valor_total'].sum()/1e6:.1f}M",
                delta=f"Ticket: R$ {dados['resumo']['valor_total'].sum()/dados['clientes_unicos']:,.0f}"
            )

        with col3:
            hs_unicos_visao = int(dados['comparacao_hs'].loc[dados['comparacao_hs']['Metrica'] == 'Qtd Clientes', 'High Spenders'].values[0])
            hs_por_shopping_visao = int(dados['resumo']['qtd_high_spenders'].sum())
            st.metric(
                "High Spenders",
                f"{hs_unicos_visao:,}",
                delta=f"Por shopping: {hs_por_shopping_visao:,}",
                help="HS únicos: cada cliente contado uma vez. Por shopping: soma inclui quem é HS em múltiplos shoppings"
            )

        with col4:
            ticket_medio_geral = dados['resumo']['valor_total'].sum() / dados['clientes_unicos']
            st.metric(
                "Ticket Médio",
                f"R$ {ticket_medio_geral:,.0f}",
                delta="valor total / clientes únicos"
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
            st.caption("⚠️ Soma inclui clientes que frequentam múltiplos shoppings")

        # Tabela resumo
        st.subheader("📋 Resumo por Shopping")
        df_display = dados['resumo'][['shopping', 'sigla', 'clientes', 'valor_total', 'ticket_medio', 'qtd_high_spenders']].copy()
        df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f'R$ {x:,.2f}')
        df_display['ticket_medio'] = df_display['ticket_medio'].apply(lambda x: f'R$ {x:,.2f}')
        df_display.columns = ['Shopping', 'Sigla', 'Clientes*', 'Valor Total', 'Ticket Médio', 'High Spenders']
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.caption("*Clientes por shopping: um cliente que compra em 2 shoppings é contado em ambos. Clientes únicos: {:,}".format(dados['clientes_unicos']))

# ============================================================================
# PÁGINA: PERSONAS
# ============================================================================
elif pagina == "🎭 Personas":
    st.markdown('<p class="main-header">🎭 Personas de Clientes</p>', unsafe_allow_html=True)

    st.markdown("""
    As **Personas** representam perfis comportamentais de clientes, agrupados por características
    similares de consumo, frequência e valor gasto.
    """)

    if modo_comparativo:
        # === MODO COMPARATIVO ===
        st.markdown(f"**Comparando:** {' vs '.join(periodos_selecionados)}")

        # Comparar valor total por persona entre períodos
        st.subheader("📊 Valor por Persona - Comparativo entre Períodos")

        df_personas_comp = []
        for nome_p in periodos_selecionados:
            d = dados_periodos[nome_p]
            for _, row in d['personas'].iterrows():
                df_personas_comp.append({
                    'Período': nome_p,
                    'Persona': row['persona'],
                    'Clientes': row['qtd_clientes'],
                    'Valor': row['valor_total'],
                    'Ticket': row['ticket_medio']
                })
        df_pers = pd.DataFrame(df_personas_comp)

        # Top 5 personas por valor (baseado no primeiro período)
        top_personas = dados['personas'].nlargest(5, 'valor_total')['persona'].tolist()
        df_pers_top = df_pers[df_pers['Persona'].isin(top_personas)]

        fig = px.bar(
            df_pers_top,
            x='Persona',
            y='Valor',
            color='Período',
            barmode='group',
            color_discrete_sequence=CORES_PERIODOS[:len(periodos_selecionados)],
            text=df_pers_top['Valor'].apply(lambda x: f'R$ {x/1e6:.1f}M')
        )
        fig.update_layout(height=450)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Comparar clientes por persona
        st.subheader("👥 Clientes por Persona - Comparativo")
        fig = px.bar(
            df_pers_top,
            x='Persona',
            y='Clientes',
            color='Período',
            barmode='group',
            color_discrete_sequence=CORES_PERIODOS[:len(periodos_selecionados)],
            text=df_pers_top['Clientes'].apply(lambda x: f'{x:,}')
        )
        fig.update_layout(height=450)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Tabelas lado a lado
        st.subheader("📋 Detalhes por Período")
        cols = st.columns(len(periodos_selecionados))
        for i, nome_p in enumerate(periodos_selecionados):
            with cols[i]:
                st.markdown(f"**{nome_p}**")
                df_p = dados_periodos[nome_p]['personas'][['persona', 'qtd_clientes', 'valor_total', 'pct_valor']].copy()
                df_p['valor_total'] = df_p['valor_total'].apply(lambda x: f'R$ {x/1e6:.1f}M')
                df_p['pct_valor'] = df_p['pct_valor'].apply(lambda x: f'{x:.1f}%')
                df_p.columns = ['Persona', 'Clientes', 'Valor', '% Valor']
                st.dataframe(df_p.head(6), use_container_width=True, hide_index=True)

    else:
        # === MODO NORMAL (1 período) ===
        st.markdown(f"**Período selecionado:** {periodo_selecionado}")

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
    if modo_comparativo:
        st.markdown(f"**Comparando:** {' vs '.join(periodos_selecionados)}")
        st.info("Para análise detalhada por shopping, selecione apenas 1 período.")
    else:
        st.markdown(f"**Período selecionado:** {periodo_selecionado}")

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
    if modo_comparativo:
        st.markdown(f"**Comparando:** {' vs '.join(periodos_selecionados)}")
    else:
        st.markdown(f"**Período selecionado:** {periodo_selecionado}")

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

        ordem_faixas = ['Gen Z (1997-2012)', 'Millennials (1981-1996)', 'Gen X (1965-1980)', 'Boomers (1946-1964)', 'Silent (antes 1946)', 'Nao Informado']
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

    if modo_comparativo:
        # === MODO COMPARATIVO ===
        st.markdown(f"**Comparando:** {' vs '.join(periodos_selecionados)}")

        # Preparar dados comparativos
        df_hs_comp = []
        for nome_p in periodos_selecionados:
            d = dados_periodos[nome_p]
            total_hs = d['resumo']['qtd_high_spenders'].sum()
            total_cli = d['resumo']['clientes'].sum()
            df_hs_comp.append({
                'Período': nome_p,
                'High Spenders': total_hs,
                '% do Total': total_hs / total_cli * 100,
                'Total Clientes': total_cli
            })
        df_hs = pd.DataFrame(df_hs_comp)

        # Métricas lado a lado
        cols = st.columns(len(periodos_selecionados))
        for i, nome_p in enumerate(periodos_selecionados):
            with cols[i]:
                d = dados_periodos[nome_p]
                total_hs = d['resumo']['qtd_high_spenders'].sum()
                total_cli = d['resumo']['clientes'].sum()
                st.markdown(f"**{nome_p}**")
                st.metric("High Spenders", f"{total_hs:,}")
                st.metric("% do Total", f"{total_hs/total_cli*100:.1f}%")

        st.markdown("---")

        # Gráfico comparativo
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⭐ High Spenders por Período")
            fig = px.bar(
                df_hs,
                x='Período',
                y='High Spenders',
                color='Período',
                color_discrete_sequence=CORES_PERIODOS[:len(periodos_selecionados)],
                text=df_hs['High Spenders'].apply(lambda x: f'{x:,}')
            )
            fig.update_layout(showlegend=False, height=400)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📊 % High Spenders por Período")
            fig = px.bar(
                df_hs,
                x='Período',
                y='% do Total',
                color='Período',
                color_discrete_sequence=CORES_PERIODOS[:len(periodos_selecionados)],
                text=df_hs['% do Total'].apply(lambda x: f'{x:.1f}%')
            )
            fig.update_layout(showlegend=False, height=400)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # HS por Shopping comparativo
        st.subheader("🏬 High Spenders por Shopping - Comparativo")
        df_hs_shop = []
        for nome_p in periodos_selecionados:
            d = dados_periodos[nome_p]
            for _, row in d['resumo'].iterrows():
                df_hs_shop.append({
                    'Período': nome_p,
                    'Shopping': row['sigla'],
                    'High Spenders': row['qtd_high_spenders']
                })
        df_hs_s = pd.DataFrame(df_hs_shop)

        fig = px.bar(
            df_hs_s,
            x='Shopping',
            y='High Spenders',
            color='Período',
            barmode='group',
            color_discrete_sequence=CORES_PERIODOS[:len(periodos_selecionados)],
            text=df_hs_s['High Spenders'].apply(lambda x: f'{x:,}')
        )
        fig.update_layout(height=450)
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

    else:
        # === MODO NORMAL (1 período) ===
        st.markdown(f"**Período selecionado:** {periodo_selecionado}")

        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)

        # HS únicos vem do comparacao_high_spenders (cliente contado uma vez)
        hs_unicos = int(dados['comparacao_hs'].loc[dados['comparacao_hs']['Metrica'] == 'Qtd Clientes', 'High Spenders'].values[0])
        # HS por shopping (soma, inclui duplicação)
        hs_por_shopping = dados['resumo']['qtd_high_spenders'].sum()
        clientes_unicos = dados['clientes_unicos']

        with col1:
            st.metric("High Spenders Únicos", f"{hs_unicos:,}",
                     delta=f"Por shopping: {hs_por_shopping:,}",
                     help="HS únicos: cada cliente contado uma vez. Por shopping: soma inclui quem é HS em múltiplos shoppings")
        with col2:
            st.metric("% dos Clientes", f"{hs_unicos/clientes_unicos*100:.1f}%",
                     help=f"Percentual sobre {clientes_unicos:,} clientes únicos")
        with col3:
            st.metric("Média por Shopping", f"{hs_por_shopping//6:,}")
        with col4:
            st.metric("Clientes Únicos", f"{clientes_unicos:,}",
                     delta=f"Por shopping: {dados['clientes_por_shopping']:,}",
                     help="Clientes únicos: cada cliente contado uma vez. Por shopping: soma inclui quem compra em múltiplos shoppings")

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
    if modo_comparativo:
        st.markdown(f"**Comparando:** {' vs '.join(periodos_selecionados)}")
    else:
        st.markdown(f"**Período selecionado:** {periodo_selecionado}")

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
            df_seg_faixa = pd.read_csv(f'Resultados/{periodo_pasta}/top_segmentos_por_faixa.csv')

            ordem_faixas = ['Gen Z (1997-2012)', 'Millennials (1981-1996)', 'Gen X (1965-1980)', 'Boomers (1946-1964)', 'Silent (antes 1946)']

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
    if modo_comparativo:
        st.markdown(f"**Comparando:** {' vs '.join(periodos_selecionados)}")
    else:
        st.markdown(f"**Período selecionado:** {periodo_selecionado}")

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
        ordem_faixas = ['Gen Z (1997-2012)', 'Millennials (1981-1996)', 'Gen X (1965-1980)', 'Boomers (1946-1964)', 'Silent (antes 1946)', 'Nao Informado']
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
    if modo_comparativo:
        st.markdown(f"**Comparando períodos:** {' vs '.join(periodos_selecionados)}")
    else:
        st.markdown(f"**Período selecionado:** {periodo_selecionado}")

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

# ============================================================================
# PÁGINA: EXPORTAR DADOS
# ============================================================================
elif pagina == "📥 Exportar Dados":
    st.markdown('<p class="main-header">📥 Exportar Relatórios</p>', unsafe_allow_html=True)

    st.markdown(f"**Período selecionado:** {periodo_selecionado}")

    st.markdown("""
    Nesta página você pode baixar os **relatórios completos** que alimentam o dashboard.
    Os dados são exportados em formato CSV, compatível com Excel e outras ferramentas de análise.
    """)

    st.markdown("---")

    # Função para converter DataFrame para CSV
    @st.cache_data
    def converter_para_csv(df):
        return df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')

    # Função para criar Excel com múltiplas abas
    @st.cache_data
    def criar_excel_completo(dados_dict, periodo):
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for nome, df in dados_dict.items():
                # Limitar nome da aba a 31 caracteres
                sheet_name = nome[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        return output.getvalue()

    # ========== SEÇÃO 1: RELATÓRIO COMPLETO (EXCEL) ==========
    st.subheader("📊 Relatório Completo (Excel)")
    st.markdown("Arquivo Excel com **todas as análises** em abas separadas.")

    # Preparar dados para Excel completo
    dados_excel = {
        'Resumo por Shopping': dados['resumo'],
        'Personas': dados['personas'],
        'Genero por Shopping': dados['genero'],
        'Faixa Etaria por Shopping': dados['faixa'],
        'Segmentos por Shopping': dados['segmentos'],
        'High Spenders por Genero': dados['hs_por_genero'],
        'High Spenders por Faixa': dados['hs_por_faixa'],
        'Comparacao HS vs Demais': dados['comparacao_hs'],
        'Matriz Clientes': dados['matriz_clientes'],
        'Matriz Valor': dados['matriz_valor'],
        'Matriz Ticket': dados['matriz_ticket'],
        'Segmentos por Genero': dados['segmentos_por_genero'],
        'Segmentos por Faixa': dados['segmentos_por_faixa'],
        'Comportamento Periodo': dados['comportamento_periodo'],
        'Comportamento Dia Semana': dados['comportamento_dia']
    }

    excel_completo = criar_excel_completo(dados_excel, periodo_selecionado)

    st.download_button(
        label="⬇️ Baixar Relatório Completo (Excel)",
        data=excel_completo,
        file_name=f"relatorio_perfil_cliente_{periodo_pasta}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Download do arquivo Excel com todas as análises"
    )

    st.markdown("---")

    # ========== SEÇÃO 2: RELATÓRIOS INDIVIDUAIS ==========
    st.subheader("📁 Relatórios Individuais (CSV)")
    st.markdown("Baixe cada relatório separadamente conforme sua necessidade.")

    # Organizar em tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumos", "👥 Demografia", "⭐ High Spenders", "🛒 Comportamento"])

    with tab1:
        st.markdown("#### Resumos Gerais")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Resumo por Shopping**")
            st.caption("Métricas consolidadas de cada shopping")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['resumo']),
                file_name="resumo_por_shopping.csv",
                mime="text/csv",
                key="download_resumo"
            )

            st.markdown("**Personas de Clientes**")
            st.caption("9 perfis comportamentais identificados")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['personas']),
                file_name="personas_clientes.csv",
                mime="text/csv",
                key="download_personas"
            )

        with col2:
            st.markdown("**Segmentos por Shopping**")
            st.caption("Top segmentos de cada shopping")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['segmentos']),
                file_name="segmentos_por_shopping.csv",
                mime="text/csv",
                key="download_segmentos"
            )

    with tab2:
        st.markdown("#### Análises Demográficas")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Distribuição por Gênero**")
            st.caption("Clientes por gênero em cada shopping")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['genero']),
                file_name="distribuicao_genero.csv",
                mime="text/csv",
                key="download_genero"
            )

            st.markdown("**Matriz Clientes (Gênero x Idade)**")
            st.caption("Quantidade de clientes por combinação")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['matriz_clientes']),
                file_name="matriz_clientes_genero_idade.csv",
                mime="text/csv",
                key="download_matriz_cli"
            )

        with col2:
            st.markdown("**Distribuição por Faixa Etária**")
            st.caption("Clientes por geração em cada shopping")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['faixa']),
                file_name="distribuicao_faixa_etaria.csv",
                mime="text/csv",
                key="download_faixa"
            )

            st.markdown("**Matriz Valor (Gênero x Idade)**")
            st.caption("Valor total por combinação")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['matriz_valor']),
                file_name="matriz_valor_genero_idade.csv",
                mime="text/csv",
                key="download_matriz_val"
            )

    with tab3:
        st.markdown("#### Análises de High Spenders")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**High Spenders por Gênero**")
            st.caption("Distribuição dos top 10% por gênero")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['hs_por_genero']),
                file_name="high_spenders_por_genero.csv",
                mime="text/csv",
                key="download_hs_genero"
            )

            st.markdown("**Comparação HS vs Demais**")
            st.caption("Métricas comparativas")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['comparacao_hs']),
                file_name="comparacao_high_spenders.csv",
                mime="text/csv",
                key="download_hs_comp"
            )

        with col2:
            st.markdown("**High Spenders por Faixa Etária**")
            st.caption("Distribuição dos top 10% por idade")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['hs_por_faixa']),
                file_name="high_spenders_por_faixa.csv",
                mime="text/csv",
                key="download_hs_faixa"
            )

    with tab4:
        st.markdown("#### Análises de Comportamento")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Comportamento por Período do Dia**")
            st.caption("Manhã, Tarde e Noite")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['comportamento_periodo']),
                file_name="comportamento_periodo_dia.csv",
                mime="text/csv",
                key="download_periodo"
            )

            st.markdown("**Segmentos por Gênero**")
            st.caption("Top 5 segmentos preferidos por gênero")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['segmentos_por_genero']),
                file_name="segmentos_por_genero.csv",
                mime="text/csv",
                key="download_seg_genero"
            )

        with col2:
            st.markdown("**Comportamento por Dia da Semana**")
            st.caption("Segunda a Domingo")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['comportamento_dia']),
                file_name="comportamento_dia_semana.csv",
                mime="text/csv",
                key="download_dia"
            )

            st.markdown("**Segmentos por Faixa Etária**")
            st.caption("Top segmentos por geração")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['segmentos_por_faixa']),
                file_name="segmentos_por_faixa.csv",
                mime="text/csv",
                key="download_seg_faixa"
            )

    st.markdown("---")

    # ========== SEÇÃO 3: DADOS POR SHOPPING ==========
    st.subheader("🏬 Dados por Shopping")
    st.markdown("Baixe os dados detalhados de cada shopping individualmente.")

    shopping_export = st.selectbox(
        "Selecione o Shopping:",
        options=list(NOMES_SHOPPING.keys()),
        format_func=lambda x: f"{x} - {NOMES_SHOPPING[x]}",
        key="shopping_export"
    )

    if shopping_export in dados['por_shopping']:
        shop_data = dados['por_shopping'][shopping_export]

        # Criar Excel com dados do shopping
        dados_shop_excel = {
            'Perfil Genero': shop_data['genero'],
            'Perfil Faixa Etaria': shop_data['faixa'],
            'Top Segmentos': shop_data['segmentos'],
            'Top Lojas': shop_data['lojas'],
            'Comportamento Periodo': shop_data['periodo'],
            'Comportamento Dia Semana': shop_data['dia_semana']
        }

        excel_shopping = criar_excel_completo(dados_shop_excel, shopping_export)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button(
                label=f"⬇️ Relatório Completo {shopping_export} (Excel)",
                data=excel_shopping,
                file_name=f"relatorio_{shopping_export}_{periodo_pasta}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_shop_excel"
            )

        with col2:
            st.download_button(
                label=f"⬇️ Top Lojas {shopping_export} (CSV)",
                data=converter_para_csv(shop_data['lojas']),
                file_name=f"top_lojas_{shopping_export}.csv",
                mime="text/csv",
                key="download_shop_lojas"
            )

        with col3:
            st.download_button(
                label=f"⬇️ Top Segmentos {shopping_export} (CSV)",
                data=converter_para_csv(shop_data['segmentos']),
                file_name=f"top_segmentos_{shopping_export}.csv",
                mime="text/csv",
                key="download_shop_seg"
            )

    st.markdown("---")
    st.info("💡 **Dica:** Os arquivos CSV podem ser abertos diretamente no Excel. Para melhores resultados, use 'Dados > De Texto/CSV' no Excel.")

# ============================================================================
# PÁGINA: ASSISTENTE
# ============================================================================
elif pagina == "🤖 Assistente":
    st.markdown('<p class="main-header">🤖 Assistente do Dashboard</p>', unsafe_allow_html=True)

    st.markdown("""
    Bem-vindo ao **Assistente do Dashboard de Perfil de Cliente**!
    Aqui você pode tirar dúvidas sobre os dados, métricas e análises apresentadas.
    """)

    # Tabs para organizar
    tab_chat, tab_faq, tab_contato = st.tabs(["💬 Perguntas Frequentes", "📖 Guia Rápido", "📧 Fale Conosco"])

    with tab_chat:
        st.subheader("💬 Perguntas Frequentes")

        # FAQ expandível
        with st.expander("❓ O que é um High Spender?", expanded=False):
            st.markdown("""
            **High Spenders** são os clientes que estão no **Top 10%** em valor de compras de cada shopping.

            - Representam aproximadamente **10% dos clientes**
            - Respondem por cerca de **40-50% do faturamento total**
            - São identificados pelo percentil 90 de gastos

            **Exemplo:** Se o threshold do BS é R$ 5.800, qualquer cliente que gastou R$ 5.800 ou mais é considerado High Spender nesse shopping.
            """)

        with st.expander("❓ Como são definidas as Personas?", expanded=False):
            st.markdown("""
            As **9 Personas** foram identificadas através de **análise de cluster (K-Means)** considerando:

            - Valor total gasto
            - Frequência de compras
            - Ticket médio
            - Idade média
            - Gênero predominante

            **Principais Personas:**
            | Persona | % Clientes | Perfil |
            |---------|------------|--------|
            | Cliente Regular | 37,1% | Perfil diverso, não categorizado |
            | Senior Tradicional | 11,4% | 55+ anos, baixa frequência |
            | Jovem Explorer | 10,5% | Jovens <30, explorando marcas |
            | Mãe Moderna | 9,3% | Mulheres 30-50, Moda/Infantil |
            | Foodie | 8,8% | Alta freq. em Gastronomia |
            | Beauty Lover | 3,4% | Mulheres, segmento Beleza |
            | Fitness | 1,8% | Segmento Esportes |
            """)

        with st.expander("❓ O que significa cada faixa etária?", expanded=False):
            st.markdown("""
            As faixas etárias são baseadas nas **gerações**:

            | Geração | Nascidos | Idade Atual |
            |---------|----------|-------------|
            | **Gen Z** | 1997-2012 | 14-29 anos |
            | **Millennials** | 1981-1996 | 30-45 anos |
            | **Gen X** | 1965-1980 | 46-61 anos |
            | **Boomers** | 1946-1964 | 62-80 anos |
            | **Silent** | Antes de 1946 | 81+ anos |
            """)

        with st.expander("❓ Como é calculado o Ticket Médio?", expanded=False):
            st.markdown("""
            O **Ticket Médio** é calculado pela fórmula:

            ```
            Ticket Médio = Valor Total de Compras / Número de Clientes
            ```

            **Importante:** O ticket médio varia significativamente entre shoppings devido a:
            - Mix de lojas diferentes
            - Perfil socioeconômico da região
            - Tipo de produtos predominantes
            """)

        with st.expander("❓ O que são os Segmentos?", expanded=False):
            st.markdown("""
            Os **Segmentos** representam as categorias de produtos/serviços das lojas:

            - **Moda** - Vestuário, roupas, acessórios de moda
            - **Beleza e Bem-estar** - Cosméticos, perfumaria, estética
            - **Calçados** - Sapatos, tênis, sandálias
            - **Joalheria** - Joias, relógios, óticas
            - **Gastronomia** - Restaurantes, fast-food, cafeterias
            - **Telefonia** - Celulares, operadoras, acessórios
            - **Eletrônicos** - Informática, eletrodomésticos
            - **Casa e Decoração** - Móveis, itens de decoração
            """)

        with st.expander("❓ Qual o período dos dados?", expanded=False):
            st.markdown(f"""
            **Período completo:** 11/12/2022 a 19/01/2026

            **Período selecionado atualmente:** {periodo_selecionado}

            Os dados são atualizados periodicamente e você pode filtrar por:
            - Período Completo
            - Por Ano
            - Por Trimestre
            - Por Mês
            """)

        with st.expander("❓ O que significam as siglas dos shoppings?", expanded=False):
            st.markdown("""
            | Sigla | Shopping | Cidade |
            |-------|----------|--------|
            | **BS** | Balneário Shopping | Balneário Camboriú |
            | **CS** | Continente Shopping | São José |
            | **GS** | Garten Shopping | Joinville |
            | **NK** | Neumarkt Shopping | Blumenau |
            | **NR** | Norte Shopping | Blumenau |
            | **NS** | Nações Shopping | Criciúma |
            """)

        with st.expander("❓ Como exportar os dados?", expanded=False):
            st.markdown("""
            Você pode exportar os dados de várias formas:

            1. **Página "📥 Exportar Dados"** - Acesse pelo menu lateral
            2. **Relatório Completo (Excel)** - Todas as análises em um arquivo
            3. **CSVs Individuais** - Baixe cada relatório separadamente
            4. **Por Shopping** - Dados específicos de cada unidade

            💡 **Dica:** Os arquivos CSV podem ser abertos diretamente no Excel.
            """)

    with tab_faq:
        st.subheader("📖 Guia Rápido de Navegação")

        st.markdown("""
        ### Como usar o Dashboard

        **1. Selecione o Período**
        - No menu lateral, escolha o período de análise
        - Você pode selecionar múltiplos períodos para comparar

        **2. Navegue pelas Páginas**
        - Use o menu lateral para acessar diferentes análises
        - Cada página oferece uma visão específica dos dados

        **3. Interaja com os Gráficos**
        - Passe o mouse sobre os gráficos para ver detalhes
        - Alguns gráficos permitem zoom e filtros

        **4. Exporte os Dados**
        - Acesse "📥 Exportar Dados" para baixar relatórios
        - Disponível em Excel e CSV

        ---

        ### Páginas Disponíveis

        | Página | O que mostra |
        |--------|--------------|
        | 📊 Visão Geral | Panorama consolidado de todos os shoppings |
        | 🎭 Personas | 9 perfis comportamentais de clientes |
        | 🏬 Por Shopping | Análise detalhada de cada unidade |
        | 👥 Perfil Demográfico | Distribuição por gênero e idade |
        | ⭐ High Spenders | Clientes top 10% em valor |
        | 🛒 Segmentos | Análise por categoria de produto |
        | ⏰ Comportamento | Padrões temporais de compra |
        | 📈 Comparativo | Comparação entre shoppings |
        | 📥 Exportar Dados | Download de relatórios |
        | 📚 Documentação | Documentação completa |
        """)

        st.markdown("---")

        st.markdown("""
        ### Dicas de Análise

        🎯 **Para identificar oportunidades:**
        - Compare o ticket médio entre shoppings
        - Analise quais segmentos têm maior crescimento
        - Identifique gaps demográficos (faixas etárias pouco atendidas)

        📈 **Para acompanhar performance:**
        - Use a comparação de períodos
        - Acompanhe a evolução dos High Spenders
        - Monitore mudanças nas personas

        🔍 **Para análises específicas:**
        - Use "Por Shopping" para dados detalhados de cada unidade
        - Exporte os dados para análises customizadas
        """)

    with tab_contato:
        st.subheader("📧 Fale Conosco")

        st.markdown("""
        Não encontrou a resposta que procurava? Tem uma dúvida específica sobre os dados?

        Preencha o formulário abaixo e nossa equipe entrará em contato.
        """)

        # Formulário de contato
        with st.form("formulario_contato", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                nome = st.text_input("Nome *", placeholder="Seu nome completo")
                email = st.text_input("E-mail *", placeholder="seu.email@empresa.com")

            with col2:
                departamento = st.selectbox(
                    "Departamento",
                    ["Marketing", "Comercial", "Operações", "TI", "Diretoria", "Outro"]
                )
                shopping_ref = st.selectbox(
                    "Shopping de Referência",
                    ["Todos", "BS - Balneário Shopping", "CS - Continente Shopping",
                     "GS - Garten Shopping", "NK - Neumarkt Shopping",
                     "NR - Norte Shopping", "NS - Nações Shopping"]
                )

            assunto = st.selectbox(
                "Assunto *",
                ["Dúvida sobre os dados", "Solicitação de análise específica",
                 "Problema técnico no dashboard", "Sugestão de melhoria",
                 "Solicitação de acesso", "Outro"]
            )

            mensagem = st.text_area(
                "Mensagem *",
                placeholder="Descreva sua dúvida ou solicitação em detalhes...",
                height=150
            )

            # Campos ocultos para contexto
            st.markdown(f"*Período selecionado: {periodo_selecionado}*")

            enviado = st.form_submit_button("📤 Enviar Mensagem", use_container_width=True)

            if enviado:
                if not nome or not email or not mensagem:
                    st.error("Por favor, preencha todos os campos obrigatórios (*)")
                elif "@" not in email:
                    st.error("Por favor, insira um e-mail válido")
                else:
                    # Criar corpo do email formatado
                    corpo_email = f"""
<strong>Dados do Remetente:</strong>
• Nome: {nome}
• E-mail: {email}
• Departamento: {departamento}
• Shopping: {shopping_ref}

<strong>Informações da Solicitação:</strong>
• Assunto: {assunto}
• Período do Dashboard: {periodo_selecionado}

<strong>Mensagem:</strong>
{mensagem}
                    """.strip()

                    # Tentar enviar email automaticamente
                    with st.spinner("Enviando mensagem..."):
                        sucesso, msg_retorno = enviar_email(
                            destinatario="carlos.gravi@almeidajunior.com.br",
                            assunto=f"[Dashboard Perfil Cliente] {assunto}",
                            corpo=corpo_email,
                            remetente_nome=nome,
                            remetente_email=email
                        )

                    if sucesso:
                        st.success("✅ Mensagem enviada com sucesso!")
                        st.balloons()
                        st.info(f"""
                        **Sua mensagem foi enviada para nossa equipe.**

                        📧 Você receberá uma resposta em **carlos.gravi@almeidajunior.com.br**

                        Respondendo para: **{email}**

                        *Prazo de resposta: até 2 dias úteis*
                        """)
                    else:
                        # Fallback para mailto se SMTP falhar
                        st.warning(f"⚠️ {msg_retorno}")
                        st.markdown("**Use o método alternativo abaixo:**")

                        import urllib.parse
                        corpo_texto = corpo_email.replace('<strong>', '').replace('</strong>', '')
                        assunto_encoded = urllib.parse.quote(f"[Dashboard Perfil Cliente] {assunto}")
                        corpo_encoded = urllib.parse.quote(corpo_texto)
                        mailto_link = f"mailto:carlos.gravi@almeidajunior.com.br?subject={assunto_encoded}&body={corpo_encoded}"

                        st.markdown(f"""
                        <a href="{mailto_link}" target="_blank">
                            <button style="
                                background-color: #1E3A5F;
                                color: white;
                                padding: 10px 20px;
                                border: none;
                                border-radius: 5px;
                                cursor: pointer;
                                font-size: 16px;
                                width: 100%;
                            ">
                                📧 Abrir Cliente de E-mail
                            </button>
                        </a>
                        """, unsafe_allow_html=True)

                        st.code(corpo_texto, language=None)

        st.markdown("---")

        st.markdown("""
        ### Contato Direto

        📧 **E-mail:** carlos.gravi@almeidajunior.com.br

        💡 **Horário de atendimento:** Segunda a Sexta, 9h às 18h

        ---

        *Sua mensagem será respondida em até 2 dias úteis.*
        """)

# ============================================================================
# PÁGINA: DOCUMENTAÇÃO
# ============================================================================
elif pagina == "📚 Documentação":
    st.markdown('<p class="main-header">📚 Documentação do Dashboard</p>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Visão Geral", "📊 Métricas", "🎭 Personas & HS", "📁 Dados", "❓ Glossário"])

    with tab1:
        # Calcular valores dinâmicos para documentação
        hs_unicos_doc = int(dados['comparacao_hs'].loc[dados['comparacao_hs']['Metrica'] == 'Qtd Clientes', 'High Spenders'].values[0])
        ticket_medio_doc = dados['resumo']['valor_total'].sum() / dados['clientes_unicos']
        transacoes_doc = int(dados['resumo']['transacoes'].sum())
        diff_clientes_doc = dados['clientes_por_shopping'] - dados['clientes_unicos']

        st.markdown(f"""
        ## Sobre o Dashboard

        O **Dashboard de Perfil de Cliente** é uma ferramenta de Business Intelligence desenvolvida para analisar
        o comportamento de consumo dos clientes da rede **Almeida Junior Shoppings**.

        ### Período dos Dados
        **Base completa:** 11/12/2022 a 19/01/2026

        **Filtros disponíveis:** Período Completo, Por Ano, Por Trimestre, Por Mês

        ### Shoppings Analisados

        | Sigla | Shopping | Cidade/Região |
        |-------|----------|---------------|
        | BS | Balneário Shopping | Balneário Camboriú |
        | CS | Continente Shopping | São José |
        | GS | Garten Shopping | Joinville |
        | NK | Neumarkt Shopping | Blumenau |
        | NR | Norte Shopping | Blumenau |
        | NS | Nações Shopping | Criciúma |

        ### Resumo Geral

        | Métrica | Valor | Observação |
        |---------|-------|------------|
        | Clientes Únicos | {dados['clientes_unicos']:,} | Cada cliente contado uma vez |
        | Clientes por Shopping | {dados['clientes_por_shopping']:,} | Soma inclui quem compra em múltiplos shoppings |
        | Total de Transações | {transacoes_doc:,} | |
        | Valor Total | R$ {dados['resumo']['valor_total'].sum():,.0f} | |
        | Ticket Médio | R$ {ticket_medio_doc:,.0f} | Valor Total ÷ Clientes Únicos |
        | High Spenders | {hs_unicos_doc:,} (10%) | Top 10% de cada shopping |

        > 🔄 **{diff_clientes_doc:,}** clientes frequentam mais de 1 shopping

        ### Páginas do Dashboard

        1. **📊 Visão Geral** - Panorama consolidado de todos os shoppings
        2. **🎭 Personas** - 9 perfis comportamentais de clientes
        3. **🏬 Por Shopping** - Análise detalhada de cada unidade
        4. **👥 Perfil Demográfico** - Distribuição por gênero e faixa etária
        5. **⭐ High Spenders** - Clientes top 10% em valor
        6. **🛒 Segmentos** - Análise por categoria de produto
        7. **⏰ Comportamento** - Padrões temporais de compra
        8. **📈 Comparativo** - Comparação entre shoppings
        """)

    with tab2:
        st.markdown("""
        ## Cálculo das Métricas

        ### Métricas Básicas

        | Métrica | Fórmula |
        |---------|---------|
        | **Total Clientes** | Contagem de clientes únicos |
        | **Valor Total** | Soma de todas as transações |
        | **Ticket Médio** | Valor Total ÷ Total de Clientes |
        | **Frequência Média** | Total Transações ÷ Total Clientes |

        ### Distribuições Demográficas

        **Por Gênero:**
        ```
        % Gênero = (Clientes do Gênero / Total Clientes) × 100
        ```

        **Por Faixa Etária:**

        | Faixa | Geração | Nascidos |
        |-------|---------|----------|
        | Gen Z | 1997-2012 | 14-29 anos |
        | Millennials | 1981-1996 | 30-45 anos |
        | Gen X | 1965-1980 | 46-61 anos |
        | Boomers | 1946-1964 | 62-80 anos |
        | Silent | Antes de 1946 | 81+ anos |

        ### Métricas de Segmentos

        Os segmentos são definidos pela categoria da loja:
        - **Moda** - Vestuário, acessórios
        - **Beleza e Bem-estar** - Cosméticos, perfumaria
        - **Calçados** - Sapatos, tênis, sandálias
        - **Joalheria** - Joias, relógios, óticas
        - **Gastronomia** - Restaurantes, fast-food
        - **Telefonia** - Celulares, acessórios
        - **Eletrônicos** - Informática, eletrodomésticos
        - **Casa e Decoração** - Móveis, decoração

        ### Comportamento Temporal

        **Períodos do Dia:**
        - Manhã: 6h às 12h
        - Tarde: 12h às 18h
        - Noite: 18h às 22h

        **Dias da Semana:**
        - Segunda a Domingo
        """)

    with tab3:
        st.markdown("""
        ## Personas de Clientes

        As personas foram identificadas através de **análise de cluster (K-Means)** considerando:
        - Valor total gasto
        - Frequência de compras
        - Ticket médio
        - Idade
        - Gênero

        ### 14 Personas Identificadas

        **HIGH SPENDERS (Top 10%):**
        | Persona | % Clientes | % Valor | Perfil |
        |---------|------------|---------|--------|
        | **Executiva Premium** | 3,2% | 16,7% | Mulheres 40-54, High Spender |
        | **Executivo Exigente** | 2,7% | 12,9% | Homens High Spender |
        | **Fashionista Premium** | 2,4% | 11,2% | Mulheres 25-39, High Spender |
        | **Senior VIP** | 1,7% | 8,9% | 55+ anos, High Spender |
        | **Cliente Premium** | 0,0% | 0,0% | High Spender (outros gêneros) |

        **CLIENTES REGULARES (baseados em segmento + comportamento):**
        | Persona | % Clientes | % Valor | Perfil |
        |---------|------------|---------|--------|
        | **Cliente Regular** | 37,1% | 15,4% | Perfil diverso, não categorizado |
        | **Mãe Moderna** | 9,3% | 8,0% | Mulheres 30-50 + Moda/Infantil/Calçados |
        | **Foodie** | 8,8% | 6,0% | Freq ≥3 + Gastronomia |
        | **Senior Tradicional** | 11,4% | 5,7% | 55+ anos |
        | **Comprador Seletivo** | 3,4% | 5,0% | Alto valor + baixa frequência |
        | **Jovem Engajado** | 4,3% | 3,5% | <30 anos + freq ≥5 |
        | **Jovem Explorer** | 10,5% | 3,1% | <30 anos |
        | **Beauty Lover** | 3,4% | 2,3% | Mulheres 25-55 + Beleza |
        | **Fitness** | 1,8% | 1,2% | Freq ≥3 + Esportes |

        ---

        ## High Spenders

        ### Definição
        Um cliente é **High Spender** se está no **percentil 90** de gastos do seu shopping.

        ### Cálculo
        ```python
        threshold = valor_por_cliente.quantile(0.90)
        high_spenders = clientes[valor >= threshold]
        ```

        ### Thresholds por Shopping

        | Shopping | Threshold |
        |----------|-----------|
        | CS | R$ 5.800 |
        | NK | R$ 5.177 |
        | NR | R$ 4.299 |
        | BS | R$ 4.000 |
        | GS | R$ 3.266 |
        | NS | R$ 3.129 |

        ### Comparação HS vs Demais

        | Métrica | High Spenders | Demais |
        |---------|---------------|--------|
        | % Clientes | 10% | 90% |
        | % Valor | 50% | 50% |
        | Ticket Médio | R$ 10.792 | R$ 1.209 |
        | Freq. Média | 26,1x | 4,3x |
        | % Feminino | 66,9% | 61,6% |
        """)

    with tab4:
        st.markdown("""
        ## Arquivos de Dados

        ### Dados Consolidados (Resultados/)

        | Arquivo | Descrição |
        |---------|-----------|
        | `resumo_por_shopping.csv` | Métricas consolidadas por shopping |
        | `personas_clientes.csv` | 9 personas identificadas |
        | `comparacao_high_spenders.csv` | HS vs Demais Clientes |
        | `high_spenders_por_genero.csv` | HS por gênero |
        | `high_spenders_por_faixa.csv` | HS por faixa etária |
        | `matriz_clientes_genero_idade.csv` | Matriz cruzada clientes |
        | `matriz_valor_genero_idade.csv` | Matriz cruzada valor |
        | `matriz_ticket_genero_idade.csv` | Matriz cruzada ticket |
        | `top_segmentos_por_genero.csv` | Top 5 segmentos/gênero |
        | `top_segmentos_por_faixa.csv` | Top segmentos/faixa |
        | `comportamento_periodo_dia.csv` | Dados por período |
        | `comportamento_dia_semana.csv` | Dados por dia |
        | `consolidado_genero_por_shopping.csv` | Gênero por shopping |
        | `consolidado_faixa_etaria_por_shopping.csv` | Faixa por shopping |

        ### Dados por Shopping (Resultados/Por_Shopping/{SIGLA}/)

        Cada shopping possui:
        - `perfil_genero.csv`
        - `perfil_faixa_etaria.csv`
        - `top_segmentos.csv`
        - `top_lojas.csv`
        - `comportamento_periodo.csv`
        - `comportamento_dia_semana.csv`
        - `high_spenders_stats.csv`
        - `lista_high_spenders.csv`
        - `base_clientes.csv`

        ### Tecnologias

        | Tecnologia | Uso |
        |------------|-----|
        | Python 3.11+ | Linguagem principal |
        | Streamlit 1.28+ | Framework web |
        | Plotly 5.18+ | Gráficos interativos |
        | Pandas 2.0+ | Manipulação de dados |
        """)

    with tab5:
        st.markdown("""
        ## Glossário de Termos

        | Termo | Definição |
        |-------|-----------|
        | **Ticket Médio** | Valor médio gasto por cliente (Valor Total / Clientes) |
        | **High Spender** | Cliente no top 10% de gastos do shopping |
        | **Threshold** | Valor mínimo para ser High Spender |
        | **Persona** | Perfil comportamental de cliente baseado em cluster |
        | **Frequência** | Número médio de compras por cliente |
        | **Segmento** | Categoria de produto/serviço da loja |
        | **Faixa Etária** | Agrupamento de clientes por idade |
        | **Gen Z** | Geração nascida entre 1997-2012 |
        | **Millennials** | Geração nascida entre 1981-1996 |
        | **Gen X** | Geração nascida entre 1965-1980 |
        | **Boomers** | Geração nascida entre 1946-1964 |
        | **Silent** | Geração nascida antes de 1946 |
        | **Matriz Cruzada** | Tabela que cruza duas dimensões (ex: gênero x idade) |
        | **Heatmap** | Mapa de calor visual para identificar padrões |
        | **Radar Chart** | Gráfico radar para comparar múltiplas métricas |

        ---

        ## Contato

        **Desenvolvido para:** Almeida Junior Shoppings

        **Repositório:** [github.com/carlosgravi/dashboard-perfil-cliente](https://github.com/carlosgravi/dashboard-perfil-cliente)

        ---

        *Documentação atualizada em Janeiro/2026*
        """)

# Footer
st.markdown("---")
footer_periodo = ' vs '.join(periodos_selecionados) if modo_comparativo else periodo_selecionado
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <p>Dashboard de Perfil de Cliente - Almeida Junior Shoppings</p>
    <p>{'Comparando: ' if modo_comparativo else 'Período: '}{footer_periodo}</p>
</div>
""", unsafe_allow_html=True)
