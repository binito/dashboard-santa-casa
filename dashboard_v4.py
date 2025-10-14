"""
Dashboard Profissional v4 - Análise Completa de Vendas
Sistema avançado de análise de vendas com categorização inteligente
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from data_loader_v4 import DataLoaderV4
from product_categorizer import ProductCategorizer
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas - Café Martins",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS customizados
st.markdown("""
    <style>
    /* Estilos profissionais */
    .main {
        background-color: #f8f9fa;
    }

    /* Cards de métricas */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
        transition: transform 0.2s;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    /* Título principal */
    .main-title {
        color: #1f77b4;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }

    .subtitle {
        color: #666;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 40px;
    }

    /* Badges de categoria */
    .category-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 600;
        margin: 5px;
        color: white;
    }

    /* Separadores */
    .section-divider {
        margin: 30px 0;
        border-top: 2px solid #e0e0e0;
    }

    /* Tabs customizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background-color: white;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-weight: 600;
        color: #333 !important;
        font-size: 16px !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white !important;
    }

    /* Garantir que o texto das tabs é visível */
    .stTabs button div {
        color: inherit !important;
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: #f8f9fa;
    }

    /* Botões */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }

    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* Dataframe */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Loading spinner */
    .stSpinner > div {
        border-color: #1f77b4 !important;
    }

    /* Info boxes */
    .info-box {
        background: #e3f2fd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 15px 0;
    }

    .warning-box {
        background: #fff3e0;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 15px 0;
    }

    .success-box {
        background: #e8f5e9;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin: 15px 0;
    }
    </style>
