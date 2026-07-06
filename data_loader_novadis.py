"""
Módulo de carregamento e análise de dados da Novadis
Carrega histórico de encomendas do fornecedor Novadis com análise de custos, margens e forecasts

CARACTERÍSTICAS:
- Carrega dados da tabela 'novadis' no MariaDB
- Adiciona IVA (23%) aos preços
- Converte produtos em embalagens para unidades vendidas
- Mapeia produtos Novadis -> produtos POS
- Calcula custos reais por unidade vendida
- Forecasting baseado em histórico de encomendas
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import warnings
import os
from pathlib import Path
from dotenv import load_dotenv
import numpy as np

warnings.filterwarnings('ignore')

# Carregar variáveis de ambiente
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


class ProductConverter:
    """
    Conversor de produtos Novadis (embalagens) para unidades vendidas no POS

    Exemplos:
    - Barril 30L -> 150 copos de Imperial (20cl) OU 200 Martinis com cerveja (15cl)
    - Caixa 24x33cl -> 24 unidades
    - Caixa 12x1,5L -> 12 unidades
    """

    # Taxa de IVA em Portugal para bebidas (23%)
    # ALTERADO: Definido como 0 para assumir preço da fatura (sem IVA) como custo, 
    # pois o IVA é dedutível. Se quiser com IVA, mudar para 0.23
    IVA_RATE = 0.0

    # Dicionário de conversões: produto_novadis -> (produto_pos, fator_conversao, unidade)
    CONVERSOES = {
        # CERVEJAS - Barrils (30L = 30000ml)
        'Sagres Branca Barril 30L': {
            'produto_pos': 'Imperial', 
            'litros_barril': 30, 
            'ml_por_unidade': 200, 
            'tipo': 'barril',
            'observacao': 'Barril 30L (Equivalente a ~150 Imperiais)'
        },
        'Sagres Preta Barril 30L': {
            'produto_pos': 'Imperial', 
            'litros_barril': 30, 
            'ml_por_unidade': 200, 
            'tipo': 'barril',
            'observacao': 'Barril 30L (Equivalente a ~150 Imperiais)'
        },
        'Super Bock Barril 30L': {
            'produto_pos': 'Imperial', 
            'litros_barril': 30, 
            'ml_por_unidade': 200, 
            'tipo': 'barril',
            'observacao': 'Barril 30L (Equivalente a ~150 Imperiais)'
        },

        # CERVEJAS - Mini (20cl)
        'Sagres Branca Mini Retornável 24x20cl': {
            'produto_pos': 'CERVEJA MINI',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 200,
            'tipo': 'garrafa'
        },
        'Sagres Preta Mini Retornável 24x20cl': {
            'produto_pos': 'CERVEJA MINI',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 200,
            'tipo': 'garrafa'
        },

        # CERVEJAS - Média (33cl)
        'Sagres Branca Média Retornável 24x33cl': {
            'produto_pos': 'CERVEJA MEDIA',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 330,
            'tipo': 'garrafa'
        },
        'Sagres Preta Média Retornável 24x33cl': {
            'produto_pos': 'Cerveja Preta 33cl',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 330,
            'tipo': 'garrafa'
        },
        'Sagres Sem Álcool 24x33cl': {
            'produto_pos': 'Cerveja Sem Álcool',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 330,
            'tipo': 'garrafa'
        },
        
        # CERVEJAS - Lata
        'Sagres Lata 24x33cl': {
            'produto_pos': 'Cerveja Lata',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 330,
            'tipo': 'lata'
        },

        # ÁGUAS
        'Luso 12x1,5L': {
            'produto_pos': 'Água 1,5L',
            'unidades_por_caixa': 12,
            'ml_por_unidade': 1500,
            'tipo': 'garrafa'
        },
        'Luso 24x33cl': {
            'produto_pos': 'Água 33cl',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 330,
            'tipo': 'garrafa'
        },
        'Luso 24x50cl': {
            'produto_pos': 'Água 50cl',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 500,
            'tipo': 'garrafa'
        },
        'Água das Pedras 24x25cl': {
            'produto_pos': 'Água Gaseificada',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 250,
            'tipo': 'garrafa'
        },

        # VINHOS E ESPUMANTES - Caixas com garrafas pequenas (5,5cl)
        'Moscatel Favaito 50x5,5cl': {
            'produto_pos': 'Moscatel',
            'unidades_por_caixa': 50,
            'ml_por_unidade': 55,
            'tipo': 'garrafa_mini'
        },
        'Martini Rosso 50x5,5cl': {
            'produto_pos': 'Martini',
            'unidades_por_caixa': 50,
            'ml_por_unidade': 55,
            'tipo': 'garrafa_mini'
        },
        'Martini Bianco 50x5,5cl': {
            'produto_pos': 'Martini Bianco',
            'unidades_por_caixa': 50,
            'ml_por_unidade': 55,
            'tipo': 'garrafa_mini'
        },

        # REFRIGERANTES
        'Coca-Cola 24x33cl': {
            'produto_pos': 'Coca-Cola',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 330,
            'tipo': 'garrafa'
        },
        'Coca-Cola Zero 24x33cl': {
            'produto_pos': 'Coca-Cola Zero',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 330,
            'tipo': 'garrafa'
        },
        'Fanta Laranja 24x33cl': {
            'produto_pos': 'Fanta',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 330,
            'tipo': 'garrafa'
        },
        'Sprite 24x33cl': {
            'produto_pos': 'Sprite',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 330,
            'tipo': 'garrafa'
        },
        'Sumol Laranja 24x33cl': {
            'produto_pos': 'Sumol Laranja',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 330,
            'tipo': 'garrafa'
        },
        'Sumol Ananás 24x33cl': {
            'produto_pos': 'Sumol Ananás',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 330,
            'tipo': 'garrafa'
        },
        'Ice Tea Pêssego 24x33cl': {
            'produto_pos': 'Ice Tea',
            'unidades_por_caixa': 24,
            'ml_por_unidade': 330,
            'tipo': 'garrafa'
        },
    }

    def __init__(self):
        self.custom_conversoes = self._carregar_mapeamentos_custom()

    def _carregar_mapeamentos_custom(self):
        """Carrega mapeamentos customizados de um arquivo CSV"""
        caminho_map = Path(__file__).parent / 'mapeamento_unidades_novadis.csv'
        if caminho_map.exists():
            try:
                df = pd.read_csv(caminho_map)
                # Criar dicionário: produto_novadis -> unidades_por_caixa
                return dict(zip(df['produto_novadis'], df['unidades_por_caixa']))
            except Exception as e:
                print(f"⚠️ Erro ao carregar mapeamento customizado: {e}")
        return {}

    @classmethod
    def adicionar_iva(cls, preco_sem_iva):
        """Adiciona IVA (23%) ao preço"""
        return preco_sem_iva * (1 + cls.IVA_RATE)

    def converter_produto(self, produto_novadis, quantidade, preco_unitario_sem_iva):
        """
        Converte produto da Novadis (embalagem) para unidades vendidas no POS

        Args:
            produto_novadis: Nome do produto na encomenda Novadis
            quantidade: Quantidade de embalagens encomendadas
            preco_unitario_sem_iva: Preço unitário da embalagem (sem IVA)

        Returns:
            Lista de dicionários com conversões:
            [{'produto_pos': str, 'unidades': int, 'custo_unitario_com_iva': float, 'tipo': str}]
        """
        # Adicionar IVA ao preço
        preco_unitario_com_iva = self.adicionar_iva(preco_unitario_sem_iva)

        # 1. Verificar se existe mapeamento customizado (carregado do CSV)
        if hasattr(self, 'custom_conversoes') and produto_novadis in self.custom_conversoes:
            unidades_por_caixa = self.custom_conversoes[produto_novadis]
            return [{
                'produto_pos': produto_novadis,
                'unidades': quantidade * unidades_por_caixa,
                'custo_unitario_com_iva': preco_unitario_com_iva / unidades_por_caixa,
                'tipo': 'custom',
                'observacao': f'Mapeamento customizado: {unidades_por_caixa} unid.'
            }]

        # 2. Verificar se produto existe no mapeamento fixo
        if produto_novadis not in self.CONVERSOES:
            # Tentar extrair do nome (ex: 24x20cl, 24 x 33cl, 12x1.5L)
            import re
            # Regex procura por: numero + x + numero + (cl|L|ml)
            match = re.search(r'(\d+)\s*[xX]\s*(\d+(?:[.,]\d+)?)\s*(cl|cl|L|l|ml|ML)', produto_novadis)
            
            if match:
                unidades_por_caixa = int(match.group(1))
                return [{
                    'produto_pos': produto_novadis,
                    'unidades': quantidade * unidades_por_caixa,
                    'custo_unitario_com_iva': preco_unitario_com_iva / unidades_por_caixa,
                    'tipo': 'extraido',
                    'observacao': f'Extraído automaticamente: {unidades_por_caixa} unid.'
                }]

            # Produto não mapeado - retornar como genérico
            return [{
                'produto_pos': produto_novadis,
                'unidades': quantidade,
                'custo_unitario_com_iva': preco_unitario_com_iva,
                'tipo': 'generico',
                'observacao': 'Produto não mapeado'
            }]

        conversao = self.CONVERSOES[produto_novadis]
        resultados = []

        if isinstance(conversao, list):
            # Caso legado ou se houver partilha real de custo (não usado para barris agora)
            for conv in conversao:
                # ... lógica existente ...
                pass
        
        # Caso especial: Barril (Dicionário com info de litros)
        elif 'litros_barril' in conversao:
            litros_barril = conversao['litros_barril']
            ml_por_unidade = conversao['ml_por_unidade']
            unidades_por_barril = (litros_barril * 1000) / ml_por_unidade

            total_unidades = int(quantidade * unidades_por_barril)
            custo_por_unidade = preco_unitario_com_iva / unidades_por_barril

            resultados.append({
                'produto_pos': conversao['produto_pos'],
                'unidades': total_unidades,
                'custo_unitario_com_iva': custo_por_unidade,
                'tipo': conversao['tipo'],
                'observacao': conversao.get('observacao', f'Convertido de barril {litros_barril}L')
            })

        # Caso normal: Caixas com unidades
        else:
            unidades_por_caixa = conversao['unidades_por_caixa']
            total_unidades = quantidade * unidades_por_caixa
            custo_por_unidade = preco_unitario_com_iva / unidades_por_caixa

            resultados.append({
                'produto_pos': conversao['produto_pos'],
                'unidades': total_unidades,
                'custo_unitario_com_iva': custo_por_unidade,
                'tipo': conversao['tipo'],
                'observacao': f'Convertido de caixa {unidades_por_caixa} unidades'
            })

        return resultados


class NovadisDataLoader:
    """
    Carregador de dados da Novadis (histórico de encomendas)
    """

    # Configuração do banco de dados
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', '3306')),
        'user': os.getenv('DB_USER', 'dashboard_app'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME_DASHBOARD', 'dashboard')
    }

    def __init__(self):
        """Inicializa o carregador Novadis"""
        self.connection = None
        self.converter = ProductConverter()

    def _conectar(self):
        """Estabelece conexão com a base de dados"""
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

    def carregar_encomendas(self, data_inicio=None, data_fim=None):
        """
        Carrega histórico de encomendas da Novadis

        Args:
            data_inicio: Data inicial do filtro (opcional)
            data_fim: Data final do filtro (opcional)

        Returns:
            DataFrame com encomendas da Novadis (dados brutos)
        """
        if not self._conectar():
            return pd.DataFrame()

        try:
            query = """
                SELECT
                    id,
                    data,
                    numero_pedido,
                    produto,
                    quantidade,
                    preco_unitario,
                    preco_total
                FROM novadis
            """

            # Adicionar filtros de data
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

            query += " ORDER BY data DESC, numero_pedido, id"

            # Executar query
            if params:
                df = pd.read_sql(query, self.connection, params=params)
            else:
                df = pd.read_sql(query, self.connection)

            if df.empty:
                return df

            # Converter data para datetime
            df['data'] = pd.to_datetime(df['data'])

            print(f"✓ Carregadas {len(df):,} encomendas da Novadis")
            return df

        except Exception as e:
            print(f"❌ Erro ao carregar encomendas Novadis: {e}")
            return pd.DataFrame()
        finally:
            self._desconectar()

    def processar_encomendas_com_conversao(self, df_encomendas=None, data_inicio=None, data_fim=None):
        """
        Processa encomendas e converte produtos para unidades vendidas no POS

        Args:
            df_encomendas: DataFrame com encomendas (se None, carrega automaticamente)
            data_inicio: Data inicial do filtro
            data_fim: Data final do filtro

        Returns:
            DataFrame com produtos convertidos para unidades POS
        """
        # Carregar encomendas se não fornecidas
        if df_encomendas is None:
            df_encomendas = self.carregar_encomendas(data_inicio, data_fim)

        if df_encomendas.empty:
            return pd.DataFrame()

        # Processar cada linha e converter produtos
        linhas_processadas = []

        for _, row in df_encomendas.iterrows():
            conversoes = self.converter.converter_produto(
                row['produto'],
                row['quantidade'],
                row['preco_unitario']
            )

            for conv in conversoes:
                linhas_processadas.append({
                    'data': row['data'],
                    'numero_pedido': row['numero_pedido'],
                    'produto_novadis': row['produto'],
                    'quantidade_encomendada': row['quantidade'],
                    'preco_unitario_sem_iva': row['preco_unitario'],
                    'preco_unitario_com_iva': self.converter.adicionar_iva(row['preco_unitario']),
                    'produto_pos': conv['produto_pos'],
                    'unidades_vendaveis': conv['unidades'],
                    'custo_unitario': conv['custo_unitario_com_iva'],
                    'custo_total': conv['custo_unitario_com_iva'] * conv['unidades'],
                    'tipo_produto': conv['tipo'],
                    'observacao': conv.get('observacao', '')
                })

        df_processado = pd.DataFrame(linhas_processadas)

        if not df_processado.empty:
            # Adicionar colunas temporais
            df_processado['ano'] = df_processado['data'].dt.year
            df_processado['mes'] = df_processado['data'].dt.month
            df_processado['semana'] = df_processado['data'].dt.isocalendar().week
            df_processado['ano_mes'] = df_processado['data'].dt.to_period('M').astype(str)

            print(f"✓ Processadas {len(df_processado):,} linhas de produtos convertidos")

        return df_processado

    def get_resumo_custos_por_produto(self, df_processado=None, data_inicio=None, data_fim=None):
        """
        Retorna resumo de custos por produto POS

        Args:
            df_processado: DataFrame processado (se None, processa automaticamente)
            data_inicio: Data inicial do filtro
            data_fim: Data final do filtro

        Returns:
            DataFrame com resumo de custos por produto
        """
        if df_processado is None:
            df_processado = self.processar_encomendas_com_conversao(data_inicio=data_inicio, data_fim=data_fim)

        if df_processado.empty:
            return pd.DataFrame()

        resumo = df_processado.groupby('produto_pos').agg({
            'unidades_vendaveis': 'sum',
            'custo_total': 'sum',
            'numero_pedido': 'nunique'
        }).reset_index()

        resumo['custo_medio_unitario'] = resumo['custo_total'] / resumo['unidades_vendaveis']
        resumo = resumo.rename(columns={
            'numero_pedido': 'num_encomendas'
        })

        return resumo.sort_values('custo_total', ascending=False)

    def get_forecast_mensal(self, df_processado=None, meses_historico=3):
        """
        Calcula forecast de encomendas baseado em histórico de consumo

        Args:
            df_processado: DataFrame processado
            meses_historico: Número de meses de histórico para calcular média

        Returns:
            DataFrame com forecast por produto
        """
        if df_processado is None:
            df_processado = self.processar_encomendas_com_conversao()

        if df_processado.empty:
            return pd.DataFrame()

        # Filtrar últimos N meses
        data_limite = df_processado['data'].max() - timedelta(days=meses_historico * 30)
        df_recente = df_processado[df_processado['data'] >= data_limite]

        if df_recente.empty:
            return pd.DataFrame()

        # Calcular consumo médio mensal por produto
        consumo_mensal = df_recente.groupby(['produto_pos', 'ano_mes']).agg({
            'unidades_vendaveis': 'sum',
            'custo_total': 'sum'
        }).reset_index()

        # Calcular média por produto
        forecast = consumo_mensal.groupby('produto_pos').agg({
            'unidades_vendaveis': 'mean',
            'custo_total': 'mean'
        }).reset_index()

        forecast = forecast.rename(columns={
            'unidades_vendaveis': 'forecast_unidades_mes',
            'custo_total': 'forecast_custo_mes'
        })

        forecast['forecast_custo_unitario'] = forecast['forecast_custo_mes'] / forecast['forecast_unidades_mes']

        return forecast.sort_values('forecast_custo_mes', ascending=False)

    def get_analise_tendencias(self, df_processado=None):
        """
        Analisa tendências de preços e consumo ao longo do tempo

        Returns:
            DataFrame com análise de tendências
        """
        if df_processado is None:
            df_processado = self.processar_encomendas_com_conversao()

        if df_processado.empty:
            return pd.DataFrame()

        # Agrupar por produto e mês
        tendencias = df_processado.groupby(['produto_pos', 'ano_mes']).agg({
            'unidades_vendaveis': 'sum',
            'custo_unitario': 'mean',
            'custo_total': 'sum'
        }).reset_index()

        return tendencias.sort_values(['produto_pos', 'ano_mes'])


def testar_novadis_loader():
    """Testa o carregador Novadis"""
    print("="*70)
    print("TESTE DO NOVADIS DATA LOADER")
    print("="*70)

    loader = NovadisDataLoader()

    # 1. Carregar encomendas
    print("\n1. Carregando encomendas...")
    df_encomendas = loader.carregar_encomendas()
    if not df_encomendas.empty:
        print(f"\n   Período: {df_encomendas['data'].min()} → {df_encomendas['data'].max()}")
        print(f"   Total de encomendas: {df_encomendas['numero_pedido'].nunique()}")
        print(f"   Total de linhas: {len(df_encomendas)}")
        print(f"\n   Produtos únicos: {df_encomendas['produto'].nunique()}")
        print("\n   Primeiras encomendas:")
        print(df_encomendas.head())

    # 2. Processar com conversão
    print("\n2. Processando com conversão de produtos...")
    df_processado = loader.processar_encomendas_com_conversao(df_encomendas)
    if not df_processado.empty:
        print("\n   Primeiras conversões:")
        print(df_processado[['data', 'produto_novadis', 'produto_pos', 'unidades_vendaveis', 'custo_unitario']].head(10))

    # 3. Resumo de custos
    print("\n3. Resumo de custos por produto POS...")
    resumo = loader.get_resumo_custos_por_produto(df_processado)
    if not resumo.empty:
        print(resumo)

    # 4. Forecast
    print("\n4. Forecast mensal...")
    forecast = loader.get_forecast_mensal(df_processado)
    if not forecast.empty:
        print(forecast)

    print("\n" + "="*70)
    print("✅ TESTE CONCLUÍDO!")
    print("="*70)


if __name__ == '__main__':
    testar_novadis_loader()
