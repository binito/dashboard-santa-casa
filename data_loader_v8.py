"""
Módulo de carregamento de dados para Dashboard v8
NOVA VERSÃO: Carrega dados diretamente do MariaDB (ultra-rápido!)
Integração com custos REAIS do Despesify + custos estimados
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import warnings
from cost_manager_v2 import CostManagerV2
from product_categorizer import ProductCategorizer

warnings.filterwarnings('ignore')


class DataLoaderV8:
    """
    Carregador de dados v8 - CARREGA DO MARIADB

    VANTAGENS:
    - 10-50x mais rápido que carregar de ficheiros
    - Filtros aplicados na query (WHERE) - muito mais eficiente
    - Índices otimizados para performance
    - Dados sempre atualizados pelos scripts cron
    """

    # Configuração do banco de dados
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'cathie',
        'database': 'dashboard'
    }

    def __init__(self, custos_dir='dados_custos', usar_despesify=True):
        """
        Inicializa o carregador v8

        Args:
            custos_dir: Diretório com arquivos de custos
            usar_despesify: Se True, usa custos reais do Despesify
        """
        self.connection = None
        self.custos_dir = custos_dir
        self.usar_despesify = usar_despesify

        # Inicializar gestor de custos v2 (com Despesify)
        self.cost_manager = CostManagerV2(custos_dir, usar_despesify=usar_despesify)

        # Inicializar categorizador de produtos
        self.categorizer = ProductCategorizer()

    def _conectar(self):
        """Estabelece conexão com a base de dados (reutiliza conexão existente)"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.DB_CONFIG)
            return True
        except Error as e:
            print(f"❌ Erro ao conectar à base de dados: {e}")
            return False

    def _desconectar(self):
        """Fecha conexão com a base de dados"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def _manter_conexao(self):
        """Mantém conexão aberta (para operações em lote)"""
        pass  # Não fecha a conexão

    def carregar_dados_dashboard(self, data_inicio=None, data_fim=None):
        """
        Carrega dados da tabela dados_dashboard (POS Café)

        Args:
            data_inicio: Data inicial do filtro (opcional)
            data_fim: Data final do filtro (opcional)

        Returns:
            DataFrame com dados do POS Café
        """
        if not self._conectar():
            return pd.DataFrame()

        try:
            # Query base
            query = """
                SELECT
                    data AS Data,
                    codigo AS Codigo,
                    produto AS Produto,
                    familia_subfamilia AS Familia,
                    quantidade AS Qtd,
                    valor_total AS Valor
                FROM dados_dashboard
            """

            # Adicionar filtros de data SE especificados
            conditions = []
            params = []

            if data_inicio is not None:
                conditions.append("data >= %s")
                params.append(data_inicio)

            if data_fim is not None:
                conditions.append("data <= %s")
                params.append(data_fim)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY data"

            # Executar query
            if params:
                df = pd.read_sql(query, self.connection, params=params)
            else:
                df = pd.read_sql(query, self.connection)

            if df.empty:
                return df

            # Converter Data para datetime
            df['Data'] = pd.to_datetime(df['Data'])

            # Adicionar metadados
            df['Fonte'] = 'POS-Café'

            # Categorizar produtos
            df = self.categorizer.categorizar_dataframe(df)

            print(f"✓ Carregados {len(df):,} registos do POS Café (MariaDB)")
            return df

        except Exception as e:
            print(f"❌ Erro ao carregar dados_dashboard: {e}")
            return pd.DataFrame()

    def carregar_pos(self, data_inicio=None, data_fim=None, incluir_raspadinhas=False):
        """
        Carrega dados da tabela pos (POS Outros Produtos)

        IMPORTANTE: Filtra apenas codigo = 50010 (Totobola/Outros) por padrão
        Para manter compatibilidade com V7

        Args:
            data_inicio: Data inicial do filtro (opcional)
            data_fim: Data final do filtro (opcional)
            incluir_raspadinhas: Se True, inclui também códigos < 50000 (raspadinhas)

        Returns:
            DataFrame com dados do POS Outros
        """
        if not self._conectar():
            return pd.DataFrame()

        try:
            # Query base
            query = """
                SELECT
                    data AS Data,
                    codigo AS Codigo,
                    designacao AS Produto,
                    qtd AS Qtd,
                    val_total AS Valor
                FROM pos
            """

            # Adicionar filtros
            conditions = []
            params = []

            # FILTRO CRÍTICO: Apenas codigo = 50010 (como V7)
            # Ou incluir raspadinhas (codigo < 50000) se solicitado
            if incluir_raspadinhas:
                conditions.append("(codigo = %s OR codigo < %s)")
                params.extend([50010, 50000])
            else:
                conditions.append("codigo = %s")
                params.append(50010)

            # Filtros de data
            if data_inicio is not None:
                conditions.append("data >= %s")
                params.append(data_inicio)

            if data_fim is not None:
                conditions.append("data <= %s")
                params.append(data_fim)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY data"

            # Executar query
            if params:
                df = pd.read_sql(query, self.connection, params=params)
            else:
                df = pd.read_sql(query, self.connection)

            if df.empty:
                return df

            # Converter Data para datetime
            df['Data'] = pd.to_datetime(df['Data'])

            # Adicionar metadados
            df['Fonte'] = 'POS-Outros'

            # Renomear todos produtos para "Outros" (compatibilidade V7)
            df['Produto'] = 'Outros'

            # Categorizar produtos
            df = self.categorizer.categorizar_dataframe(df)

            print(f"✓ Carregados {len(df):,} registos do POS Outros (MariaDB)")
            return df

        except Exception as e:
            print(f"❌ Erro ao carregar pos: {e}")
            return pd.DataFrame()

    def carregar_santa_casa(self, data_inicio=None, data_fim=None):
        """
        Carrega dados da tabela dados_santa_casa (Jogos)

        Args:
            data_inicio: Data inicial do filtro (opcional)
            data_fim: Data final do filtro (opcional)

        Returns:
            DataFrame com dados dos Jogos Santa Casa
        """
        if not self._conectar():
            return pd.DataFrame()

        try:
            # Query base
            query = """
                SELECT
                    data AS Data_Str,
                    categoria AS Categoria_Original,
                    jogo AS Jogo,
                    tipo AS Tipo,
                    jogo_rececionado AS Jogo_Rececionado,
                    qt_macos AS Qt_Macos,
                    vendas_iliquidas AS Vendas_Iliquidas,
                    remuneracoes AS Remuneracoes,
                    premios AS Premios,
                    valor AS Valor
                FROM dados_santa_casa
                WHERE categoria != 'PRESTAÇÃO DE CONTAS'
            """

            # NOTA: Campo data é VARCHAR no formato "DD-MM-YYYY" - converter depois
            # Não podemos filtrar diretamente na query sem converter o campo

            # Executar query
            df = pd.read_sql(query, self.connection)

            if df.empty:
                return df

            # Converter Data (formato DD-MM-YYYY para datetime)
            df['Data'] = pd.to_datetime(df['Data_Str'], format='%d-%m-%Y', errors='coerce')
            df = df.dropna(subset=['Data'])  # Remover linhas com datas inválidas

            # Filtrar por data SE especificado (depois da conversão)
            if data_inicio is not None:
                df = df[df['Data'] >= pd.Timestamp(data_inicio)]

            if data_fim is not None:
                df = df[df['Data'] <= pd.Timestamp(data_fim)]

            # Criar coluna Produto baseado em Jogo + Tipo
            def criar_produto(row):
                if row['Tipo'] and row['Tipo'].strip():
                    return f"{row['Jogo']} {row['Tipo']}"
                elif row['Jogo_Rececionado'] and str(row['Jogo_Rececionado']).strip():
                    return f"{row['Jogo']} - {row['Jogo_Rececionado']}"
                else:
                    return row['Jogo']

            df['Produto'] = df.apply(criar_produto, axis=1)

            # CORREÇÃO CRÍTICA: Usar Vendas_Iliquidas (não "Valor")
            # "Valor" = líquido após prémios/remunerações
            # "Vendas_Iliquidas" = vendas brutas (compatível com V7)
            df['Valor'] = df['Vendas_Iliquidas'].fillna(0)

            # Adicionar metadados
            df['Fonte'] = 'Santa Casa'
            df['Categoria'] = 'Jogos Santa Casa'
            df['Subcategoria'] = df['Produto']
            df['Qtd'] = 1.0  # Jogos são vendas agregadas, não unidades

            # Selecionar colunas finais
            df = df[['Data', 'Produto', 'Valor', 'Qtd', 'Fonte', 'Categoria', 'Subcategoria']].copy()

            print(f"✓ Carregados {len(df):,} registos da Santa Casa (MariaDB)")
            return df

        except Exception as e:
            print(f"❌ Erro ao carregar dados_santa_casa: {e}")
            return pd.DataFrame()

    def carregar_tudo_integrado_com_custos(self, data_inicio=None, data_fim=None):
        """
        Carrega todos os dados e adiciona informações de custos

        ULTRA-RÁPIDO: Queries SQL otimizadas com filtros WHERE
        OTIMIZADO: Reutiliza conexão única para todas as tabelas

        Args:
            data_inicio: Data inicial do filtro (opcional)
            data_fim: Data final do filtro (opcional)

        Returns:
            DataFrame completo com vendas e custos
        """
        print("🚀 Carregando dados do MariaDB (V8 - Ultra-Rápido)...")

        # Abrir conexão única para todas as operações
        if not self._conectar():
            print("❌ Falha ao conectar à base de dados")
            return pd.DataFrame()

        try:
            # Carregar dados das 3 tabelas (reutiliza conexão)
            df_cafe = self.carregar_dados_dashboard(data_inicio, data_fim)
            df_outros = self.carregar_pos(data_inicio, data_fim)
            df_santa_casa = self.carregar_santa_casa(data_inicio, data_fim)

            # Combinar todos os DataFrames
            dfs = []
            if not df_cafe.empty:
                dfs.append(df_cafe)
            if not df_outros.empty:
                dfs.append(df_outros)
            if not df_santa_casa.empty:
                dfs.append(df_santa_casa)

            if not dfs:
                print("⚠️  Nenhum dado encontrado")
                return pd.DataFrame()

            df_vendas = pd.concat(dfs, ignore_index=True)
            df_vendas = df_vendas.sort_values('Data').reset_index(drop=True)

            # Adicionar colunas temporais (vectorizado - rápido)
            df_vendas['Ano'] = df_vendas['Data'].dt.year
            df_vendas['Mes'] = df_vendas['Data'].dt.month
            df_vendas['Semana'] = df_vendas['Data'].dt.isocalendar().week
            df_vendas['Dia_Semana'] = df_vendas['Data'].dt.dayofweek
            df_vendas['Trimestre'] = df_vendas['Data'].dt.quarter

            print(f"📊 Total: {len(df_vendas):,} registos carregados")

            # Adicionar informações de custos
            print("💰 Calculando custos e comissões...")
            df_completo = self.cost_manager.calcular_custos_vendas(df_vendas)

            return df_completo

        finally:
            # Fechar conexão apenas no final
            self._desconectar()

    def get_resumo_financeiro(self, df: pd.DataFrame = None, data_inicio=None, data_fim=None) -> dict:
        """
        Retorna resumo financeiro completo

        Args:
            df: DataFrame com dados (se None, carrega tudo)
            data_inicio: Data inicial do filtro
            data_fim: Data final do filtro

        Returns:
            Dicionário com métricas financeiras
        """
        # Carregar dados se não fornecido (com filtros opcionais)
        if df is None:
            df = self.carregar_tudo_integrado_com_custos(data_inicio, data_fim)

        if df.empty:
            return {}

        # Filtrar por data se especificado (caso df já tenha sido fornecido)
        if data_inicio is not None:
            df = df[df['Data'] >= pd.Timestamp(data_inicio)]
        if data_fim is not None:
            df = df[df['Data'] <= pd.Timestamp(data_fim)]

        # Calcular dias do período e datas
        if not df.empty and 'Data' in df.columns:
            data_min = df['Data'].min().to_pydatetime()
            data_max = df['Data'].max().to_pydatetime()
            dias_periodo = (data_max - data_min).days + 1
        else:
            data_min = datetime.now().replace(day=1)
            data_max = datetime.now()
            dias_periodo = 30

        # Calcular métricas (com datas para integração Despesify)
        metricas = self.cost_manager.calcular_metricas_financeiras(df, data_min, data_max)

        # Adicionar informações extras
        metricas['num_transacoes'] = len(df)
        metricas['ticket_medio'] = metricas['receita_total'] / metricas['num_transacoes'] if metricas['num_transacoes'] > 0 else 0

        if 'Qtd' in df.columns:
            metricas['qtd_total'] = df['Qtd'].sum()
            metricas['preco_medio_unitario'] = metricas['receita_total'] / metricas['qtd_total'] if metricas['qtd_total'] > 0 else 0

        # Projeção mensal
        if dias_periodo > 0:
            fator_projecao = 30 / dias_periodo
            metricas['projecao_receita_mensal'] = metricas['receita_total'] * fator_projecao
            metricas['projecao_lucro_mensal'] = metricas['lucro_liquido'] * fator_projecao

        return metricas

    # Métodos auxiliares (compatibilidade com V7)

    def get_analise_break_even(self, df: pd.DataFrame = None) -> dict:
        """Retorna análise de break-even"""
        if df is None:
            df = self.carregar_tudo_integrado_com_custos()

        if df.empty:
            return {}

        # Calcular margem de contribuição média
        if 'Margem_Bruta_Pct' in df.columns:
            margem_media = df['Margem_Bruta_Pct'].mean()
        else:
            margem_media = 50.0

        # Calcular break-even
        break_even = self.cost_manager.calcular_break_even(margem_media)

        # Adicionar informações do período atual
        if not df.empty:
            dias_periodo = (df['Data'].max() - df['Data'].min()).days + 1
            vendas_atuais_diarias = df['Valor'].sum() / dias_periodo

            break_even['vendas_atuais_diarias'] = vendas_atuais_diarias
            break_even['margem_seguranca_pct'] = (
                (vendas_atuais_diarias - break_even['vendas_break_even_diaria']) /
                vendas_atuais_diarias * 100
            ) if vendas_atuais_diarias > 0 else 0

            if vendas_atuais_diarias > 0:
                break_even['dias_para_break_even'] = (
                    break_even['vendas_break_even_mensal'] / vendas_atuais_diarias
                )

        return break_even

    def get_produtos_margem_negativa(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Retorna produtos com margem negativa ou muito baixa"""
        if df is None:
            df = self.carregar_tudo_integrado_com_custos()

        if df.empty or 'Margem_Bruta_Pct' not in df.columns:
            return pd.DataFrame()

        # Filtrar produtos com margem < 20%
        df_problemas = df[df['Margem_Bruta_Pct'] < 20].copy()

        if df_problemas.empty:
            return pd.DataFrame()

        # Agrupar por produto
        analise = df_problemas.groupby(['Produto', 'Categoria']).agg({
            'Valor': 'sum',
            'Custo_Total': 'sum',
            'Lucro_Bruto': 'sum',
            'Qtd': 'sum'
        }).round(2)

        analise['Margem_Bruta_Pct'] = (analise['Lucro_Bruto'] / analise['Valor'] * 100).round(2)
        analise = analise.sort_values('Margem_Bruta_Pct')

        return analise

    def get_produtos_estrela(self, df: pd.DataFrame = None, top_n: int = 10) -> pd.DataFrame:
        """Retorna produtos estrela (alta margem + alto volume)"""
        if df is None:
            df = self.carregar_tudo_integrado_com_custos()

        if df.empty or 'Margem_Bruta_Pct' not in df.columns:
            return pd.DataFrame()

        # Agrupar por produto
        analise = df.groupby(['Produto', 'Categoria']).agg({
            'Valor': 'sum',
            'Lucro_Bruto': 'sum',
            'Qtd': 'sum'
        }).round(2)

        analise['Margem_Bruta_Pct'] = (analise['Lucro_Bruto'] / analise['Valor'] * 100).round(2)

        # Filtrar alta margem (>50%) e alto lucro
        estrelas = analise[
            (analise['Margem_Bruta_Pct'] > 50) &
            (analise['Lucro_Bruto'] > analise['Lucro_Bruto'].quantile(0.5))
        ].copy()

        # Calcular score
        estrelas['Score'] = estrelas['Lucro_Bruto'] * estrelas['Margem_Bruta_Pct']
        estrelas = estrelas.sort_values('Score', ascending=False)

        return estrelas.head(top_n)

    def get_analise_por_categoria(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Retorna análise financeira por categoria"""
        if df is None:
            df = self.carregar_tudo_integrado_com_custos()

        return self.cost_manager.analisar_rentabilidade_categorias(df)

    def comparar_periodo(self, df_atual: pd.DataFrame, df_anterior: pd.DataFrame) -> dict:
        """Compara métricas entre dois períodos"""
        if df_atual.empty or df_anterior.empty:
            return {}

        # Calcular datas e dias
        data_min_atual = df_atual['Data'].min().to_pydatetime()
        data_max_atual = df_atual['Data'].max().to_pydatetime()
        data_min_anterior = df_anterior['Data'].min().to_pydatetime()
        data_max_anterior = df_anterior['Data'].max().to_pydatetime()

        dias_atual = (data_max_atual - data_min_atual).days + 1
        dias_anterior = (data_max_anterior - data_min_anterior).days + 1

        # Métricas dos dois períodos
        metricas_atual = self.cost_manager.calcular_metricas_financeiras(df_atual, data_min_atual, data_max_atual)
        metricas_anterior = self.cost_manager.calcular_metricas_financeiras(df_anterior, data_min_anterior, data_max_anterior)

        # Calcular variações
        comparacao = {}
        for chave in ['receita_total', 'lucro_bruto', 'lucro_liquido', 'margem_bruta_pct', 'margem_liquida_pct']:
            valor_atual = metricas_atual.get(chave, 0)
            valor_anterior = metricas_anterior.get(chave, 0)

            if valor_anterior != 0:
                variacao_pct = ((valor_atual - valor_anterior) / valor_anterior) * 100
            else:
                variacao_pct = 0

            comparacao[f'{chave}_atual'] = valor_atual
            comparacao[f'{chave}_anterior'] = valor_anterior
            comparacao[f'{chave}_variacao_pct'] = variacao_pct

        return comparacao

    def testar_conexao(self) -> bool:
        """
        Testa conexão com a base de dados

        Returns:
            True se conexão OK
        """
        if self._conectar():
            print("✅ Conexão com MariaDB OK")
            self._desconectar()
            return True
        else:
            print("❌ Falha na conexão com MariaDB")
            return False


# Função auxiliar para uso rápido
def carregar_dados_completos_v8(data_inicio=None, data_fim=None):
    """Função conveniente para carregar dados v8"""
    loader = DataLoaderV8()
    return loader.carregar_tudo_integrado_com_custos(data_inicio, data_fim)


if __name__ == '__main__':
    print("=== Teste do DataLoaderV8 (MariaDB) ===\n")
    loader = DataLoaderV8()

    # Testar conexão
    if not loader.testar_conexao():
        print("❌ Erro de conexão - verifique as credenciais do MariaDB")
        exit(1)

    print("\n" + "="*70)
    print("Carregando dados...")

    # Carregar dados
    df = loader.carregar_tudo_integrado_com_custos()

    print(f"\n📊 Total de registos: {len(df):,}")

    if not df.empty:
        print(f"\n📅 Período: {df['Data'].min().strftime('%d/%m/%Y')} → {df['Data'].max().strftime('%d/%m/%Y')}")

        print(f"\n📋 Colunas disponíveis:")
        print(df.columns.tolist())

        print(f"\n🔍 Primeiras linhas:")
        print(df[['Data', 'Produto', 'Categoria', 'Valor', 'Custo_Unitario', 'Lucro_Bruto', 'Margem_Bruta_Pct']].head())

        # Resumo financeiro
        print("\n" + "="*70)
        print("💰 RESUMO FINANCEIRO")
        print("="*70)
        resumo = loader.get_resumo_financeiro(df)
        for chave, valor in resumo.items():
            if isinstance(valor, float):
                if 'pct' in chave or 'margem' in chave:
                    print(f"{chave:.<40} {valor:.2f}%")
                else:
                    print(f"{chave:.<40} €{valor:,.2f}")

        # Break-even
        print("\n" + "="*70)
        print("⚖️  ANÁLISE BREAK-EVEN")
        print("="*70)
        be = loader.get_analise_break_even(df)
        print(f"Vendas diárias para break-even: €{be.get('vendas_break_even_diaria', 0):,.2f}")
        print(f"Margem de segurança: {be.get('margem_seguranca_pct', 0):.1f}%")

    print("\n" + "="*70)
    print("✅ DataLoaderV8 funcionando corretamente!")
    print("="*70)
