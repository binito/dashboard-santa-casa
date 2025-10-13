"""
Dashboard Interativo v3 - Análise Integrada de Vendas
- Jogos Santa Casa
- Vendas de Café
- Outros Produtos

Utilize: streamlit run dashboard_v3.py
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
from data_loader_v3 import DataLoaderV3

warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Vendas v3 - Análise Integrada",
    page_icon="📊",
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
    .source-tag {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .source-santa-casa { background-color: #1f77b4; color: white; }
    .source-cafe { background-color: #ff7f0e; color: white; }
    .source-outros { background-color: #2ca02c; color: white; }
</style>
""", unsafe_allow_html=True)


# ====================================================================================
# FUNÇÕES DE CARREGAMENTO E PROCESSAMENTO
# ====================================================================================

@st.cache_data(ttl=3600)
def carregar_dados_completos():
    """Carrega todos os dados de todas as fontes"""
    loader = DataLoaderV3()
    return loader.carregar_todos_dados()


def processar_dados_para_analise(dados):
    """Processa e prepara dados para análise"""
    dfs_processados = []

    # Processar Santa Casa
    if len(dados['santa_casa']) > 0:
        df_sc = dados['santa_casa'].copy()
        df_sc['Categoria'] = df_sc['Jogo']
        df_sc = df_sc.rename(columns={'Jogo': 'Produto_Tipo'})
        df_sc['Fonte_Display'] = 'Jogos Santa Casa'
        df_sc['Cor_Fonte'] = '#1f77b4'
        dfs_processados.append(df_sc[['Data', 'Valor', 'Categoria', 'Fonte', 'Fonte_Display', 'Cor_Fonte']])

    # Processar Café
    if len(dados['cafe']) > 0:
        df_cafe = dados['cafe'].copy()
        df_cafe['Categoria'] = 'Café'
        df_cafe['Fonte_Display'] = 'Vendas Café'
        df_cafe['Cor_Fonte'] = '#ff7f0e'
        dfs_processados.append(df_cafe[['Data', 'Valor', 'Categoria', 'Fonte', 'Fonte_Display', 'Cor_Fonte']])

    # Processar Outros
    if len(dados['outros']) > 0:
        df_outros = dados['outros'].copy()
        df_outros['Categoria'] = 'Outros'
        df_outros['Fonte_Display'] = 'Outros Produtos'
        df_outros['Cor_Fonte'] = '#2ca02c'
        dfs_processados.append(df_outros[['Data', 'Valor', 'Categoria', 'Fonte', 'Fonte_Display', 'Cor_Fonte']])

    if not dfs_processados:
        return pd.DataFrame()

    # Combinar tudo
    df_completo = pd.concat(dfs_processados, ignore_index=True)
    df_completo = df_completo.sort_values('Data').reset_index(drop=True)

    # Adicionar colunas temporais
    df_completo['Ano'] = df_completo['Data'].dt.year
    df_completo['Mes'] = df_completo['Data'].dt.month
    df_completo['Mes_Nome'] = df_completo['Data'].dt.strftime('%B')
    df_completo['Semana'] = df_completo['Data'].dt.isocalendar().week
    df_completo['Dia_Semana'] = df_completo['Data'].dt.dayofweek
    df_completo['Dia_Semana_Nome'] = df_completo['Data'].dt.strftime('%A')
    df_completo['Trimestre'] = df_completo['Data'].dt.quarter

    return df_completo


# ====================================================================================
# MAIN APP
# ====================================================================================

