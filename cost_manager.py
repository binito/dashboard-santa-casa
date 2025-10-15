"""
Módulo de Gestão de Custos - Dashboard v5
Gestão de custos de produtos e operacionais
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')


class CostManager:
    """Gestor de custos de produtos e operacionais"""

    def __init__(self, custos_dir='dados_custos'):
        """
        Inicializa o gestor de custos

        Args:
            custos_dir: Diretório com ficheiros de custos
        """
        self.custos_dir = Path(custos_dir)
        self.custos_produtos = None
        self.custos_operacionais = None
        self.margens_categorias = None

        # Carregar dados
        self._carregar_custos()

    def _carregar_custos(self):
        """Carrega todos os ficheiros de custos"""
        try:
            # Custos de produtos
            arquivo_produtos = self.custos_dir / 'custos_produtos.csv'
            if arquivo_produtos.exists():
                self.custos_produtos = pd.read_csv(arquivo_produtos)
                # Converter percentagens
                if 'Margem_Bruta' in self.custos_produtos.columns:
                    self.custos_produtos['Margem_Bruta'] = self.custos_produtos['Margem_Bruta'].str.replace('%', '').astype(float)
            else:
                print(f"Aviso: {arquivo_produtos} não encontrado")
                self.custos_produtos = pd.DataFrame()

            # Custos operacionais
            arquivo_operacionais = self.custos_dir / 'custos_operacionais.csv'
            if arquivo_operacionais.exists():
                self.custos_operacionais = pd.read_csv(arquivo_operacionais)
            else:
                print(f"Aviso: {arquivo_operacionais} não encontrado")
                self.custos_operacionais = pd.DataFrame()

            # Margens por categoria
            arquivo_margens = self.custos_dir / 'margens_categorias.csv'
            if arquivo_margens.exists():
                self.margens_categorias = pd.read_csv(arquivo_margens)
                # Converter percentagens
                if 'Margem_Objetivo' in self.margens_categorias.columns:
                    self.margens_categorias['Margem_Objetivo'] = self.margens_categorias['Margem_Objetivo'].str.replace('%', '').astype(float)
                if 'IVA_Aplicavel' in self.margens_categorias.columns:
                    self.margens_categorias['IVA_Aplicavel'] = self.margens_categorias['IVA_Aplicavel'].str.replace('%', '').astype(float)
            else:
                print(f"Aviso: {arquivo_margens} não encontrado")
                self.margens_categorias = pd.DataFrame()

        except Exception as e:
            print(f"Erro ao carregar custos: {e}")
            self.custos_produtos = pd.DataFrame()
            self.custos_operacionais = pd.DataFrame()
            self.margens_categorias = pd.DataFrame()

    def get_custo_produto(self, nome_produto: str, categoria: str = None) -> float:
        """
        Retorna o custo unitário de um produto

        Args:
            nome_produto: Nome do produto
            categoria: Categoria do produto (opcional)

        Returns:
            Custo unitário (0 se não encontrado)
        """
        if self.custos_produtos is None or self.custos_produtos.empty:
            return 0.0

        # Buscar por nome exato
        filtro = self.custos_produtos['Produto'].str.lower() == nome_produto.lower()

        if filtro.any():
            return self.custos_produtos.loc[filtro, 'Custo_Unitario'].iloc[0]

        # Buscar por nome parcial
        filtro_parcial = self.custos_produtos['Produto'].str.lower().str.contains(nome_produto.lower(), na=False)

        if filtro_parcial.any():
            return self.custos_produtos.loc[filtro_parcial, 'Custo_Unitario'].iloc[0]

        # Se não encontrou, usar custo médio da categoria
        if categoria and not self.margens_categorias.empty:
            filtro_cat = self.margens_categorias['Categoria'] == categoria
            if filtro_cat.any():
                return self.margens_categorias.loc[filtro_cat, 'Custo_Medio_Estimado'].iloc[0]

        return 0.0

    def get_margem_categoria(self, categoria: str) -> float:
        """
        Retorna a margem objetivo de uma categoria

        Args:
            categoria: Nome da categoria

        Returns:
            Margem objetivo em % (0 se não encontrado)
        """
        if self.margens_categorias is None or self.margens_categorias.empty:
            return 0.0

        filtro = self.margens_categorias['Categoria'] == categoria

        if filtro.any():
            return self.margens_categorias.loc[filtro, 'Margem_Objetivo'].iloc[0]

        return 0.0

    def get_iva_categoria(self, categoria: str) -> float:
        """
        Retorna a taxa de IVA aplicável a uma categoria

        Args:
            categoria: Nome da categoria

        Returns:
            Taxa de IVA em % (23 se não encontrado)
        """
        if self.margens_categorias is None or self.margens_categorias.empty:
            return 23.0

        filtro = self.margens_categorias['Categoria'] == categoria

        if filtro.any():
            return self.margens_categorias.loc[filtro, 'IVA_Aplicavel'].iloc[0]

        return 23.0

    def calcular_custos_vendas(self, df_vendas: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona informações de custo ao DataFrame de vendas

        Args:
            df_vendas: DataFrame com vendas (deve ter colunas: Produto, Categoria, Valor, Qtd)

        Returns:
            DataFrame com colunas adicionais de custo
        """
        df = df_vendas.copy()

        # Verificar colunas necessárias
        if 'Produto' not in df.columns or 'Valor' not in df.columns:
            print("Erro: DataFrame deve ter colunas 'Produto' e 'Valor'")
            return df

        # Adicionar custo unitário
        df['Custo_Unitario'] = df.apply(
            lambda row: self.get_custo_produto(
                row['Produto'],
                row.get('Categoria')
            ),
            axis=1
        )

        # Calcular custo total
        if 'Qtd' in df.columns:
            df['Custo_Total'] = df['Custo_Unitario'] * df['Qtd']
        else:
            df['Custo_Total'] = df['Custo_Unitario']

        # Calcular lucro bruto
        df['Lucro_Bruto'] = df['Valor'] - df['Custo_Total']

        # Calcular margem bruta %
        df['Margem_Bruta_Pct'] = np.where(
            df['Valor'] > 0,
            (df['Lucro_Bruto'] / df['Valor']) * 100,
            0
        )

        # Adicionar margem objetivo da categoria
        if 'Categoria' in df.columns:
            df['Margem_Objetivo'] = df['Categoria'].apply(self.get_margem_categoria)
            df['IVA_Aplicavel'] = df['Categoria'].apply(self.get_iva_categoria)

        # Flag de margem abaixo do objetivo
        if 'Margem_Objetivo' in df.columns:
            df['Abaixo_Objetivo'] = df['Margem_Bruta_Pct'] < df['Margem_Objetivo']

        return df

    def get_custos_operacionais_mensais(self) -> float:
        """
        Retorna o total de custos operacionais mensais

        Returns:
            Total de custos mensais
        """
        if self.custos_operacionais is None or self.custos_operacionais.empty:
            return 0.0

        # Somar apenas custos fixos e variáveis (excluir "Calculado")
        custos_mensais = self.custos_operacionais[
            self.custos_operacionais['Tipo'] != 'Calculado'
        ]['Valor_Mensal'].sum()

        return custos_mensais

    def get_custos_operacionais_periodo(self, dias: int) -> float:
        """
        Retorna custos operacionais proporcionais a um período

        Args:
            dias: Número de dias do período

        Returns:
            Custos do período
        """
        custo_mensal = self.get_custos_operacionais_mensais()
        custo_diario = custo_mensal / 30
        return custo_diario * dias

    def get_resumo_custos_operacionais(self) -> pd.DataFrame:
        """
        Retorna resumo dos custos operacionais por categoria

        Returns:
            DataFrame com resumo
        """
        if self.custos_operacionais is None or self.custos_operacionais.empty:
            return pd.DataFrame()

        # Filtrar custos não calculados
        df = self.custos_operacionais[
            self.custos_operacionais['Tipo'] != 'Calculado'
        ].copy()

        resumo = df.groupby('Categoria').agg({
            'Valor_Mensal': 'sum',
            'Tipo': 'first'
        }).round(2)

        resumo.columns = ['Total_Mensal', 'Tipo']
        resumo['Percentual'] = (resumo['Total_Mensal'] / resumo['Total_Mensal'].sum() * 100).round(1)
        resumo = resumo.sort_values('Total_Mensal', ascending=False)

        return resumo

    def calcular_break_even(self, margem_contribuicao_media: float) -> Dict:
        """
        Calcula o ponto de equilíbrio (break-even)

        Args:
            margem_contribuicao_media: Margem de contribuição média (em %)

        Returns:
            Dicionário com informações de break-even
        """
        custos_fixos_mensais = self.get_custos_operacionais_mensais()

        if margem_contribuicao_media <= 0:
            return {
                'custos_fixos': custos_fixos_mensais,
                'margem_contribuicao': 0,
                'vendas_break_even': 0,
                'vendas_diarias_break_even': 0,
                'erro': 'Margem de contribuição deve ser positiva'
            }

        # Vendas necessárias para break-even
        vendas_break_even = custos_fixos_mensais / (margem_contribuicao_media / 100)
        vendas_diarias = vendas_break_even / 30

        return {
            'custos_fixos_mensais': custos_fixos_mensais,
            'margem_contribuicao_pct': margem_contribuicao_media,
            'vendas_break_even_mensal': vendas_break_even,
            'vendas_break_even_diaria': vendas_diarias,
            'custos_fixos_diarios': custos_fixos_mensais / 30
        }

    def analisar_rentabilidade_produtos(self, df_vendas: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
        """
        Analisa rentabilidade dos produtos

        Args:
            df_vendas: DataFrame com vendas e custos calculados
            top_n: Número de produtos a retornar

        Returns:
            DataFrame com análise de rentabilidade
        """
        if df_vendas.empty:
            return pd.DataFrame()

        # Agrupar por produto
        analise = df_vendas.groupby(['Produto', 'Categoria']).agg({
            'Valor': 'sum',
            'Custo_Total': 'sum',
            'Lucro_Bruto': 'sum',
            'Qtd': 'sum'
        }).round(2)

        # Calcular margem
        analise['Margem_Bruta_Pct'] = (
            (analise['Lucro_Bruto'] / analise['Valor']) * 100
        ).round(2)

        # Calcular ticket médio
        analise['Preco_Medio'] = (analise['Valor'] / analise['Qtd']).round(2)
        analise['Custo_Medio'] = (analise['Custo_Total'] / analise['Qtd']).round(2)

        # Classificar produtos
        analise['Classificacao'] = analise.apply(
            lambda row: self._classificar_produto(
                row['Lucro_Bruto'],
                row['Margem_Bruta_Pct'],
                row['Qtd']
            ),
            axis=1
        )

        # Ordenar por lucro bruto
        analise = analise.sort_values('Lucro_Bruto', ascending=False)

        return analise.head(top_n)

    def _classificar_produto(self, lucro: float, margem: float, volume: float) -> str:
        """
        Classifica produto segundo critérios de rentabilidade

        Returns:
            Classificação: Estrela, Cash Cow, Problema, ou Descontinuar
        """
        # Critérios (podem ser ajustados)
        alta_margem = margem > 50
        baixa_margem = margem < 30
        alto_volume = volume > 100
        baixo_volume = volume < 20

        if alta_margem and alto_volume:
            return '⭐ Estrela'
        elif baixa_margem and alto_volume:
            return '🐄 Cash Cow'
        elif alta_margem and baixo_volume:
            return '💎 Nicho Premium'
        elif baixa_margem and baixo_volume:
            return '⚠️ Descontinuar'
        else:
            return '📊 Normal'

    def analisar_rentabilidade_categorias(self, df_vendas: pd.DataFrame) -> pd.DataFrame:
        """
        Analisa rentabilidade por categoria

        Args:
            df_vendas: DataFrame com vendas e custos

        Returns:
            DataFrame com análise por categoria
        """
        if df_vendas.empty or 'Categoria' not in df_vendas.columns:
            return pd.DataFrame()

        analise = df_vendas.groupby('Categoria').agg({
            'Valor': 'sum',
            'Custo_Total': 'sum',
            'Lucro_Bruto': 'sum',
            'Qtd': 'sum'
        }).round(2)

        # Calcular métricas
        analise['Margem_Bruta_Pct'] = (
            (analise['Lucro_Bruto'] / analise['Valor']) * 100
        ).round(2)

        # Adicionar margem objetivo
        analise['Margem_Objetivo'] = analise.index.map(self.get_margem_categoria)

        # Diferença vs objetivo
        analise['Diferenca_Objetivo'] = (
            analise['Margem_Bruta_Pct'] - analise['Margem_Objetivo']
        ).round(2)

        # Status
        analise['Status'] = analise['Diferenca_Objetivo'].apply(
            lambda x: '✅ Acima' if x > 0 else '⚠️ Abaixo' if x < -5 else '➡️ No Alvo'
        )

        analise = analise.sort_values('Lucro_Bruto', ascending=False)

        return analise

    def calcular_metricas_financeiras(self, df_vendas: pd.DataFrame, dias_periodo: int) -> Dict:
        """
        Calcula métricas financeiras principais

        Args:
            df_vendas: DataFrame com vendas e custos
            dias_periodo: Número de dias do período

        Returns:
            Dicionário com métricas
        """
        if df_vendas.empty:
            return {}

        # Receitas e custos
        receita_total = df_vendas['Valor'].sum()
        cogs_total = df_vendas['Custo_Total'].sum() if 'Custo_Total' in df_vendas.columns else 0
        lucro_bruto = df_vendas['Lucro_Bruto'].sum() if 'Lucro_Bruto' in df_vendas.columns else 0

        # Custos operacionais
        custos_operacionais = self.get_custos_operacionais_periodo(dias_periodo)

        # Lucro líquido
        lucro_liquido = lucro_bruto - custos_operacionais

        # Margens
        margem_bruta_pct = (lucro_bruto / receita_total * 100) if receita_total > 0 else 0
        margem_liquida_pct = (lucro_liquido / receita_total * 100) if receita_total > 0 else 0

        # ROI
        roi = (lucro_liquido / custos_operacionais * 100) if custos_operacionais > 0 else 0

        return {
            'receita_total': receita_total,
            'cogs_total': cogs_total,
            'lucro_bruto': lucro_bruto,
            'custos_operacionais': custos_operacionais,
            'lucro_liquido': lucro_liquido,
            'margem_bruta_pct': margem_bruta_pct,
            'margem_liquida_pct': margem_liquida_pct,
            'roi_pct': roi,
            'custo_total': cogs_total + custos_operacionais,
            'dias_periodo': dias_periodo
        }


# Função auxiliar
def adicionar_custos_vendas(df_vendas: pd.DataFrame) -> pd.DataFrame:
    """Função conveniente para adicionar custos às vendas"""
    manager = CostManager()
    return manager.calcular_custos_vendas(df_vendas)


if __name__ == '__main__':
    # Teste do módulo
    print("=== Teste do CostManager ===\n")

    manager = CostManager()

    # Testar custos operacionais
    print(f"Custos operacionais mensais: €{manager.get_custos_operacionais_mensais():.2f}")
    print(f"Custos operacionais (30 dias): €{manager.get_custos_operacionais_periodo(30):.2f}\n")

    # Testar custos de produtos
    produtos_teste = ['Café', 'Imperial', 'Vinho Tinto']
    print("Custos de produtos:")
    for produto in produtos_teste:
        custo = manager.get_custo_produto(produto)
        print(f"  {produto}: €{custo:.3f}")

    print("\n✅ CostManager funcionando corretamente!")
