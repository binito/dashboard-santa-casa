"""
Módulo de carregamento de dados para Dashboard v9
NOVA VERSÃO: Otimizada e com integração Novadis
Carrega dados diretamente do MariaDB (ultra-rápido!)
Integração com custos REAIS do Despesify + custos estimados + Encomendas Novadis
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import warnings
import os
from pathlib import Path
from dotenv import load_dotenv
from cost_manager_v2 import CostManagerV2
from product_categorizer import ProductCategorizer
from data_loader_novadis import NovadisDataLoader  # Integração Novadis

warnings.filterwarnings('ignore')

# Carregar variáveis de ambiente do ficheiro .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class DataLoaderV9:
    """
    Carregador de dados v9 - OTIMIZADO

    MELHORIAS V9:
    - Integração com dados da Novadis (encomendas)
    - Otimização de queries
    - Melhor gestão de conexões
    """

    # Configuração do banco de dados (carregada de variáveis de ambiente)
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME_DASHBOARD', 'dashboard')
    }

    def __init__(self, custos_dir='dados_custos', usar_despesify=True):
        """
        Inicializa o carregador v9

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
        
        # Inicializar carregador Novadis
        self.novadis_loader = NovadisDataLoader()

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

    def carregar_dados_dashboard(self, data_inicio=None, data_fim=None):
        """
        Carrega dados da tabela dados_dashboard (POS Café)
        """
        if not self._conectar():
            return pd.DataFrame()

        try:
            # Query base otimizada - Seleciona apenas colunas necessárias
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

            # Ordenação feita no banco para ser mais rápido que no pandas
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

            # Categorizar produtos (pode ser otimizado futuramente movendo para SQL ou cache)
            df = self.categorizer.categorizar_dataframe(df)

            return df

        except Exception as e:
            print(f"❌ Erro ao carregar dados_dashboard: {e}")
            return pd.DataFrame()

    def carregar_pos(self, data_inicio=None, data_fim=None, incluir_raspadinhas=False):
        """
        Carrega dados da tabela pos (POS Outros Produtos)
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

            conditions = []
            params = []

            # FILTRO CRÍTICO: Apenas codigo = 50010 (como V7)
            if incluir_raspadinhas:
                conditions.append("(codigo = %s OR codigo < %s)")
                params.extend([50010, 50000])
            else:
                conditions.append("codigo = %s")
                params.append(50010)

            if data_inicio is not None:
                conditions.append("data >= %s")
                params.append(data_inicio)

            if data_fim is not None:
                conditions.append("data <= %s")
                params.append(data_fim)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY data"

            if params:
                df = pd.read_sql(query, self.connection, params=params)
            else:
                df = pd.read_sql(query, self.connection)

            if df.empty:
                return df

            df['Data'] = pd.to_datetime(df['Data'])
            df['Fonte'] = 'POS-Outros'
            df['Produto'] = 'Outros'
            df = self.categorizer.categorizar_dataframe(df)

            return df

        except Exception as e:
            print(f"❌ Erro ao carregar pos: {e}")
            return pd.DataFrame()

    def carregar_santa_casa(self, data_inicio=None, data_fim=None):
        """
        Carrega dados da tabela dados_santa_casa (Jogos)
        """
        if not self._conectar():
            return pd.DataFrame()

        try:
            # Query otimizada - Evita trazer colunas desnecessárias
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

            df = pd.read_sql(query, self.connection)

            if df.empty:
                return df

            # Converter Data
            df['Data'] = pd.to_datetime(df['Data_Str'], format='%d-%m-%Y', errors='coerce')
            df = df.dropna(subset=['Data'])

            if data_inicio is not None:
                df = df[df['Data'] >= pd.Timestamp(data_inicio)]

            if data_fim is not None:
                df = df[df['Data'] <= pd.Timestamp(data_fim)]

            # Criar coluna Produto
            # Vetorização simples para performance
            df['Produto'] = df['Jogo']
            mask_tipo = df['Tipo'].notna() & (df['Tipo'] != '')
            df.loc[mask_tipo, 'Produto'] = df.loc[mask_tipo, 'Jogo'] + ' ' + df.loc[mask_tipo, 'Tipo']
            
            mask_recec = ~mask_tipo & (df['Jogo_Rececionado'].notna()) & (df['Jogo_Rececionado'] != '')
            # Ajuste para evitar erro de tipo se for numérico
            df.loc[mask_recec, 'Produto'] = df.loc[mask_recec, 'Jogo'] + ' - ' + df.loc[mask_recec, 'Jogo_Rececionado'].astype(str)

            df['Valor'] = df['Vendas_Iliquidas'].fillna(0)
            df['Fonte'] = 'Santa Casa'
            df['Categoria'] = 'Jogos Santa Casa'
            df['Subcategoria'] = df['Produto']
            df['Qtd'] = 1.0

            return df[['Data', 'Produto', 'Valor', 'Qtd', 'Fonte', 'Categoria', 'Subcategoria']]

        except Exception as e:
            print(f"❌ Erro ao carregar dados_santa_casa: {e}")
            return pd.DataFrame()

    def carregar_novadis(self, data_inicio=None, data_fim=None):
        """
        Carrega dados da tabela novadis (Encomendas)
        """
        print("📦 Carregando dados da Novadis...")
        return self.novadis_loader.carregar_encomendas(data_inicio, data_fim)

    def carregar_novadis_processado(self, data_inicio=None, data_fim=None):
        """
        Carrega e processa dados da Novadis (conversão para unidades)
        """
        print("📦 Processando dados da Novadis...")
        return self.novadis_loader.processar_encomendas_com_conversao(data_inicio=data_inicio, data_fim=data_fim)

    def carregar_delta(self, data_inicio=None, data_fim=None):
        """
        Carrega dados das encomendas Delta (Nabeiro) do CSV
        """
        print("📦 Carregando dados da Delta (Nabeiro)...")
        csv_path = Path(os.getenv(
            'DELTA_FATURAS_CSV',
            '/home/jorge/Documentos/delta/dados/faturas_nabeiro.csv'
        ))
        
        if not csv_path.exists():
            print(f"⚠️ Arquivo Delta não encontrado: {csv_path}")
            return pd.DataFrame()
            
        try:
            df = pd.read_csv(csv_path)
            
            if df.empty:
                return df
                
            # Converter data
            df['Data_Fatura'] = pd.to_datetime(df['Data_Fatura'], format='%d/%m/%Y', errors='coerce')
            
            # Filtrar por data se necessário
            if data_inicio is not None:
                df = df[df['Data_Fatura'] >= pd.Timestamp(data_inicio)]
            if data_fim is not None:
                df = df[df['Data_Fatura'] <= pd.Timestamp(data_fim)]
                
            # Converter Total_EUR para numérico
            df['Total_EUR'] = pd.to_numeric(df['Total_EUR'], errors='coerce').fillna(0.0)
            
            return df.sort_values('Data_Fatura', ascending=False)
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados Delta: {e}")
            return pd.DataFrame()

    def carregar_delta_itens(self, numero_fatura=None):
        """
        Carrega os itens detalhados das faturas Delta
        """
        csv_path = Path(os.getenv(
            'DELTA_ITENS_CSV',
            '/home/jorge/Documentos/delta/dados/itens_faturas_nabeiro.csv'
        ))
        if not csv_path.exists():
            return pd.DataFrame()
        try:
            df = pd.read_csv(csv_path)
            if numero_fatura:
                # Converter para string para garantir match
                df['Numero_Fatura'] = df['Numero_Fatura'].astype(str)
                df = df[df['Numero_Fatura'] == str(numero_fatura)]
            return df
        except Exception as e:
            print(f"❌ Erro ao carregar itens Delta: {e}")
            return pd.DataFrame()

    def carregar_tudo_integrado_com_custos(self, data_inicio=None, data_fim=None):
        """
        Carrega todos os dados e adiciona informações de custos
        """
        print("🚀 Carregando dados do MariaDB (V9 - Otimizado)...")

        if not self._conectar():
            return pd.DataFrame()

        try:
            df_cafe = self.carregar_dados_dashboard(data_inicio, data_fim)
            df_outros = self.carregar_pos(data_inicio, data_fim)
            df_santa_casa = self.carregar_santa_casa(data_inicio, data_fim)

            dfs = []
            if not df_cafe.empty: dfs.append(df_cafe)
            if not df_outros.empty: dfs.append(df_outros)
            if not df_santa_casa.empty: dfs.append(df_santa_casa)

            if not dfs:
                return pd.DataFrame()

            df_vendas = pd.concat(dfs, ignore_index=True)
            df_vendas = df_vendas.sort_values('Data').reset_index(drop=True)

            # Adicionar colunas temporais (vectorizado)
            df_vendas['Ano'] = df_vendas['Data'].dt.year
            df_vendas['Mes'] = df_vendas['Data'].dt.month
            df_vendas['Semana'] = df_vendas['Data'].dt.isocalendar().week
            df_vendas['Dia_Semana'] = df_vendas['Data'].dt.dayofweek
            df_vendas['Trimestre'] = df_vendas['Data'].dt.quarter

            print(f"📊 Total: {len(df_vendas):,} registos carregados")

            print("💰 Calculando custos e comissões...")
            df_completo = self.cost_manager.calcular_custos_vendas(df_vendas)

            return df_completo

        finally:
            self._desconectar()

    def get_analise_break_even(self, df_vendas: pd.DataFrame) -> dict:
        """
        Calcula a análise de Break-Even (Ponto de Equilíbrio)

        Args:
            df_vendas: DataFrame com as vendas (já com custos calculados)

        Returns:
            Dicionário com métricas de Break-Even detalhadas
        """
        if df_vendas.empty:
            return {}

        # 1. Calcular margem de contribuição média (usar coluna já calculada)
        if 'Margem_Bruta_Pct' in df_vendas.columns:
            margem_media = df_vendas['Margem_Bruta_Pct'].mean()
        else:
            margem_media = 50.0  # Fallback se não existir

        # 2. Calcular break-even usando cost_manager
        # IMPORTANTE: Usar custos ESTIMADOS do CSV (não os reais parciais do Despesify)
        # porque as despesas fixas (renda, ordenados) só caem no dia 28
        data_inicio = df_vendas['Data'].min()
        data_fim = df_vendas['Data'].max()

        break_even = self.cost_manager.calcular_break_even(
            margem_contribuicao_media=margem_media,
            iva_medio=18.0,
            margem_seguranca_pct=15.0,
            usar_custos_reais=False,  # Sempre usar custos estimados para break-even
            data_inicio=data_inicio,
            data_fim=data_fim
        )

        # 3. Adicionar métricas atuais para comparação (Diário)
        dias_periodo = (data_fim - data_inicio).days + 1
        if dias_periodo < 1:
            dias_periodo = 1

        total_vendas = df_vendas['Valor'].sum()
        vendas_atuais_diarias = total_vendas / dias_periodo
        break_even['vendas_atuais_diarias'] = vendas_atuais_diarias

        # Recalcular margem de segurança real com base nas vendas atuais
        vendas_be_diaria = break_even.get('vendas_break_even_diaria', 0)

        if vendas_atuais_diarias > 0 and vendas_be_diaria > 0:
            margem_seg_real = ((vendas_atuais_diarias - vendas_be_diaria) / vendas_atuais_diarias) * 100
            break_even['margem_seguranca_pct'] = margem_seg_real
        else:
            break_even['margem_seguranca_pct'] = -100.0

        # Calcular dias para break-even (CORRETO)
        # Responde à pergunta: "Quantos dias de vendas são necessários para acumular
        # margem suficiente para cobrir os custos fixos mensais (que caem no dia 28)?"
        if vendas_atuais_diarias > 0 and margem_media > 0:
            custos_fixos_mensais = break_even.get('custos_fixos_mensais', 0)
            if custos_fixos_mensais > 0:
                # Margem de contribuição diária = vendas diárias × margem %
                margem_diaria = vendas_atuais_diarias * (margem_media / 100)
                # Dias necessários para cobrir os custos fixos
                break_even['dias_para_break_even'] = custos_fixos_mensais / margem_diaria
            else:
                break_even['dias_para_break_even'] = 0

        return break_even

    def testar_conexao(self) -> bool:
        if self._conectar():
            print("✅ Conexão com MariaDB OK")
            self._desconectar()
            return True
        else:
            print("❌ Falha na conexão com MariaDB")
            return False
