"""
DASHBOARD - PERFIL DE CLIENTE POR SHOPPING
Visualização interativa dos dados de perfil de cliente
Atualizado em: 2026-01-27 - Adicionado controle de acesso
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
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

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

# =============================================================================
# SISTEMA DE AUTENTICAÇÃO
# =============================================================================

def converter_para_dict(obj):
    """Converte recursivamente objetos AttrDict do Streamlit para dict Python padrão"""
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, 'items'):
        return {k: converter_para_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [converter_para_dict(item) for item in obj]
    else:
        return obj

def carregar_config_auth():
    """Carrega configuração de autenticação dos secrets do Streamlit"""
    try:
        # Tentar carregar dos secrets do Streamlit Cloud
        if "credentials" in st.secrets:
            # Converter todos os objetos para dict Python padrão recursivamente
            credentials = converter_para_dict(st.secrets['credentials'])
            cookie = converter_para_dict(st.secrets['cookie'])

            config = {
                'credentials': credentials,
                'cookie': cookie
            }

            return config
        else:
            # Configuração padrão para desenvolvimento local
            return None
    except Exception as e:
        st.error(f"Erro ao carregar configuração: {e}")
        return None

def verificar_autenticacao():
    """Verifica se o usuário está autenticado"""
    config = carregar_config_auth()

    if config is None:
        # Modo desenvolvimento - sem autenticação
        st.warning("⚠️ Modo desenvolvimento - Autenticação desabilitada")
        return True, "dev_user", "Desenvolvedor", "admin"

    # Criar autenticador (API v0.3+)
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Armazenar authenticator na sessão para logout
    st.session_state['authenticator'] = authenticator
    st.session_state['config'] = config

    # Tela de login (API v0.3+)
    authenticator.login()

    # Verificar status de autenticação
    if st.session_state.get('authentication_status') == False:
        st.error('❌ Usuário ou senha incorretos')
        return False, None, None, None
    elif st.session_state.get('authentication_status') == None:
        st.info('👋 Por favor, faça login para acessar o dashboard')

        # Mostrar informações de contato para solicitar acesso
        st.markdown("---")
        st.markdown("""
        ### 🔐 Acesso Restrito

        Este dashboard é de uso exclusivo da equipe Almeida Junior.

        **Para solicitar acesso, entre em contato:**
        - 📧 Email: carlos.gravi@almeidajunior.com.br
        - 📱 WhatsApp: (48) 98472-8399
        """)
        return False, None, None, None
    else:
        # Usuário autenticado - obter dados da sessão
        username = st.session_state.get('username')
        name = st.session_state.get('name')

        # Obter role do usuário
        user_role = config['credentials']['usernames'][username].get('role', 'viewer')
        st.session_state['role'] = user_role

        return True, username, name, user_role

def mostrar_logout():
    """Mostra botão de logout na sidebar"""
    if 'authenticator' in st.session_state:
        st.session_state['authenticator'].logout('Sair', 'sidebar', key='logout_btn')

def get_user_role():
    """Retorna o papel do usuário atual"""
    return st.session_state.get('role', 'viewer')

def is_admin():
    """Verifica se o usuário é administrador"""
    return get_user_role() == 'admin'

# Verificar autenticação
autenticado, username, nome_usuario, user_role = verificar_autenticacao()

if not autenticado:
    st.stop()

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

    /* Botão de logout na sidebar - apenas botões de formulário, não os de controle */
    section[data-testid="stSidebar"] .stButton > button {
        background-color: #E74C3C !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #C0392B !important;
    }

    /* Botão de recolher/expandir sidebar - forçar visibilidade */
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarNav"] button,
    .stSidebar button[kind="header"],
    div[data-testid="stSidebarCollapsedControl"] button,
    section[data-testid="stSidebar"] > div:first-child button {
        background-color: #2C3E50 !important;
        color: #FFFFFF !important;
        border: 1px solid #B0C4DE !important;
        border-radius: 4px !important;
        opacity: 1 !important;
        visibility: visible !important;
    }

    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    section[data-testid="stSidebar"] > div:first-child button svg {
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
        color: #FFFFFF !important;
    }

    /* Garantir que o ícone do botão collapse seja visível */
    button[kind="header"] svg,
    .stAppHeader button svg {
        fill: #1E3A5F !important;
        color: #1E3A5F !important;
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

    # Dados RFV (se existirem para este período)
    rfv_path = f'{base_path}/RFV'
    if os.path.exists(rfv_path):
        try:
            dados['rfv'] = {
                'perfil_historico': pd.read_csv(f'{rfv_path}/metricas_perfil_historico.csv'),
                'perfil_periodo': pd.read_csv(f'{rfv_path}/metricas_perfil_periodo.csv'),
                'shopping': pd.read_csv(f'{rfv_path}/metricas_shopping_rfv.csv'),
            }
            # Arquivos opcionais
            seg_path = f'{rfv_path}/TOP10_SEGMENTOS_POR_PERFIL_SHOPPING.csv'
            if os.path.exists(seg_path):
                dados['rfv']['seg_perfil_shop'] = pd.read_csv(seg_path)
            lojas_path = f'{rfv_path}/TOP10_LOJAS_POR_GENERO_SHOPPING_PERFIL.csv'
            if os.path.exists(lojas_path):
                dados['rfv']['lojas'] = pd.read_csv(lojas_path, sep=';', decimal=',')
            resumo_path = f'{rfv_path}/resumo_rfv.csv'
            if os.path.exists(resumo_path):
                dados['rfv']['resumo'] = pd.read_csv(resumo_path)

            # =============================================
            # NOVO: Dados RFV por Quintis
            # =============================================
            dados['rfv_quintis'] = {}

            # Dados de clientes com scores - Escopo Global
            quintis_global_path = f'{rfv_path}/rfv_quintis_global.csv'
            if os.path.exists(quintis_global_path):
                dados['rfv_quintis']['clientes_global'] = pd.read_csv(quintis_global_path)

            # Dados de clientes com scores - Escopo Por Shopping
            quintis_shopping_path = f'{rfv_path}/rfv_quintis_por_shopping.csv'
            if os.path.exists(quintis_shopping_path):
                dados['rfv_quintis']['clientes_shopping'] = pd.read_csv(quintis_shopping_path)

            # Métricas agregadas por perfil - Global
            perfil_quintis_global_path = f'{rfv_path}/metricas_perfil_quintis_global.csv'
            if os.path.exists(perfil_quintis_global_path):
                dados['rfv_quintis']['perfil_global'] = pd.read_csv(perfil_quintis_global_path)

            # Métricas agregadas por perfil - Por Shopping
            perfil_quintis_shopping_path = f'{rfv_path}/metricas_perfil_quintis_shopping.csv'
            if os.path.exists(perfil_quintis_shopping_path):
                dados['rfv_quintis']['perfil_shopping'] = pd.read_csv(perfil_quintis_shopping_path)

            # Métricas por shopping - Escopo Global
            shopping_quintis_global_path = f'{rfv_path}/metricas_shopping_quintis_global.csv'
            if os.path.exists(shopping_quintis_global_path):
                dados['rfv_quintis']['shopping_global'] = pd.read_csv(shopping_quintis_global_path)

            # Métricas por shopping - Escopo Por Shopping
            shopping_quintis_shopping_path = f'{rfv_path}/metricas_shopping_quintis_shopping.csv'
            if os.path.exists(shopping_quintis_shopping_path):
                dados['rfv_quintis']['shopping_shopping'] = pd.read_csv(shopping_quintis_shopping_path)

            # Thresholds dos quintis para referência
            thresholds_global_path = f'{rfv_path}/quintile_thresholds_global.csv'
            if os.path.exists(thresholds_global_path):
                dados['rfv_quintis']['thresholds_global'] = pd.read_csv(thresholds_global_path)

            thresholds_shopping_path = f'{rfv_path}/quintile_thresholds_shopping.csv'
            if os.path.exists(thresholds_shopping_path):
                dados['rfv_quintis']['thresholds_shopping'] = pd.read_csv(thresholds_shopping_path)

            # Verificar se há dados de quintis disponíveis
            if not dados['rfv_quintis']:
                dados['rfv_quintis'] = None

        except Exception as e:
            dados['rfv'] = None
            dados['rfv_quintis'] = None
    else:
        dados['rfv'] = None
        dados['rfv_quintis'] = None

    return dados

# Sidebar
# Logo - carrega GIF
logo_file = "AJ-AJFANS V2 - GIF.gif"
if os.path.exists(logo_file):
    st.sidebar.image(logo_file, use_container_width=True)

st.sidebar.title("🛍️ Almeida Junior")
st.sidebar.markdown("**Dashboard Perfil de Cliente**")

# Informações do usuário logado
st.sidebar.markdown("---")
st.sidebar.markdown(f"👤 **{nome_usuario}**")
role_display = "Administrador" if user_role == "admin" else "Visualizador"
st.sidebar.caption(f"Perfil: {role_display}")

# Botão de logout
mostrar_logout()

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

# Menu de navegação - Admin tem opções extras
opcoes_menu = ["📊 Visão Geral", "🎭 Personas", "🏬 Por Shopping", "👥 Perfil Demográfico",
               "⭐ High Spenders", "🏆 Top Consumidores", "🛒 Segmentos", "🎯 RFV", "⏰ Comportamento", "📈 Comparativo",
               "📥 Exportar Dados", "🤖 Assistente", "📚 Documentação"]

# Adicionar opção de administração apenas para admins
if is_admin():
    opcoes_menu.append("⚙️ Administração")

pagina = st.sidebar.radio(
    "Selecione a visão:",
    opcoes_menu
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
    As **14 Personas** representam perfis comportamentais de clientes, classificados por regras baseadas em
    gênero, faixa etária, nível de gasto (High Spender ou não) e frequência de compras.
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
# PÁGINA: TOP CONSUMIDORES
# ============================================================================
elif pagina == "🏆 Top Consumidores":
    st.markdown('<p class="main-header">🏆 Top 150 Consumidores por Shopping</p>', unsafe_allow_html=True)

    st.markdown("""
    Lista dos **150 maiores consumidores** de cada shopping, ordenados por valor total de compras.
    Inclui dados de contato, métricas RFV e informações de comportamento de compra.

    **Nota:** Colaboradores dos shoppings foram excluídos desta lista.
    """)

    # Carregar arquivo de top consumidores
    arquivo_top = 'Resultados/top_consumidores_rfv.csv'

    if os.path.exists(arquivo_top):
        df_top = pd.read_csv(arquivo_top, sep=';', decimal=',', encoding='utf-8-sig')

        # Métricas gerais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total na Lista", f"{len(df_top):,}")
        with col2:
            st.metric("Shoppings", f"{df_top['Shopping'].nunique()}")
        with col3:
            st.metric("Valor Total", f"R$ {df_top['Valor_Total'].sum()/1e6:.1f}M")
        with col4:
            pct_vip = len(df_top[df_top['Perfil_Cliente'] == 'VIP']) / len(df_top) * 100
            st.metric("% VIP", f"{pct_vip:.1f}%")

        st.markdown("---")

        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            shopping_filtro = st.selectbox(
                "Filtrar por Shopping:",
                ["Todos"] + sorted(df_top['Shopping'].unique().tolist()),
                key="top_shopping_filtro"
            )
        with col2:
            perfil_filtro = st.selectbox(
                "Filtrar por Perfil:",
                ["Todos"] + sorted(df_top['Perfil_Cliente'].unique().tolist()),
                key="top_perfil_filtro"
            )
        with col3:
            segmento_filtro = st.selectbox(
                "Filtrar por Segmento:",
                ["Todos"] + sorted(df_top['Segmento_Principal'].dropna().unique().tolist()),
                key="top_segmento_filtro"
            )

        # Aplicar filtros
        df_filtrado = df_top.copy()
        if shopping_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Shopping'] == shopping_filtro]
        if perfil_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Perfil_Cliente'] == perfil_filtro]
        if segmento_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Segmento_Principal'] == segmento_filtro]

        st.markdown(f"**Exibindo {len(df_filtrado):,} clientes**")

        # Colunas para exibição
        colunas_exibir = [
            'Ranking', 'Shopping', 'Nome', 'Logradouro', 'Numero', 'Complemento', 'Bairro',
            'Cidade', 'Estado', 'CEP', 'Valor_Total', 'Frequencia_Compras',
            'Perfil_Cliente', 'Segmento_Principal', 'Loja_Favorita',
            'Data_Primeira_Compra', 'Data_Ultima_Compra'
        ]

        # Exibir tabela
        st.dataframe(
            df_filtrado[colunas_exibir],
            use_container_width=True,
            hide_index=True,
            height=500
        )

        st.markdown("---")

        # Botão de download
        @st.cache_data
        def converter_para_csv_top(df):
            return df.to_csv(index=False, encoding='utf-8-sig', sep=';', decimal=',').encode('utf-8-sig')

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="⬇️ Baixar Lista Filtrada (CSV)",
                data=converter_para_csv_top(df_filtrado),
                file_name="top_consumidores_filtrado.csv",
                mime="text/csv",
                help="Download da lista com os filtros aplicados"
            )

        with col2:
            st.download_button(
                label="⬇️ Baixar Lista Completa (CSV)",
                data=converter_para_csv_top(df_top),
                file_name="top_consumidores_completo.csv",
                mime="text/csv",
                help="Download da lista completa (900 clientes)"
            )

        # Análises adicionais
        st.markdown("---")
        st.subheader("📊 Análises")

        tab1, tab2, tab3 = st.tabs(["Por Shopping", "Por Perfil", "Por Segmento"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                # Valor por shopping
                df_shop = df_top.groupby('Shopping').agg({
                    'Valor_Total': 'sum',
                    'Cliente_ID': 'count'
                }).reset_index()
                df_shop.columns = ['Shopping', 'Valor_Total', 'Qtd_Clientes']

                fig = px.bar(
                    df_shop.sort_values('Valor_Total', ascending=True),
                    x='Valor_Total',
                    y='Shopping',
                    orientation='h',
                    title='Valor Total por Shopping',
                    text=df_shop.sort_values('Valor_Total', ascending=True)['Valor_Total'].apply(lambda x: f'R$ {x/1e6:.1f}M')
                )
                fig.update_layout(showlegend=False, height=400)
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Top 10 geral
                df_top10 = df_top.nlargest(10, 'Valor_Total')
                fig = px.bar(
                    df_top10,
                    x='Valor_Total',
                    y='Nome',
                    orientation='h',
                    color='Shopping',
                    title='Top 10 Consumidores (Geral)',
                    text=df_top10['Valor_Total'].apply(lambda x: f'R$ {x/1e3:.0f}K')
                )
                fig.update_layout(height=400, yaxis={'categoryorder': 'total ascending'})
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                # Distribuição por perfil
                df_perfil = df_top['Perfil_Cliente'].value_counts().reset_index()
                df_perfil.columns = ['Perfil', 'Quantidade']
                fig = px.pie(
                    df_perfil,
                    values='Quantidade',
                    names='Perfil',
                    title='Distribuição por Perfil RFV',
                    color='Perfil',
                    color_discrete_map={'VIP': '#FFD700', 'Premium': '#C0C0C0', 'Potencial': '#CD7F32', 'Pontual': '#808080'}
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Valor médio por perfil
                df_perfil_valor = df_top.groupby('Perfil_Cliente')['Valor_Total'].mean().reset_index()
                df_perfil_valor.columns = ['Perfil', 'Valor_Medio']
                fig = px.bar(
                    df_perfil_valor.sort_values('Valor_Medio', ascending=True),
                    x='Valor_Medio',
                    y='Perfil',
                    orientation='h',
                    title='Valor Médio por Perfil',
                    text=df_perfil_valor.sort_values('Valor_Medio', ascending=True)['Valor_Medio'].apply(lambda x: f'R$ {x/1e3:.0f}K')
                )
                fig.update_layout(showlegend=False, height=400)
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

        with tab3:
            # Top segmentos
            df_seg = df_top.groupby('Segmento_Principal').agg({
                'Valor_Total': 'sum',
                'Cliente_ID': 'count'
            }).reset_index()
            df_seg.columns = ['Segmento', 'Valor_Total', 'Qtd_Clientes']
            df_seg = df_seg.nlargest(10, 'Valor_Total')

            fig = px.bar(
                df_seg.sort_values('Valor_Total', ascending=True),
                x='Valor_Total',
                y='Segmento',
                orientation='h',
                title='Top 10 Segmentos (por Valor)',
                text=df_seg.sort_values('Valor_Total', ascending=True)['Valor_Total'].apply(lambda x: f'R$ {x/1e6:.1f}M')
            )
            fig.update_layout(showlegend=False, height=450)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.error(f"Arquivo de top consumidores não encontrado: {arquivo_top}")
        st.info("Execute o script `gerar_top_consumidores_rfv.py` para gerar a lista.")

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
            df_seg_faixa = pd.read_csv('Resultados/top_segmentos_por_faixa.csv')

            # Usar as faixas existentes no arquivo
            ordem_faixas = ['16-24 (Gen Z)', '25-39 (Millennials)', '40-54 (Gen X)', '55-69 (Boomers)', '70+ (Silent)']

            # Cores para cada faixa
            cores_faixas = {
                '16-24 (Gen Z)': 'Purples',
                '25-39 (Millennials)': 'Blues',
                '40-54 (Gen X)': 'Greens',
                '55-69 (Boomers)': 'Oranges',
                '70+ (Silent)': 'Reds'
            }

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
                        color_continuous_scale=cores_faixas.get(faixa, 'Oranges'),
                        text=df_f['valor'].apply(lambda x: f'R$ {x/1e6:.1f}M')
                    )
                    fig.update_layout(height=200, showlegend=False, yaxis={'categoryorder': 'total ascending'})
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info(f"Dados de segmentos por faixa etária não disponíveis. Erro: {e}")

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
# PÁGINA: RFV (Recência, Frequência, Valor)
# ============================================================================
elif pagina == "🎯 RFV":
    st.markdown('<p class="main-header">🎯 Análise RFV - Recência, Frequência e Valor</p>', unsafe_allow_html=True)

    # Mostrar período selecionado
    if modo_comparativo:
        st.markdown(f"**Comparando:** {' vs '.join(periodos_selecionados)}")
    else:
        st.markdown(f"**Período selecionado:** {periodo_selecionado}")

    # =========================================================================
    # TOGGLE PRINCIPAL: MÉTODO DE CLASSIFICAÇÃO
    # =========================================================================
    st.markdown("### Método de Classificação")

    # Verificar se dados de quintis estão disponíveis
    tem_quintis = dados.get('rfv_quintis') is not None and len(dados.get('rfv_quintis', {})) > 0

    col_metodo1, col_metodo2 = st.columns([3, 1])
    with col_metodo1:
        metodo_rfv = st.radio(
            "Selecione o método:",
            ["Por Valor (R$)", "Por Quintis (R+F+V)"],
            horizontal=True,
            help="""
            **Por Valor (R$):** Classificação baseada em thresholds fixos de valor em reais.
            **Por Quintis (R+F+V):** Classificação baseada na soma de scores de Recência, Frequência e Valor (cada um de 1-5).
            """,
            key='rfv_metodo_principal'
        )

    usar_quintis = metodo_rfv == "Por Quintis (R+F+V)"

    # Toggle de escopo (apenas para método Quintis)
    escopo_quintis = "Global"
    if usar_quintis:
        with col_metodo2:
            escopo_quintis = st.radio(
                "Escopo:",
                ["Global", "Por Shopping"],
                horizontal=False,
                help="""
                **Global:** Quintis calculados sobre todos os clientes (comparação justa entre shoppings).
                **Por Shopping:** Quintis calculados dentro de cada shopping (cada shopping tem seus "melhores").
                """,
                key='rfv_escopo_quintis'
            )

    # Descrição dinâmica do método
    if usar_quintis:
        if not tem_quintis:
            st.warning("⚠️ Dados de Quintis não disponíveis para este período. Execute o script `gerar_rfv_por_periodo.py` para gerar os dados. Usando método Por Valor.")
            usar_quintis = False
        else:
            st.markdown(f"""
            **Método selecionado: Por Quintis ({escopo_quintis})**

            Cada cliente recebe scores de 1-5 em cada dimensão (R, F, V):
            - **Recência (R):** Score 5 = comprou recentemente, Score 1 = não compra há muito tempo
            - **Frequência (F):** Score 5 = muitas compras, Score 1 = poucas compras
            - **Valor (V):** Score 5 = alto valor gasto, Score 1 = baixo valor gasto

            | Score Total (R+F+V) | Perfil | Descrição |
            |---------------------|--------|-----------|
            | 13 a 15 | **VIP** | Excelente em todas as dimensões |
            | 10 a 12 | **Premium** | Bom desempenho geral |
            | 7 a 9 | **Potencial** | Médio, com espaço para crescer |
            | 3 a 6 | **Pontual** | Baixo engajamento |
            """)

    if not usar_quintis:
        st.markdown("""
        **Método selecionado: Por Valor (R$)**

        Classificação baseada em **thresholds fixos** de valor:
        - **Classificação Histórica:** baseada no valor total acumulado do cliente
        - **Classificação por Período:** baseada no valor gasto no período selecionado

        As métricas de Recência e Frequência são calculadas, mas a segmentação usa apenas o Valor.
        """)

    # Constantes de configuração
    CORES_PERFIL = {
        'VIP': '#9B59B6',
        'Premium': '#3498DB',
        'Potencial': '#2ECC71',
        'Pontual': '#95A5A6'
    }
    ORDEM_PERFIL = ['VIP', 'Premium', 'Potencial', 'Pontual']

    # Verificar se há dados RFV disponíveis
    dados_rfv_disponivel = dados.get('rfv') is not None

    if not dados_rfv_disponivel and not modo_comparativo:
        st.warning("⚠️ Dados RFV não encontrados para este período. Execute o script `gerar_rfv_por_periodo.py` para gerar os dados.")
        st.stop()

    # Modo comparativo
    if modo_comparativo:
        # Verificar quais períodos têm dados RFV
        periodos_com_rfv = {nome: dados_periodos[nome].get('rfv') for nome in periodos_selecionados if dados_periodos[nome].get('rfv') is not None}

        if len(periodos_com_rfv) == 0:
            st.warning("⚠️ Nenhum dos períodos selecionados possui dados RFV. Execute o script `gerar_rfv_por_periodo.py` para gerar os dados.")
            st.stop()

        if len(periodos_com_rfv) < len(periodos_selecionados):
            st.info(f"ℹ️ Mostrando dados RFV de {len(periodos_com_rfv)} de {len(periodos_selecionados)} períodos selecionados.")

        # Toggle para tipo de classificação
        tipo_rfv = st.radio(
            "Tipo de Classificação:",
            ["Histórica (Valor Total)", "Por Período (Valor do Período)"],
            horizontal=True,
            key='rfv_tipo_comparativo'
        )
        usar_historico = tipo_rfv == "Histórica (Valor Total)"

        st.subheader("Comparação de Perfis RFV entre Períodos")

        # Coletar dados de todos os períodos
        dados_comparacao = []
        for nome_periodo, rfv_data in periodos_com_rfv.items():
            df_perfil = rfv_data['perfil_historico' if usar_historico else 'perfil_periodo'].copy()
            df_perfil['periodo'] = nome_periodo
            dados_comparacao.append(df_perfil)

        df_comparacao = pd.concat(dados_comparacao, ignore_index=True)

        # Gráfico comparativo de clientes por perfil
        col1, col2 = st.columns(2)

        with col1:
            fig_comp_cli = px.bar(
                df_comparacao,
                x='perfil_cliente',
                y='qtd_clientes',
                color='periodo',
                barmode='group',
                title='Clientes por Perfil - Comparativo',
                color_discrete_sequence=px.colors.qualitative.Set2,
                category_orders={'perfil_cliente': ORDEM_PERFIL}
            )
            fig_comp_cli.update_layout(xaxis_title='Perfil', yaxis_title='Clientes')
            st.plotly_chart(fig_comp_cli, use_container_width=True)

        with col2:
            fig_comp_valor = px.bar(
                df_comparacao,
                x='perfil_cliente',
                y='valor_total',
                color='periodo',
                barmode='group',
                title='Valor por Perfil - Comparativo',
                color_discrete_sequence=px.colors.qualitative.Set2,
                category_orders={'perfil_cliente': ORDEM_PERFIL}
            )
            fig_comp_valor.update_layout(xaxis_title='Perfil', yaxis_title='Valor (R$)')
            st.plotly_chart(fig_comp_valor, use_container_width=True)

        # Tabela comparativa
        st.subheader("Tabela Comparativa")
        df_pivot = df_comparacao.pivot_table(
            values=['qtd_clientes', 'valor_total', 'pct_valor'],
            index='perfil_cliente',
            columns='periodo',
            aggfunc='sum'
        ).round(2)

        # Reordenar índice
        df_pivot = df_pivot.reindex(ORDEM_PERFIL)
        st.dataframe(df_pivot, use_container_width=True)

        # Evolução de VIPs
        st.subheader("Evolução de Clientes VIP")
        vips_por_periodo = df_comparacao[df_comparacao['perfil_cliente'] == 'VIP'][['periodo', 'qtd_clientes', 'valor_total']].copy()
        vips_por_periodo['ticket_medio'] = vips_por_periodo['valor_total'] / vips_por_periodo['qtd_clientes']

        col1, col2, col3 = st.columns(3)
        for i, (_, row) in enumerate(vips_por_periodo.iterrows()):
            with [col1, col2, col3][i % 3]:
                st.metric(
                    f"🏆 VIP - {row['periodo']}",
                    f"{int(row['qtd_clientes']):,}",
                    f"Ticket: R$ {row['ticket_medio']:,.2f}"
                )

    else:
        # Modo período único
        dados_rfv = dados['rfv']
        dados_rfv_quintis = dados.get('rfv_quintis')

        # =====================================================================
        # LÓGICA PARA SELECIONAR DADOS CONFORME MÉTODO
        # =====================================================================
        if usar_quintis and dados_rfv_quintis:
            # MÉTODO POR QUINTIS
            # Selecionar dados conforme escopo
            if escopo_quintis == "Global":
                df_perfil = dados_rfv_quintis.get('perfil_global', pd.DataFrame()).copy()
                df_shopping_quintis = dados_rfv_quintis.get('shopping_global', pd.DataFrame())
                df_clientes_quintis = dados_rfv_quintis.get('clientes_global', pd.DataFrame())
            else:
                df_perfil = dados_rfv_quintis.get('perfil_shopping', pd.DataFrame()).copy()
                df_shopping_quintis = dados_rfv_quintis.get('shopping_shopping', pd.DataFrame())
                df_clientes_quintis = dados_rfv_quintis.get('clientes_shopping', pd.DataFrame())

            # Usar tipo_rfv_label para exibição
            tipo_rfv_label = f"Quintis ({escopo_quintis})"
            # Definir usar_historico como False para quintis (não aplicável)
            usar_historico = False

            if df_perfil.empty:
                st.warning("⚠️ Dados de quintis não disponíveis. Usando método Por Valor.")
                usar_quintis = False

        if not usar_quintis:
            # MÉTODO POR VALOR (existente)
            # Toggle para tipo de classificação (Histórica vs Período)
            tipo_rfv = st.radio(
                "Tipo de Classificação:",
                ["Histórica (Valor Total)", "Por Período (Valor do Período)"],
                horizontal=True,
                help="**Histórica:** classifica pelo valor total acumulado do cliente. **Por Período:** classifica pelo valor gasto no período selecionado.",
                key='rfv_tipo_unico'
            )
            usar_historico = tipo_rfv == "Histórica (Valor Total)"

            # Selecionar dados conforme tipo
            df_perfil = dados_rfv['perfil_historico' if usar_historico else 'perfil_periodo'].copy()
            tipo_rfv_label = tipo_rfv.split(' (')[0]

        # Garantir ordenação correta
        df_perfil['ordem'] = df_perfil['perfil_cliente'].map({p: i for i, p in enumerate(ORDEM_PERFIL)})
        df_perfil = df_perfil.sort_values('ordem')

        # Tabs principais - adicionar tab de Scores se usando quintis
        if usar_quintis:
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Visão Geral", "📈 Scores R/F/V", "🏬 Por Shopping", "🛒 Segmentos & Lojas", "📋 Resumo"])
        else:
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "🏬 Por Shopping", "🛒 Segmentos & Lojas", "📋 Resumo"])

        with tab1:
            # Filtro de shopping
            shoppings_disponiveis = ["Todos"]
            # Usar dados de shopping conforme método
            if usar_quintis and 'df_shopping_quintis' in dir() and not df_shopping_quintis.empty:
                shoppings_disponiveis += list(df_shopping_quintis['shopping_principal'].unique())
                df_shop_vg = df_shopping_quintis
                sufixo_vg = '_quintis'
            elif 'shopping' in dados_rfv and dados_rfv['shopping'] is not None:
                shoppings_disponiveis += list(dados_rfv['shopping']['shopping_principal'].unique())
                df_shop_vg = dados_rfv['shopping']
                sufixo_vg = '_hist' if usar_historico else '_periodo'
            else:
                df_shop_vg = None
                sufixo_vg = '_hist'

            shopping_visao = st.selectbox(
                "Filtrar por Shopping:",
                shoppings_disponiveis,
                key='rfv_shopping_visao_geral'
            )

            # Montar dados de perfil conforme filtro de shopping
            if shopping_visao != "Todos" and df_shop_vg is not None:
                row_shop = df_shop_vg[df_shop_vg['shopping_principal'] == shopping_visao]

                if not row_shop.empty:
                    row = row_shop.iloc[0]
                    dados_perfil_list = []
                    for perfil in ORDEM_PERFIL:
                        p = perfil.lower()
                        qtd = int(row.get(f'{p}{sufixo_vg}', 0))
                        valor = float(row.get(f'{p}_valor{sufixo_vg}', 0))
                        ticket = valor / qtd if qtd > 0 else 0
                        dados_perfil_list.append({
                            'perfil_cliente': perfil,
                            'qtd_clientes': qtd,
                            'valor_total': valor,
                            'ticket_medio': ticket
                        })
                    df_perfil_filtrado = pd.DataFrame(dados_perfil_list)
                    total_cli = df_perfil_filtrado['qtd_clientes'].sum()
                    total_val = df_perfil_filtrado['valor_total'].sum()
                    df_perfil_filtrado['pct_clientes'] = (df_perfil_filtrado['qtd_clientes'] / total_cli * 100).round(2) if total_cli > 0 else 0
                    df_perfil_filtrado['pct_valor'] = (df_perfil_filtrado['valor_total'] / total_val * 100).round(2) if total_val > 0 else 0
                else:
                    df_perfil_filtrado = df_perfil.copy()

                st.subheader(f"Distribuição por Perfil - {shopping_visao} ({tipo_rfv_label})")
            else:
                df_perfil_filtrado = df_perfil.copy()
                st.subheader(f"Distribuição por Perfil de Cliente ({tipo_rfv_label})")

            # KPIs
            col1, col2, col3, col4 = st.columns(4)
            for i, perfil in enumerate(ORDEM_PERFIL):
                dados_p = df_perfil_filtrado[df_perfil_filtrado['perfil_cliente'] == perfil]
                if not dados_p.empty:
                    qtd = int(dados_p['qtd_clientes'].values[0])
                    pct_valor = dados_p['pct_valor'].values[0] if isinstance(dados_p['pct_valor'].values[0], (int, float)) else 0
                    with [col1, col2, col3, col4][i]:
                        icone = "🏆" if perfil == 'VIP' else "⭐" if perfil == 'Premium' else "🎯" if perfil == 'Potencial' else "👤"
                        st.metric(
                            f"{icone} {perfil}",
                            f"{qtd:,}",
                            f"{pct_valor:.1f}% do valor"
                        )

            col1, col2 = st.columns(2)

            with col1:
                # Gráfico de pizza - distribuição de clientes
                fig_pizza = px.pie(
                    df_perfil_filtrado,
                    values='qtd_clientes',
                    names='perfil_cliente',
                    title='Distribuição de Clientes por Perfil',
                    color='perfil_cliente',
                    color_discrete_map=CORES_PERFIL,
                    hole=0.4,
                    category_orders={'perfil_cliente': ORDEM_PERFIL}
                )
                fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pizza, use_container_width=True)

            with col2:
                # Gráfico de pizza - distribuição de valor
                fig_valor = px.pie(
                    df_perfil_filtrado,
                    values='valor_total',
                    names='perfil_cliente',
                    title='Distribuição de Valor por Perfil',
                    color='perfil_cliente',
                    color_discrete_map=CORES_PERFIL,
                    hole=0.4,
                    category_orders={'perfil_cliente': ORDEM_PERFIL}
                )
                fig_valor.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_valor, use_container_width=True)

            # Tabela resumo
            st.subheader("Resumo por Perfil")
            df_resumo = df_perfil_filtrado[['perfil_cliente', 'qtd_clientes', 'valor_total', 'ticket_medio', 'pct_clientes', 'pct_valor']].copy()
            df_resumo.columns = ['Perfil', 'Clientes', 'Valor Total', 'Ticket Médio', '% Clientes', '% Valor']
            df_resumo['Valor Total'] = df_resumo['Valor Total'].apply(lambda x: f"R$ {x:,.2f}")
            df_resumo['Ticket Médio'] = df_resumo['Ticket Médio'].apply(lambda x: f"R$ {x:,.2f}")
            df_resumo['% Clientes'] = df_resumo['% Clientes'].apply(lambda x: f"{x:.1f}%")
            df_resumo['% Valor'] = df_resumo['% Valor'].apply(lambda x: f"{x:.1f}%")
            st.dataframe(df_resumo, use_container_width=True, hide_index=True)

            # Insight dinâmico
            vip_data = df_perfil_filtrado[df_perfil_filtrado['perfil_cliente'] == 'VIP']
            if not vip_data.empty:
                pct_cli_vip = vip_data['pct_clientes'].values[0] if isinstance(vip_data['pct_clientes'].values[0], (int, float)) else 0
                pct_val_vip = vip_data['pct_valor'].values[0] if isinstance(vip_data['pct_valor'].values[0], (int, float)) else 0
                label_shop = f" no **{shopping_visao}**" if shopping_visao != "Todos" else ""
                st.info(f"""
                💡 **Princípio de Pareto:** Os clientes **VIP**{label_shop} representam {pct_cli_vip:.1f}% da base,
                mas geram **{pct_val_vip:.1f}%** do faturamento. Investir na retenção desses clientes é fundamental.
                """)

        # =====================================================================
        # TAB SCORES R/F/V (apenas para método Quintis)
        # =====================================================================
        if usar_quintis:
            with tab2:
                st.subheader(f"📈 Distribuição de Scores R/F/V ({escopo_quintis})")

                if 'df_clientes_quintis' in dir() and not df_clientes_quintis.empty:
                    # Distribuição de scores por dimensão
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        # Histograma de Recência
                        fig_r = px.histogram(
                            df_clientes_quintis,
                            x='R_score',
                            nbins=5,
                            title='Distribuição Score Recência (R)',
                            color_discrete_sequence=['#E74C3C'],
                            labels={'R_score': 'Score R', 'count': 'Clientes'}
                        )
                        fig_r.update_layout(bargap=0.1, xaxis=dict(tickmode='linear', tick0=1, dtick=1))
                        st.plotly_chart(fig_r, use_container_width=True)

                        # Estatísticas R
                        r_stats = df_clientes_quintis['R_score'].describe()
                        st.caption(f"Média: {r_stats['mean']:.2f} | Mediana: {r_stats['50%']:.0f}")

                    with col2:
                        # Histograma de Frequência
                        fig_f = px.histogram(
                            df_clientes_quintis,
                            x='F_score',
                            nbins=5,
                            title='Distribuição Score Frequência (F)',
                            color_discrete_sequence=['#3498DB'],
                            labels={'F_score': 'Score F', 'count': 'Clientes'}
                        )
                        fig_f.update_layout(bargap=0.1, xaxis=dict(tickmode='linear', tick0=1, dtick=1))
                        st.plotly_chart(fig_f, use_container_width=True)

                        # Estatísticas F
                        f_stats = df_clientes_quintis['F_score'].describe()
                        st.caption(f"Média: {f_stats['mean']:.2f} | Mediana: {f_stats['50%']:.0f}")

                    with col3:
                        # Histograma de Valor
                        fig_v = px.histogram(
                            df_clientes_quintis,
                            x='V_score',
                            nbins=5,
                            title='Distribuição Score Valor (V)',
                            color_discrete_sequence=['#2ECC71'],
                            labels={'V_score': 'Score V', 'count': 'Clientes'}
                        )
                        fig_v.update_layout(bargap=0.1, xaxis=dict(tickmode='linear', tick0=1, dtick=1))
                        st.plotly_chart(fig_v, use_container_width=True)

                        # Estatísticas V
                        v_stats = df_clientes_quintis['V_score'].describe()
                        st.caption(f"Média: {v_stats['mean']:.2f} | Mediana: {v_stats['50%']:.0f}")

                    # Distribuição do Score Total
                    st.subheader("Distribuição do Score Total (R+F+V)")
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        fig_total = px.histogram(
                            df_clientes_quintis,
                            x='score_total',
                            nbins=13,
                            title='Distribuição do Score Total (3-15)',
                            color_discrete_sequence=['#9B59B6'],
                            labels={'score_total': 'Score Total', 'count': 'Clientes'}
                        )
                        # Adicionar linhas de corte dos perfis
                        fig_total.add_vline(x=6.5, line_dash="dash", line_color="gray", annotation_text="Pontual/Potencial")
                        fig_total.add_vline(x=9.5, line_dash="dash", line_color="gray", annotation_text="Potencial/Premium")
                        fig_total.add_vline(x=12.5, line_dash="dash", line_color="gray", annotation_text="Premium/VIP")
                        fig_total.update_layout(bargap=0.1, xaxis=dict(tickmode='linear', tick0=3, dtick=1))
                        st.plotly_chart(fig_total, use_container_width=True)

                    with col2:
                        # Contagem por faixa de score
                        st.markdown("**Distribuição por Faixa:**")
                        faixas = {
                            '3-6 (Pontual)': len(df_clientes_quintis[df_clientes_quintis['score_total'] <= 6]),
                            '7-9 (Potencial)': len(df_clientes_quintis[(df_clientes_quintis['score_total'] >= 7) & (df_clientes_quintis['score_total'] <= 9)]),
                            '10-12 (Premium)': len(df_clientes_quintis[(df_clientes_quintis['score_total'] >= 10) & (df_clientes_quintis['score_total'] <= 12)]),
                            '13-15 (VIP)': len(df_clientes_quintis[df_clientes_quintis['score_total'] >= 13])
                        }
                        total = sum(faixas.values())
                        for faixa, qtd in faixas.items():
                            pct = (qtd / total * 100) if total > 0 else 0
                            st.markdown(f"- **{faixa}:** {qtd:,} ({pct:.1f}%)")

                    # Radar Chart - Scores médios por Perfil
                    st.subheader("Radar Chart - Scores Médios por Perfil")

                    # Calcular médias por perfil
                    medias_perfil = df_clientes_quintis.groupby('perfil_quintis').agg({
                        'R_score': 'mean',
                        'F_score': 'mean',
                        'V_score': 'mean'
                    }).reset_index()

                    # Criar radar chart
                    fig_radar = go.Figure()

                    cores_radar = {'VIP': '#9B59B6', 'Premium': '#3498DB', 'Potencial': '#2ECC71', 'Pontual': '#95A5A6'}

                    for _, row in medias_perfil.iterrows():
                        perfil = row['perfil_quintis']
                        fig_radar.add_trace(go.Scatterpolar(
                            r=[row['R_score'], row['F_score'], row['V_score'], row['R_score']],
                            theta=['Recência (R)', 'Frequência (F)', 'Valor (V)', 'Recência (R)'],
                            fill='toself',
                            name=perfil,
                            line_color=cores_radar.get(perfil, '#888888'),
                            opacity=0.7
                        ))

                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 5])
                        ),
                        showlegend=True,
                        title='Comparação de Scores Médios entre Perfis'
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

                    st.info("""
                    💡 **Interpretação do Radar Chart:**
                    - Perfis **VIP** devem ter scores altos em todas as dimensões (área maior)
                    - Perfis **Pontual** têm scores baixos em geral (área menor)
                    - Perfis **desequilibrados** (ex: alto em V, baixo em R) indicam oportunidades de ação
                    """)

                    # Tabela com scores detalhados
                    st.subheader("Tabela de Scores por Perfil")
                    df_scores_tabela = medias_perfil.copy()
                    df_scores_tabela.columns = ['Perfil', 'R Médio', 'F Médio', 'V Médio']
                    df_scores_tabela['Score Total Médio'] = df_scores_tabela['R Médio'] + df_scores_tabela['F Médio'] + df_scores_tabela['V Médio']
                    df_scores_tabela = df_scores_tabela.round(2)

                    # Ordenar por perfil
                    ordem = {'VIP': 0, 'Premium': 1, 'Potencial': 2, 'Pontual': 3}
                    df_scores_tabela['ordem'] = df_scores_tabela['Perfil'].map(ordem)
                    df_scores_tabela = df_scores_tabela.sort_values('ordem').drop('ordem', axis=1)

                    st.dataframe(df_scores_tabela, use_container_width=True, hide_index=True)
                else:
                    st.warning("Dados de clientes com scores não disponíveis.")

            # Definir tab de shopping como tab3 quando usando quintis
            tab_shopping = tab3
            tab_segmentos = tab4
            tab_resumo = tab5
        else:
            # Quando não usa quintis, manter as tabs originais
            tab_shopping = tab2
            tab_segmentos = tab3
            tab_resumo = tab4

        with tab_shopping:
            st.subheader("Análise RFV por Shopping")

            # Selecionar dados de shopping conforme método
            if usar_quintis and 'df_shopping_quintis' in dir() and not df_shopping_quintis.empty:
                df_shopping = df_shopping_quintis.copy()
                sufixo = '_quintis'
                perfis_cols = ['vip_quintis', 'premium_quintis', 'potencial_quintis', 'pontual_quintis']
                tem_perfis = all(col in df_shopping.columns for col in perfis_cols)
            elif 'shopping' in dados_rfv and dados_rfv['shopping'] is not None:
                df_shopping = dados_rfv['shopping'].copy()
                # Definir sufixo baseado no tipo de classificação
                sufixo = '_hist' if usar_historico else '_periodo'
                perfis_cols = [f'vip{sufixo}', f'premium{sufixo}', f'potencial{sufixo}', f'pontual{sufixo}']
                tem_perfis = all(col in df_shopping.columns for col in perfis_cols)
            else:
                df_shopping = None
                tem_perfis = False

            if df_shopping is not None:
                # Filtros
                col_filtro1, col_filtro2 = st.columns(2)
                with col_filtro1:
                    shopping_selecionado = st.selectbox(
                        "Filtrar por Shopping:",
                        ["Todos"] + list(df_shopping['shopping_principal'].unique()),
                        key='rfv_shopping_filter'
                    )
                with col_filtro2:
                    perfil_filtro_shop = st.selectbox(
                        "Filtrar por Perfil:",
                        ["Todos", "VIP", "Premium", "Potencial", "Pontual"],
                        key='rfv_perfil_shop_filter'
                    )

                if shopping_selecionado != "Todos":
                    df_shopping = df_shopping[df_shopping['shopping_principal'] == shopping_selecionado]

                col1, col2 = st.columns(2)

                with col1:
                    # Valor por shopping
                    fig_shop_valor = px.bar(
                        df_shopping.sort_values('valor_total', ascending=True),
                        x='valor_total',
                        y='shopping_principal',
                        orientation='h',
                        title='Valor Total por Shopping',
                        color='valor_total',
                        color_continuous_scale='Blues'
                    )
                    fig_shop_valor.update_layout(showlegend=False, yaxis_title='', xaxis_title='Valor (R$)')
                    st.plotly_chart(fig_shop_valor, use_container_width=True)

                with col2:
                    # Distribuição de perfis por shopping (gráfico de barras empilhadas)
                    if tem_perfis:
                        # Preparar dados para gráfico empilhado
                        df_perfis_shop = df_shopping[['shopping_principal'] + perfis_cols].copy()
                        df_perfis_shop.columns = ['Shopping', 'VIP', 'Premium', 'Potencial', 'Pontual']

                        # Filtrar perfis se selecionado
                        if perfil_filtro_shop != "Todos":
                            perfis_mostrar = [perfil_filtro_shop]
                        else:
                            perfis_mostrar = ['VIP', 'Premium', 'Potencial', 'Pontual']

                        df_melted = df_perfis_shop.melt(
                            id_vars=['Shopping'],
                            value_vars=perfis_mostrar,
                            var_name='Perfil',
                            value_name='Clientes'
                        )

                        titulo_grafico = f'Distribuição de Perfis por Shopping ({tipo_rfv_label})'
                        if perfil_filtro_shop != "Todos":
                            titulo_grafico = f'Clientes {perfil_filtro_shop} por Shopping ({tipo_rfv_label})'

                        fig_perfis = px.bar(
                            df_melted,
                            x='Shopping',
                            y='Clientes',
                            color='Perfil',
                            title=titulo_grafico,
                            color_discrete_map=CORES_PERFIL,
                            category_orders={'Perfil': ORDEM_PERFIL}
                        )
                        fig_perfis.update_layout(xaxis_tickangle=-45, barmode='stack')
                        st.plotly_chart(fig_perfis, use_container_width=True)
                    else:
                        st.info("Dados de perfis por shopping não disponíveis. Execute novamente o script de geração.")

                # KPIs por perfil (apenas se temos os dados)
                if tem_perfis:
                    titulo_kpi = "Total de Clientes por Perfil"
                    if shopping_selecionado != "Todos":
                        titulo_kpi += f" - {shopping_selecionado}"
                    st.subheader(titulo_kpi)

                    totais = {
                        'VIP': int(df_shopping[f'vip{sufixo}'].sum()),
                        'Premium': int(df_shopping[f'premium{sufixo}'].sum()),
                        'Potencial': int(df_shopping[f'potencial{sufixo}'].sum()),
                        'Pontual': int(df_shopping[f'pontual{sufixo}'].sum())
                    }
                    total_geral = sum(totais.values())

                    # Se filtro de perfil está ativo, mostrar métricas detalhadas do perfil
                    if perfil_filtro_shop != "Todos":
                        perfil = perfil_filtro_shop
                        perfil_lower = perfil.lower()
                        qtd = totais[perfil]
                        pct = (qtd / total_geral * 100) if total_geral > 0 else 0
                        icone = "🏆" if perfil == 'VIP' else "⭐" if perfil == 'Premium' else "🎯" if perfil == 'Potencial' else "👤"

                        # Verificar se temos as colunas de valor e ticket por perfil
                        col_valor = f'{perfil_lower}_valor{sufixo}'
                        tem_valor = col_valor in df_shopping.columns

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric(f"{icone} Clientes {perfil}", f"{qtd:,}", f"{pct:.1f}% do total")
                        with col2:
                            if tem_valor:
                                valor_perfil = df_shopping[col_valor].sum()
                                st.metric(f"Valor {perfil}", f"R$ {valor_perfil:,.2f}")
                            else:
                                st.metric("Total de Clientes", f"{total_geral:,}")
                        with col3:
                            if tem_valor and qtd > 0:
                                valor_perfil = df_shopping[col_valor].sum()
                                ticket_perfil = valor_perfil / qtd
                                st.metric(f"Ticket Médio {perfil}", f"R$ {ticket_perfil:,.2f}")
                            else:
                                valor_total = df_shopping['valor_total'].sum()
                                st.metric("Valor Total", f"R$ {valor_total:,.2f}")
                        with col4:
                            if tem_valor:
                                valor_perfil = df_shopping[col_valor].sum()
                                valor_total = df_shopping['valor_total'].sum()
                                pct_valor = (valor_perfil / valor_total * 100) if valor_total > 0 else 0
                                st.metric(f"% do Faturamento", f"{pct_valor:.1f}%")
                            else:
                                st.metric("High Spenders", f"{int(df_shopping['high_spenders'].sum()):,}")
                    else:
                        col1, col2, col3, col4 = st.columns(4)
                        for i, (perfil, qtd) in enumerate(totais.items()):
                            pct = (qtd / total_geral * 100) if total_geral > 0 else 0
                            icone = "🏆" if perfil == 'VIP' else "⭐" if perfil == 'Premium' else "🎯" if perfil == 'Potencial' else "👤"
                            with [col1, col2, col3, col4][i]:
                                st.metric(f"{icone} {perfil}", f"{qtd:,}", f"{pct:.1f}%")

                # Tabela detalhada com todos os perfis
                st.subheader("Métricas Detalhadas por Shopping")
                df_shop_display = df_shopping.copy()

                # Verificar se temos as colunas de valor e ticket por perfil
                perfil_lower = perfil_filtro_shop.lower() if perfil_filtro_shop != "Todos" else None
                tem_metricas_perfil = perfil_lower and f'{perfil_lower}_valor{sufixo}' in df_shop_display.columns

                if perfil_filtro_shop != "Todos" and tem_metricas_perfil:
                    # Mostrar dados filtrados pelo perfil selecionado
                    colunas_exibir = [
                        'shopping_principal',
                        f'{perfil_lower}{sufixo}',
                        f'{perfil_lower}_valor{sufixo}',
                        f'{perfil_lower}_ticket{sufixo}'
                    ]
                    nomes_colunas = ['Shopping', 'Clientes', 'Valor Total', 'Ticket Médio']

                    df_shop_display = df_shop_display[colunas_exibir].copy()
                    df_shop_display.columns = nomes_colunas

                    # Calcular % do valor total
                    total_valor_perfil = df_shop_display['Valor Total'].sum()
                    df_shop_display['% Valor'] = (df_shop_display['Valor Total'] / total_valor_perfil * 100).round(1)

                    # Formatar valores
                    df_shop_display['Valor Total'] = df_shop_display['Valor Total'].apply(lambda x: f"R$ {x:,.2f}")
                    df_shop_display['Ticket Médio'] = df_shop_display['Ticket Médio'].apply(lambda x: f"R$ {x:.2f}")
                    df_shop_display['% Valor'] = df_shop_display['% Valor'].apply(lambda x: f"{x:.1f}%")

                    st.caption(f"Mostrando dados do perfil **{perfil_filtro_shop}** ({tipo_rfv_label})")
                else:
                    # Mostrar visão geral com todos os perfis
                    colunas_exibir = ['shopping_principal', 'qtd_clientes', 'valor_total', 'ticket_medio']
                    nomes_colunas = ['Shopping', 'Total Clientes', 'Valor Total', 'Ticket Médio']

                    if tem_perfis:
                        colunas_exibir.extend(perfis_cols)
                        nomes_colunas.extend(['VIP', 'Premium', 'Potencial', 'Pontual'])

                    # High spenders só existe no método Por Valor
                    if 'high_spenders' in df_shop_display.columns:
                        colunas_exibir.append('high_spenders')
                        nomes_colunas.append('High Spenders')

                    colunas_exibir.append('pct_valor')
                    nomes_colunas.append('% Valor')

                    df_shop_display = df_shop_display[colunas_exibir].copy()
                    df_shop_display.columns = nomes_colunas

                    # Formatar valores
                    df_shop_display['Valor Total'] = df_shop_display['Valor Total'].apply(lambda x: f"R$ {x:,.2f}")
                    df_shop_display['Ticket Médio'] = df_shop_display['Ticket Médio'].apply(lambda x: f"R$ {x:.2f}")
                    df_shop_display['% Valor'] = df_shop_display['% Valor'].apply(lambda x: f"{x:.1f}%")

                st.dataframe(df_shop_display, use_container_width=True, hide_index=True)
            else:
                st.warning("Dados de shopping não disponíveis para este período.")

        with tab_segmentos:
            st.subheader("Segmentos e Lojas por Perfil")

            # Sub-tabs para segmentos e lojas
            subtab1, subtab2 = st.tabs(["🏷️ Segmentos", "🏪 Lojas"])

            with subtab1:
                if 'seg_perfil_shop' in dados_rfv and dados_rfv['seg_perfil_shop'] is not None:
                    # Filtros
                    col1, col2 = st.columns(2)
                    with col1:
                        perfil_filtro = st.selectbox(
                            "Filtrar por Perfil:",
                            ["Todos", "VIP", "Premium", "Potencial", "Pontual"],
                            key='rfv_perfil_seg'
                        )
                    with col2:
                        shopping_filtro = st.selectbox(
                            "Filtrar por Shopping:",
                            ["Todos"] + list(dados_rfv['seg_perfil_shop']['shopping'].unique()),
                            key='rfv_shopping_seg'
                        )

                    df_seg = dados_rfv['seg_perfil_shop'].copy()

                    if perfil_filtro != "Todos":
                        df_seg = df_seg[df_seg['perfil_historico'] == perfil_filtro]
                    if shopping_filtro != "Todos":
                        df_seg = df_seg[df_seg['shopping'] == shopping_filtro]

                    if len(df_seg) > 0:
                        # Top 10 segmentos
                        df_seg_top = df_seg.groupby('segmento').agg({
                            'valor': 'sum',
                            'cupons': 'sum',
                            'clientes': 'sum'
                        }).reset_index().sort_values('valor', ascending=False).head(10)

                        fig_seg = px.bar(
                            df_seg_top,
                            x='segmento',
                            y='valor',
                            title=f'Top 10 Segmentos por Valor{" - " + perfil_filtro if perfil_filtro != "Todos" else ""}{" - " + shopping_filtro if shopping_filtro != "Todos" else ""}',
                            color='valor',
                            color_continuous_scale='Viridis'
                        )
                        fig_seg.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_seg, use_container_width=True)

                        # Tabela detalhada
                        df_seg_display = df_seg[['shopping', 'perfil_historico', 'segmento', 'valor', 'cupons', 'clientes', 'pct_valor']].copy()
                        df_seg_display['valor'] = df_seg_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                        df_seg_display['pct_valor'] = df_seg_display['pct_valor'].apply(lambda x: f"{x:.1f}%")
                        df_seg_display.columns = ['Shopping', 'Perfil', 'Segmento', 'Valor', 'Cupons', 'Clientes', '% Valor']
                        st.dataframe(df_seg_display.head(20), use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhum dado encontrado com os filtros selecionados.")
                else:
                    st.warning("Dados de segmentos não disponíveis para este período.")

            with subtab2:
                if 'lojas' in dados_rfv and dados_rfv['lojas'] is not None:
                    # Filtros para lojas
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        perfil_filtro_loja = st.selectbox(
                            "Filtrar por Perfil:",
                            ["Todos", "VIP", "Premium", "Potencial", "Pontual"],
                            key='rfv_perfil_loja'
                        )
                    with col2:
                        shopping_filtro_loja = st.selectbox(
                            "Filtrar por Shopping:",
                            ["Todos"] + list(dados_rfv['lojas']['shopping'].unique()),
                            key='rfv_shopping_loja'
                        )
                    with col3:
                        genero_filtro = st.selectbox(
                            "Filtrar por Gênero:",
                            ["Todos", "Feminino", "Masculino"],
                            key='rfv_genero_loja'
                        )

                    df_lojas = dados_rfv['lojas'].copy()

                    if perfil_filtro_loja != "Todos":
                        df_lojas = df_lojas[df_lojas['perfil'] == perfil_filtro_loja]
                    if shopping_filtro_loja != "Todos":
                        df_lojas = df_lojas[df_lojas['shopping'] == shopping_filtro_loja]
                    if genero_filtro != "Todos":
                        df_lojas = df_lojas[df_lojas['genero'] == genero_filtro]

                    if len(df_lojas) > 0:
                        # Top 10 lojas
                        df_lojas_top = df_lojas.groupby('loja').agg({
                            'valor': 'sum',
                            'cupons': 'sum',
                            'clientes': 'sum'
                        }).reset_index().sort_values('valor', ascending=False).head(10)

                        fig_lojas = px.bar(
                            df_lojas_top,
                            x='loja',
                            y='valor',
                            title='Top 10 Lojas por Valor',
                            color='valor',
                            color_continuous_scale='Oranges'
                        )
                        fig_lojas.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_lojas, use_container_width=True)

                        # Tabela detalhada
                        df_lojas_display = df_lojas[['perfil', 'shopping', 'genero', 'loja', 'valor', 'cupons', 'clientes', 'pct_valor']].copy()
                        df_lojas_display['valor'] = df_lojas_display['valor'].apply(lambda x: f"R$ {x:,.2f}")
                        df_lojas_display['pct_valor'] = df_lojas_display['pct_valor'].apply(lambda x: f"{x:.1f}%")
                        df_lojas_display.columns = ['Perfil', 'Shopping', 'Gênero', 'Loja', 'Valor', 'Cupons', 'Clientes', '% Valor']
                        st.dataframe(df_lojas_display.head(20), use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhum dado encontrado com os filtros selecionados.")
                else:
                    st.warning("Dados de lojas não disponíveis para este período.")

        with tab_resumo:
            st.subheader("Resumo RFV")

            st.info("""
            📋 A lista completa de clientes RFV está disponível para download na página **Exportar Dados**.
            Aqui você pode visualizar um resumo das métricas por perfil e shopping.
            """)

            # Resumo cruzado Perfil x Shopping
            if 'seg_perfil_shop' in dados_rfv and dados_rfv['seg_perfil_shop'] is not None:
                st.subheader("Matriz: Perfil x Shopping")

                df_seg_shop = dados_rfv['seg_perfil_shop'].copy()

                # Criar matriz pivoteada
                matriz = df_seg_shop.groupby(['shopping', 'perfil_historico']).agg({
                    'valor': 'sum',
                    'clientes': 'sum'
                }).reset_index()

                # Pivot para clientes
                matriz_clientes = matriz.pivot(index='shopping', columns='perfil_historico', values='clientes').fillna(0)
                matriz_clientes = matriz_clientes.reindex(columns=['VIP', 'Premium', 'Potencial', 'Pontual'], fill_value=0)

                # Pivot para valor
                matriz_valor = matriz.pivot(index='shopping', columns='perfil_historico', values='valor').fillna(0)
                matriz_valor = matriz_valor.reindex(columns=['VIP', 'Premium', 'Potencial', 'Pontual'], fill_value=0)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Quantidade de Clientes**")
                    fig_heat_cli = px.imshow(
                        matriz_clientes,
                        labels=dict(x="Perfil", y="Shopping", color="Clientes"),
                        color_continuous_scale='Blues',
                        text_auto=True
                    )
                    fig_heat_cli.update_layout(height=400)
                    st.plotly_chart(fig_heat_cli, use_container_width=True)

                with col2:
                    st.markdown("**Valor Total (R$)**")
                    fig_heat_val = px.imshow(
                        matriz_valor / 1e6,
                        labels=dict(x="Perfil", y="Shopping", color="Valor (M)"),
                        color_continuous_scale='Greens',
                        text_auto='.1f'
                    )
                    fig_heat_val.update_layout(height=400)
                    st.plotly_chart(fig_heat_val, use_container_width=True)

            # Metodologia
            with st.expander("📖 Metodologia RFV"):
                st.markdown("""
                ## Métodos de Classificação Disponíveis

                Este dashboard oferece **dois métodos** de classificação de clientes:

                ---

                ### 1️⃣ Método Por Valor (R$) - Thresholds Fixos

                A segmentação utiliza **faixas de valor fixas (thresholds)** para classificar cada cliente
                em um dos 4 perfis. A classificação é baseada exclusivamente no **Valor** gasto.

                As métricas de Recência e Frequência são calculadas, mas **não são utilizadas como critério**.

                #### Classificação Histórica (Valor Total Acumulado)

                | Perfil | Faixa de Valor | Descrição |
                |--------|----------------|-----------|
                | **VIP** | >= R$ 5.000 | Clientes de altíssimo valor |
                | **Premium** | R$ 2.500 a R$ 4.999 | Alto valor, potencial VIP |
                | **Potencial** | R$ 1.000 a R$ 2.499 | Bom potencial de crescimento |
                | **Pontual** | < R$ 1.000 | Ocasionais ou novos |

                #### Classificação Por Período

                | Perfil | Faixa de Valor | Descrição |
                |--------|----------------|-----------|
                | **VIP** | >= R$ 2.000 | Alto gasto no período |
                | **Premium** | R$ 1.000 a R$ 1.999 | Gasto relevante |
                | **Potencial** | R$ 500 a R$ 999 | Gasto moderado |
                | **Pontual** | < R$ 500 | Baixo gasto |

                ---

                ### 2️⃣ Método Por Quintis (R+F+V) - Scores Dinâmicos

                A segmentação utiliza **quintis dinâmicos** que se adaptam à distribuição dos dados.
                Cada cliente recebe scores de **1 a 5** em cada dimensão:

                - **Recência (R):** Score 5 = comprou recentemente, Score 1 = há muito tempo
                - **Frequência (F):** Score 5 = muitas compras, Score 1 = poucas compras
                - **Valor (V):** Score 5 = alto valor, Score 1 = baixo valor

                #### Classificação por Soma de Scores (R+F+V = 3 a 15)

                | Score Total | Perfil | Descrição |
                |-------------|--------|-----------|
                | 13 a 15 | **VIP** | Excelente em todas as dimensões |
                | 10 a 12 | **Premium** | Bom desempenho geral |
                | 7 a 9 | **Potencial** | Médio, espaço para crescer |
                | 3 a 6 | **Pontual** | Baixo engajamento |

                #### Escopos Disponíveis

                - **Global:** Quintis calculados sobre todos os clientes (comparação justa entre shoppings)
                - **Por Shopping:** Quintis calculados dentro de cada shopping (cada um tem seus "melhores")

                ---

                ### 📊 Comparativo dos Métodos

                | Aspecto | Por Valor (R$) | Por Quintis (R+F+V) |
                |---------|----------------|---------------------|
                | Dimensões | Apenas Valor | Recência + Frequência + Valor |
                | Critério | Thresholds fixos em R$ | Distribuição percentual |
                | Adaptabilidade | Pode ficar defasado | Ajusta automaticamente |
                | Distribuição | Variável | ~20% por quintil |

                ### 💡 Quando usar cada método?

                - **Por Valor:** Análises históricas, comparação entre períodos diferentes, consistência de critérios.
                - **Por Quintis:** Segmentação relativa, identificação de risco de churn (R baixo), análise multidimensional.

                ### Cálculo do Ticket Médio

                ```
                Ticket Médio = Valor Total do Perfil / Quantidade de Clientes do Perfil
                ```
                """)

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

    # Adicionar dados RFV ao Excel se disponíveis
    dados_rfv_excel = dados.get('rfv')
    if dados_rfv_excel is not None:
        if dados_rfv_excel.get('perfil_historico') is not None:
            dados_excel['RFV Perfil Historico'] = dados_rfv_excel['perfil_historico']
        if dados_rfv_excel.get('perfil_periodo') is not None:
            dados_excel['RFV Perfil Periodo'] = dados_rfv_excel['perfil_periodo']
        if dados_rfv_excel.get('shopping') is not None:
            dados_excel['RFV por Shopping'] = dados_rfv_excel['shopping']
        if dados_rfv_excel.get('seg_perfil_shop') is not None:
            dados_excel['RFV Segmentos Perfil Shop'] = dados_rfv_excel['seg_perfil_shop']
        if dados_rfv_excel.get('lojas') is not None:
            dados_excel['RFV Lojas Genero Perfil'] = dados_rfv_excel['lojas']
        if dados_rfv_excel.get('resumo') is not None:
            dados_excel['RFV Resumo'] = dados_rfv_excel['resumo']

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Resumos", "👥 Demografia", "⭐ High Spenders", "🛒 Comportamento", "🎯 RFV"])

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

            st.markdown("**Matriz Ticket Médio (Gênero x Idade)**")
            st.caption("Ticket médio por combinação")
            st.download_button(
                label="⬇️ Baixar CSV",
                data=converter_para_csv(dados['matriz_ticket']),
                file_name="matriz_ticket_genero_idade.csv",
                mime="text/csv",
                key="download_matriz_ticket"
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

    with tab5:
        st.markdown("#### Análise RFV (Recência, Frequência, Valor)")

        dados_rfv_export = dados.get('rfv')

        if dados_rfv_export is not None:
            col1, col2 = st.columns(2)

            with col1:
                if dados_rfv_export.get('perfil_historico') is not None:
                    st.markdown("**Perfil Histórico (Valor Total)**")
                    st.caption("Classificação por valor total acumulado do cliente")
                    st.download_button(
                        label="⬇️ Baixar CSV",
                        data=converter_para_csv(dados_rfv_export['perfil_historico']),
                        file_name="metricas_perfil_historico.csv",
                        mime="text/csv",
                        key="download_rfv_hist"
                    )

                if dados_rfv_export.get('perfil_periodo') is not None:
                    st.markdown("**Perfil por Período (Valor do Período)**")
                    st.caption("Classificação por valor gasto no período selecionado")
                    st.download_button(
                        label="⬇️ Baixar CSV",
                        data=converter_para_csv(dados_rfv_export['perfil_periodo']),
                        file_name="metricas_perfil_periodo.csv",
                        mime="text/csv",
                        key="download_rfv_periodo"
                    )

                if dados_rfv_export.get('shopping') is not None:
                    st.markdown("**Métricas por Shopping**")
                    st.caption("Clientes, valor e ticket médio por perfil e shopping")
                    st.download_button(
                        label="⬇️ Baixar CSV",
                        data=converter_para_csv(dados_rfv_export['shopping']),
                        file_name="metricas_shopping_rfv.csv",
                        mime="text/csv",
                        key="download_rfv_shopping"
                    )

            with col2:
                if dados_rfv_export.get('seg_perfil_shop') is not None:
                    st.markdown("**Top Segmentos por Perfil e Shopping**")
                    st.caption("Top 10 segmentos para cada perfil em cada shopping")
                    st.download_button(
                        label="⬇️ Baixar CSV",
                        data=converter_para_csv(dados_rfv_export['seg_perfil_shop']),
                        file_name="top10_segmentos_por_perfil_shopping.csv",
                        mime="text/csv",
                        key="download_rfv_seg"
                    )

                if dados_rfv_export.get('lojas') is not None:
                    st.markdown("**Top Lojas por Gênero, Shopping e Perfil**")
                    st.caption("Top 10 lojas por combinação de perfil, shopping e gênero")
                    st.download_button(
                        label="⬇️ Baixar CSV",
                        data=converter_para_csv(dados_rfv_export['lojas']),
                        file_name="top10_lojas_por_genero_shopping_perfil.csv",
                        mime="text/csv",
                        key="download_rfv_lojas"
                    )

                if dados_rfv_export.get('resumo') is not None:
                    st.markdown("**Resumo RFV**")
                    st.caption("Resumo geral com totais de clientes e valores")
                    st.download_button(
                        label="⬇️ Baixar CSV",
                        data=converter_para_csv(dados_rfv_export['resumo']),
                        file_name="resumo_rfv.csv",
                        mime="text/csv",
                        key="download_rfv_resumo"
                    )

            # Dados de Quintis (se disponíveis)
            dados_rfv_quintis_export = dados.get('rfv_quintis')
            if dados_rfv_quintis_export:
                st.markdown("---")
                st.markdown("#### 📈 Dados RFV por Quintis (Scores R+F+V)")

                col1, col2 = st.columns(2)

                with col1:
                    if dados_rfv_quintis_export.get('clientes_global') is not None:
                        st.markdown("**Clientes com Scores (Escopo Global)**")
                        st.caption("Lista de clientes com scores R, F, V e perfil quintis")
                        st.download_button(
                            label="⬇️ Baixar CSV",
                            data=converter_para_csv(dados_rfv_quintis_export['clientes_global']),
                            file_name="rfv_quintis_global.csv",
                            mime="text/csv",
                            key="download_quintis_clientes_global"
                        )

                    if dados_rfv_quintis_export.get('perfil_global') is not None:
                        st.markdown("**Métricas por Perfil (Escopo Global)**")
                        st.caption("Agregado por perfil com scores médios")
                        st.download_button(
                            label="⬇️ Baixar CSV",
                            data=converter_para_csv(dados_rfv_quintis_export['perfil_global']),
                            file_name="metricas_perfil_quintis_global.csv",
                            mime="text/csv",
                            key="download_quintis_perfil_global"
                        )

                    if dados_rfv_quintis_export.get('shopping_global') is not None:
                        st.markdown("**Por Shopping (Escopo Global)**")
                        st.caption("Métricas por shopping com perfis quintis")
                        st.download_button(
                            label="⬇️ Baixar CSV",
                            data=converter_para_csv(dados_rfv_quintis_export['shopping_global']),
                            file_name="metricas_shopping_quintis_global.csv",
                            mime="text/csv",
                            key="download_quintis_shopping_global"
                        )

                with col2:
                    if dados_rfv_quintis_export.get('clientes_shopping') is not None:
                        st.markdown("**Clientes com Scores (Por Shopping)**")
                        st.caption("Quintis calculados dentro de cada shopping")
                        st.download_button(
                            label="⬇️ Baixar CSV",
                            data=converter_para_csv(dados_rfv_quintis_export['clientes_shopping']),
                            file_name="rfv_quintis_por_shopping.csv",
                            mime="text/csv",
                            key="download_quintis_clientes_shopping"
                        )

                    if dados_rfv_quintis_export.get('perfil_shopping') is not None:
                        st.markdown("**Métricas por Perfil (Por Shopping)**")
                        st.caption("Agregado por perfil com escopo por shopping")
                        st.download_button(
                            label="⬇️ Baixar CSV",
                            data=converter_para_csv(dados_rfv_quintis_export['perfil_shopping']),
                            file_name="metricas_perfil_quintis_shopping.csv",
                            mime="text/csv",
                            key="download_quintis_perfil_shopping"
                        )

                    if dados_rfv_quintis_export.get('thresholds_global') is not None:
                        st.markdown("**Thresholds dos Quintis**")
                        st.caption("Valores de corte dos quintis para auditoria")
                        st.download_button(
                            label="⬇️ Baixar CSV",
                            data=converter_para_csv(dados_rfv_quintis_export['thresholds_global']),
                            file_name="quintile_thresholds.csv",
                            mime="text/csv",
                            key="download_quintis_thresholds"
                        )
        else:
            st.warning("⚠️ Dados RFV não disponíveis para este período. Execute o script `gerar_rfv_por_periodo.py`.")

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
        if shop_data.get('hs_stats') is not None:
            dados_shop_excel['High Spenders Stats'] = shop_data['hs_stats']

        excel_shopping = criar_excel_completo(dados_shop_excel, shopping_export)

        # Excel completo
        st.download_button(
            label=f"⬇️ Relatório Completo {shopping_export} (Excel)",
            data=excel_shopping,
            file_name=f"relatorio_{shopping_export}_{periodo_pasta}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_shop_excel"
        )

        # CSVs individuais
        st.markdown("**Arquivos individuais (CSV):**")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.download_button(
                label=f"⬇️ Perfil Gênero",
                data=converter_para_csv(shop_data['genero']),
                file_name=f"perfil_genero_{shopping_export}.csv",
                mime="text/csv",
                key="download_shop_genero"
            )
            st.download_button(
                label=f"⬇️ Top Lojas",
                data=converter_para_csv(shop_data['lojas']),
                file_name=f"top_lojas_{shopping_export}.csv",
                mime="text/csv",
                key="download_shop_lojas"
            )

        with col2:
            st.download_button(
                label=f"⬇️ Perfil Faixa Etária",
                data=converter_para_csv(shop_data['faixa']),
                file_name=f"perfil_faixa_etaria_{shopping_export}.csv",
                mime="text/csv",
                key="download_shop_faixa"
            )
            st.download_button(
                label=f"⬇️ Comportamento Período",
                data=converter_para_csv(shop_data['periodo']),
                file_name=f"comportamento_periodo_{shopping_export}.csv",
                mime="text/csv",
                key="download_shop_periodo"
            )

        with col3:
            st.download_button(
                label=f"⬇️ Top Segmentos",
                data=converter_para_csv(shop_data['segmentos']),
                file_name=f"top_segmentos_{shopping_export}.csv",
                mime="text/csv",
                key="download_shop_seg"
            )
            st.download_button(
                label=f"⬇️ Comportamento Dia Semana",
                data=converter_para_csv(shop_data['dia_semana']),
                file_name=f"comportamento_dia_semana_{shopping_export}.csv",
                mime="text/csv",
                key="download_shop_dia"
            )

        if shop_data.get('hs_stats') is not None:
            st.download_button(
                label=f"⬇️ High Spenders Stats {shopping_export}",
                data=converter_para_csv(shop_data['hs_stats']),
                file_name=f"high_spenders_stats_{shopping_export}.csv",
                mime="text/csv",
                key="download_shop_hs"
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
            As **14 Personas** foram identificadas através de **classificação baseada em regras** considerando:

            - Se o cliente é High Spender (top 10% de valor por shopping)
            - Gênero e faixa etária
            - Frequência de compras
            - Segmento de consumo principal
            - Valor total gasto (percentil 75 para Comprador Seletivo)

            **Personas High Spender (Top 10%):**
            | Persona | Critério |
            |---------|----------|
            | Executiva Premium | Mulheres 40-54, High Spender |
            | Executivo Exigente | Homens High Spender |
            | Fashionista Premium | Mulheres 25-39 (ou <25), High Spender |
            | Senior VIP | 55+ anos, High Spender |
            | Cliente Premium | High Spender (outros) |

            **Personas Regulares:**
            | Persona | Critério |
            |---------|----------|
            | Jovem Engajado | < 30 anos, frequência >= 5 |
            | Mãe Moderna | Mulheres 30-49, freq >= 3, Moda/Infantil/Calçados |
            | Beauty Lover | Mulheres 25-54, freq >= 3, Beleza |
            | Foodie | Freq >= 3, Gastronomia |
            | Fitness | Freq >= 3, Esportes |
            | Comprador Seletivo | Valor >= percentil 75, freq <= 3 |
            | Senior Tradicional | 55+ anos |
            | Jovem Explorer | < 30 anos |
            | Cliente Regular | Demais clientes |
            """)

        with st.expander("❓ O que significa cada faixa etária?", expanded=False):
            st.markdown("""
            As faixas etárias são definidas por **intervalos fixos de idade**:

            | Faixa | Idade | Geração Aproximada |
            |-------|-------|-------------------|
            | **16-24 (Gen Z)** | Menos de 25 anos | Geração Z |
            | **25-39 (Millennials)** | 25 a 39 anos | Millennials |
            | **40-54 (Gen X)** | 40 a 54 anos | Geração X |
            | **55-69 (Boomers)** | 55 a 69 anos | Baby Boomers |
            | **70+ (Silent)** | 70 anos ou mais | Geração Silenciosa |

            A classificação é feita pela idade calculada a partir da data de nascimento do cliente.
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

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Visão Geral", "📊 Métricas", "🎯 RFV", "🎭 Personas & HS", "📁 Dados", "❓ Glossário"])

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
        **Base completa:** 11/12/2022 a 28/01/2026

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
        2. **🎭 Personas** - 14 perfis comportamentais de clientes
        3. **🏬 Por Shopping** - Análise detalhada de cada unidade
        4. **👥 Perfil Demográfico** - Distribuição por gênero e faixa etária
        5. **⭐ High Spenders** - Clientes top 10% em valor
        6. **🏆 Top Consumidores** - Top 150 consumidores por shopping com dados de contato
        7. **🛒 Segmentos** - Análise por categoria de produto
        8. **🎯 RFV** - Análise de Recência, Frequência e Valor
        9. **⏰ Comportamento** - Padrões temporais de compra
        10. **📈 Comparativo** - Comparação entre shoppings
        11. **📥 Exportar Dados** - Download de relatórios em CSV e Excel
        12. **🤖 Assistente** - Chat para dúvidas e sugestões
        13. **📚 Documentação** - Documentação completa do dashboard
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

        | Faixa | Idade | Geração Aproximada |
        |-------|-------|-------------------|
        | Gen Z | Menos de 25 anos | Geração Z |
        | Millennials | 25 a 39 anos | Millennials |
        | Gen X | 40 a 54 anos | Geração X |
        | Boomers | 55 a 69 anos | Baby Boomers |
        | Silent | 70 anos ou mais | Geração Silenciosa |

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

        **Períodos do Dia (baseados na hora da transação):**
        - Manhã: 0h às 11:59
        - Tarde: 12h às 17:59
        - Noite: 18h às 23:59

        **Dias da Semana:**
        - Segunda a Domingo
        """)

    with tab3:
        st.markdown("""
        ## Análise RFV - Segmentação por Valor

        A análise classifica clientes em **4 perfis** utilizando **faixas de valor fixas (thresholds)**.

        ### Método Aplicado

        A segmentação é baseada exclusivamente no **Valor** gasto pelo cliente.
        As métricas de Recência (dias desde a última compra) e Frequência (quantidade de compras)
        são calculadas e armazenadas, mas **não são utilizadas como critério de classificação**.

        **Não é utilizado scoring por quintis (R1-R5, F1-F5, V1-V5).**

        ---

        ### Classificação Histórica (Valor Total Acumulado)

        | Perfil | Faixa de Valor | Descrição | Estratégia Recomendada |
        |--------|----------------|-----------|------------------------|
        | **VIP** | >= R$ 5.000 | Altíssimo valor, responsáveis pela maior parte do faturamento | Retenção prioritária, benefícios exclusivos |
        | **Premium** | R$ 2.500 a R$ 4.999 | Alto valor com potencial de se tornarem VIP | Programas de upgrade, incentivos para aumentar ticket |
        | **Potencial** | R$ 1.000 a R$ 2.499 | Bom potencial de crescimento | Campanhas de engajamento, cross-sell |
        | **Pontual** | < R$ 1.000 | Clientes ocasionais ou novos | Campanhas de ativação |

        ### Classificação por Período (Valor no Período Selecionado)

        | Perfil | Faixa de Valor | Descrição |
        |--------|----------------|-----------|
        | **VIP** | >= R$ 2.000 | Alto gasto no período selecionado |
        | **Premium** | R$ 1.000 a R$ 1.999 | Gasto relevante no período |
        | **Potencial** | R$ 500 a R$ 999 | Gasto moderado no período |
        | **Pontual** | < R$ 500 | Baixo gasto no período |

        ---

        ### Métricas Calculadas por Cliente

        | Métrica | Descrição | Uso na Classificação |
        |---------|-----------|----------------------|
        | **Valor Total** | Soma de todas as transações do cliente | Sim - critério de classificação |
        | **Valor no Período** | Soma das transações no período selecionado | Sim - classificação por período |
        | **Recência** | Dias desde a última compra até o final do período | Calculado, não usado na classificação |
        | **Frequência** | Quantidade de transações no período | Calculado, não usado na classificação |
        | **Ticket Médio** | Valor Total / Quantidade de Clientes | Exibido nos relatórios |

        ---

        ### Quando usar cada classificação?

        - **Histórica:** Segmentação estratégica de longo prazo, programas de fidelidade, identificação de clientes fiéis
        - **Por Período:** Campanhas táticas, análise de sazonalidade, ativação de clientes recentes

        ---

        ### Princípio de Pareto

        A análise confirma o **Princípio de Pareto** (80/20):

        > **~10% dos clientes (VIP + Premium) geram ~55% do faturamento**

        ---

        ### Arquivos RFV Gerados por Período

        | Arquivo | Conteúdo |
        |---------|----------|
        | `metricas_perfil_historico.csv` | Métricas agregadas por perfil (classificação histórica) |
        | `metricas_perfil_periodo.csv` | Métricas agregadas por perfil (classificação por período) |
        | `metricas_shopping_rfv.csv` | Métricas por shopping com valor e ticket por perfil |
        | `TOP10_SEGMENTOS_POR_PERFIL_SHOPPING.csv` | Top 10 segmentos por perfil e shopping |
        | `TOP10_LOJAS_POR_GENERO_SHOPPING_PERFIL.csv` | Top 10 lojas por gênero, shopping e perfil |
        | `resumo_rfv.csv` | Resumo geral do RFV |
        """)

    with tab4:
        st.markdown("""
        ## Personas de Clientes

        ### Método Aplicado

        As personas foram identificadas através de **classificação baseada em regras (if/elif)**,
        avaliando sequencialmente os seguintes critérios para cada cliente:

        1. Se é **High Spender** (top 10% de valor por shopping) - classifica nas personas HS
        2. **Gênero** e **faixa etária**
        3. **Frequência de compras** (quantidade de transações)
        4. **Segmento de consumo principal** (categoria da loja mais frequentada)
        5. **Valor total gasto** (percentil 75 para Comprador Seletivo)

        A classificação é **determinística e hierárquica**: cada cliente recebe a primeira persona
        cujos critérios satisfaz, na ordem definida abaixo.

        ### 14 Personas Identificadas

        **HIGH SPENDERS (Top 10% de valor por shopping):**
        | Persona | Critério |
        |---------|----------|
        | **Fashionista Premium** | Mulheres < 25 ou 25-39, High Spender |
        | **Executiva Premium** | Mulheres 40-54, High Spender |
        | **Senior VIP** | 55+ anos, High Spender |
        | **Executivo Exigente** | Homens, High Spender |
        | **Cliente Premium** | High Spender (demais) |

        **CLIENTES REGULARES (avaliados nesta ordem):**
        | Persona | Critério |
        |---------|----------|
        | **Jovem Engajado** | < 30 anos, frequência >= 5 |
        | **Mãe Moderna** | Mulheres 30-49, freq >= 3, segmento Moda/Infantil/Calçados |
        | **Beauty Lover** | Mulheres 25-54, freq >= 3, segmento Beleza |
        | **Foodie** | Freq >= 3, segmento Gastronomia |
        | **Fitness** | Freq >= 3, segmento Esportes |
        | **Comprador Seletivo** | Valor >= percentil 75, freq <= 3 |
        | **Senior Tradicional** | 55+ anos |
        | **Jovem Explorer** | < 30 anos |
        | **Cliente Regular** | Demais clientes (fallback) |

        ---

        ## High Spenders

        ### Definição
        Um cliente é **High Spender** se está no **percentil 90** de valor total gasto no seu shopping.
        O threshold é calculado **individualmente por shopping**.

        ### Cálculo
        ```
        Para cada shopping:
          threshold = percentil 90 do valor_total dos clientes daquele shopping
          high_spender = cliente com valor_total >= threshold
        ```

        ### Observações
        - Os thresholds variam por shopping conforme o perfil de consumo da região
        - Um cliente é avaliado apenas no shopping onde mais compra (shopping preferido)
        - Os valores dos thresholds são recalculados a cada atualização dos dados
        """)

    with tab5:
        st.markdown("""
        ## Arquivos de Dados

        ### Dados Consolidados (Resultados/)

        | Arquivo | Descrição |
        |---------|-----------|
        | `resumo_por_shopping.csv` | Métricas consolidadas por shopping |
        | `personas_clientes.csv` | 14 personas identificadas |
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

        ### Top Consumidores (Resultados/)

        | Arquivo | Descrição |
        |---------|-----------|
        | `top_consumidores_rfv.csv` | Top 150 consumidores por shopping com dados de contato |

        **Colunas do arquivo:**
        - Ranking, Shopping, Cliente_ID, Nome, CPF, Email, Celular
        - Logradouro, Numero, Complemento, Bairro, Cidade, Estado, CEP
        - Genero, Valor_Total, Frequencia_Compras, Recencia_Dias
        - Data_Primeira_Compra, Data_Ultima_Compra
        - Segmento_Principal, Valor_Segmento_Principal
        - Loja_Favorita, Valor_Loja_Favorita
        - Score_Recencia, Score_Frequencia, Score_Valor, Score_Total_RFV, Perfil_Cliente

        **Observação:** Colaboradores dos shoppings são excluídos da lista.

        ### Dados RFV (Resultados/RFV/)

        | Arquivo | Descrição |
        |---------|-----------|
        | `metricas_perfil_historico.csv` | Classificação por valor total acumulado |
        | `metricas_perfil_periodo.csv` | Classificação por valor do período |
        | `metricas_shopping_rfv.csv` | Métricas RFV agregadas por shopping |
        | `TOP10_SEGMENTOS_POR_PERFIL_SHOPPING.csv` | Top segmentos por perfil e shopping |
        | `TOP10_LOJAS_POR_GENERO_SHOPPING_PERFIL.csv` | Top lojas por gênero, shopping e perfil |
        | `resumo_rfv.csv` | Resumo geral da classificação RFV |

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

    with tab6:
        st.markdown("""
        ## Glossário de Termos

        ### Métricas Gerais
        | Termo | Definição |
        |-------|-----------|
        | **Ticket Médio** | Valor médio gasto por cliente (Valor Total / Clientes) |
        | **High Spender** | Cliente no top 10% de gastos do shopping |
        | **Threshold** | Valor mínimo para ser High Spender |
        | **Persona** | Perfil comportamental de cliente baseado em regras hierárquicas (gênero, idade, gasto, frequência) |
        | **Frequência** | Número médio de compras por cliente |
        | **Segmento** | Categoria de produto/serviço da loja |

        ### RFV (Classificação por Valor)
        | Termo | Definição |
        |-------|-----------|
        | **RFV** | Metodologia de segmentação baseada em faixas de valor de compra |
        | **Classificação Histórica** | Perfil baseado no valor total acumulado do cliente |
        | **Classificação por Período** | Perfil baseado no valor gasto no período selecionado |
        | **VIP** | Perfil de cliente com valor histórico ≥ R$ 5.000 (ou ≥ R$ 2.000 no período) |
        | **Premium** | Perfil de cliente com valor histórico R$ 2.500-R$ 4.999 (ou R$ 1.000-R$ 1.999 no período) |
        | **Potencial** | Perfil de cliente com valor histórico R$ 1.000-R$ 2.499 (ou R$ 500-R$ 999 no período) |
        | **Pontual** | Perfil de cliente com valor histórico < R$ 1.000 (ou < R$ 500 no período) |

        ### Faixas Etárias
        | Termo | Definição |
        |-------|-----------|
        | **Faixa Etária** | Agrupamento de clientes por idade (calculada a partir da data de nascimento) |
        | **Gen Z** | Menos de 25 anos |
        | **Millennials** | 25 a 39 anos |
        | **Gen X** | 40 a 54 anos |
        | **Boomers** | 55 a 69 anos |
        | **Silent** | 70 anos ou mais |

        ### Visualizações
        | Termo | Definição |
        |-------|-----------|
        | **Matriz Cruzada** | Tabela que cruza duas dimensões (ex: gênero x idade) |
        | **Heatmap** | Mapa de calor visual para identificar padrões |
        | **Radar Chart** | Gráfico radar para comparar múltiplas métricas |
        | **Treemap** | Visualização hierárquica de proporções |

        ---

        ## Contato

        **Desenvolvido para:** Almeida Junior Shoppings

        **Repositório:** [github.com/carlosgravi/dashboard-perfil-cliente](https://github.com/carlosgravi/dashboard-perfil-cliente)

        ---

        *Documentação atualizada em Janeiro/2026*
        """)

# ============================================================================
# PÁGINA: ADMINISTRAÇÃO (apenas para admins)
# ============================================================================
elif pagina == "⚙️ Administração":
    if not is_admin():
        st.error("❌ Acesso negado. Esta página é exclusiva para administradores.")
        st.stop()

    st.markdown('<p class="main-header">⚙️ Painel de Administração</p>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["👥 Usuários", "📊 Logs de Acesso", "⚙️ Configurações", "📋 Instruções"])

    with tab1:
        st.subheader("👥 Gerenciamento de Usuários")

        st.info("""
        **Como gerenciar usuários:**

        Os usuários são configurados no arquivo `secrets.toml` do Streamlit Cloud.
        Para adicionar, editar ou remover usuários, acesse:

        1. [Streamlit Cloud](https://share.streamlit.io/)
        2. Selecione o app `dashboard-perfil-cliente`
        3. Clique em **Settings** → **Secrets**
        4. Edite a configuração conforme instruções abaixo
        """)

        st.markdown("### Usuários Atuais")

        # Mostrar lista de usuários (sem senhas)
        config = carregar_config_auth()
        if config and 'credentials' in config and 'usernames' in config['credentials']:
            usuarios = []
            for username, user_data in config['credentials']['usernames'].items():
                usuarios.append({
                    'Usuário': username,
                    'Nome': user_data.get('name', 'N/A'),
                    'Email': user_data.get('email', 'N/A'),
                    'Perfil': 'Administrador' if user_data.get('role', 'viewer') == 'admin' else 'Visualizador'
                })

            df_usuarios = pd.DataFrame(usuarios)
            st.dataframe(df_usuarios, use_container_width=True, hide_index=True)

            st.metric("Total de Usuários", len(usuarios))

            # Estatísticas
            col1, col2 = st.columns(2)
            with col1:
                admins = len([u for u in usuarios if u['Perfil'] == 'Administrador'])
                st.metric("Administradores", admins)
            with col2:
                viewers = len([u for u in usuarios if u['Perfil'] == 'Visualizador'])
                st.metric("Visualizadores", viewers)
        else:
            st.warning("Não foi possível carregar a lista de usuários.")

        st.markdown("---")

        st.markdown("### Gerar Hash de Senha")
        st.caption("Use esta ferramenta para gerar o hash de uma nova senha")

        nova_senha = st.text_input("Digite a nova senha:", type="password", key="nova_senha_hash")
        if st.button("Gerar Hash"):
            if nova_senha:
                # Gerar hash da senha
                hashed = stauth.Hasher([nova_senha]).generate()[0]
                st.code(hashed, language=None)
                st.success("✅ Hash gerado! Copie e cole no secrets.toml")
            else:
                st.warning("Digite uma senha para gerar o hash")

    with tab2:
        st.subheader("📊 Logs de Acesso")

        st.info("""
        **Logs de acesso** não estão disponíveis nesta versão.

        Para monitoramento avançado, considere:
        - Integração com Google Analytics
        - Logs do Streamlit Cloud (disponível no painel)
        - Ferramenta externa de monitoramento
        """)

        # Informações da sessão atual
        st.markdown("### Sessão Atual")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Usuário", st.session_state.get('username', 'N/A'))
        with col2:
            st.metric("Nome", st.session_state.get('name', 'N/A'))
        with col3:
            st.metric("Perfil", "Admin" if st.session_state.get('role') == 'admin' else "Viewer")

    with tab3:
        st.subheader("⚙️ Configurações do Sistema")

        st.markdown("### Informações do Dashboard")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Clientes Únicos", f"{dados['clientes_unicos']:,}")
            st.metric("Valor Total", f"R$ {dados['resumo']['valor_total'].sum()/1e6:.1f}M")
        with col2:
            st.metric("Shoppings", len(dados['resumo']))
            st.metric("Personas", len(dados['personas']))

        st.markdown("---")

        st.markdown("### Links Úteis")
        st.markdown("""
        - [Streamlit Cloud - Configurações](https://share.streamlit.io/)
        - [GitHub - Repositório](https://github.com/carlosgravi/dashboard-perfil-cliente)
        - [Documentação Streamlit Authenticator](https://github.com/mkhorasani/Streamlit-Authenticator)
        """)

    with tab4:
        st.subheader("📋 Instruções de Configuração")

        st.markdown("""
        ## Como Adicionar Novos Usuários

        ### 1. Gerar Hash da Senha

        Use a ferramenta na aba **"Usuários"** ou execute localmente:

        ```python
        import streamlit_authenticator as stauth
        hashed = stauth.Hasher(['senha123']).generate()
        print(hashed[0])
        ```

        ### 2. Editar secrets.toml no Streamlit Cloud

        Acesse: **Settings → Secrets** no Streamlit Cloud e adicione:

        ```toml
        [credentials]
        [credentials.usernames]

        [credentials.usernames.novo_usuario]
        name = "Nome do Usuário"
        email = "email@empresa.com"
        password = "$2b$12$hash_gerado_aqui"
        role = "viewer"  # ou "admin"

        [cookie]
        name = "dashboard_perfil_cliente"
        key = "sua_chave_secreta_aqui"
        expiry_days = 30

        [preauthorized]
        emails = []
        ```

        ### 3. Níveis de Acesso

        | Perfil | Permissões |
        |--------|------------|
        | **admin** | Acesso total + Painel de Administração |
        | **viewer** | Visualização de todas as páginas (exceto Admin) |

        ### 4. Exemplo Completo

        ```toml
        [credentials]
        [credentials.usernames]

        [credentials.usernames.admin]
        name = "Administrador"
        email = "admin@almeidajunior.com.br"
        password = "$2b$12$..."
        role = "admin"

        [credentials.usernames.maria]
        name = "Maria Silva"
        email = "maria.silva@almeidajunior.com.br"
        password = "$2b$12$..."
        role = "viewer"

        [credentials.usernames.joao]
        name = "João Santos"
        email = "joao.santos@almeidajunior.com.br"
        password = "$2b$12$..."
        role = "viewer"

        [cookie]
        name = "dashboard_perfil_cliente"
        key = "chave_secreta_muito_longa_e_aleatoria_123456"
        expiry_days = 30

        [preauthorized]
        emails = []
        ```

        ### 5. Remover Usuário

        Simplesmente delete o bloco do usuário no secrets.toml.

        ### 6. Alterar Senha

        1. Gere novo hash com a ferramenta
        2. Substitua o campo `password` do usuário

        ---

        **Importante:**
        - Nunca compartilhe senhas em texto claro
        - Use senhas fortes (mínimo 8 caracteres, letras, números e símbolos)
        - O cookie permite login automático por 30 dias
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