""", unsafe_allow_html=True)


# Funções auxiliares
@st.cache_data(ttl=1800)
def carregar_dados():
    """Carrega dados com cache de 30 minutos"""
    with st.spinner("Carregando dados..."):
        loader = DataLoaderV4()
        df = loader.carregar_tudo_integrado()
        return df


def formatar_moeda(valor):
    """Formata valor em euros sem casas decimais"""
    return f"€ {valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")


def formatar_percentagem(valor):
    """Formata percentagem"""
    return f"{valor:.1f}%"


def calcular_delta(atual, anterior):
    """Calcula variação percentual"""
    if anterior == 0:
        return 0
    return ((atual - anterior) / anterior) * 100


def filtrar_dados(df, categorias, subcategorias, fontes, data_inicio, data_fim, apenas_dias_uteis):
    """Aplica filtros aos dados"""
    df_filtrado = df.copy()

    # Filtro de data
    df_filtrado = df_filtrado[
        (df_filtrado['Data'] >= pd.Timestamp(data_inicio)) &
        (df_filtrado['Data'] <= pd.Timestamp(data_fim))
    ]

    # Filtro de categoria
    if categorias:
        df_filtrado = df_filtrado[df_filtrado['Categoria'].isin(categorias)]

    # Filtro de subcategoria
    if subcategorias:
        df_filtrado = df_filtrado[df_filtrado['Subcategoria'].isin(subcategorias)]

    # Filtro de fonte
    if fontes:
        df_filtrado = df_filtrado[df_filtrado['Fonte'].isin(fontes)]

    # Filtro de dias úteis
    if apenas_dias_uteis:
        df_filtrado = df_filtrado[df_filtrado['Dia_Semana'] < 5]

    return df_filtrado


def calcular_metricas_periodo(df, periodo_dias):
    """Calcula métricas para um período específico"""
    data_fim = df['Data'].max()
    data_inicio = data_fim - timedelta(days=periodo_dias)

    df_periodo = df[df['Data'] >= data_inicio]

    return {
        'total': df_periodo['Valor'].sum(),
        'media_diaria': df_periodo.groupby('Data')['Valor'].sum().mean(),
        'quantidade': df_periodo['Qtd'].sum() if 'Qtd' in df_periodo.columns else 0,
        'vendas': len(df_periodo)
    }


def criar_grafico_pizza(df, coluna, titulo, mostrar_percentagem=True):
    """Cria gráfico de pizza profissional"""
    dados = df.groupby(coluna)['Valor'].sum().sort_values(ascending=False)

    fig = go.Figure(data=[go.Pie(
        labels=dados.index,
        values=dados.values,
        hole=0.4,
        textposition='auto',
        textinfo='label+percent' if mostrar_percentagem else 'label+value',
        marker=dict(line=dict(color='white', width=2))
    )])

    fig.update_layout(
        title=titulo,
        showlegend=True,
        height=400,
        margin=dict(t=50, b=20, l=20, r=20)
    )

    return fig


def criar_grafico_barras(df, x, y, titulo, orientacao='v', cor=None):
    """Cria gráfico de barras profissional"""
    fig = px.bar(
        df,
        x=x,
        y=y,
        title=titulo,
        orientation=orientacao,
        color=cor,
        text_auto='.2f'
    )

    fig.update_layout(
        height=400,
        showlegend=True if cor else False,
        margin=dict(t=50, b=50, l=50, r=50),
        xaxis_title=x,
        yaxis_title=y
    )

    fig.update_traces(texttemplate='€%{text:.2f}', textposition='outside')

    return fig


def criar_grafico_linha(df, x, y, titulo, cor=None):
    """Cria gráfico de linha profissional"""
    fig = px.line(
        df,
        x=x,
        y=y,
        title=titulo,
        color=cor,
        markers=True
    )

    fig.update_layout(
        height=400,
        showlegend=True if cor else False,
        margin=dict(t=50, b=50, l=50, r=50),
        hovermode='x unified'
    )

    return fig


def criar_heatmap(df, titulo):
    """Cria heatmap profissional"""
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale='Blues',
        text=df.values,
        texttemplate='€%{text:.0f}',
        textfont={"size": 10},
        colorbar=dict(title="Vendas (€)")
    ))

    fig.update_layout(
        title=titulo,
        height=500,
        margin=dict(t=50, b=50, l=100, r=50)
    )

    return fig


def criar_grafico_waterfall(valores, labels, titulo):
    """Cria gráfico waterfall"""
    fig = go.Figure(go.Waterfall(
        name="Contribuição",
        orientation="v",
        measure=["relative"] * (len(valores) - 1) + ["total"],
        x=labels,
        textposition="outside",
        text=[f"€{v:,.0f}" for v in valores],
        y=valores,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))

    fig.update_layout(
        title=titulo,
        showlegend=False,
        height=500,
        margin=dict(t=50, b=100, l=50, r=50)
    )

    return fig


# Interface principal
def main():
    # Cabeçalho
    st.markdown('<h1 class="main-title">☕ Dashboard de Vendas - Café Martins</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Análise Completa de Vendas com Categorização Inteligente</p>', unsafe_allow_html=True)

    # Carregar dados
    try:
        df = carregar_dados()
        categorizer = ProductCategorizer()
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return

    if df.empty:
        st.warning("Nenhum dado disponível.")
        return

    # Sidebar - Filtros
    st.sidebar.header("🔍 Filtros Avançados")

    # Filtro de data
    st.sidebar.subheader("📅 Período")
    data_min = df['Data'].min().date()
    data_max = df['Data'].max().date()

    col1, col2 = st.sidebar.columns(2)
    with col1:
        data_inicio = st.date_input(
            "Data Início",
            value=data_min,
            min_value=data_min,
            max_value=data_max
        )
    with col2:
        data_fim = st.date_input(
            "Data Fim",
            value=data_max,
            min_value=data_min,
            max_value=data_max
        )

    # Filtro de categoria
    st.sidebar.subheader("📂 Categorias")
    categorias_disponiveis = sorted(df['Categoria'].unique())
    categorias_selecionadas = st.sidebar.multiselect(
        "Selecionar Categorias",
        options=categorias_disponiveis,
        default=categorias_disponiveis
    )

    # Filtro de subcategoria (dependente da categoria)
    if categorias_selecionadas:
        subcategorias_disponiveis = sorted(
            df[df['Categoria'].isin(categorias_selecionadas)]['Subcategoria'].unique()
        )
        subcategorias_selecionadas = st.sidebar.multiselect(
            "Selecionar Subcategorias",
            options=subcategorias_disponiveis,
            default=[]
        )
    else:
        subcategorias_selecionadas = []

    # Filtro de fonte
    st.sidebar.subheader("📍 Fonte de Dados")
    fontes_disponiveis = sorted(df['Fonte'].unique())
    fontes_selecionadas = st.sidebar.multiselect(
        "Selecionar Fontes",
        options=fontes_disponiveis,
        default=fontes_disponiveis
    )

    # Opção de dias úteis
    st.sidebar.subheader("⚙️ Opções")
    apenas_dias_uteis = st.sidebar.checkbox("Mostrar apenas dias úteis", value=False)

    # Aplicar filtros
    df_filtrado = filtrar_dados(
        df,
        categorias_selecionadas,
        subcategorias_selecionadas,
        fontes_selecionadas,
        data_inicio,
        data_fim,
        apenas_dias_uteis
    )

    if df_filtrado.empty:
        st.warning("Nenhum dado disponível com os filtros selecionados.")
        return

    # Informações do filtro
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Registos filtrados:** {len(df_filtrado):,}")
    st.sidebar.markdown(f"**Total original:** {len(df):,}")
    st.sidebar.markdown(f"**Período:** {(data_fim - data_inicio).days + 1} dias")

    # Métricas principais
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Calcular métricas atuais
    total_vendas = df_filtrado['Valor'].sum()
    total_quantidade = df_filtrado['Qtd'].sum() if 'Qtd' in df_filtrado.columns else 0
    media_diaria = df_filtrado.groupby('Data')['Valor'].sum().mean()
    ticket_medio = total_vendas / total_quantidade if total_quantidade > 0 else 0

    # Calcular período anterior para comparação
    dias_periodo = (data_fim - data_inicio).days + 1
    data_inicio_anterior = data_inicio - timedelta(days=dias_periodo)
    data_fim_anterior = data_inicio - timedelta(days=1)

    df_anterior = filtrar_dados(
        df,
        categorias_selecionadas,
        subcategorias_selecionadas,
        fontes_selecionadas,
        data_inicio_anterior,
        data_fim_anterior,
        apenas_dias_uteis
    )

    if not df_anterior.empty:
        total_anterior = df_anterior['Valor'].sum()
        media_anterior = df_anterior.groupby('Data')['Valor'].sum().mean()
        qtd_anterior = df_anterior['Qtd'].sum() if 'Qtd' in df_anterior.columns else 0
        ticket_anterior = total_anterior / qtd_anterior if qtd_anterior > 0 else 0

        delta_total = calcular_delta(total_vendas, total_anterior)
        delta_media = calcular_delta(media_diaria, media_anterior)
        delta_ticket = calcular_delta(ticket_medio, ticket_anterior)
    else:
        delta_total = 0
        delta_media = 0
        delta_ticket = 0

    # Calcular taxa de crescimento mensal
    if 'Mes' in df_filtrado.columns:
        vendas_por_mes = df_filtrado.groupby('Mes')['Valor'].sum()
        if len(vendas_por_mes) >= 2:
            crescimento_mensal = calcular_delta(
                vendas_por_mes.iloc[-1],
                vendas_por_mes.iloc[-2]
            )
        else:
            crescimento_mensal = 0
    else:
        crescimento_mensal = 0

    # Exibir métricas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Total de Vendas",
            value=formatar_moeda(total_vendas),
            delta=f"{delta_total:+.1f}%" if delta_total != 0 else None
        )

    with col2:
        st.metric(
            label="📊 Média Diária",
            value=formatar_moeda(media_diaria),
            delta=f"{delta_media:+.1f}%" if delta_media != 0 else None
        )

    with col3:
        st.metric(
            label="🎯 Ticket Médio",
            value=formatar_moeda(ticket_medio),
            delta=f"{delta_ticket:+.1f}%" if delta_ticket != 0 else None
        )

    with col4:
        st.metric(
            label="📈 Crescimento Mensal",
            value=formatar_percentagem(crescimento_mensal),
            delta=f"{crescimento_mensal:+.1f}%"
        )

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Tabs principais
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Visão Geral",
        "☕ Análise por Categoria",
        "📈 Análise Temporal",
        "🎯 Performance & KPIs",
        "💰 Análise Financeira",
        "📊 Comparação & Benchmarks",
        "📑 Dados Detalhados"
    ])

    # TAB 1 - Visão Geral
    with tab1:
        st.header("📊 Visão Geral das Vendas")

        # KPIs por categoria
        st.subheader("🏆 Performance por Categoria")

        resumo_categorias = df_filtrado.groupby('Categoria').agg({
            'Valor': 'sum',
            'Qtd': 'sum',
            'Icone_Categoria': 'first'
        }).sort_values('Valor', ascending=False)

        cols = st.columns(min(4, len(resumo_categorias)))
        for idx, (categoria, row) in enumerate(resumo_categorias.head(8).iterrows()):
            col = cols[idx % 4]
            with col:
                percentual = (row['Valor'] / total_vendas) * 100
                st.metric(
                    label=f"{row['Icone_Categoria']} {categoria}",
                    value=formatar_moeda(row['Valor']),
                    delta=f"{formatar_percentagem(percentual)} do total"
                )

        st.markdown("---")

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            # Gráfico de pizza - Distribuição por categoria
            fig_pizza = criar_grafico_pizza(
                df_filtrado,
                'Categoria',
                '🥧 Distribuição de Vendas por Categoria'
            )
            st.plotly_chart(fig_pizza, use_container_width=True)

        with col2:
            # Top 10 produtos
            top_produtos = df_filtrado.groupby('Produto')['Valor'].sum().sort_values(ascending=True).tail(10)

            fig_top = go.Figure(go.Bar(
                x=top_produtos.values,
                y=top_produtos.index,
                orientation='h',
                text=[formatar_moeda(v) for v in top_produtos.values],
                textposition='auto',
                marker=dict(color='#1f77b4')
            ))

            fig_top.update_layout(
                title="🏆 Top 10 Produtos Mais Vendidos",
                height=400,
                margin=dict(t=50, b=50, l=200, r=50),
                xaxis_title="Vendas (€)",
                yaxis_title=""
            )

            st.plotly_chart(fig_top, use_container_width=True)

        # Evolução temporal
        st.subheader("📈 Evolução Temporal de Vendas")

        vendas_diarias = df_filtrado.groupby('Data')['Valor'].sum().reset_index()

        fig_evolucao = px.line(
            vendas_diarias,
            x='Data',
            y='Valor',
            title='Evolução Diária de Vendas',
            markers=True
        )

        fig_evolucao.update_layout(
            height=400,
            xaxis_title="Data",
            yaxis_title="Vendas (€)",
            hovermode='x unified'
        )

        fig_evolucao.add_hline(
            y=media_diaria,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Média: {formatar_moeda(media_diaria)}"
        )

        st.plotly_chart(fig_evolucao, use_container_width=True)

    # TAB 2 - Análise por Categoria
    with tab2:
        st.header("☕ Análise Detalhada por Categoria")

        # Seletor de categoria
        categoria_selecionada = st.selectbox(
            "Selecione uma categoria para análise detalhada:",
            options=sorted(df_filtrado['Categoria'].unique())
        )

        df_categoria = df_filtrado[df_filtrado['Categoria'] == categoria_selecionada]

        # Métricas da categoria
        col1, col2, col3, col4 = st.columns(4)

        total_cat = df_categoria['Valor'].sum()
        vendas_cat = len(df_categoria)
        media_cat = df_categoria['Valor'].mean()
        participacao_cat = (total_cat / total_vendas) * 100

        with col1:
            st.metric("💰 Total da Categoria", formatar_moeda(total_cat))

        with col2:
            st.metric("📊 Número de Vendas", f"{vendas_cat:,}")

        with col3:
            st.metric("📈 Média por Venda", formatar_moeda(media_cat))

        with col4:
            st.metric("🎯 Participação", formatar_percentagem(participacao_cat))

        st.markdown("---")

        # Análises da categoria
        col1, col2 = st.columns(2)

        with col1:
            # Top 10 subcategorias
            st.subheader(f"🏅 Top 10 Subcategorias")
            top_subcat = df_categoria.groupby('Subcategoria')['Valor'].sum().sort_values(ascending=True).tail(10)

            fig_subcat = go.Figure(go.Bar(
                x=top_subcat.values,
                y=top_subcat.index,
                orientation='h',
                text=[formatar_moeda(v) for v in top_subcat.values],
                textposition='auto',
                marker=dict(color='#2ca02c')
            ))

            fig_subcat.update_layout(
                height=400,
                xaxis_title="Vendas (€)",
                yaxis_title=""
            )

            st.plotly_chart(fig_subcat, use_container_width=True)

        with col2:
            # Distribuição por subcategoria
            fig_pizza_subcat = criar_grafico_pizza(
                df_categoria,
                'Subcategoria',
                '📊 Distribuição por Subcategoria'
            )
            st.plotly_chart(fig_pizza_subcat, use_container_width=True)

        # Top 20 produtos da categoria
        st.subheader(f"🌟 Top 20 Produtos - {categoria_selecionada}")

        top_produtos_cat = df_categoria.groupby('Produto').agg({
            'Valor': 'sum',
            'Qtd': 'sum',
            'Subcategoria': 'first'
        }).sort_values('Valor', ascending=False).head(20)

        top_produtos_cat['Valor'] = top_produtos_cat['Valor'].apply(formatar_moeda)
        top_produtos_cat['Qtd'] = top_produtos_cat['Qtd'].apply(lambda x: f"{x:,.0f}")

        st.dataframe(top_produtos_cat, use_container_width=True)

        # Evolução da categoria
        st.subheader(f"📈 Evolução Temporal - {categoria_selecionada}")

        evolucao_cat = df_categoria.groupby('Data')['Valor'].sum().reset_index()

        fig_evolucao_cat = px.area(
            evolucao_cat,
            x='Data',
            y='Valor',
            title=f'Evolução de Vendas - {categoria_selecionada}',
            color_discrete_sequence=['#1f77b4']
        )

        fig_evolucao_cat.update_layout(
            height=400,
            xaxis_title="Data",
            yaxis_title="Vendas (€)"
        )

        st.plotly_chart(fig_evolucao_cat, use_container_width=True)

    # TAB 3 - Análise Temporal
    with tab3:
        st.header("📈 Análise Temporal Avançada")

        # Seletor de granularidade
        granularidade = st.radio(
            "Selecione a granularidade:",
            options=['Diária', 'Semanal', 'Mensal'],
            horizontal=True
        )

        st.markdown("---")

        # Vendas por dia da semana
        st.subheader("📅 Vendas por Dia da Semana")

        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        df_filtrado['Dia_Semana_Nome'] = df_filtrado['Dia_Semana'].apply(lambda x: dias_semana[x])

        vendas_por_dia_semana = df_filtrado.groupby('Dia_Semana_Nome')['Valor'].sum()
        vendas_por_dia_semana = vendas_por_dia_semana.reindex(dias_semana)

        fig_dia_semana = px.bar(
            x=vendas_por_dia_semana.index,
            y=vendas_por_dia_semana.values,
            title='Vendas por Dia da Semana',
            labels={'x': 'Dia da Semana', 'y': 'Vendas (€)'},
            text=[formatar_moeda(v) for v in vendas_por_dia_semana.values],
            color=vendas_por_dia_semana.values,
            color_continuous_scale='Blues'
        )

        fig_dia_semana.update_layout(
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig_dia_semana, use_container_width=True)

        # Heatmap: Dia da semana vs Categoria
        st.subheader("🔥 Heatmap: Vendas por Dia da Semana e Categoria")

        heatmap_data = df_filtrado.pivot_table(
            values='Valor',
            index='Dia_Semana_Nome',
            columns='Categoria',
            aggfunc='sum',
            fill_value=0
        )

        heatmap_data = heatmap_data.reindex(dias_semana)

        fig_heatmap = criar_heatmap(heatmap_data, 'Distribuição de Vendas')
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Análise por hora (se disponível)
        if 'Data' in df_filtrado.columns:
            st.subheader("🕐 Análise por Hora do Dia")

            # Tentar extrair hora
            df_filtrado['Hora'] = df_filtrado['Data'].dt.hour

            if df_filtrado['Hora'].notna().any():
                vendas_por_hora = df_filtrado.groupby('Hora')['Valor'].sum()

                fig_hora = px.line(
                    x=vendas_por_hora.index,
                    y=vendas_por_hora.values,
                    title='Vendas por Hora do Dia',
                    labels={'x': 'Hora', 'y': 'Vendas (€)'},
                    markers=True
                )

                fig_hora.update_layout(height=400)
                st.plotly_chart(fig_hora, use_container_width=True)
            else:
                st.info("Informação de hora não disponível nos dados.")

        # Vendas por mês
        st.subheader("📆 Vendas por Mês")

        if 'Mes' in df_filtrado.columns and 'Ano' in df_filtrado.columns:
            df_filtrado['Mes_Ano'] = df_filtrado['Data'].dt.to_period('M').astype(str)
            vendas_por_mes = df_filtrado.groupby('Mes_Ano')['Valor'].sum().reset_index()

            fig_mes = px.bar(
                vendas_por_mes,
                x='Mes_Ano',
                y='Valor',
                title='Vendas Mensais',
                text=[formatar_moeda(v) for v in vendas_por_mes['Valor']],
                color='Valor',
                color_continuous_scale='Viridis'
            )

            fig_mes.update_layout(
                height=400,
                xaxis_title="Mês/Ano",
                yaxis_title="Vendas (€)",
                showlegend=False
            )

            st.plotly_chart(fig_mes, use_container_width=True)

        # Sazonalidade
        st.subheader("🌊 Análise de Sazonalidade")

        col1, col2 = st.columns(2)

        with col1:
            # Vendas por trimestre
            if 'Trimestre' in df_filtrado.columns:
                vendas_trimestre = df_filtrado.groupby('Trimestre')['Valor'].sum()

                fig_trimestre = px.pie(
                    values=vendas_trimestre.values,
                    names=[f'Q{i}' for i in vendas_trimestre.index],
                    title='Distribuição por Trimestre',
                    hole=0.4
                )

                fig_trimestre.update_layout(height=400)
                st.plotly_chart(fig_trimestre, use_container_width=True)

        with col2:
            # Vendas por semana
            if 'Semana' in df_filtrado.columns:
                vendas_semana = df_filtrado.groupby('Semana')['Valor'].sum().head(20)

                fig_semana = px.line(
                    x=vendas_semana.index,
                    y=vendas_semana.values,
                    title='Vendas por Semana (Top 20)',
                    labels={'x': 'Semana do Ano', 'y': 'Vendas (€)'},
                    markers=True
                )

                fig_semana.update_layout(height=400)
                st.plotly_chart(fig_semana, use_container_width=True)

    # TAB 4 - Performance & KPIs
    with tab4:
        st.header("🎯 Performance & KPIs Avançados")

        # Taxa de crescimento por categoria
        st.subheader("📊 Taxa de Crescimento por Categoria")

        if not df_anterior.empty:
            crescimento_cat = pd.DataFrame({
                'Atual': df_filtrado.groupby('Categoria')['Valor'].sum(),
                'Anterior': df_anterior.groupby('Categoria')['Valor'].sum()
            }).fillna(0)

            crescimento_cat['Crescimento (%)'] = crescimento_cat.apply(
                lambda row: calcular_delta(row['Atual'], row['Anterior']),
                axis=1
            )

            crescimento_cat = crescimento_cat.sort_values('Crescimento (%)', ascending=False)

            fig_crescimento = px.bar(
                x=crescimento_cat.index,
                y=crescimento_cat['Crescimento (%)'],
                title='Taxa de Crescimento por Categoria (vs Período Anterior)',
                labels={'x': 'Categoria', 'y': 'Crescimento (%)'},
                color=crescimento_cat['Crescimento (%)'],
                color_continuous_scale='RdYlGn',
                text=[f"{v:+.1f}%" for v in crescimento_cat['Crescimento (%)']]
            )

            fig_crescimento.update_layout(height=400, showlegend=False)
            fig_crescimento.add_hline(y=0, line_dash="dash", line_color="black")

            st.plotly_chart(fig_crescimento, use_container_width=True)
        else:
            st.info("Dados do período anterior não disponíveis para comparação.")

        st.markdown("---")

        # Análise de margem (Top vs Bottom performers)
        st.subheader("🏆 Top & Bottom Performers")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🥇 Top 10 Produtos**")
            top_performers = df_filtrado.groupby('Produto')['Valor'].sum().sort_values(ascending=False).head(10)

            for idx, (produto, valor) in enumerate(top_performers.items(), 1):
                percentual = (valor / total_vendas) * 100
                st.markdown(f"{idx}. **{produto}**: {formatar_moeda(valor)} ({percentual:.1f}%)")

        with col2:
            st.markdown("**📉 Bottom 10 Produtos**")
            bottom_performers = df_filtrado.groupby('Produto')['Valor'].sum().sort_values(ascending=True).head(10)

            for idx, (produto, valor) in enumerate(bottom_performers.items(), 1):
                percentual = (valor / total_vendas) * 100
                st.markdown(f"{idx}. **{produto}**: {formatar_moeda(valor)} ({percentual:.1f}%)")

        st.markdown("---")

        # Análise de Pareto (80/20)
        st.subheader("📈 Análise de Pareto (Regra 80/20)")

        vendas_produtos = df_filtrado.groupby('Produto')['Valor'].sum().sort_values(ascending=False)
        vendas_produtos_cum = vendas_produtos.cumsum() / vendas_produtos.sum() * 100

        # Encontrar onde atinge 80%
        produtos_80 = (vendas_produtos_cum <= 80).sum()
        percentual_produtos_80 = (produtos_80 / len(vendas_produtos)) * 100

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "🎯 Produtos que representam 80% das vendas",
                f"{produtos_80} produtos"
            )

        with col2:
            st.metric(
                "📊 Percentual do catálogo",
                formatar_percentagem(percentual_produtos_80)
            )

        with col3:
            total_produtos = len(vendas_produtos)
            st.metric(
                "📦 Total de produtos",
                f"{total_produtos} produtos"
            )

        # Gráfico de Pareto
        fig_pareto = go.Figure()

        fig_pareto.add_trace(go.Bar(
            x=list(range(1, min(51, len(vendas_produtos) + 1))),
            y=vendas_produtos.head(50).values,
            name='Vendas',
            yaxis='y',
            marker=dict(color='#1f77b4')
        ))

        fig_pareto.add_trace(go.Scatter(
            x=list(range(1, min(51, len(vendas_produtos_cum) + 1))),
            y=vendas_produtos_cum.head(50).values,
            name='Acumulado (%)',
            yaxis='y2',
            mode='lines+markers',
            marker=dict(color='#ff7f0e'),
            line=dict(width=2)
        ))

        # Linha horizontal em 80% no eixo secundário
        fig_pareto.add_shape(
            type="line",
            xref="paper", x0=0, x1=1,
            yref="y2", y0=80, y1=80,
            line=dict(color="red", width=2, dash="dash")
        )
        fig_pareto.add_annotation(
            x=0.5, xref="paper",
            y=80, yref="y2",
            text="80%",
            showarrow=False,
            bgcolor="white"
        )

        fig_pareto.update_layout(
            title='Gráfico de Pareto - Top 50 Produtos',
            xaxis=dict(title='Ranking de Produtos'),
            yaxis=dict(title='Vendas (€)', side='left'),
            yaxis2=dict(title='Acumulado (%)', side='right', overlaying='y', range=[0, 100]),
            height=500,
            hovermode='x unified'
        )

        st.plotly_chart(fig_pareto, use_container_width=True)

        st.markdown("---")

        # Correlação entre categorias
        st.subheader("🔗 Correlação entre Categorias")

        # Criar matriz de correlação
        vendas_diarias_cat = df_filtrado.pivot_table(
            values='Valor',
            index='Data',
            columns='Categoria',
            aggfunc='sum',
            fill_value=0
        )

        if len(vendas_diarias_cat.columns) > 1:
            correlacao = vendas_diarias_cat.corr()

            fig_corr = go.Figure(data=go.Heatmap(
                z=correlacao.values,
                x=correlacao.columns,
                y=correlacao.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(correlacao.values, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Correlação")
            ))

            fig_corr.update_layout(
                title='Matriz de Correlação entre Categorias',
                height=500
            )

            st.plotly_chart(fig_corr, use_container_width=True)

            st.info("A correlação varia de -1 (correlação negativa perfeita) a +1 (correlação positiva perfeita). Valores próximos de 0 indicam pouca ou nenhuma correlação.")
        else:
            st.info("Dados insuficientes para análise de correlação.")

        st.markdown("---")

        # Índice de diversificação
        st.subheader("🌈 Índice de Diversificação de Produtos")

        # Calcular índice Herfindahl-Hirschman (HHI)
        market_shares = (vendas_produtos / vendas_produtos.sum()) ** 2
        hhi = market_shares.sum() * 10000  # Multiplicar por 10000 para escala tradicional

        # Interpretar HHI
        if hhi < 1500:
            interpretacao = "📊 Mercado Altamente Competitivo/Diversificado"
            cor_hhi = "green"
        elif hhi < 2500:
            interpretacao = "⚠️ Mercado Moderadamente Concentrado"
            cor_hhi = "orange"
        else:
            interpretacao = "🎯 Mercado Altamente Concentrado"
            cor_hhi = "red"

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Índice HHI",
                f"{hhi:.0f}"
            )

        with col2:
            st.metric(
                "Total de Produtos",
                f"{len(vendas_produtos)}"
            )

        with col3:
            st.markdown(f"**Interpretação:**")
            st.markdown(f"<p style='color: {cor_hhi}; font-weight: bold;'>{interpretacao}</p>", unsafe_allow_html=True)

        st.markdown("""
        **Sobre o Índice HHI:**
        - HHI < 1500: Mercado diversificado
        - 1500 ≤ HHI < 2500: Concentração moderada
        - HHI ≥ 2500: Alta concentração
        """)

    # TAB 5 - Análise Financeira
    with tab5:
        st.header("💰 Análise Financeira Detalhada")

        # Faturamento por categoria
        st.subheader("💵 Faturamento Total por Categoria")

        faturamento_cat = df_filtrado.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)

        fig_faturamento = px.bar(
            x=faturamento_cat.index,
            y=faturamento_cat.values,
            title='Faturamento por Categoria',
            labels={'x': 'Categoria', 'y': 'Faturamento (€)'},
            text=[formatar_moeda(v) for v in faturamento_cat.values],
            color=faturamento_cat.values,
            color_continuous_scale='Greens'
        )

        fig_faturamento.update_layout(
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig_faturamento, use_container_width=True)

        st.markdown("---")

        # Métricas financeiras
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("📊 Faturamento Médio")
            num_transacoes = len(df_filtrado)
            faturamento_medio_transacao = total_vendas / num_transacoes if num_transacoes > 0 else 0
            st.metric("Por Transação", formatar_moeda(faturamento_medio_transacao))

        with col2:
            st.subheader("🎯 Ticket Médio")
            ticket_medio_cat = df_filtrado.groupby('Categoria').apply(
                lambda x: x['Valor'].sum() / x['Qtd'].sum() if x['Qtd'].sum() > 0 else 0
            ).mean()
            st.metric("Por Categoria", formatar_moeda(ticket_medio_cat))

        with col3:
            st.subheader("📈 Projeção Mensal")
            if dias_periodo > 0:
                projecao_mensal = (total_vendas / dias_periodo) * 30
                st.metric("Estimativa", formatar_moeda(projecao_mensal))

        st.markdown("---")

        # Ticket médio por categoria
        st.subheader("🎫 Ticket Médio por Categoria")

        ticket_medio_categoria = df_filtrado.groupby('Categoria').apply(
            lambda x: x['Valor'].sum() / x['Qtd'].sum() if x['Qtd'].sum() > 0 else 0
        ).sort_values(ascending=False)

        fig_ticket = px.bar(
            x=ticket_medio_categoria.index,
            y=ticket_medio_categoria.values,
            title='Ticket Médio por Categoria',
            labels={'x': 'Categoria', 'y': 'Ticket Médio (€)'},
            text=[formatar_moeda(v) for v in ticket_medio_categoria.values],
            color=ticket_medio_categoria.values,
            color_continuous_scale='Blues'
        )

        fig_ticket.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_ticket, use_container_width=True)

        st.markdown("---")

        # Gráfico Waterfall de contribuições
        st.subheader("💧 Contribuição por Categoria (Waterfall)")

        contribuicoes = df_filtrado.groupby('Categoria')['Valor'].sum().sort_values(ascending=False)

        if len(contribuicoes) > 0:
            labels = list(contribuicoes.index) + ['Total']
            valores = list(contribuicoes.values) + [0]  # 0 para o total

            fig_waterfall = criar_grafico_waterfall(valores, labels, 'Contribuição de Cada Categoria')
            st.plotly_chart(fig_waterfall, use_container_width=True)

        st.markdown("---")

        # Projeção de faturamento
        st.subheader("🔮 Projeção de Faturamento (Regressão Linear)")

        # Preparar dados para regressão
        vendas_diarias_reg = df_filtrado.groupby('Data')['Valor'].sum().reset_index()
        vendas_diarias_reg['Dias'] = (vendas_diarias_reg['Data'] - vendas_diarias_reg['Data'].min()).dt.days

        if len(vendas_diarias_reg) >= 5:
            # Calcular regressão linear
            from numpy.polynomial import Polynomial

            x = vendas_diarias_reg['Dias'].values
            y = vendas_diarias_reg['Valor'].values

            # Fit linear
            p = Polynomial.fit(x, y, 1)

            # Projetar próximos 30 dias
            dias_futuros = np.arange(x[-1] + 1, x[-1] + 31)
            projecao = p(dias_futuros)

            # Criar gráfico
            fig_projecao = go.Figure()

            # Dados históricos
            fig_projecao.add_trace(go.Scatter(
                x=vendas_diarias_reg['Data'],
                y=vendas_diarias_reg['Valor'],
                mode='markers',
                name='Vendas Reais',
                marker=dict(size=6, color='#1f77b4')
            ))

            # Linha de tendência
            fig_projecao.add_trace(go.Scatter(
                x=vendas_diarias_reg['Data'],
                y=p(x),
                mode='lines',
                name='Tendência',
                line=dict(color='red', dash='dash')
            ))

            # Projeção
            datas_futuras = pd.date_range(
                start=vendas_diarias_reg['Data'].max() + timedelta(days=1),
                periods=30
            )

            fig_projecao.add_trace(go.Scatter(
                x=datas_futuras,
                y=projecao,
                mode='lines+markers',
                name='Projeção (30 dias)',
                line=dict(color='green', dash='dot'),
                marker=dict(size=4)
            ))

            fig_projecao.update_layout(
                title='Projeção de Vendas - Próximos 30 Dias',
                xaxis_title='Data',
                yaxis_title='Vendas (€)',
                height=500,
                hovermode='x unified'
            )

            st.plotly_chart(fig_projecao, use_container_width=True)

            # Métricas da projeção
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Projeção Total (30 dias)", formatar_moeda(projecao.sum()))

            with col2:
                st.metric("Média Diária Projetada", formatar_moeda(projecao.mean()))

            with col3:
                tendencia = "📈 Crescente" if p.coef[1] > 0 else "📉 Decrescente"
                st.metric("Tendência", tendencia)

            st.info("⚠️ Esta é uma projeção simples baseada em regressão linear. Considere fatores sazonais e externos para decisões estratégicas.")
        else:
            st.info("Dados insuficientes para projeção (mínimo 5 dias).")

    # TAB 6 - Comparação & Benchmarks
    with tab6:
        st.header("📊 Comparação & Benchmarks")

        # Comparação entre categorias (Scatter Plot)
        st.subheader("🎯 Comparação: Volume vs Valor Médio")

        comparacao_cat = df_filtrado.groupby('Categoria').agg({
            'Valor': ['sum', 'mean', 'count']
        })

        comparacao_cat.columns = ['Total', 'Media', 'Vendas']
        comparacao_cat = comparacao_cat.reset_index()

        # Adicionar ícones
        comparacao_cat['Icone'] = comparacao_cat['Categoria'].apply(
            lambda x: categorizer.CATEGORIAS.get(x, {}).get('icone', '📦')
        )

        fig_scatter = px.scatter(
            comparacao_cat,
            x='Vendas',
            y='Media',
            size='Total',
            color='Categoria',
            hover_name='Categoria',
            title='Análise: Número de Vendas vs Valor Médio (Tamanho = Faturamento Total)',
            labels={
                'Vendas': 'Número de Vendas',
                'Media': 'Valor Médio por Venda (€)',
                'Total': 'Faturamento Total (€)'
            },
            size_max=60
        )

        fig_scatter.update_layout(
            height=500,
            showlegend=True
        )

        st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown("---")

        # Benchmarks por fonte
        st.subheader("📍 Performance por Fonte de Dados")

        col1, col2 = st.columns(2)

        with col1:
            # Faturamento por fonte
            faturamento_fonte = df_filtrado.groupby('Fonte')['Valor'].sum().sort_values(ascending=False)

            fig_fonte = px.pie(
                values=faturamento_fonte.values,
                names=faturamento_fonte.index,
                title='Distribuição de Faturamento por Fonte',
                hole=0.4
            )

            fig_fonte.update_layout(height=400)
            st.plotly_chart(fig_fonte, use_container_width=True)

        with col2:
            # Ticket médio por fonte
            ticket_fonte = df_filtrado.groupby('Fonte').apply(
                lambda x: x['Valor'].sum() / x['Qtd'].sum() if x['Qtd'].sum() > 0 else 0
            ).sort_values(ascending=False)

            fig_ticket_fonte = px.bar(
                x=ticket_fonte.index,
                y=ticket_fonte.values,
                title='Ticket Médio por Fonte',
                labels={'x': 'Fonte', 'y': 'Ticket Médio (€)'},
                text=[formatar_moeda(v) for v in ticket_fonte.values],
                color=ticket_fonte.values,
                color_continuous_scale='Viridis'
            )

            fig_ticket_fonte.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_ticket_fonte, use_container_width=True)

        st.markdown("---")

        # Tabela de benchmarks
        st.subheader("📊 Tabela de Benchmarks Detalhados")

        benchmark = df_filtrado.groupby('Fonte').agg({
            'Valor': ['sum', 'mean', 'std'],
            'Qtd': 'sum',
            'Data': 'count'
        }).round(2)

        benchmark.columns = ['Faturamento Total', 'Média por Venda', 'Desvio Padrão', 'Qtd Total', 'Nº Vendas']
        benchmark['Ticket Médio'] = (benchmark['Faturamento Total'] / benchmark['Qtd Total']).round(2)
        benchmark['% do Total'] = ((benchmark['Faturamento Total'] / benchmark['Faturamento Total'].sum()) * 100).round(1)

        # Formatar para exibição
        benchmark_display = benchmark.copy()
        benchmark_display['Faturamento Total'] = benchmark_display['Faturamento Total'].apply(formatar_moeda)
        benchmark_display['Média por Venda'] = benchmark_display['Média por Venda'].apply(formatar_moeda)
        benchmark_display['Desvio Padrão'] = benchmark_display['Desvio Padrão'].apply(formatar_moeda)
        benchmark_display['Ticket Médio'] = benchmark_display['Ticket Médio'].apply(formatar_moeda)
        benchmark_display['% do Total'] = benchmark_display['% do Total'].apply(lambda x: f"{x}%")

        st.dataframe(benchmark_display, use_container_width=True)

        st.markdown("---")

        # Análise de sazonalidade comparativa
        st.subheader("🌊 Sazonalidade: Comparação entre Categorias")

        # Vendas por mês e categoria
        if 'Mes' in df_filtrado.columns:
            vendas_mes_cat = df_filtrado.pivot_table(
                values='Valor',
                index='Mes',
                columns='Categoria',
                aggfunc='sum',
                fill_value=0
            )

            fig_sazonalidade = go.Figure()

            for categoria in vendas_mes_cat.columns:
                fig_sazonalidade.add_trace(go.Scatter(
                    x=vendas_mes_cat.index,
                    y=vendas_mes_cat[categoria],
                    mode='lines+markers',
                    name=categoria,
                    line=dict(width=2),
                    marker=dict(size=8)
                ))

            fig_sazonalidade.update_layout(
                title='Sazonalidade por Categoria (Mensal)',
                xaxis_title='Mês',
                yaxis_title='Vendas (€)',
                height=500,
                hovermode='x unified'
            )

            st.plotly_chart(fig_sazonalidade, use_container_width=True)

        st.markdown("---")

        # Performance relativa
        st.subheader("🏅 Performance Relativa por Categoria")

        # Normalizar valores para comparação
        performance_rel = df_filtrado.groupby('Categoria').agg({
            'Valor': 'sum',
            'Qtd': 'sum'
        })

        # Normalizar (0-100)
        performance_rel['Score_Valor'] = (performance_rel['Valor'] / performance_rel['Valor'].max() * 100).round(1)
        performance_rel['Score_Qtd'] = (performance_rel['Qtd'] / performance_rel['Qtd'].max() * 100).round(1)
        performance_rel['Score_Final'] = ((performance_rel['Score_Valor'] + performance_rel['Score_Qtd']) / 2).round(1)

        performance_rel = performance_rel.sort_values('Score_Final', ascending=False)

        fig_performance = go.Figure()

        fig_performance.add_trace(go.Bar(
            name='Score Valor',
            x=performance_rel.index,
            y=performance_rel['Score_Valor'],
            marker_color='#1f77b4'
        ))

        fig_performance.add_trace(go.Bar(
            name='Score Quantidade',
            x=performance_rel.index,
            y=performance_rel['Score_Qtd'],
            marker_color='#ff7f0e'
        ))

        fig_performance.add_trace(go.Scatter(
            name='Score Final',
            x=performance_rel.index,
            y=performance_rel['Score_Final'],
            mode='lines+markers',
            marker=dict(size=10, color='red'),
            line=dict(width=3, color='red'),
            yaxis='y2'
        ))

        fig_performance.update_layout(
            title='Performance Relativa (Normalizada 0-100)',
            barmode='group',
            height=500,
            yaxis=dict(title='Score Individual'),
            yaxis2=dict(title='Score Final', overlaying='y', side='right'),
            hovermode='x unified'
        )

        st.plotly_chart(fig_performance, use_container_width=True)

    # TAB 7 - Dados Detalhados
    with tab7:
        st.header("📑 Dados Detalhados & Exportação")

        # Opções de agrupamento
        st.subheader("⚙️ Opções de Visualização")

        col1, col2, col3 = st.columns(3)

        with col1:
            agrupar_por = st.selectbox(
                "Agrupar dados por:",
                options=['Sem agrupamento', 'Categoria', 'Subcategoria', 'Produto', 'Fonte', 'Data'],
                index=0
            )

        with col2:
            ordenar_por = st.selectbox(
                "Ordenar por:",
                options=['Valor', 'Qtd', 'Data', 'Categoria'],
                index=0
            )

        with col3:
            ordem = st.radio(
                "Ordem:",
                options=['Decrescente', 'Crescente'],
                horizontal=True
            )

        # Preparar dados para exibição
        if agrupar_por == 'Sem agrupamento':
            df_exibir = df_filtrado.copy()

            # Selecionar colunas relevantes
            colunas_exibir = ['Data', 'Produto', 'Categoria', 'Subcategoria', 'Valor', 'Qtd', 'Fonte']
            colunas_exibir = [col for col in colunas_exibir if col in df_exibir.columns]

            df_exibir = df_exibir[colunas_exibir]

            # Ordenar
            ascending = (ordem == 'Crescente')
            df_exibir = df_exibir.sort_values(by=ordenar_por, ascending=ascending)

        else:
            # Agrupar dados
            df_exibir = df_filtrado.groupby(agrupar_por).agg({
                'Valor': 'sum',
                'Qtd': 'sum',
                'Data': 'count'
            }).round(2)

            df_exibir = df_exibir.rename(columns={'Data': 'Nº Vendas'})
            df_exibir['Valor Médio'] = (df_exibir['Valor'] / df_exibir['Nº Vendas']).round(2)

            # Ordenar
            ascending = (ordem == 'Crescente')
            df_exibir = df_exibir.sort_values(by=ordenar_por if ordenar_por in df_exibir.columns else 'Valor', ascending=ascending)

            df_exibir = df_exibir.reset_index()

        # Estatísticas resumidas
        st.subheader("📊 Estatísticas Resumidas")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Total de Registos", f"{len(df_exibir):,}")

        with col2:
            soma_total = df_filtrado['Valor'].sum()
            st.metric("Soma Total", formatar_moeda(soma_total))

        with col3:
            media_total = df_filtrado['Valor'].mean()
            st.metric("Média", formatar_moeda(media_total))

        with col4:
            mediana_total = df_filtrado['Valor'].median()
            st.metric("Mediana", formatar_moeda(mediana_total))

        with col5:
            desvio_total = df_filtrado['Valor'].std()
            st.metric("Desvio Padrão", formatar_moeda(desvio_total))

        st.markdown("---")

        # Exibir tabela
        st.subheader("📋 Tabela de Dados")

        # Formatar valores monetários para exibição
        df_display = df_exibir.copy()

        if 'Valor' in df_display.columns:
            df_display['Valor'] = df_display['Valor'].apply(formatar_moeda)

        if 'Valor Médio' in df_display.columns:
            df_display['Valor Médio'] = df_display['Valor Médio'].apply(formatar_moeda)

        if 'Qtd' in df_display.columns:
            df_display['Qtd'] = df_display['Qtd'].apply(lambda x: f"{x:,.0f}")

        # Exibir com altura ajustável
        st.dataframe(df_display, use_container_width=True, height=500)

        st.markdown("---")

        # Botões de exportação
        st.subheader("💾 Exportar Dados")

        col1, col2 = st.columns(2)

        with col1:
            # Exportar para CSV
            csv = df_exibir.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descarregar CSV",
                data=csv,
                file_name=f"vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            # Exportar para Excel
            from io import BytesIO

            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_exibir.to_excel(writer, sheet_name='Vendas', index=False)

                # Adicionar resumo
                df_resumo = pd.DataFrame({
                    'Métrica': ['Total de Vendas', 'Média', 'Mediana', 'Desvio Padrão', 'Total de Registos'],
                    'Valor': [
                        soma_total,
                        media_total,
                        mediana_total,
                        desvio_total,
                        len(df_filtrado)
                    ]
                })
                df_resumo.to_excel(writer, sheet_name='Resumo', index=False)

            st.download_button(
                label="📥 Descarregar Excel",
                data=buffer.getvalue(),
                file_name=f"vendas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        st.markdown("---")

        # Informações adicionais
        st.subheader("ℹ️ Informações do Dataset")

        info_cols = st.columns(3)

        with info_cols[0]:
            st.markdown("**📅 Período dos Dados:**")
            st.write(f"Início: {df_filtrado['Data'].min().strftime('%d/%m/%Y')}")
            st.write(f"Fim: {df_filtrado['Data'].max().strftime('%d/%m/%Y')}")

        with info_cols[1]:
            st.markdown("**📊 Categorias:**")
            st.write(f"Total: {df_filtrado['Categoria'].nunique()}")
            st.write(f"Subcategorias: {df_filtrado['Subcategoria'].nunique()}")

        with info_cols[2]:
            st.markdown("**📦 Produtos:**")
            st.write(f"Total: {df_filtrado['Produto'].nunique()}")
            st.write(f"Fontes: {df_filtrado['Fonte'].nunique()}")

    # Footer
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align: center; color: #666; padding: 20px;">
            <p><strong>Dashboard de Vendas - Café Martins</strong> | Desenvolvido com Streamlit & Plotly</p>
            <p>Última atualização: {}</p>
        </div>
    """.format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')), unsafe_allow_html=True)


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
