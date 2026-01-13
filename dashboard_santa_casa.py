"""
Dashboard Interativo de Análise Completa - Jogos Santa Casa
Dados completos com remunerações e prémios transparentes
Utilize: streamlit run dashboard_santa_casa.py --server.port 8503
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import warnings
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# Tentar importar bibliotecas para exportação (opcionais)
try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.utils.dataframe import dataframe_to_rows
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Dashboard Santa Casa - Análise Completa",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }

    /* Cards KPI Profissionais */
    .kpi-card-green {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: white;
        text-align: center;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .kpi-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: white;
        text-align: center;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .kpi-card-orange {
        background: linear-gradient(135deg, #f77737 0%, #fe8a4d 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: white;
        text-align: center;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .kpi-card-yellow {
        background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: white;
        text-align: center;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .kpi-card-purple {
        background: linear-gradient(135deg, #8e44ad 0%, #3a0f5c 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        color: white;
        text-align: center;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .kpi-card-green:hover, .kpi-card-blue:hover, .kpi-card-orange:hover,
    .kpi-card-yellow:hover, .kpi-card-purple:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
    }
    .kpi-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 2.8rem;
        font-weight: bold;
        margin: 10px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .kpi-label {
        font-size: 1rem;
        opacity: 0.95;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-delta {
        font-size: 0.9rem;
        margin-top: 8px;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def carregar_dados():
    """Carrega e processa os dados do arquivo CSV."""
    data_file = Path('/home/jorge/Documentos/Santa casa/dados/dados.csv')

    if not data_file.exists():
        st.error(f"Arquivo não encontrado: {data_file}")
        return None

    # Ler CSV com separador ;
    try:
        df = pd.read_csv(
            data_file,
            sep=';',
            encoding='utf-8'
        )
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

    # Converter Data para datetime
    df['Data'] = pd.to_datetime(df['Data'], format='%d-%m-%Y', errors='coerce')

    # Separar prestação de contas
    df_prestacao = df[df['Categoria'] == 'PRESTAÇÃO DE CONTAS'].copy()

    # Remover linhas de PRESTAÇÃO DE CONTAS dos dados principais (são apenas resumos)
    df = df[df['Categoria'] != 'PRESTAÇÃO DE CONTAS'].copy()

    # Converter colunas numéricas (pode ter formato 171.00 ou 1.164,00)
    numeric_cols = ['Qt Maços', 'Vendas ilíquidas (€)', 'Remunerações (€)', 'Prémios (€)', 'Valor (€)']
    for col in numeric_cols:
        if col in df.columns:
            def converter_numero(val):
                val_str = str(val)
                if ',' in val_str:
                    # Formato europeu: 1.234,56 -> remove pontos, troca vírgula por ponto
                    val_str = val_str.replace('.', '').replace(',', '.')
                # Senão, mantém como está (formato 171.00 já está correto)
                try:
                    return float(val_str)
                except:
                    return 0.0

            df[col] = df[col].apply(converter_numero)

    # Adicionar colunas temporais
    df['Ano'] = df['Data'].dt.year
    df['Mes'] = df['Data'].dt.month
    df['Mes_Nome'] = df['Data'].dt.strftime('%B')
    df['Semana_Ano'] = df['Data'].dt.isocalendar().week
    df['Trimestre'] = df['Data'].dt.quarter
    df['Dia_Semana'] = df['Data'].dt.day_name()
    df['Ano_Semana'] = df['Ano'].astype(str) + '-S' + df['Semana_Ano'].astype(str).str.zfill(2)
    df['Ano_Mes'] = df['Data'].dt.to_period('M').astype(str)

    # Processar prestação de contas também
    if len(df_prestacao) > 0:
        # Converter Data para datetime (se ainda não foi)
        df_prestacao['Data'] = pd.to_datetime(df_prestacao['Data'], format='%d-%m-%Y', errors='coerce')

        numeric_cols = ['Valor (€)']
        for col in numeric_cols:
            if col in df_prestacao.columns:
                def converter_numero(val):
                    val_str = str(val)
                    if ',' in val_str:
                        # Formato europeu: 1.234,56 -> remove pontos, troca vírgula por ponto
                        val_str = val_str.replace('.', '').replace(',', '.')
                    # Senão, mantém como está (formato 171.00 já está correto)
                    try:
                        return float(val_str)
                    except:
                        return 0.0

                df_prestacao[col] = df_prestacao[col].apply(converter_numero)

        df_prestacao['Ano'] = df_prestacao['Data'].dt.year
        df_prestacao['Mes'] = df_prestacao['Data'].dt.month
        df_prestacao['Ano_Mes'] = df_prestacao['Data'].dt.to_period('M').astype(str)

    # Ordenar por data
    df = df.sort_values('Data')

    return df, df_prestacao


def carregar_objetivos():
    """Carrega objetivos semanais do CSV."""
    objetivos_file = Path('objetivos_semanais.csv')

    if not objetivos_file.exists():
        # Criar arquivo padrão se não existir
        df_objetivos = pd.DataFrame({
            'Jogo': [],
            'Objetivo': []
        })
        df_objetivos.to_csv(objetivos_file, sep=';', index=False)
        return {}

    try:
        df_objetivos = pd.read_csv(objetivos_file, sep=';')
        return dict(zip(df_objetivos['Jogo'], df_objetivos['Objetivo']))
    except Exception as e:
        st.warning(f"Erro ao carregar objetivos: {e}")
        return {}


def guardar_objetivos(objetivos_dict):
    """Guarda objetivos semanais em CSV."""
    objetivos_file = Path('/home/jorge/Documentos/Streamlit/objetivos_semanais.csv')

    df_objetivos = pd.DataFrame({
        'Jogo': list(objetivos_dict.keys()),
        'Objetivo': list(objetivos_dict.values())
    })

    try:
        df_objetivos.to_csv(objetivos_file, sep=';', index=False)
        return True
    except Exception as e:
        st.error(f"Erro ao guardar objetivos: {e}")
        return False


def formatar_euro(valor):
    """Formata valor em euros."""
    return f"{valor:,.0f}€".replace(',', '.')


def prever_atingimento_objetivo(df_jogo, objetivo_semanal, semanas_restantes=4):
    """Prevê probabilidade de atingir objetivo baseado em tendência."""
    if len(df_jogo) < 3 or objetivo_semanal == 0:
        return None

    vendas_temporal = df_jogo.groupby('Data')['Valor (€)'].sum().sort_index()
    media_atual = vendas_temporal.mean()

    # Tendência recente (últimas 4 semanas)
    ultimas_semanas = vendas_temporal.tail(4)
    if len(ultimas_semanas) > 1:
        tendencia = ultimas_semanas.pct_change().mean() * 100
    else:
        tendencia = 0

    # Projeção
    projecao = media_atual * (1 + tendencia/100) ** semanas_restantes

    # Probabilidade de atingir objetivo
    probabilidade = min((projecao / objetivo_semanal) * 100, 100)

    return {
        'media_atual': media_atual,
        'tendencia_%': tendencia,
        'projecao': projecao,
        'objetivo': objetivo_semanal,
        'probabilidade_%': probabilidade
    }


def criar_grafico_vendas_tempo(df, periodo='Mes'):
    """Cria gráfico de evolução de vendas ao longo do tempo."""
    col_periodo = 'Ano_Mes' if periodo == 'Mes' else 'Ano_Semana'

    vendas_periodo = df.groupby(col_periodo).agg({
        'Vendas ilíquidas (€)': 'sum',
        'Remunerações (€)': 'sum',
        'Prémios (€)': 'sum',
        'Valor (€)': 'sum'
    }).reset_index()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=vendas_periodo[col_periodo],
        y=vendas_periodo['Vendas ilíquidas (€)'],
        name='Vendas Ilíquidas',
        mode='lines+markers',
        line=dict(color='#1f77b4', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=vendas_periodo[col_periodo],
        y=vendas_periodo['Remunerações (€)'],
        name='Remunerações',
        mode='lines+markers',
        line=dict(color='#2ca02c', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=vendas_periodo[col_periodo],
        y=vendas_periodo['Valor (€)'],
        name='Valor Líquido',
        mode='lines+markers',
        line=dict(color='#ff7f0e', width=2)
    ))

    fig.update_layout(
        title=f"Evolução de Vendas por {periodo}",
        xaxis_title=periodo,
        yaxis_title="Valor (€)",
        hovermode='x unified',
        height=500
    )

    return fig


def criar_grafico_categoria(df):
    """Cria gráfico de vendas por categoria."""
    vendas_cat = df.groupby('Categoria').agg({
        'Vendas ilíquidas (€)': 'sum',
        'Remunerações (€)': 'sum',
        'Valor (€)': 'sum'
    }).reset_index()

    vendas_cat = vendas_cat.sort_values('Vendas ilíquidas (€)', ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=vendas_cat['Categoria'],
        x=vendas_cat['Vendas ilíquidas (€)'],
        name='Vendas Ilíquidas',
        orientation='h',
        marker_color='#1f77b4'
    ))

    fig.add_trace(go.Bar(
        y=vendas_cat['Categoria'],
        x=vendas_cat['Remunerações (€)'],
        name='Remunerações',
        orientation='h',
        marker_color='#2ca02c'
    ))

    fig.update_layout(
        title="Vendas e Remunerações por Categoria",
        xaxis_title="Valor (€)",
        yaxis_title="Categoria",
        barmode='group',
        height=400
    )

    return fig


def criar_grafico_jogo(df, top_n=10):
    """Cria gráfico de top jogos."""
    vendas_jogo = df.groupby('Jogo').agg({
        'Vendas ilíquidas (€)': 'sum',
        'Remunerações (€)': 'sum',
        'Valor (€)': 'sum'
    }).reset_index()

    vendas_jogo = vendas_jogo.sort_values('Vendas ilíquidas (€)', ascending=False).head(top_n)

    fig = px.bar(
        vendas_jogo,
        x='Jogo',
        y=['Vendas ilíquidas (€)', 'Remunerações (€)', 'Valor (€)'],
        title=f"Top {top_n} Jogos",
        barmode='group',
        height=500
    )

    fig.update_layout(
        xaxis_title="Jogo",
        yaxis_title="Valor (€)",
        legend_title="Métrica"
    )

    return fig


def criar_grafico_raspadinhas(df):
    """Cria análise específica das raspadinhas."""
    raspadinhas = df[df['Jogo'] == 'Raspadinha'].copy()

    if len(raspadinhas) == 0:
        return None

    # Análise por jogo rececionado
    analise_jogo = raspadinhas.groupby('Jogo Rececionado').agg({
        'Qt Maços': 'sum',
        'Vendas ilíquidas (€)': 'sum',
        'Remunerações (€)': 'sum',
        'Prémios (€)': 'sum',
        'Valor (€)': 'sum'
    }).reset_index()

    analise_jogo = analise_jogo.sort_values('Vendas ilíquidas (€)', ascending=False).head(15)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=analise_jogo['Jogo Rececionado'],
        y=analise_jogo['Vendas ilíquidas (€)'],
        name='Vendas Ilíquidas',
        marker_color='#1f77b4'
    ))

    fig.add_trace(go.Bar(
        x=analise_jogo['Jogo Rececionado'],
        y=analise_jogo['Prémios (€)'],
        name='Prémios Pagos',
        marker_color='#d62728'
    ))

    fig.add_trace(go.Bar(
        x=analise_jogo['Jogo Rececionado'],
        y=analise_jogo['Valor (€)'],
        name='Valor Líquido',
        marker_color='#2ca02c'
    ))

    fig.update_layout(
        title="Análise de Raspadinhas por Jogo Rececionado (Top 15)",
        xaxis_title="Jogo Rececionado",
        yaxis_title="Valor (€)",
        barmode='group',
        height=500
    )

    return fig


def criar_analise_macos(df):
    """Cria análise de maços de raspadinhas."""
    raspadinhas = df[df['Jogo'] == 'Raspadinha'].copy()

    if len(raspadinhas) == 0:
        return None

    # Filtrar apenas jogos com maços comprados
    macos_comprados = raspadinhas[raspadinhas['Qt Maços'] > 0].copy()

    if len(macos_comprados) == 0:
        return None

    # Análise por jogo rececionado
    analise = macos_comprados.groupby('Jogo Rececionado').agg({
        'Qt Maços': 'sum',
        'Vendas ilíquidas (€)': 'sum',
        'Valor (€)': 'sum'
    }).reset_index()

    analise['Média por Maço'] = analise['Valor (€)'] / analise['Qt Maços']
    analise = analise.sort_values('Qt Maços', ascending=False)

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Quantidade de Maços por Jogo', 'Rentabilidade Média por Maço'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}]]
    )

    fig.add_trace(
        go.Bar(
            x=analise['Jogo Rececionado'],
            y=analise['Qt Maços'],
            name='Maços Comprados',
            marker_color='#1f77b4'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=analise['Jogo Rececionado'],
            y=analise['Média por Maço'],
            name='€ por Maço',
            marker_color='#2ca02c'
        ),
        row=1, col=2
    )

    fig.update_layout(
        title="Análise de Maços de Raspadinhas",
        height=500,
        showlegend=False
    )

    fig.update_xaxes(title_text="Jogo Rececionado", row=1, col=1)
    fig.update_xaxes(title_text="Jogo Rececionado", row=1, col=2)
    fig.update_yaxes(title_text="Quantidade", row=1, col=1)
    fig.update_yaxes(title_text="Valor (€)", row=1, col=2)

    return fig


def criar_grafico_dia_semana(df):
    """Cria gráfico de vendas por dia da semana."""
    ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    nomes_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

    vendas_dia = df.groupby('Dia_Semana').agg({
        'Vendas ilíquidas (€)': 'sum',
        'Remunerações (€)': 'sum',
        'Valor (€)': 'sum'
    }).reindex(ordem_dias).reset_index()

    vendas_dia['Dia_PT'] = nomes_pt

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=vendas_dia['Dia_PT'],
        y=vendas_dia['Vendas ilíquidas (€)'],
        name='Vendas Ilíquidas',
        marker_color='#1f77b4'
    ))

    fig.add_trace(go.Bar(
        x=vendas_dia['Dia_PT'],
        y=vendas_dia['Remunerações (€)'],
        name='Remunerações',
        marker_color='#2ca02c'
    ))

    fig.update_layout(
        title="Vendas por Dia da Semana",
        xaxis_title="Dia da Semana",
        yaxis_title="Valor (€)",
        barmode='group',
        height=400
    )

    return fig


def criar_tabela_resumo(df):
    """Cria tabela resumo por categoria e jogo."""
    resumo = df.groupby(['Categoria', 'Jogo']).agg({
        'Vendas ilíquidas (€)': 'sum',
        'Remunerações (€)': 'sum',
        'Prémios (€)': 'sum',
        'Valor (€)': 'sum',
        'Data': 'count'
    }).reset_index()

    resumo.columns = ['Categoria', 'Jogo', 'Vendas Ilíquidas', 'Remunerações', 'Prémios Pagos', 'Valor Líquido', 'Nº Transações']

    # Calcular percentagens
    resumo['% Remuneração'] = (resumo['Remunerações'] / resumo['Vendas Ilíquidas'] * 100).round(2)
    resumo['% Prémios'] = (resumo['Prémios Pagos'] / resumo['Vendas Ilíquidas'] * 100).round(2)
    resumo['Margem %'] = (resumo['Valor Líquido'] / resumo['Vendas Ilíquidas'] * 100).round(2)

    resumo = resumo.sort_values('Vendas Ilíquidas', ascending=False)

    return resumo


def exportar_excel(df):
    """Exporta dados para Excel com formatação."""
    if not EXCEL_AVAILABLE:
        st.warning("Biblioteca openpyxl não disponível. Instalando...")
        return None

    output = BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Criar resumo
        resumo = criar_tabela_resumo(df)
        resumo.to_excel(writer, sheet_name='Resumo por Jogo', index=False)

        # Vendas por mês
        vendas_mes = df.groupby('Ano_Mes').agg({
            'Vendas ilíquidas (€)': 'sum',
            'Remunerações (€)': 'sum',
            'Prémios (€)': 'sum',
            'Valor (€)': 'sum'
        }).reset_index()
        vendas_mes.to_excel(writer, sheet_name='Vendas Mensais', index=False)

        # Análise de raspadinhas
        raspadinhas = df[df['Jogo'] == 'Raspadinha'].copy()
        if len(raspadinhas) > 0:
            analise_rasp = raspadinhas.groupby('Jogo Rececionado').agg({
                'Qt Maços': 'sum',
                'Vendas ilíquidas (€)': 'sum',
                'Remunerações (€)': 'sum',
                'Prémios (€)': 'sum',
                'Valor (€)': 'sum'
            }).reset_index()
            analise_rasp.to_excel(writer, sheet_name='Raspadinhas', index=False)

        # Dados completos
        df_export = df.drop(columns=['Ano', 'Mes', 'Semana_Ano', 'Trimestre'], errors='ignore')
        df_export.to_excel(writer, sheet_name='Dados Completos', index=False)

    output.seek(0)
    return output


# ============= PÁGINAS =============

def renderizar_indicadores_principais(df):
    """Renderiza os KPI cards principais."""
    st.markdown("### 💎 Indicadores Principais")

    col1, col2, col3, col4, col5 = st.columns(5)

    total_vendas = df['Vendas ilíquidas (€)'].sum()
    total_remuneracoes = df['Remunerações (€)'].sum()
    total_premios = df['Prémios (€)'].sum()
    total_liquido = df['Valor (€)'].sum()
    num_transacoes = len(df)

    with col1:
        st.markdown(f"""
        <div class="kpi-card-green">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Vendas Ilíquidas</div>
            <div class="kpi-value">{formatar_euro(total_vendas)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card-blue">
            <div class="kpi-icon">💵</div>
            <div class="kpi-label">Remunerações</div>
            <div class="kpi-value">{formatar_euro(total_remuneracoes)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card-orange">
            <div class="kpi-icon">🎁</div>
            <div class="kpi-label">Prémios Pagos</div>
            <div class="kpi-value">{formatar_euro(total_premios)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card-yellow">
            <div class="kpi-icon">💎</div>
            <div class="kpi-label">Prestações</div>
            <div class="kpi-value">{formatar_euro(total_liquido)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card-purple">
            <div class="kpi-icon">📊</div>
            <div class="kpi-label">Transações</div>
            <div class="kpi-value">{num_transacoes:,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Métricas adicionais com cards
    col1, col2 = st.columns(2)

    remuneracao_pct = (total_remuneracoes / total_vendas * 100) if total_vendas > 0 else 0
    premios_pct = (total_premios / total_vendas * 100) if total_vendas > 0 else 0

    with col1:
        st.markdown(f"""
        <div class="kpi-card-blue">
            <div class="kpi-icon">💼</div>
            <div class="kpi-label">% Remuneração</div>
            <div class="kpi-value">{remuneracao_pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card-orange">
            <div class="kpi-icon">🎯</div>
            <div class="kpi-label">% Prémios</div>
            <div class="kpi-value">{premios_pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()


def pagina_visao_geral(df):
    """Página Visão Geral."""

    # Tabs para diferentes análises
    tab1, tab2 = st.tabs(["📈 Evolução Temporal", "🎰 Por Categoria"])

    with tab1:
        st.subheader("Evolução Temporal")

        col1, col2 = st.columns(2)
        with col1:
            periodo = st.radio("Período", ["Mes", "Semana"], horizontal=True)

        fig_tempo = criar_grafico_vendas_tempo(df, periodo)
        st.plotly_chart(fig_tempo, use_container_width=True, key="visao_geral_evolucao_temporal")

    with tab2:
        st.subheader("Vendas por Categoria")
        fig_cat = criar_grafico_categoria(df)
        st.plotly_chart(fig_cat, use_container_width=True, key="visao_geral_vendas_por_categoria")


def pagina_por_categoria(df):
    """Página Análise por Categoria."""


    # Tabs para diferentes análises
    tab1, tab2, tab3 = st.tabs(["📊 Resumo", "🥧 Distribuição", "📈 Evolução"])

    with tab1:
        st.subheader("Resumo por Categoria")

        # Resumo por categoria
        resumo_cat = df.groupby('Categoria').agg({
            'Vendas ilíquidas (€)': 'sum',
            'Remunerações (€)': 'sum',
            'Prémios (€)': 'sum',
            'Valor (€)': 'sum',
            'Data': 'count'
        }).reset_index()

        resumo_cat.columns = ['Categoria', 'Vendas Ilíquidas', 'Remunerações', 'Prémios', 'Valor Líquido', 'Transações']
        resumo_cat['Margem %'] = (resumo_cat['Valor Líquido'] / resumo_cat['Vendas Ilíquidas'] * 100).round(2)
        resumo_cat = resumo_cat.sort_values('Vendas Ilíquidas', ascending=False)

        st.dataframe(resumo_cat, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Distribuição de Vendas")

        # Resumo para gráficos
        resumo_cat = df.groupby('Categoria').agg({
            'Vendas ilíquidas (€)': 'sum',
            'Remunerações (€)': 'sum',
            'Prémios (€)': 'sum',
            'Valor (€)': 'sum'
        }).reset_index()

        # Gráfico de pizza
        fig_pizza = px.pie(
            resumo_cat,
            values='Vendas ilíquidas (€)',
            names='Categoria',
            title='Distribuição de Vendas por Categoria',
            height=500
        )
        st.plotly_chart(fig_pizza, use_container_width=True, key="por_categoria_distribuicao_vendas")

    with tab3:
        st.subheader("Evolução por Categoria")

        # Evolução temporal por categoria
        vendas_cat_tempo = df.groupby(['Ano_Mes', 'Categoria'])['Vendas ilíquidas (€)'].sum().reset_index()

        fig = px.line(
            vendas_cat_tempo,
            x='Ano_Mes',
            y='Vendas ilíquidas (€)',
            color='Categoria',
            title='Evolução de Vendas por Categoria',
            markers=True,
            height=500
        )

        st.plotly_chart(fig, use_container_width=True, key="por_categoria_evolucao_vendas")


def pagina_por_jogo(df):
    """Página Análise por Jogo."""


    # Tabs para diferentes análises
    tab1, tab2 = st.tabs(["📊 Top Jogos", "📋 Detalhes Completos"])

    with tab1:
        st.subheader("Análise dos Melhores Jogos")

        col1, col2 = st.columns([1, 3])
        with col1:
            top_n = st.slider("Top N Jogos", 5, 20, 10)

        fig_jogo = criar_grafico_jogo(df, top_n)
        st.plotly_chart(fig_jogo, use_container_width=True, key="por_jogo_top_jogos")

    with tab2:
        st.subheader("Resumo Detalhado por Jogo")
        resumo = criar_tabela_resumo(df)
        st.dataframe(resumo, use_container_width=True, hide_index=True)


def pagina_raspadinhas(df):
    """Página Análise de Raspadinhas."""


    raspadinhas = df[df['Jogo'] == 'Raspadinha']

    if len(raspadinhas) == 0:
        st.info("Nenhum dado de raspadinhas encontrado no período selecionado.")
    else:
        # KPIs de raspadinhas
        col1, col2, col3, col4 = st.columns(4)

        total_macos = raspadinhas['Qt Maços'].sum()
        vendas_rasp = raspadinhas['Vendas ilíquidas (€)'].sum()
        premios_rasp = raspadinhas['Prémios (€)'].sum()
        liquido_rasp = raspadinhas['Valor (€)'].sum()

        with col1:
            st.metric("Total de Maços", f"{int(total_macos)}")

        with col2:
            st.metric("Vendas", formatar_euro(vendas_rasp))

        with col3:
            st.metric("Prémios Pagos", formatar_euro(premios_rasp))

        with col4:
            st.metric("Valor Líquido", formatar_euro(liquido_rasp))

        st.divider()

        # Tabs para diferentes análises
        tab1, tab2, tab3 = st.tabs(["📊 Por Jogo", "📦 Análise de Maços", "📋 Detalhes"])

        with tab1:
            st.subheader("Vendas por Jogo Rececionado")

            fig_rasp = criar_grafico_raspadinhas(df)
            if fig_rasp:
                st.plotly_chart(fig_rasp, use_container_width=True, key="raspadinhas_vendas_por_jogo")

        with tab2:
            st.subheader("Análise de Maços Comprados")

            fig_macos = criar_analise_macos(df)
            if fig_macos:
                st.plotly_chart(fig_macos, use_container_width=True, key="raspadinhas_analise_macos")
            else:
                st.info("Nenhum maço comprado no período selecionado.")

        with tab3:
            st.subheader("Detalhes por Jogo Rececionado")

            analise_rasp = raspadinhas.groupby('Jogo Rececionado').agg({
                'Qt Maços': 'sum',
                'Vendas ilíquidas (€)': 'sum',
                'Remunerações (€)': 'sum',
                'Prémios (€)': 'sum',
                'Valor (€)': 'sum',
                'Data': 'count'
            }).reset_index()

            analise_rasp.columns = ['Jogo Rececionado', 'Maços', 'Vendas', 'Remunerações', 'Prémios', 'Valor Líquido', 'Transações']
            analise_rasp = analise_rasp.sort_values('Vendas', ascending=False)

            st.dataframe(analise_rasp, use_container_width=True, hide_index=True)


def pagina_temporal(df):
    """Página Análise Temporal."""


    # Seletor de agrupamento
    col1, col2 = st.columns([1, 3])
    with col1:
        agrupamento = st.selectbox("Agrupar por", ["Mês", "Semana", "Dia da Semana", "Trimestre"])

    # Mapear seleção para coluna
    mapa_agrupamento = {
        "Mês": "Ano_Mes",
        "Semana": "Ano_Semana",
        "Dia da Semana": "Dia_Semana",
        "Trimestre": "Trimestre"
    }

    col_grupo = mapa_agrupamento[agrupamento]

    vendas_temporal = df.groupby(col_grupo).agg({
        'Vendas ilíquidas (€)': 'sum',
        'Remunerações (€)': 'sum',
        'Prémios (€)': 'sum',
        'Valor (€)': 'sum',
        'Data': 'count'
    }).reset_index()

    vendas_temporal.columns = [agrupamento, 'Vendas Ilíquidas', 'Remunerações', 'Prémios', 'Valor Líquido', 'Transações']

    # Tabs para diferentes análises
    tab1, tab2 = st.tabs(["📊 Tabela de Dados", "📈 Gráfico de Evolução"])

    with tab1:
        st.subheader(f"Dados por {agrupamento}")
        st.dataframe(vendas_temporal, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader(f"Evolução por {agrupamento}")

        # Gráfico de barras empilhadas
        fig_temporal = go.Figure()

        fig_temporal.add_trace(go.Bar(
            x=vendas_temporal[agrupamento],
            y=vendas_temporal['Vendas Ilíquidas'],
            name='Vendas Ilíquidas',
            marker_color='#1f77b4'
        ))

        fig_temporal.add_trace(go.Bar(
            x=vendas_temporal[agrupamento],
            y=vendas_temporal['Remunerações'],
            name='Remunerações',
            marker_color='#2ca02c'
        ))

        fig_temporal.add_trace(go.Bar(
            x=vendas_temporal[agrupamento],
            y=vendas_temporal['Prémios'],
            name='Prémios',
            marker_color='#d62728'
        ))

        fig_temporal.update_layout(
            title=f"Análise por {agrupamento}",
            xaxis_title=agrupamento,
            yaxis_title="Valor (€)",
            barmode='group',
            height=500
        )

        st.plotly_chart(fig_temporal, use_container_width=True, key="temporal_analise_por_agrupamento")


def pagina_premios(df):
    """Página Análise de Prémios."""


    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)

    total_premios = df['Prémios (€)'].sum()
    total_vendas = df['Vendas ilíquidas (€)'].sum()
    total_remuneracoes = df['Remunerações (€)'].sum()

    with col1:
        st.metric("Total Prémios Pagos", formatar_euro(total_premios))

    with col2:
        if total_vendas > 0:
            rtp = (total_premios / total_vendas * 100)
            st.metric("RTP (Return to Player)", f"{rtp:.2f}%")
        else:
            st.metric("RTP (Return to Player)", "N/A")

    with col3:
        if total_vendas > 0:
            taxa_retencao = 100 - (total_premios / total_vendas * 100)
            st.metric("Taxa de Retenção", f"{taxa_retencao:.2f}%")
        else:
            st.metric("Taxa de Retenção", "N/A")

    with col4:
        if total_remuneracoes > 0:
            razao = total_premios / total_remuneracoes
            st.metric("Prémios / Remunerações", f"{razao:.2f}x")
        else:
            st.metric("Prémios / Remunerações", "N/A")

    st.divider()

    # Tabs para diferentes análises
    tab1, tab2, tab3, tab4 = st.tabs(["🎮 Por Jogo", "🎰 Por Categoria", "📈 Evolução Temporal", "🎁 Raspadinhas com Prémios"])

    with tab1:
        st.subheader("Top 10 Jogos - Prémios Pagos")

        premios_jogo = df.groupby('Jogo').agg({
            'Prémios (€)': 'sum',
            'Vendas ilíquidas (€)': 'sum',
            'Valor (€)': 'sum'
        }).reset_index()

        premios_jogo['RTP %'] = (premios_jogo['Prémios (€)'] / premios_jogo['Vendas ilíquidas (€)'] * 100).round(2)
        premios_jogo = premios_jogo.sort_values('Prémios (€)', ascending=False).head(10)

        # Gráfico de barras
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=premios_jogo['Jogo'],
            y=premios_jogo['Prémios (€)'],
            name='Prémios Pagos',
            marker_color='#d62728'
        ))

        fig.update_layout(
            title="Top 10 Jogos - Prémios Pagos",
            xaxis_title="Jogo",
            yaxis_title="Prémios (€)",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True, key="premios_top_10_jogos")

        # Tabela detalhada
        st.dataframe(premios_jogo, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Prémios por Categoria")

        premios_cat = df.groupby('Categoria').agg({
            'Prémios (€)': 'sum',
            'Vendas ilíquidas (€)': 'sum'
        }).reset_index()

        premios_cat['RTP %'] = (premios_cat['Prémios (€)'] / premios_cat['Vendas ilíquidas (€)'] * 100).round(2)
        premios_cat = premios_cat.sort_values('Prémios (€)', ascending=False)

        # Gráfico de pizza
        fig_cat = px.pie(
            premios_cat,
            values='Prémios (€)',
            names='Categoria',
            title='Distribuição de Prémios por Categoria',
            height=400
        )

        st.plotly_chart(fig_cat, use_container_width=True, key="premios_distribuicao_categoria")

        st.dataframe(premios_cat, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Evolução Temporal de Prémios")

        premios_mes = df.groupby('Ano_Mes').agg({
            'Prémios (€)': 'sum',
            'Vendas ilíquidas (€)': 'sum'
        }).reset_index()

        premios_mes['RTP %'] = (premios_mes['Prémios (€)'] / premios_mes['Vendas ilíquidas (€)'] * 100).round(2)

        fig_tempo = go.Figure()

        fig_tempo.add_trace(go.Scatter(
            x=premios_mes['Ano_Mes'],
            y=premios_mes['Prémios (€)'],
            name='Prémios Pagos',
            mode='lines+markers',
            line=dict(color='#d62728', width=2)
        ))

        fig_tempo.add_trace(go.Scatter(
            x=premios_mes['Ano_Mes'],
            y=premios_mes['RTP %'],
            name='RTP %',
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=2),
            yaxis='y2'
        ))

        fig_tempo.update_layout(
            title="Evolução de Prémios e RTP ao Longo do Tempo",
            xaxis_title="Mês",
            yaxis_title="Prémios (€)",
            yaxis2=dict(
                title="RTP %",
                overlaying='y',
                side='right'
            ),
            height=500
        )

        st.plotly_chart(fig_tempo, use_container_width=True, key="premios_evolucao_temporal")

    with tab4:
        st.subheader("🎁 Análise de Rentabilidade de Raspadinhas")

        # Filtrar apenas raspadinhas
        raspadinhas = df[df['Jogo'] == 'Raspadinha'].copy()

        if len(raspadinhas) == 0:
            st.info("Nenhum dado de raspadinhas disponível.")
        else:
            # Data máxima para cálculo de períodos
            data_max = raspadinhas['Data'].max()

            # Definir períodos
            data_6_meses_atras = data_max - timedelta(days=180)
            data_2_meses_atras = data_max - timedelta(days=60)
            data_1_semana_atras = data_max - timedelta(days=7)

            # Análise Desde Sempre
            analise_sempre = raspadinhas.groupby('Jogo Rececionado').agg({
                'Qt Maços': 'sum',
                'Prémios (€)': 'sum',
                'Vendas ilíquidas (€)': 'sum',
                'Valor (€)': 'sum'
            }).reset_index()

            # Evitar divisão por zero
            analise_sempre['Prémios por Maço'] = analise_sempre.apply(
                lambda row: row['Prémios (€)'] / row['Qt Maços'] if row['Qt Maços'] > 0 else 0,
                axis=1
            )
            analise_sempre['Rentabilidade por Maço'] = analise_sempre.apply(
                lambda row: row['Valor (€)'] / row['Qt Maços'] if row['Qt Maços'] > 0 else 0,
                axis=1
            )

            # Filtrar apenas registos com Qt Maços > 0 para o ranking
            analise_sempre_valida = analise_sempre[analise_sempre['Qt Maços'] > 0].copy()
            # Top 10 por Prémios
            top_premios_sempre = analise_sempre_valida.sort_values('Prémios (€)', ascending=False).head(10)
            # Top 10 por Rentabilidade
            top_rentabilidade_sempre = analise_sempre_valida.sort_values('Rentabilidade por Maço', ascending=False).head(10)

            # Análise Últimos 6 Meses
            raspadinhas_6m = raspadinhas[raspadinhas['Data'] >= data_6_meses_atras]
            analise_6m = raspadinhas_6m.groupby('Jogo Rececionado').agg({
                'Qt Maços': 'sum',
                'Prémios (€)': 'sum',
                'Vendas ilíquidas (€)': 'sum',
                'Valor (€)': 'sum'
            }).reset_index()

            if len(analise_6m) > 0:
                # Evitar divisão por zero
                analise_6m['Prémios por Maço'] = analise_6m.apply(
                    lambda row: row['Prémios (€)'] / row['Qt Maços'] if row['Qt Maços'] > 0 else 0,
                    axis=1
                )
                analise_6m['Rentabilidade por Maço'] = analise_6m.apply(
                    lambda row: row['Valor (€)'] / row['Qt Maços'] if row['Qt Maços'] > 0 else 0,
                    axis=1
                )
                # Filtrar apenas registos com Qt Maços > 0 para o ranking
                analise_6m_valida = analise_6m[analise_6m['Qt Maços'] > 0].copy()
                if len(analise_6m_valida) > 0:
                    top_premios_6m = analise_6m_valida.sort_values('Prémios (€)', ascending=False).head(10)
                    top_rentabilidade_6m = analise_6m_valida.sort_values('Rentabilidade por Maço', ascending=False).head(10)
                else:
                    top_premios_6m = pd.DataFrame()
                    top_rentabilidade_6m = pd.DataFrame()
            else:
                analise_6m = pd.DataFrame()
                top_premios_6m = pd.DataFrame()
                top_rentabilidade_6m = pd.DataFrame()

            # Análise Últimos 2 Meses
            raspadinhas_2m = raspadinhas[raspadinhas['Data'] >= data_2_meses_atras]
            analise_2m = raspadinhas_2m.groupby('Jogo Rececionado').agg({
                'Qt Maços': 'sum',
                'Prémios (€)': 'sum',
                'Vendas ilíquidas (€)': 'sum',
                'Valor (€)': 'sum'
            }).reset_index()

            if len(analise_2m) > 0:
                # Evitar divisão por zero
                analise_2m['Prémios por Maço'] = analise_2m.apply(
                    lambda row: row['Prémios (€)'] / row['Qt Maços'] if row['Qt Maços'] > 0 else 0,
                    axis=1
                )
                analise_2m['Rentabilidade por Maço'] = analise_2m.apply(
                    lambda row: row['Valor (€)'] / row['Qt Maços'] if row['Qt Maços'] > 0 else 0,
                    axis=1
                )
                # Filtrar apenas registos com Qt Maços > 0 para o ranking
                analise_2m_valida = analise_2m[analise_2m['Qt Maços'] > 0].copy()
                if len(analise_2m_valida) > 0:
                    top_premios_2m = analise_2m_valida.sort_values('Prémios (€)', ascending=False).head(10)
                    top_rentabilidade_2m = analise_2m_valida.sort_values('Rentabilidade por Maço', ascending=False).head(10)
                else:
                    top_premios_2m = pd.DataFrame()
                    top_rentabilidade_2m = pd.DataFrame()
            else:
                analise_2m = pd.DataFrame()
                top_premios_2m = pd.DataFrame()
                top_rentabilidade_2m = pd.DataFrame()

            # Análise Última Semana (apenas hoje - data máxima)
            raspadinhas_1s = raspadinhas[raspadinhas['Data'] == data_max]
            analise_1s = raspadinhas_1s.groupby('Jogo Rececionado').agg({
                'Qt Maços': 'sum',
                'Prémios (€)': 'sum',
                'Vendas ilíquidas (€)': 'sum',
                'Valor (€)': 'sum'
            }).reset_index()

            if len(analise_1s) > 0:
                # Evitar divisão por zero
                analise_1s['Prémios por Maço'] = analise_1s.apply(
                    lambda row: row['Prémios (€)'] / row['Qt Maços'] if row['Qt Maços'] > 0 else 0,
                    axis=1
                )
                analise_1s['Rentabilidade por Maço'] = analise_1s.apply(
                    lambda row: row['Valor (€)'] / row['Qt Maços'] if row['Qt Maços'] > 0 else 0,
                    axis=1
                )
                # Filtrar apenas registos com Qt Maços > 0 para o ranking
                analise_1s_valida = analise_1s[analise_1s['Qt Maços'] > 0].copy()
                if len(analise_1s_valida) > 0:
                    top_premios_1s = analise_1s_valida.sort_values('Prémios (€)', ascending=False).head(10)
                    top_rentabilidade_1s = analise_1s_valida.sort_values('Rentabilidade por Maço', ascending=False).head(10)
                else:
                    top_premios_1s = pd.DataFrame()
                    top_rentabilidade_1s = pd.DataFrame()
            else:
                analise_1s = pd.DataFrame()
                top_premios_1s = pd.DataFrame()
                top_rentabilidade_1s = pd.DataFrame()

            # Sub-tabs para os períodos
            sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["📅 Desde Sempre", "📆 Últimos 6 Meses", "📊 Últimos 2 Meses", "📆 Última Semana"])

            with sub_tab1:
                st.markdown("#### 🎁 Análise Desde Sempre")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("##### 💰 Top 10 com Mais Prémios Pagos")

                    # Gráfico Prémios
                    fig_premios = go.Figure()
                    fig_premios.add_trace(go.Bar(
                        x=top_premios_sempre['Jogo Rececionado'],
                        y=top_premios_sempre['Prémios (€)'],
                        name='Prémios Totais (€)',
                        marker_color='#d62728',
                        text=top_premios_sempre['Prémios (€)'].apply(lambda x: f'{x:.0f}€'),
                        textposition='outside'
                    ))
                    fig_premios.update_layout(
                        title="Prémios Totais Pagos",
                        xaxis_title="Jogo Rececionado",
                        yaxis_title="Prémios (€)",
                        height=400,
                        showlegend=False
                    )
                    st.plotly_chart(fig_premios, use_container_width=True, key="raspadinhas_premios_desde_sempre")

                    # Tabela Prémios
                    tabela_premios = top_premios_sempre.copy()
                    tabela_premios['Prémios (€)'] = tabela_premios['Prémios (€)'].apply(lambda x: f"{x:.2f}€")
                    tabela_premios['Prémios por Maço'] = tabela_premios['Prémios por Maço'].apply(lambda x: f"{x:.2f}€")
                    tabela_premios['Qt Maços'] = tabela_premios['Qt Maços'].astype(int)
                    tabela_premios['Vendas ilíquidas (€)'] = tabela_premios['Vendas ilíquidas (€)'].apply(lambda x: f"{x:.2f}€")

                    st.dataframe(
                        tabela_premios[['Jogo Rececionado', 'Qt Maços', 'Prémios (€)', 'Prémios por Maço']],
                        use_container_width=True,
                        hide_index=True
                    )

                with col2:
                    st.markdown("##### 📈 Top 10 Mais Rentáveis")

                    # Gráfico Rentabilidade
                    fig_rent = go.Figure()
                    fig_rent.add_trace(go.Bar(
                        x=top_rentabilidade_sempre['Jogo Rececionado'],
                        y=top_rentabilidade_sempre['Rentabilidade por Maço'],
                        name='Rentabilidade (€)',
                        marker_color='#2ca02c',
                        text=top_rentabilidade_sempre['Rentabilidade por Maço'].apply(lambda x: f'{x:.2f}€'),
                        textposition='outside'
                    ))
                    fig_rent.update_layout(
                        title="Rentabilidade por Maço",
                        xaxis_title="Jogo Rececionado",
                        yaxis_title="Rentabilidade (€/Maço)",
                        height=400,
                        showlegend=False
                    )
                    st.plotly_chart(fig_rent, use_container_width=True, key="raspadinhas_rentabilidade_desde_sempre")

                    # Tabela Rentabilidade
                    tabela_rent = top_rentabilidade_sempre.copy()
                    tabela_rent['Rentabilidade por Maço'] = tabela_rent['Rentabilidade por Maço'].apply(lambda x: f"{x:.2f}€")
                    tabela_rent['Valor (€)'] = tabela_rent['Valor (€)'].apply(lambda x: f"{x:.2f}€")
                    tabela_rent['Qt Maços'] = tabela_rent['Qt Maços'].astype(int)

                    st.dataframe(
                        tabela_rent[['Jogo Rececionado', 'Qt Maços', 'Valor (€)', 'Rentabilidade por Maço']],
                        use_container_width=True,
                        hide_index=True
                    )

            with sub_tab2:
                if len(analise_6m) > 0:
                    st.markdown("#### 🎁 Análise Últimos 6 Meses")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("##### 💰 Top 10 com Mais Prémios Pagos")

                        # Gráfico Prémios
                        fig_premios = go.Figure()
                        fig_premios.add_trace(go.Bar(
                            x=top_premios_6m['Jogo Rececionado'],
                            y=top_premios_6m['Prémios (€)'],
                            name='Prémios Totais (€)',
                            marker_color='#ff7f0e',
                            text=top_premios_6m['Prémios (€)'].apply(lambda x: f'{x:.0f}€'),
                            textposition='outside'
                        ))
                        fig_premios.update_layout(
                            title="Prémios Totais Pagos",
                            xaxis_title="Jogo Rececionado",
                            yaxis_title="Prémios (€)",
                            height=400,
                            showlegend=False
                        )
                        st.plotly_chart(fig_premios, use_container_width=True, key="raspadinhas_premios_ultimos_6_meses")

                        # Tabela Prémios
                        tabela_premios = top_premios_6m.copy()
                        tabela_premios['Prémios (€)'] = tabela_premios['Prémios (€)'].apply(lambda x: f"{x:.2f}€")
                        tabela_premios['Prémios por Maço'] = tabela_premios['Prémios por Maço'].apply(lambda x: f"{x:.2f}€")
                        tabela_premios['Qt Maços'] = tabela_premios['Qt Maços'].astype(int)

                        st.dataframe(
                            tabela_premios[['Jogo Rececionado', 'Qt Maços', 'Prémios (€)', 'Prémios por Maço']],
                            use_container_width=True,
                            hide_index=True
                        )

                    with col2:
                        st.markdown("##### 📈 Top 10 Mais Rentáveis")

                        # Gráfico Rentabilidade
                        fig_rent = go.Figure()
                        fig_rent.update_layout(
                            title="Rentabilidade por Maço",
                            xaxis_title="Jogo Rececionado",
                            yaxis_title="Rentabilidade (€/Maço)",
                            height=400,
                            showlegend=False
                        )
                        st.plotly_chart(fig_rent, use_container_width=True, key="raspadinhas_rentabilidade_ultimos_6_meses")

                        # Tabela Rentabilidade
                        tabela_rent = top_rentabilidade_6m.copy()
                        tabela_rent['Rentabilidade por Maço'] = tabela_rent['Rentabilidade por Maço'].apply(lambda x: f"{x:.2f}€")
                        tabela_rent['Valor (€)'] = tabela_rent['Valor (€)'].apply(lambda x: f"{x:.2f}€")
                        tabela_rent['Qt Maços'] = tabela_rent['Qt Maços'].astype(int)

                        st.dataframe(
                            tabela_rent[['Jogo Rececionado', 'Qt Maços', 'Valor (€)', 'Rentabilidade por Maço']],
                            use_container_width=True,
                            hide_index=True
                        )
                else:
                    st.info("Nenhum dado disponível para os últimos 6 meses.")

            with sub_tab3:
                if len(analise_2m) > 0:
                    st.markdown("#### 🎁 Análise Últimos 2 Meses")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("##### 💰 Top 10 com Mais Prémios Pagos")

                        # Gráfico Prémios
                        fig_premios = go.Figure()
                        fig_premios.add_trace(go.Bar(
                            x=top_premios_2m['Jogo Rececionado'],
                            y=top_premios_2m['Prémios (€)'],
                            name='Prémios Totais (€)',
                            marker_color='#1f77b4',
                            text=top_premios_2m['Prémios (€)'].apply(lambda x: f'{x:.0f}€'),
                            textposition='outside'
                        ))
                        fig_premios.update_layout(
                            title="Prémios Totais Pagos",
                            xaxis_title="Jogo Rececionado",
                            yaxis_title="Prémios (€)",
                            height=400,
                            showlegend=False
                        )
                        st.plotly_chart(fig_premios, use_container_width=True, key="raspadinhas_premios_ultimos_2_meses")

                        # Tabela Prémios
                        tabela_premios = top_premios_2m.copy()
                        tabela_premios['Prémios (€)'] = tabela_premios['Prémios (€)'].apply(lambda x: f"{x:.2f}€")
                        tabela_premios['Prémios por Maço'] = tabela_premios['Prémios por Maço'].apply(lambda x: f"{x:.2f}€")
                        tabela_premios['Qt Maços'] = tabela_premios['Qt Maços'].astype(int)

                        st.dataframe(
                            tabela_premios[['Jogo Rececionado', 'Qt Maços', 'Prémios (€)', 'Prémios por Maço']],
                            use_container_width=True,
                            hide_index=True
                        )

                    with col2:
                        st.markdown("##### 📈 Top 10 Mais Rentáveis")

                        # Gráfico Rentabilidade
                        fig_rent = go.Figure()
                        fig_rent.update_layout(
                            title="Rentabilidade por Maço",
                            xaxis_title="Jogo Rececionado",
                            yaxis_title="Rentabilidade (€/Maço)",
                            height=400,
                            showlegend=False
                        )
                        st.plotly_chart(fig_rent, use_container_width=True, key="raspadinhas_rentabilidade_ultimos_2_meses")

                        # Tabela Rentabilidade
                        tabela_rent = top_rentabilidade_2m.copy()
                        tabela_rent['Rentabilidade por Maço'] = tabela_rent['Rentabilidade por Maço'].apply(lambda x: f"{x:.2f}€")
                        tabela_rent['Valor (€)'] = tabela_rent['Valor (€)'].apply(lambda x: f"{x:.2f}€")
                        tabela_rent['Qt Maços'] = tabela_rent['Qt Maços'].astype(int)

                        st.dataframe(
                            tabela_rent[['Jogo Rececionado', 'Qt Maços', 'Valor (€)', 'Rentabilidade por Maço']],
                            use_container_width=True,
                            hide_index=True
                        )
                else:
                    st.info("Nenhum dado disponível para os últimos 2 meses.")

            with sub_tab4:
                if len(analise_1s) > 0:
                    st.markdown("#### 🎁 Análise Última Semana")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("##### 💰 Top 10 com Mais Prémios Pagos")

                        # Gráfico Prémios
                        fig_premios = go.Figure()
                        fig_premios.add_trace(go.Bar(
                            x=top_premios_1s['Jogo Rececionado'],
                            y=top_premios_1s['Prémios (€)'],
                            name='Prémios Totais (€)',
                            marker_color='#9467bd',
                            text=top_premios_1s['Prémios (€)'].apply(lambda x: f'{x:.0f}€'),
                            textposition='outside'
                        ))
                        fig_premios.update_layout(
                            title="Prémios Totais Pagos",
                            xaxis_title="Jogo Rececionado",
                            yaxis_title="Prémios (€)",
                            height=400,
                            showlegend=False
                        )
                        st.plotly_chart(fig_premios, use_container_width=True, key="raspadinhas_premios_ultima_semana")

                        # Tabela Prémios
                        tabela_premios = top_premios_1s.copy()
                        tabela_premios['Prémios (€)'] = tabela_premios['Prémios (€)'].apply(lambda x: f"{x:.2f}€")
                        tabela_premios['Prémios por Maço'] = tabela_premios['Prémios por Maço'].apply(lambda x: f"{x:.2f}€")
                        tabela_premios['Qt Maços'] = tabela_premios['Qt Maços'].astype(int)

                        st.dataframe(
                            tabela_premios[['Jogo Rececionado', 'Qt Maços', 'Prémios (€)', 'Prémios por Maço']],
                            use_container_width=True,
                            hide_index=True
                        )

                    with col2:
                        st.markdown("##### 📈 Top 10 Mais Rentáveis")

                        # Gráfico Rentabilidade
                        fig_rent = go.Figure()
                        fig_rent.add_trace(go.Bar(
                            x=top_rentabilidade_1s['Jogo Rececionado'],
                            y=top_rentabilidade_1s['Rentabilidade por Maço'],
                            name='Rentabilidade (€)',
                            marker_color='#2ca02c',
                            text=top_rentabilidade_1s['Rentabilidade por Maço'].apply(lambda x: f'{x:.2f}€'),
                            textposition='outside'
                        ))
                        fig_rent.update_layout(
                            title="Rentabilidade por Maço",
                            xaxis_title="Jogo Rececionado",
                            yaxis_title="Rentabilidade (€/Maço)",
                            height=400,
                            showlegend=False
                        )
                        st.plotly_chart(fig_rent, use_container_width=True, key="raspadinhas_rentabilidade_ultima_semana")

                        # Tabela Rentabilidade
                        tabela_rent = top_rentabilidade_1s.copy()
                        tabela_rent['Rentabilidade por Maço'] = tabela_rent['Rentabilidade por Maço'].apply(lambda x: f"{x:.2f}€")
                        tabela_rent['Valor (€)'] = tabela_rent['Valor (€)'].apply(lambda x: f"{x:.2f}€")
                        tabela_rent['Qt Maços'] = tabela_rent['Qt Maços'].astype(int)

                        st.dataframe(
                            tabela_rent[['Jogo Rececionado', 'Qt Maços', 'Valor (€)', 'Rentabilidade por Maço']],
                            use_container_width=True,
                            hide_index=True
                        )
                else:
                    st.info("Nenhum dado disponível para a última semana.")


def pagina_prestacao_contas(df, df_prestacao):
    """Página Prestação de Contas - Listagem Semanal com Cruzamento de Dados."""

    if df_prestacao is None or len(df_prestacao) == 0:
        st.warning("Sem dados de prestação de contas disponíveis.")
        return

    st.markdown("## 📋 Prestação de Contas")
    st.markdown("### Listagem Semanal com Cruzamento de Dados")

    # Adicionar semana
    df_prestacoes = df_prestacao.copy()
    df_prestacoes['Data'] = pd.to_datetime(df_prestacoes['Data'])
    df_prestacoes['Semana'] = df_prestacoes['Data'].dt.isocalendar().week
    df_prestacoes['Ano'] = df_prestacoes['Data'].dt.year
    df_prestacoes['Ano_Semana'] = df_prestacoes['Ano'].astype(str) + '-W' + df_prestacoes['Semana'].astype(str).str.zfill(2)

    st.divider()

    # ==================== RESUMO POR SEMANA ====================
    st.markdown("### 📊 Resumo Semanal")

    resumo_semanal = df_prestacoes.groupby('Ano_Semana').agg({
        'Valor (€)': 'sum',
        'Data': ['min', 'max', 'count']
    }).reset_index()

    resumo_semanal.columns = ['Ano_Semana', 'Total_Prestado', 'Data_Inicio', 'Data_Fim', 'Num_Registos']
    resumo_semanal = resumo_semanal.sort_values('Ano_Semana', ascending=False)

    # Formatar para exibição
    resumo_semanal['Total_Prestado_Fmt'] = resumo_semanal['Total_Prestado'].apply(lambda x: f"{x:,.2f}€")
    resumo_semanal['Data_Inicio_Fmt'] = resumo_semanal['Data_Inicio'].dt.strftime('%d-%m-%Y')
    resumo_semanal['Data_Fim_Fmt'] = resumo_semanal['Data_Fim'].dt.strftime('%d-%m-%Y')

    st.dataframe(
        resumo_semanal[['Ano_Semana', 'Data_Inicio_Fmt', 'Data_Fim_Fmt', 'Total_Prestado_Fmt', 'Num_Registos']],
        use_container_width=True,
        hide_index=True,
        column_config={
            'Ano_Semana': st.column_config.TextColumn('Semana'),
            'Data_Inicio_Fmt': st.column_config.TextColumn('Início'),
            'Data_Fim_Fmt': st.column_config.TextColumn('Fim'),
            'Total_Prestado_Fmt': st.column_config.TextColumn('Total Prestado'),
            'Num_Registos': st.column_config.NumberColumn('Nº Registos')
        }
    )

    st.divider()

    # ==================== DETALHAMENTO POR SEMANA ====================
    st.markdown("### 📈 Detalhes por Semana")

    semanas = sorted(resumo_semanal['Ano_Semana'].unique(), reverse=True)
    semana_selecionada = st.selectbox("Seleccione a semana:", semanas)

    df_semana = df_prestacoes[df_prestacoes['Ano_Semana'] == semana_selecionada].copy()
    df_semana = df_semana.sort_values('Data', ascending=False)

    # Extrair número da semana para filtrar todo o dataframe
    num_semana = int(semana_selecionada.split('-W')[1])
    ano_semana = int(semana_selecionada.split('-W')[0])

    # Dados agregados da semana
    col1, col2, col3, col4 = st.columns(4)

    total_semana = df_semana['Valor (€)'].sum()

    # Filtrar por semana e ano - garantir que Data é datetime
    df_temp = df.copy()
    df_temp['Data'] = pd.to_datetime(df_temp['Data'])

    df_semana_completa = df_temp[(df_temp['Data'].dt.isocalendar().week == num_semana) &
                                   (df_temp['Data'].dt.year == ano_semana) &
                                   (df_temp['Categoria'] != 'PRESTAÇÃO DE CONTAS')].copy()

    total_vendas_semana = df_semana_completa['Vendas ilíquidas (€)'].sum()
    total_premios_semana = df_semana_completa['Prémios (€)'].sum()
    total_remuneracoes_semana = df_semana_completa['Remunerações (€)'].sum()
    total_calculado_semana = total_vendas_semana - total_premios_semana - total_remuneracoes_semana

    with col1:
        st.metric("Prestado (CSV)", formatar_euro(total_semana))

    with col2:
        st.metric("Vendas Ilíquidas", formatar_euro(total_vendas_semana))

    with col3:
        st.metric("Prémios + Remun", formatar_euro(total_premios_semana + total_remuneracoes_semana))

    with col4:
        st.metric("Calculado", formatar_euro(total_calculado_semana))

    st.divider()

    # Tabela de detalhes da semana selecionada
    st.markdown(f"#### 📋 Registos da Semana {semana_selecionada}")

    df_semana_display = df_semana.copy()
    df_semana_display['Data'] = df_semana_display['Data'].dt.strftime('%d-%m-%Y')
    df_semana_display['Valor (€)'] = df_semana_display['Valor (€)'].apply(lambda x: f"{x:,.2f}€")

    st.dataframe(
        df_semana_display[['Data', 'Categoria', 'Valor (€)']],
        use_container_width=True,
        hide_index=True
    )


def pagina_dados_detalhados(df):
    """Página Dados Detalhados."""


    # Opção de exportação
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("📥 Exportar Excel"):
            excel_data = exportar_excel(df)
            if excel_data:
                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name=f"santa_casa_dados_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    # Tabs para diferentes análises
    tab1, tab2 = st.tabs(["📋 Dados Completos", "📊 Estatísticas"])

    with tab1:
        st.subheader("Todos os Dados")

        # Mostrar dados completos
        df_display = df.copy()
        df_display['Data'] = df_display['Data'].dt.strftime('%d-%m-%Y')

        st.dataframe(df_display, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Estatísticas Descritivas")

        stats = df[['Vendas ilíquidas (€)', 'Remunerações (€)', 'Prémios (€)', 'Valor (€)']].describe()
        st.dataframe(stats, use_container_width=True)


def pagina_dashboard_executivo(df):
    """Dashboard executivo profissional com KPIs e Top performant."""
    st.markdown('<h1 style="text-align: center; color: #1f77b4;">🎯 Dashboard Executivo</h1>', unsafe_allow_html=True)
    st.caption("📊 Visão executiva de alto nível com métricas-chave e top performers")

    # KPIs Executivos em Cards
    st.markdown("### 📊 KPIs Executivos")

    col1, col2, col3 = st.columns(3)

    total_vendas = df['Vendas ilíquidas (€)'].sum()
    total_remuneracoes = df['Remunerações (€)'].sum()
    total_liquido = df['Valor (€)'].sum()

    with col1:
        st.markdown(f"""
        <div class="kpi-card-green">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">Vendas Totais</div>
            <div class="kpi-value">{formatar_euro(total_vendas)}</div>
            <div class="kpi-delta">Receita bruta</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card-blue">
            <div class="kpi-icon">💵</div>
            <div class="kpi-label">Remunerações</div>
            <div class="kpi-value">{formatar_euro(total_remuneracoes)}</div>
            <div class="kpi-delta">Comissões</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card-yellow">
            <div class="kpi-icon">💎</div>
            <div class="kpi-label">Valor Líquido</div>
            <div class="kpi-value">{formatar_euro(total_liquido)}</div>
            <div class="kpi-delta">Lucro</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # Top 5 Jogos
    st.markdown("### 🏆 Top 5 Jogos por Vendas")

    top_jogos = df.groupby('Jogo')['Vendas ilíquidas (€)'].sum().sort_values(ascending=False).head(5).reset_index()

    col1, col2 = st.columns([1, 2])

    with col1:
        for idx, row in top_jogos.iterrows():
            medal = ["🥇", "🥈", "🥉", "🏅", "🏅"][idx]
            pct = (row['Vendas ilíquidas (€)'] / total_vendas * 100) if total_vendas > 0 else 0
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 15px; border-radius: 10px; margin-bottom: 10px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.2); color: white;">
                <div style="font-size: 1.5rem;">{medal} <strong>{row['Jogo']}</strong></div>
                <div style="font-size: 1.3rem; margin-top: 5px;">
                    {formatar_euro(row['Vendas ilíquidas (€)'])} <span style="font-size: 0.9rem; opacity: 0.9;">({pct:.1f}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        fig = go.Figure(go.Bar(
            x=top_jogos['Vendas ilíquidas (€)'],
            y=top_jogos['Jogo'],
            orientation='h',
            marker=dict(
                color=top_jogos['Vendas ilíquidas (€)'],
                colorscale='Blues',
                showscale=False
            ),
            text=top_jogos['Vendas ilíquidas (€)'].apply(lambda x: f'{x:,.0f}€'),
            textposition='outside'
        ))

        fig.update_layout(
            title="Comparação de Vendas",
            xaxis_title="Vendas (€)",
            yaxis_title="",
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True, key="dashboard_executivo_comparacao_vendas_top_jogos")

    st.divider()

    # Gráfico de Evolução Temporal
    st.markdown("### 📈 Evolução Temporal")

    df_temporal = df.copy()
    df_temporal['Ano_Mes'] = df_temporal['Data'].dt.to_period('M').astype(str)

    vendas_mes = df_temporal.groupby('Ano_Mes')['Vendas ilíquidas (€)'].sum().reset_index()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=vendas_mes['Ano_Mes'],
        y=vendas_mes['Vendas ilíquidas (€)'],
        mode='lines+markers',
        name='Vendas',
        line=dict(color='#667eea', width=3),
        marker=dict(size=8),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))

    fig.update_layout(
        title="Evolução de Vendas Mensais",
        xaxis_title="Mês",
        yaxis_title="Vendas (€)",
        height=400,
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True, key="dashboard_executivo_evolucao_vendas_mensais")

    st.divider()

    # Seção de Previsão vs Objetivos - Layout limpo como em dashboard_v6
    st.subheader("🔮 Previsão vs Objetivos")

    # Carregar objetivos guardados
    objetivos_guardados = carregar_objetivos()

    # Calcular tendências para todos os jogos
    df_trend = df.copy()
    vendas_por_jogo = df_trend.groupby('Jogo')['Vendas ilíquidas (€)'].sum().reset_index()
    vendas_por_jogo = vendas_por_jogo.sort_values('Vendas ilíquidas (€)', ascending=False)

    st.markdown("#### 🎯 Comparação: Atual vs Objetivo")

    for idx, row in vendas_por_jogo.iterrows():
        jogo = row['Jogo']
        vendas_total = row['Vendas ilíquidas (€)']

        # Calcular média semanal
        df_jogo = df_trend[df_trend['Jogo'] == jogo].sort_values('Data')
        vendas_semana_jogo = df_jogo.groupby('Data')['Vendas ilíquidas (€)'].sum()
        media_semana = vendas_semana_jogo.mean() if len(vendas_semana_jogo) > 0 else 0

        # Obter objetivo do CSV
        objetivo_semanal = objetivos_guardados.get(jogo, 0)

        # Projeção para 4 semanas e anual
        projecao_4sem = media_semana * 4
        projecao_anual = media_semana * 52

        # Calcular % de cumprimento vs objetivo
        pct_cumprimento = (media_semana / objetivo_semanal * 100) if objetivo_semanal > 0 else 0
        diferenca = media_semana - objetivo_semanal

        # Determinar status
        if objetivo_semanal == 0:
            status = "⚫ Sem Objetivo"
            status_tipo = "secondary"
        elif pct_cumprimento >= 100:
            status = "✅ Acima do Objetivo"
            status_tipo = "success"
        elif pct_cumprimento >= 90:
            status = "📈 Próximo do Objetivo"
            status_tipo = "info"
        else:
            status = "⚠️ Abaixo do Objetivo"
            status_tipo = "warning"

        # Mostrar métricas em colunas
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.metric(f"🎮 {jogo}", f"{media_semana:,.0f}€".replace(',', '.'), "Média/Sem")

        with col2:
            st.metric("🎯 Objetivo", f"{objetivo_semanal:,.0f}€".replace(',', '.'), "Meta/Sem")

        with col3:
            st.metric("📊 % Cumprimento", f"{pct_cumprimento:.1f}%", f"{diferenca:+.0f}€")

        with col4:
            st.metric("📅 Proj. 4 Sem", f"{projecao_4sem:,.0f}€".replace(',', '.'), "")

        with col5:
            st.metric("📈 Proj. Anual", f"{projecao_anual:,.0f}€".replace(',', '.'), "")

        with col6:
            st.metric("Status", status, "")

        # Info box com análise detalhada + gráfico
        col_txt, col_graf = st.columns([2.5, 1])

        with col_txt:
            if objetivo_semanal == 0:
                st.info(f"ℹ️ **{jogo}** - Sem objetivo definido para este ano")
            elif pct_cumprimento >= 100:
                objetivo_fmt = f"{objetivo_semanal:,.0f}€".replace(',', '.')
                projecao_fmt = f"{projecao_anual:,.0f}€".replace(',', '.')
                st.success(f"""
                ✅ **{jogo}** está **acima do objetivo**!
                - Objetivo semanal: {objetivo_fmt}
                - Projeção anual: {projecao_fmt}
                - Tendência: Excelente 🚀
                """)
            elif pct_cumprimento >= 90:
                objetivo_fmt = f"{objetivo_semanal:,.0f}€".replace(',', '.')
                media_fmt = f"{media_semana:,.0f}€".replace(',', '.')
                diferenca_fmt = f"{diferenca:+.0f}€"
                projecao_fmt = f"{projecao_anual:,.0f}€".replace(',', '.')
                st.info(f"""
                📈 **{jogo}** está **próximo do objetivo**!
                - Objetivo semanal: {objetivo_fmt}
                - Performance atual: {media_fmt} ({pct_cumprimento:.1f}%)
                - Diferença: {diferenca_fmt}
                - Projeção anual: {projecao_fmt}
                - Tendência: Bom desempenho 💪
                """)
            else:
                objetivo_fmt = f"{objetivo_semanal:,.0f}€".replace(',', '.')
                media_fmt = f"{media_semana:,.0f}€".replace(',', '.')
                diferenca_fmt = f"{diferenca:+.0f}€"
                projecao_fmt = f"{projecao_anual:,.0f}€".replace(',', '.')
                st.warning(f"""
                ⚠️ **{jogo}** está **abaixo do objetivo**.
                - Objetivo semanal: {objetivo_fmt}
                - Performance atual: {media_fmt} ({pct_cumprimento:.1f}%)
                - Diferença: {diferenca_fmt}
                - Projeção anual: {projecao_fmt}
                - Tendência: Necessário esforço adicional 💡
                """)

        # Pequeno gráfico ao lado
        with col_graf:
            if objetivo_semanal > 0:
                media_fmt = f'{media_semana:,.0f}€'.replace(',', '.')
                objetivo_fmt = f'{objetivo_semanal:,.0f}€'.replace(',', '.')
                fig_mini = go.Figure(data=[
                    go.Bar(
                        x=['Atual', 'Objetivo'],
                        y=[media_semana, objetivo_semanal],
                        text=[media_fmt, objetivo_fmt],
                        textposition='outside',
                        marker=dict(
                            color=['#1f77b4' if media_semana >= objetivo_semanal else '#ff7f0e', '#2ca02c'],
                            opacity=0.8
                        )
                    )
                ])
                fig_mini.update_layout(
                    showlegend=False,
                    height=200,
                    margin=dict(l=20, r=20, t=20, b=20),
                    yaxis_title='€',
                    xaxis_tickfont=dict(size=10),
                    font=dict(size=9)
                )
                st.plotly_chart(fig_mini, use_container_width=True, key=f"previsao_objetivo_mini_chart_{jogo}")

        st.divider()

        # Opção para editar objetivo do jogo
        with st.expander(f"✏️ Editar Objetivo - {jogo}"):
            novo_objetivo = st.number_input(
                f"Novo objetivo semanal para {jogo}",
                value=float(objetivo_semanal) if objetivo_semanal > 0 else 0.0,
                min_value=0.0,
                step=100.0,
                key=f"edit_objetivo_{jogo}"
            )

            if st.button(f"💾 Guardar Objetivo - {jogo}", key=f"btn_guardar_{jogo}"):
                objetivos_guardados[jogo] = novo_objetivo
                if guardar_objetivos(objetivos_guardados):
                    st.success(f"✅ Objetivo de {novo_objetivo:.0f}€ guardado para {jogo}!")
                    st.rerun()
                else:
                    st.error("Erro ao guardar objetivo")


def pagina_analise_semanal(df):
    """Análise semanal avançada com comparações e insights."""
    st.markdown('<h1 style="text-align: center; color: #1f77b4;">🔬 Análise Semanal Avançada</h1>', unsafe_allow_html=True)
    st.caption("📊 Análise detalhada semanal com comparações WoW e insights")

    # Verificar se temos dados suficientes
    datas_unicas = sorted(df['Data'].unique(), reverse=True)
    if len(datas_unicas) < 2:
        st.warning("⚠️ Dados insuficientes. São necessárias pelo menos 2 semanas.")
        return

    # Última e penúltima semana
    ultima_semana = datas_unicas[0]
    penultima_semana = datas_unicas[1]

    df_ultima = df[df['Data'] == ultima_semana]
    df_penultima = df[df['Data'] == penultima_semana]

    st.info(f"📅 **Última semana:** {ultima_semana.strftime('%d/%m/%Y')} | **Semana anterior:** {penultima_semana.strftime('%d/%m/%Y')}")

    # Tabs para diferentes análises
    tab1, tab2, tab3, tab4 = st.tabs(["📊 WoW (Week over Week)", "🔥 Heatmap Performance", "📈 Tendências", "💬 Comentários & Insights"])

    with tab1:
        st.markdown("### 📊 Comparação Week over Week")

        # Calcular vendas por jogo
        vendas_ultima = df_ultima.groupby('Jogo')['Vendas ilíquidas (€)'].sum().reset_index()
        vendas_penultima = df_penultima.groupby('Jogo')['Vendas ilíquidas (€)'].sum().reset_index()

        # Merge
        comparacao = vendas_ultima.merge(
            vendas_penultima,
            on='Jogo',
            how='outer',
            suffixes=(' Atual', ' Anterior')
        ).fillna(0)

        comparacao['Crescimento %'] = ((comparacao['Vendas ilíquidas (€) Atual'] - comparacao['Vendas ilíquidas (€) Anterior']) /
                                        comparacao['Vendas ilíquidas (€) Anterior'] * 100).replace([np.inf, -np.inf], 0).fillna(0)

        comparacao = comparacao.sort_values('Crescimento %', ascending=False)

        col1, col2 = st.columns(2)

        with col1:
            # Top crescimentos
            st.markdown("#### 🚀 Maiores Crescimentos")
            top_crescimento = comparacao.head(5)

            for idx, row in top_crescimento.iterrows():
                crescimento = row['Crescimento %']
                color = "#4caf50" if crescimento > 0 else "#f44336"
                st.markdown(f"""
                <div style="background: white; padding: 12px; border-radius: 8px;
                            margin-bottom: 8px; border-left: 4px solid {color};
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <div style="font-size: 1.1rem; font-weight: bold; color: #333;">{row['Jogo']}</div>
                    <div style="color: {color}; font-size: 1.3rem; font-weight: bold;">
                        {crescimento:+.1f}%
                    </div>
                    <div style="font-size: 0.9rem; color: #666;">
                        {formatar_euro(row['Vendas ilíquidas (€) Atual'])} vs {formatar_euro(row['Vendas ilíquidas (€) Anterior'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            # Gráfico de barras
            fig = go.Figure()

            colors = ['#4caf50' if x > 0 else '#f44336' for x in comparacao['Crescimento %']]

            fig.add_trace(go.Bar(
                x=comparacao['Jogo'],
                y=comparacao['Crescimento %'],
                marker_color=colors,
                text=comparacao['Crescimento %'].apply(lambda x: f'{x:+.1f}%'),
                textposition='outside'
            ))

            fig.add_hline(y=0, line_dash="dash", line_color="gray")

            fig.update_layout(
                title="Crescimento WoW por Jogo",
                xaxis_title="Jogo",
                yaxis_title="Crescimento (%)",
                height=400,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True, key="analise_semanal_comparacao_vendas_wow")

    with tab2:
        st.markdown("### 🔥 Heatmap de Performance Semanal")

        # Criar heatmap das últimas 8 semanas
        ultimas_8_semanas = datas_unicas[:min(8, len(datas_unicas))]

        # Preparar dados para heatmap
        heatmap_data = []
        jogos_unicos = sorted(df['Jogo'].unique())

        for jogo in jogos_unicos:
            valores = []
            for data in reversed(ultimas_8_semanas):
                valor = df[(df['Data'] == data) & (df['Jogo'] == jogo)]['Vendas ilíquidas (€)'].sum()
                valores.append(valor)
            heatmap_data.append(valores)

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=[d.strftime('%d/%m') for d in reversed(ultimas_8_semanas)],
            y=jogos_unicos,
            colorscale='RdYlGn',
            text=np.array(heatmap_data).astype(int),
            texttemplate='%{text}€',
            textfont={"size": 10},
            colorbar=dict(title="Vendas (€)")
        ))

        fig.update_layout(
            title="Performance Semanal por Jogo (Últimas 8 Semanas)",
            xaxis_title="Semana",
            yaxis_title="Jogo",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True, key="analise_semanal_heatmap_performance")

        # Insights automáticos
        st.markdown("#### 💡 Insights Automáticos")

        # Jogo mais consistente
        std_devs = np.std(heatmap_data, axis=1)
        jogo_consistente = jogos_unicos[np.argmin(std_devs)]
        st.success(f"🎯 **Jogo mais consistente:** {jogo_consistente} (menor volatilidade)")

        # Jogo em crescimento
        tendencias = [sum(valores[-4:]) - sum(valores[:4]) for valores in heatmap_data]
        jogo_crescimento = jogos_unicos[np.argmax(tendencias)]
        st.info(f"📈 **Jogo em crescimento:** {jogo_crescimento} (últimas 4 semanas vs primeiras 4)")

    with tab3:
        st.markdown("### 📈 Análise de Tendências")

        # Gráfico de linha temporal por categoria
        df_temp = df.copy()
        df_temp = df_temp.sort_values('Data')

        vendas_categoria = df_temp.groupby(['Data', 'Categoria'])['Vendas ilíquidas (€)'].sum().reset_index()

        fig = px.line(
            vendas_categoria,
            x='Data',
            y='Vendas ilíquidas (€)',
            color='Categoria',
            title='Evolução de Vendas por Categoria',
            markers=True
        )

        fig.update_layout(
            xaxis_title="Data",
            yaxis_title="Vendas (€)",
            height=500,
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True, key="analise_semanal_tendencias_categoria")

        # Estatísticas por categoria
        st.markdown("#### 📊 Estatísticas por Categoria")

        stats_categoria = df.groupby('Categoria')['Vendas ilíquidas (€)'].agg(['sum', 'mean', 'std']).reset_index()
        stats_categoria.columns = ['Categoria', 'Total', 'Média', 'Desvio Padrão']
        stats_categoria['Total'] = stats_categoria['Total'].apply(lambda x: formatar_euro(x))
        stats_categoria['Média'] = stats_categoria['Média'].apply(lambda x: formatar_euro(x))
        stats_categoria['Desvio Padrão'] = stats_categoria['Desvio Padrão'].apply(lambda x: f'{x:.0f}€')

        st.dataframe(stats_categoria, use_container_width=True, hide_index=True)

    with tab4:
        st.markdown("### 💬 Análise Semanal - O que Correu Bem e Mal")

        # Carregar objetivos
        objetivos = carregar_objetivos()

        # Calcular métricas da última semana
        total_vendas_ultima = df_ultima['Vendas ilíquidas (€)'].sum()
        total_vendas_penultima = df_penultima['Vendas ilíquidas (€)'].sum()
        crescimento_geral = ((total_vendas_ultima - total_vendas_penultima) / total_vendas_penultima * 100) if total_vendas_penultima > 0 else 0

        # Análise por jogo
        vendas_ultima_jogo = df_ultima.groupby('Jogo')['Vendas ilíquidas (€)'].sum()
        vendas_penultima_jogo = df_penultima.groupby('Jogo')['Vendas ilíquidas (€)'].sum()

        # Calcular crescimento por jogo
        crescimento_jogo = {}
        objetivos_atingidos = {}

        for jogo in vendas_ultima_jogo.index:
            venda_atual = vendas_ultima_jogo.get(jogo, 0)
            venda_anterior = vendas_penultima_jogo.get(jogo, 0)

            if venda_anterior > 0:
                crescimento_jogo[jogo] = ((venda_atual - venda_anterior) / venda_anterior * 100)
            else:
                crescimento_jogo[jogo] = 100 if venda_atual > 0 else 0

            # Verificar se atingiu objetivo
            objetivo = objetivos.get(jogo, 0)
            if objetivo > 0:
                percentagem_objetivo = (venda_atual / objetivo) * 100
                objetivos_atingidos[jogo] = percentagem_objetivo

        # Layout em colunas para melhor visualização
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### ✅ O que Correu Bem")
            st.markdown("")

            # Jogos com crescimento positivo
            jogos_crescimento_positivo = sorted(
                [(jogo, crescimento) for jogo, crescimento in crescimento_jogo.items() if crescimento > 0],
                key=lambda x: x[1],
                reverse=True
            )

            if jogos_crescimento_positivo:
                for jogo, crescimento in jogos_crescimento_positivo[:5]:
                    venda_atual = vendas_ultima_jogo.get(jogo, 0)
                    objetivo = objetivos.get(jogo, 0)
                    percentagem_obj = (venda_atual / objetivo * 100) if objetivo > 0 else 0

                    # Determinar emoji baseado na performance vs objetivo
                    if percentagem_obj >= 100:
                        emoji = "🎯"
                        status = "Objetivo atingido"
                    elif percentagem_obj >= 80:
                        emoji = "📈"
                        status = "Próximo do objetivo"
                    else:
                        emoji = "⬆️"
                        status = "Em crescimento"

                    st.markdown(f"""
                    <div style="background: #e8f5e9; padding: 12px; border-radius: 8px; margin-bottom: 10px;
                                border-left: 4px solid #4caf50;">
                        <div style="font-weight: bold; color: #2e7d32; font-size: 1rem;">{emoji} {jogo}</div>
                        <div style="color: #4caf50; font-size: 1.3rem; font-weight: bold;">+{crescimento:.1f}%</div>
                        <div style="font-size: 0.85rem; color: #555;">
                            {formatar_euro(venda_atual)} | {status} ({percentagem_obj:.0f}% do objetivo)
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Nenhum jogo teve crescimento positivo esta semana.")

        with col2:
            st.markdown("#### ❌ Áreas de Melhoria")
            st.markdown("")

            # Jogos com crescimento negativo ou objetivos não atingidos
            problemas = []

            for jogo, crescimento in crescimento_jogo.items():
                if crescimento < 0:
                    problemas.append((jogo, "Queda", crescimento))
                elif objetivos.get(jogo, 0) > 0:
                    venda_atual = vendas_ultima_jogo.get(jogo, 0)
                    percentagem_obj = (venda_atual / objetivos.get(jogo, 0)) * 100
                    if percentagem_obj < 100:
                        problemas.append((jogo, "Objetivo Baixo", percentagem_obj - 100))

            problemas.sort(key=lambda x: x[2])

            if problemas:
                for jogo, tipo, valor in problemas[:5]:
                    venda_atual = vendas_ultima_jogo.get(jogo, 0)
                    objetivo = objetivos.get(jogo, 0)
                    percentagem_obj = (venda_atual / objetivo * 100) if objetivo > 0 else 0

                    if tipo == "Queda":
                        emoji = "📉"
                        mensagem = f"{valor:.1f}% de queda"
                    else:
                        emoji = "⚠️"
                        falta = objetivo - venda_atual
                        mensagem = f"Faltam {formatar_euro(falta)} ({percentagem_obj:.0f}% do objetivo)"

                    st.markdown(f"""
                    <div style="background: #ffebee; padding: 12px; border-radius: 8px; margin-bottom: 10px;
                                border-left: 4px solid #f44336;">
                        <div style="font-weight: bold; color: #c62828; font-size: 1rem;">{emoji} {jogo}</div>
                        <div style="color: #f44336; font-size: 1rem; font-weight: bold;">{mensagem}</div>
                        <div style="font-size: 0.85rem; color: #555;">
                            Vendas: {formatar_euro(venda_atual)} | Objetivo: {formatar_euro(objetivo)}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("Todos os jogos atingiram os objetivos! 🎉")

        st.divider()

        # Resumo Executivo
        st.markdown("#### 📋 Resumo Executivo da Semana")

        col_res1, col_res2, col_res3, col_res4 = st.columns(4)

        with col_res1:
            st.metric(
                "Total Vendas",
                formatar_euro(total_vendas_ultima),
                f"{crescimento_geral:+.1f}%"
            )

        with col_res2:
            objectivos_atingidos_count = sum(1 for j, p in objetivos_atingidos.items() if p >= 100)
            total_jogos = len(objetivos_atingidos) if objetivos_atingidos else 1
            st.metric(
                "Objetivos Atingidos",
                f"{objectivos_atingidos_count}/{total_jogos}",
                f"{(objectivos_atingidos_count/total_jogos*100):.0f}%"
            )

        with col_res3:
            jogos_crescimento = sum(1 for c in crescimento_jogo.values() if c > 0)
            st.metric(
                "Jogos em Crescimento",
                f"{jogos_crescimento}/{len(crescimento_jogo)}",
                f"{(jogos_crescimento/len(crescimento_jogo)*100):.0f}%"
            )

        with col_res4:
            if crescimento_geral > 5:
                tendencia = "📈 Positiva"
                delta = f"+{crescimento_geral:.1f}%"
            elif crescimento_geral < -5:
                tendencia = "📉 Negativa"
                delta = f"{crescimento_geral:.1f}%"
            else:
                tendencia = "➡️ Estável"
                delta = f"{crescimento_geral:+.1f}%"

            st.metric(
                "Tendência",
                tendencia,
                delta
            )

        st.divider()

        # Comentários detalhados
        st.markdown("#### 🎯 Análise Detalhada")

        analise_text = []

        # Análise geral
        if crescimento_geral > 5:
            analise_text.append("✅ **Semana positiva**: O crescimento geral foi superior a 5%, indicando boa performance.")
        elif crescimento_geral < -5:
            analise_text.append("⚠️ **Semana desafiante**: Houve uma queda geral nas vendas. Recomenda-se investigação sobre as causas.")
        else:
            analise_text.append("➡️ **Semana estável**: O crescimento foi próximo de zero, mantendo a performance anterior.")

        # Jogos destaques
        if jogos_crescimento_positivo:
            top_jogo = jogos_crescimento_positivo[0][0]
            top_crescimento = jogos_crescimento_positivo[0][1]
            analise_text.append(f"🚀 **Destaque positivo**: {top_jogo} teve o melhor desempenho com crescimento de {top_crescimento:.1f}%.")

        # Preocupações
        jogos_queda = [jogo for jogo, c in crescimento_jogo.items() if c < -10]
        if jogos_queda:
            analise_text.append(f"📉 **Preocupações**: {', '.join(jogos_queda)} tiveram queda significativa (>10%).")

        # Objetivos
        objectivos_nao_atingidos = [(j, p) for j, p in objetivos_atingidos.items() if p < 100]
        if objectivos_nao_atingidos:
            pior_jogo, pior_perc = min(objectivos_nao_atingidos, key=lambda x: x[1])
            analise_text.append(f"⚠️ **Objetivo crítico**: {pior_jogo} atingiu apenas {pior_perc:.0f}% do objetivo semanal.")

        for texto in analise_text:
            st.markdown(f"• {texto}")


def pagina_comparacoes_avancadas(df_base, jogos_selecionados=None):
    """Análise avançada com comparações MoM, YoY e previsões."""
    st.markdown('<h1 style="text-align: center; color: #1f77b4;">📊 Comparações Avançadas</h1>', unsafe_allow_html=True)
    st.caption("Análise profunda de tendências com comparações temporais")

    if not jogos_selecionados:
        jogos_unicos = sorted(df_base['Jogo'].unique())
        jogos_selecionados = jogos_unicos[:3] if len(jogos_unicos) > 3 else jogos_unicos

    if not jogos_selecionados:
        st.warning("Por favor, selecione pelo menos um jogo para análise.")
        return

    df_filtrado = df_base[df_base['Jogo'].isin(jogos_selecionados)]

    # Tabs para diferentes análises
    tab1, tab2, tab3, tab4 = st.tabs(["📈 MoM (Mês a Mês)", "📅 YoY (Ano a Ano)", "📆 Semana a Semana", "🔮 Previsão"])

    with tab1:
        st.markdown("### 📈 Análise Mês a Mês (MoM)")

        # Preparar dados mensais
        df_mes = df_filtrado.copy()
        df_mes['Ano_Mes'] = df_mes['Data'].dt.to_period('M').astype(str)
        vendas_mes = df_mes.groupby(['Ano_Mes', 'Jogo'])['Vendas ilíquidas (€)'].sum().reset_index()

        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de Vendas Mensais
            fig = px.line(
                vendas_mes,
                x='Ano_Mes',
                y='Vendas ilíquidas (€)',
                color='Jogo',
                title='Vendas Mensais por Jogo',
                markers=True
            )
            fig.update_layout(height=400, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Crescimento MoM %
            vendas_mes['Vendas_Anterior'] = vendas_mes.groupby('Jogo')['Vendas ilíquidas (€)'].shift(1)
            vendas_mes['Crescimento_MoM'] = ((vendas_mes['Vendas ilíquidas (€)'] - vendas_mes['Vendas_Anterior']) /
                                              vendas_mes['Vendas_Anterior'] * 100).fillna(0)

            fig = px.bar(
                vendas_mes.dropna(subset=['Crescimento_MoM']),
                x='Ano_Mes',
                y='Crescimento_MoM',
                color='Jogo',
                title='Crescimento MoM (%)',
                barmode='group'
            )
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.markdown("### 📅 Análise Ano a Ano (YoY)")

        # Preparar dados por mês do ano
        df_yoy = df_filtrado.copy()
        df_yoy['Mes'] = df_yoy['Data'].dt.month
        df_yoy['Ano'] = df_yoy['Data'].dt.year
        vendas_yoy = df_yoy.groupby(['Ano', 'Mes', 'Jogo'])['Vendas ilíquidas (€)'].sum().reset_index()
        vendas_yoy['Mes_Nome'] = pd.to_datetime(vendas_yoy['Mes'].astype(str), format='%m').dt.strftime('%B')

        col1, col2 = st.columns(2)

        with col1:
            # Comparação YoY por mês
            fig = px.line(
                vendas_yoy,
                x='Mes',
                y='Vendas ilíquidas (€)',
                color='Ano',
                facet_col='Jogo',
                facet_col_wrap=2,
                title='Vendas por Mês (Ano a Ano)',
                markers=True
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Tabela de comparação
            vendas_pivot = vendas_yoy.pivot_table(
                index='Mes_Nome',
                columns='Ano',
                values='Vendas ilíquidas (€)',
                aggfunc='sum'
            )
            vendas_pivot_formatted = vendas_pivot.map(lambda x: formatar_euro(x) if pd.notna(x) else '-')
            st.dataframe(vendas_pivot_formatted, use_container_width=True)

    with tab3:
        st.markdown("### 📆 Análise Semana a Semana")

        # Preparar dados semanais
        df_semana = df_filtrado.copy()
        vendas_semana = df_semana.groupby(['Data', 'Jogo'])['Vendas ilíquidas (€)'].sum().reset_index()
        vendas_semana = vendas_semana.sort_values('Data')

        col1, col2 = st.columns(2)

        with col1:
            # Vendas Semanais
            fig = px.line(
                vendas_semana,
                x='Data',
                y='Vendas ilíquidas (€)',
                color='Jogo',
                title='Vendas Semanais por Jogo',
                markers=True
            )
            fig.update_layout(height=400, hovermode='x unified')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Estatísticas por jogo
            stats_jogo = df_filtrado.groupby('Jogo')['Vendas ilíquidas (€)'].agg([
                ('Total', 'sum'),
                ('Média Semanal', 'mean'),
                ('Máximo', 'max'),
                ('Mínimo', 'min')
            ]).reset_index()

            stats_jogo['Total'] = stats_jogo['Total'].apply(formatar_euro)
            stats_jogo['Média Semanal'] = stats_jogo['Média Semanal'].apply(formatar_euro)
            stats_jogo['Máximo'] = stats_jogo['Máximo'].apply(formatar_euro)
            stats_jogo['Mínimo'] = stats_jogo['Mínimo'].apply(formatar_euro)

            st.dataframe(stats_jogo, use_container_width=True, hide_index=True)

    with tab4:
        st.markdown("### 🔮 Previsão de Objetivos")

        # Calcular tendências e fazer previsão simples
        df_trend = df_filtrado.copy()
        vendas_por_jogo = df_trend.groupby('Jogo')['Vendas ilíquidas (€)'].sum().reset_index()
        vendas_por_jogo = vendas_por_jogo.sort_values('Vendas ilíquidas (€)', ascending=False)

        st.markdown("#### 🎯 Top Jogos por Vendas e Projeção")

        for idx, row in vendas_por_jogo.head(5).iterrows():
            jogo = row['Jogo']
            vendas_total = row['Vendas ilíquidas (€)']

            # Calcular média semanal
            df_jogo = df_trend[df_trend['Jogo'] == jogo].sort_values('Data')
            vendas_semana_jogo = df_jogo.groupby('Data')['Vendas ilíquidas (€)'].sum()
            media_semana = vendas_semana_jogo.mean() if len(vendas_semana_jogo) > 0 else 0

            # Projeção para 4 semanas
            projecao_4sem = media_semana * 4
            projecao_anual = media_semana * 52

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(jogo, formatar_euro(vendas_total), "Total")
            with col2:
                st.metric("Média/Semana", formatar_euro(media_semana), "")
            with col3:
                st.metric("Projeção 4 Sem", formatar_euro(projecao_4sem), "")
            with col4:
                st.metric("Projeção Anual", formatar_euro(projecao_anual), "")

            st.divider()


# ============= INTERFACE PRINCIPAL =============

def main():
    st.markdown('<h1 class="main-header">Dashboard Santa Casa - Análise Completa 🎲</h1>', unsafe_allow_html=True)

    # Carregar dados
    result = carregar_dados()

    if result is None:
        st.error("Não foi possível carregar os dados.")
        return

    df, df_prestacao = result

    if df is None or len(df) == 0:
        st.error("Não foi possível carregar os dados.")
        return

    # Sidebar com filtros
    st.sidebar.header("Filtros")

    # Filtro de data
    min_date = df['Data'].min()
    max_date = df['Data'].max()

    # Botões rápidos para anos com Pills modernas
    st.sidebar.markdown("**⚡ Atalhos de Ano:**")

    anos_unicos = sorted(df['Data'].dt.year.unique())
    opcoes_anos = [str(ano) for ano in anos_unicos] + ["Todos"]

    # Determinar seleção padrão
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = datetime.now().year  # Abre por padrão no ano atual

    default_selection = str(st.session_state.selected_year) if st.session_state.selected_year else "Todos"

    ano_selecionado = st.sidebar.pills(
        "Selecionar período",
        options=opcoes_anos,
        default=default_selection,
        label_visibility="collapsed"
    )

    # Atualizar session_state baseado na seleção
    if ano_selecionado == "Todos":
        st.session_state.selected_year = None
    else:
        st.session_state.selected_year = int(ano_selecionado)

    # Aplicar filtro de ano rápido se selecionado
    if st.session_state.selected_year:
        ano = st.session_state.selected_year
        date_range = (pd.Timestamp(f"{ano}-01-01"), pd.Timestamp(f"{ano}-12-31"))
    else:
        date_range = st.sidebar.date_input(
            "Período",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    if len(date_range) == 2:
        df_filtrado = df[(df['Data'] >= pd.to_datetime(date_range[0])) &
                        (df['Data'] <= pd.to_datetime(date_range[1]))]
    else:
        df_filtrado = df

    # Filtro de categoria
    categorias = ['Todas'] + sorted(df_filtrado['Categoria'].unique().tolist())
    categoria_selecionada = st.sidebar.selectbox("Categoria", categorias)

    if categoria_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria_selecionada]

    # Filtro de jogo
    jogos = ['Todos'] + sorted(df_filtrado['Jogo'].unique().tolist())
    jogo_selecionado = st.sidebar.selectbox("Jogo", jogos)

    if jogo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Jogo'] == jogo_selecionado]

    # Container para Jogos para Análise (aparece no topo se Comparações Avançadas selecionado)
    container_jogos = st.sidebar.container()

    # ======== BOTÃO DE RESET ========
    st.sidebar.divider()
    if st.sidebar.button("🔄 Reset Total", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # ======== NAVEGAÇÃO ========
    st.sidebar.divider()
    pagina = st.sidebar.radio(
        "Navegação",
        ["📊 Visão Geral", "🎯 Dashboard Executivo", "🔬 Análise Semanal", "📊 Comparações Avançadas", "🎰 Por Categoria", "🎮 Por Jogo", "🎫 Raspadinhas", "📅 Temporal", "💰 Prémios", "📋 Prestação de Contas", "📋 Dados Detalhados"]
    )

    # Seletor de jogos para Comparações Avançadas (preenchido no container criado antes)
    comparacoes_jogos = None
    if pagina == "📊 Comparações Avançadas":
        with container_jogos:
            st.divider()
            st.markdown("**📍 Jogos para Análise:**")
            jogos_unicos = sorted(df['Jogo'].unique())
            comparacoes_jogos = st.multiselect(
                "Selecionar jogos:",
                jogos_unicos,
                default=jogos_unicos[:3] if len(jogos_unicos) > 3 else jogos_unicos,
                key="comparacoes_jogos_main"
            )

    # Mostrar Indicadores Principais apenas em Visão Geral (antes de Métricas)
    if pagina == "📊 Visão Geral":
        renderizar_indicadores_principais(df_filtrado)

    # ======== MÉTRICAS DE PERFORMANCE ========
    # Mostrar apenas em Visão Geral e Dashboard Executivo
    if pagina in ["📊 Visão Geral", "🎯 Dashboard Executivo"]:
        st.subheader("📊 Métricas de Performance")
        st.caption(f"📅 Dados atualizados até: {max_date.strftime('%d/%m/%Y')}")

        # Calcular períodos - cada data representa uma semana completa
        hoje = max_date

        # Obter datas únicas ordenadas (domingos)
        datas_unicas = sorted(df['Data'].unique(), reverse=True)

        # Performance Semanal
        if len(datas_unicas) >= 1:
            ultima_data = datas_unicas[0]
            df_ultima_semana = df[df['Data'] == ultima_data]
            valor_ultima_semana = df_ultima_semana['Vendas ilíquidas (€)'].sum()
        else:
            valor_ultima_semana = 0

        if len(datas_unicas) >= 2:
            penultima_data = datas_unicas[1]
            df_semana_anterior = df[df['Data'] == penultima_data]
            valor_semana_anterior = df_semana_anterior['Vendas ilíquidas (€)'].sum()
        else:
            valor_semana_anterior = 0

        # SWLY - mesma semana ISO do ano passado (ciclo semanal)
        semana_atual_iso = 0
        ano_anterior = hoje.year - 1

        if len(datas_unicas) >= 1:
            semana_atual_iso = ultima_data.isocalendar()[1]
            ano_anterior = ultima_data.year - 1

            # Procurar a mesma semana ISO no ano anterior
            semanas_ano_anterior = [d for d in datas_unicas if d.year == ano_anterior]
            swly_data_real = None
            for data in semanas_ano_anterior:
                if data.isocalendar()[1] == semana_atual_iso:
                    swly_data_real = data
                    break

            if swly_data_real:
                df_swly = df[df['Data'] == swly_data_real]
                valor_swly = df_swly['Vendas ilíquidas (€)'].sum()
            else:
                valor_swly = 0
        else:
            valor_swly = 0

        # Performance Mensal (por Ciclos Semanais)
        # Calcular quantas semanas do mês atual já foram faturadas
        mes_atual_inicio = hoje.replace(day=1)

        # Semanas do mês atual (até a data mais recente)
        semanas_mes_atual = [d for d in datas_unicas if d >= mes_atual_inicio and d <= hoje]
        num_semanas_mes_atual = len(semanas_mes_atual)
        valor_mes_atual = df[df['Data'].isin(semanas_mes_atual)]['Vendas ilíquidas (€)'].sum()

        # Mês anterior: mesma quantidade de semanas
        mes_anterior_inicio = (mes_atual_inicio - timedelta(days=1)).replace(day=1)
        mes_anterior_fim = mes_atual_inicio - timedelta(days=1)
        semanas_mes_anterior_todas = [d for d in datas_unicas if mes_anterior_inicio <= d <= mes_anterior_fim]
        # Pegar as primeiras N semanas do mês anterior
        semanas_mes_anterior = sorted(semanas_mes_anterior_todas)[:num_semanas_mes_atual]
        valor_mes_anterior = df[df['Data'].isin(semanas_mes_anterior)]['Vendas ilíquidas (€)'].sum()

        # SMLY: mesmo mês do ano passado, mesma quantidade de semanas
        smly_mes_inicio = mes_atual_inicio.replace(year=mes_atual_inicio.year - 1)
        smly_mes_fim = (mes_atual_inicio.replace(month=mes_atual_inicio.month % 12 + 1, day=1) if mes_atual_inicio.month < 12
                        else mes_atual_inicio.replace(year=mes_atual_inicio.year + 1, month=1, day=1)) - timedelta(days=1)
        smly_mes_fim = smly_mes_fim.replace(year=smly_mes_fim.year - 1)

        # Todas as semanas do mesmo mês do ano passado
        semanas_smly_todas = [d for d in datas_unicas if smly_mes_inicio <= d <= smly_mes_fim]
        # Pegar as primeiras N semanas (ordenadas cronologicamente)
        semanas_smly = sorted(semanas_smly_todas)[:num_semanas_mes_atual]
        valor_smly = df[df['Data'].isin(semanas_smly)]['Vendas ilíquidas (€)'].sum()

        # Performance Anual (por Ciclos Semanais)
        ano_atual_inicio = hoje.replace(month=1, day=1)
        ano_anterior_inicio = ano_atual_inicio.replace(year=ano_atual_inicio.year - 1)
        ano_anterior_fim = ano_atual_inicio - timedelta(days=1)

        # Semanas do ano atual (até a data mais recente)
        semanas_ano_atual = [d for d in datas_unicas if d >= ano_atual_inicio and d <= hoje]
        num_semanas_ano_atual = len(semanas_ano_atual)
        valor_ytd = df[df['Data'].isin(semanas_ano_atual)]['Vendas ilíquidas (€)'].sum()

        # Ano anterior: mesma quantidade de semanas
        semanas_ano_anterior_todas = [d for d in datas_unicas if ano_anterior_inicio <= d <= ano_anterior_fim]
        semanas_ano_anterior_ytd = sorted(semanas_ano_anterior_todas)[:num_semanas_ano_atual]
        valor_ano_anterior_ytd = df[df['Data'].isin(semanas_ano_anterior_ytd)]['Vendas ilíquidas (€)'].sum()

        # Ano anterior completo (todas as semanas)
        valor_ano_anterior_completo = df[df['Data'].isin(semanas_ano_anterior_todas)]['Vendas ilíquidas (€)'].sum()

        # Variações
        var_semana = ((valor_ultima_semana / valor_semana_anterior - 1) * 100) if valor_semana_anterior > 0 else 0
        var_swly = ((valor_ultima_semana / valor_swly - 1) * 100) if valor_swly > 0 else 0

        var_mes = ((valor_mes_atual / valor_mes_anterior - 1) * 100) if valor_mes_anterior > 0 else 0
        var_smly = ((valor_mes_atual / valor_smly - 1) * 100) if valor_smly > 0 else 0

        var_ytd = ((valor_ytd / valor_ano_anterior_ytd - 1) * 100) if valor_ano_anterior_ytd > 0 else 0

        # Layout em 3 colunas
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📅 Performance Semanal")
            semana_iso_texto = f"Semana {semana_atual_iso}" if len(datas_unicas) >= 1 else ""
            st.metric(f"Última Semana ({semana_iso_texto})", formatar_euro(valor_ultima_semana), f"{var_semana:+.1f}% vs Semana Anterior")
            st.metric("Semana Anterior", formatar_euro(valor_semana_anterior))
            st.metric(f"SWLY ({semana_iso_texto}/{ano_anterior})", formatar_euro(valor_swly), f"{var_swly:+.1f}% vs SWLY")

        with col2:
            st.markdown("### 📆 Performance Mensal")
            semana_texto = f"{num_semanas_mes_atual} semana{'s' if num_semanas_mes_atual != 1 else ''}"
            st.metric(f"Mês em Curso ({semana_texto})", formatar_euro(valor_mes_atual), f"{var_mes:+.1f}% vs Mês Anterior")
            st.metric(f"Mês Anterior (primeiras {semana_texto})", formatar_euro(valor_mes_anterior))
            st.metric(f"SMLY (primeiras {semana_texto})", formatar_euro(valor_smly), f"{var_smly:+.1f}% vs SMLY")

        with col3:
            st.markdown("### 📈 Performance Anual")
            semana_texto_anual = f"{num_semanas_ano_atual} semana{'s' if num_semanas_ano_atual != 1 else ''}"
            st.metric(f"Ano em Curso ({semana_texto_anual})", formatar_euro(valor_ytd), f"{var_ytd:+.1f}% vs Ano Anterior")
            st.metric(f"Ano Anterior (primeiras {semana_texto_anual})", formatar_euro(valor_ano_anterior_ytd))
            st.metric("Ano Anterior (Total)", formatar_euro(valor_ano_anterior_completo))

        st.divider()

    # Renderizar página selecionada
    if pagina == "📊 Visão Geral":
        pagina_visao_geral(df_filtrado)
    elif pagina == "🎯 Dashboard Executivo":
        pagina_dashboard_executivo(df_filtrado)
    elif pagina == "🔬 Análise Semanal":
        pagina_analise_semanal(df_filtrado)
    elif pagina == "📊 Comparações Avançadas":
        pagina_comparacoes_avancadas(df_filtrado, comparacoes_jogos if comparacoes_jogos else None)
    elif pagina == "🎰 Por Categoria":
        pagina_por_categoria(df_filtrado)
    elif pagina == "🎮 Por Jogo":
        pagina_por_jogo(df_filtrado)
    elif pagina == "🎫 Raspadinhas":
        pagina_raspadinhas(df_filtrado)
    elif pagina == "📅 Temporal":
        pagina_temporal(df_filtrado)
    elif pagina == "💰 Prémios":
        pagina_premios(df_filtrado)
    elif pagina == "📋 Prestação de Contas":
        pagina_prestacao_contas(df_filtrado, df_prestacao)
    elif pagina == "📋 Dados Detalhados":
        pagina_dados_detalhados(df_filtrado)

    # Footer
    st.divider()
    st.caption(f"Dashboard Santa Casa - Análise Completa | Dados atualizados até {max_date.strftime('%d-%m-%Y')}")


if __name__ == '__main__':
    # Configuração de autenticação
    config_file = Path(__file__).parent / 'config.yaml'

    # Verificar se o arquivo de configuração existe
    if not config_file.exists():
        st.error(f'Arquivo de configuração não encontrado: {config_file}')
        st.stop()

    with open(config_file) as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Criar objeto de autenticação
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Renderizar formulário de login
    try:
        authenticator.login()
    except Exception as e:
        st.error(f'Erro ao processar login: {e}')
        st.stop()

    # Verificar status de autenticação
    if st.session_state.get("authentication_status"):
        # Usuário autenticado - adicionar logout na sidebar
        authenticator.logout()
        st.sidebar.write(f'Bem-vindo, **{st.session_state["name"]}**!')

        # Executar aplicação principal
        main()

    elif st.session_state.get("authentication_status") is False:
        st.error('Utilizador ou password incorretos')
    elif st.session_state.get("authentication_status") is None:
        st.warning('Por favor, introduza as suas credenciais')