def main():
    # Cabeçalho
    st.markdown('<h1 class="main-header">📊 Dashboard de Vendas v3</h1>', unsafe_allow_html=True)
    st.markdown("### Análise Integrada: Jogos Santa Casa + Café + Outros Produtos")

    # Carregar dados
    with st.spinner('Carregando dados...'):
        dados = carregar_dados_completos()
        df = processar_dados_para_analise(dados)

    if df.empty:
        st.error("⚠️ Nenhum dado encontrado. Verifique os ficheiros de dados.")
        return

    # ====================================================================================
    # SIDEBAR - FILTROS
    # ====================================================================================

    st.sidebar.title("🎛️ Filtros")

    # Filtro de fonte de dados
    st.sidebar.subheader("Fonte de Dados")
    fontes_disponiveis = df['Fonte_Display'].unique().tolist()
    fontes_selecionadas = st.sidebar.multiselect(
        "Selecione as fontes:",
        options=fontes_disponiveis,
        default=fontes_disponiveis
    )

    # Filtro de período
    st.sidebar.subheader("Período")
    data_min = df['Data'].min().date()
    data_max = df['Data'].max().date()

    periodo = st.sidebar.date_input(
        "Selecione o intervalo:",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max
    )

    # Aplicar filtros
    df_filtrado = df[df['Fonte_Display'].isin(fontes_selecionadas)].copy()

    if len(periodo) == 2:
        data_inicio, data_fim = periodo
        df_filtrado = df_filtrado[
            (df_filtrado['Data'].dt.date >= data_inicio) &
            (df_filtrado['Data'].dt.date <= data_fim)
        ]

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado disponível com os filtros selecionados.")
        return

    # ====================================================================================
    # MÉTRICAS PRINCIPAIS
    # ====================================================================================

    st.markdown("---")
    st.subheader("📈 Métricas Principais")

    col1, col2, col3, col4 = st.columns(4)

    total_vendas = df_filtrado['Valor'].sum()
    media_diaria = df_filtrado.groupby('Data')['Valor'].sum().mean()
    num_dias = df_filtrado['Data'].nunique()
    melhor_dia_valor = df_filtrado.groupby('Data')['Valor'].sum().max()

    with col1:
        st.metric(
            label="💰 Total de Vendas",
            value=f"€{total_vendas:,.2f}"
        )

    with col2:
        st.metric(
            label="📊 Média Diária",
            value=f"€{media_diaria:,.2f}"
        )

    with col3:
        st.metric(
            label="📅 Dias com Vendas",
            value=f"{num_dias}"
        )

    with col4:
        st.metric(
            label="🏆 Melhor Dia",
            value=f"€{melhor_dia_valor:,.2f}"
        )

    # ====================================================================================
    # ANÁLISE POR FONTE
    # ====================================================================================

    st.markdown("---")
    st.subheader("📊 Análise por Fonte de Dados")

    # Resumo por fonte
    resumo_fontes = df_filtrado.groupby('Fonte_Display').agg({
        'Valor': ['sum', 'mean', 'count']
    }).round(2)
    resumo_fontes.columns = ['Total (€)', 'Média (€)', 'Registos']
    resumo_fontes['% do Total'] = (resumo_fontes['Total (€)'] / resumo_fontes['Total (€)'].sum() * 100).round(1)

    col1, col2 = st.columns([1, 2])

    with col1:
        st.dataframe(resumo_fontes, use_container_width=True)

    with col2:
        # Gráfico de pizza
        fig_pie = px.pie(
            resumo_fontes.reset_index(),
            values='Total (€)',
            names='Fonte_Display',
            title='Distribuição de Vendas por Fonte',
            color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c']
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    # ====================================================================================
    # EVOLUÇÃO TEMPORAL
    # ====================================================================================

    st.markdown("---")
    st.subheader("📈 Evolução Temporal")

    # Seletor de granularidade
    granularidade = st.radio(
        "Granularidade:",
        options=['Diária', 'Semanal', 'Mensal'],
        horizontal=True
    )

    # Agrupar por granularidade
    if granularidade == 'Diária':
        df_temporal = df_filtrado.groupby(['Data', 'Fonte_Display'])['Valor'].sum().reset_index()
        x_col = 'Data'
    elif granularidade == 'Semanal':
        df_filtrado['Ano_Semana'] = df_filtrado['Data'].dt.strftime('%Y-W%W')
        df_temporal = df_filtrado.groupby(['Ano_Semana', 'Fonte_Display'])['Valor'].sum().reset_index()
        x_col = 'Ano_Semana'
    else:  # Mensal
        df_filtrado['Ano_Mes'] = df_filtrado['Data'].dt.strftime('%Y-%m')
        df_temporal = df_filtrado.groupby(['Ano_Mes', 'Fonte_Display'])['Valor'].sum().reset_index()
        x_col = 'Ano_Mes'

    # Gráfico de linhas
    fig_temporal = px.line(
        df_temporal,
        x=x_col,
        y='Valor',
        color='Fonte_Display',
        title=f'Evolução de Vendas ({granularidade})',
        labels={'Valor': 'Vendas (€)', x_col: 'Período'},
        color_discrete_map={
            'Jogos Santa Casa': '#1f77b4',
            'Vendas Café': '#ff7f0e',
            'Outros Produtos': '#2ca02c'
        }
    )
    fig_temporal.update_layout(hovermode='x unified')
    st.plotly_chart(fig_temporal, use_container_width=True)

    # ====================================================================================
    # TABS DE ANÁLISE DETALHADA
    # ====================================================================================

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Análise Comparativa",
        "📅 Análise Temporal",
        "🎯 Top Vendas",
        "📑 Dados Detalhados"
    ])

    # ===== TAB 1: ANÁLISE COMPARATIVA =====
    with tab1:
        st.subheader("Comparação entre Fontes de Dados")

        col1, col2 = st.columns(2)

        with col1:
            # Vendas por mês e fonte
            df_mes_fonte = df_filtrado.groupby([df_filtrado['Data'].dt.strftime('%Y-%m'), 'Fonte_Display'])['Valor'].sum().reset_index()
            df_mes_fonte.columns = ['Mês', 'Fonte', 'Valor']

            fig_bar = px.bar(
                df_mes_fonte,
                x='Mês',
                y='Valor',
                color='Fonte',
                title='Vendas Mensais por Fonte',
                barmode='group',
                color_discrete_map={
                    'Jogos Santa Casa': '#1f77b4',
                    'Vendas Café': '#ff7f0e',
                    'Outros Produtos': '#2ca02c'
                }
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            # Box plot
            fig_box = px.box(
                df_filtrado,
                x='Fonte_Display',
                y='Valor',
                title='Distribuição de Valores por Fonte',
                color='Fonte_Display',
                color_discrete_map={
                    'Jogos Santa Casa': '#1f77b4',
                    'Vendas Café': '#ff7f0e',
                    'Outros Produtos': '#2ca02c'
                }
            )
            st.plotly_chart(fig_box, use_container_width=True)

    # ===== TAB 2: ANÁLISE TEMPORAL =====
    with tab2:
        st.subheader("Padrões Temporais")

        col1, col2 = st.columns(2)

        with col1:
            # Vendas por dia da semana
            df_dia_semana = df_filtrado.groupby(['Dia_Semana_Nome', 'Fonte_Display'])['Valor'].sum().reset_index()

            ordem_dias = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            df_dia_semana['Ordem'] = df_dia_semana['Dia_Semana_Nome'].apply(lambda x: ordem_dias.index(x) if x in ordem_dias else 99)
            df_dia_semana = df_dia_semana.sort_values('Ordem')

            fig_dia = px.bar(
                df_dia_semana,
                x='Dia_Semana_Nome',
                y='Valor',
                color='Fonte_Display',
                title='Vendas por Dia da Semana',
                barmode='stack',
                color_discrete_map={
                    'Jogos Santa Casa': '#1f77b4',
                    'Vendas Café': '#ff7f0e',
                    'Outros Produtos': '#2ca02c'
                }
            )
            st.plotly_chart(fig_dia, use_container_width=True)

        with col2:
            # Vendas por trimestre
            df_trimestre = df_filtrado.groupby(['Ano', 'Trimestre', 'Fonte_Display'])['Valor'].sum().reset_index()
            df_trimestre['Periodo'] = df_trimestre['Ano'].astype(str) + ' - Q' + df_trimestre['Trimestre'].astype(str)

            fig_trim = px.bar(
                df_trimestre,
                x='Periodo',
                y='Valor',
                color='Fonte_Display',
                title='Vendas por Trimestre',
                barmode='group',
                color_discrete_map={
                    'Jogos Santa Casa': '#1f77b4',
                    'Vendas Café': '#ff7f0e',
                    'Outros Produtos': '#2ca02c'
                }
            )
            st.plotly_chart(fig_trim, use_container_width=True)

    # ===== TAB 3: TOP VENDAS =====
    with tab3:
        st.subheader("Análise de Top Vendas")

        fonte_analise = st.selectbox(
            "Selecione a fonte para análise:",
            options=df_filtrado['Fonte_Display'].unique()
        )

        df_fonte = df_filtrado[df_filtrado['Fonte_Display'] == fonte_analise].copy()

        col1, col2 = st.columns(2)

        with col1:
            # Top 10 dias
            top_dias = df_fonte.groupby('Data')['Valor'].sum().sort_values(ascending=False).head(10)

            st.markdown("#### 🏆 Top 10 Dias com Mais Vendas")
            for i, (data, valor) in enumerate(top_dias.items(), 1):
                st.markdown(f"**{i}.** {data.strftime('%Y-%m-%d')} - €{valor:,.2f}")

        with col2:
            # Top 10 meses
            df_fonte['Ano_Mes'] = df_fonte['Data'].dt.strftime('%Y-%m')
            top_meses = df_fonte.groupby('Ano_Mes')['Valor'].sum().sort_values(ascending=False).head(10)

            st.markdown("#### 📅 Top 10 Meses com Mais Vendas")
            for i, (mes, valor) in enumerate(top_meses.items(), 1):
                st.markdown(f"**{i}.** {mes} - €{valor:,.2f}")

        # Gráfico de evolução do top mês
        st.markdown("---")
        melhor_mes = top_meses.index[0]
        df_melhor_mes = df_fonte[df_fonte['Ano_Mes'] == melhor_mes].copy()

        vendas_diarias = df_melhor_mes.groupby('Data')['Valor'].sum().reset_index()

        fig_melhor = px.line(
            vendas_diarias,
            x='Data',
            y='Valor',
            title=f'Evolução Diária do Melhor Mês ({melhor_mes})',
            markers=True
        )
        st.plotly_chart(fig_melhor, use_container_width=True)

    # ===== TAB 4: DADOS DETALHADOS =====
    with tab4:
        st.subheader("Dados Detalhados")

        fonte_detalhe = st.selectbox(
            "Filtrar por fonte:",
            options=['Todas'] + list(df_filtrado['Fonte_Display'].unique())
        )

        if fonte_detalhe != 'Todas':
            df_detalhe = df_filtrado[df_filtrado['Fonte_Display'] == fonte_detalhe].copy()
        else:
            df_detalhe = df_filtrado.copy()

        # Preparar dados para exibição
        df_exibir = df_detalhe[['Data', 'Fonte_Display', 'Categoria', 'Valor']].copy()
        df_exibir['Data'] = df_exibir['Data'].dt.strftime('%Y-%m-%d')
        df_exibir['Valor'] = df_exibir['Valor'].round(2)
        df_exibir = df_exibir.sort_values('Data', ascending=False)

        st.dataframe(df_exibir, use_container_width=True, height=400)

        # Botão de exportação
        csv = df_exibir.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar para CSV",
            data=csv,
            file_name=f'vendas_detalhadas_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv'
        )

    # ====================================================================================
    # FOOTER
    # ====================================================================================

    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666; padding: 1rem;'>
            Dashboard v3 - Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            <br>
            Dados de {data_min} a {data_max}
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == '__main__':
    main()
