"""
Módulo de carregamento de dados para Dashboard v7
Com integração de custos REAIS do Despesify + custos estimados
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import warnings
import re
from data_loader_v4 import DataLoaderV4
from cost_manager_v2 import CostManagerV2  # NOVA VERSÃO COM DESPESIFY

warnings.filterwarnings('ignore')


class DataLoaderV7(DataLoaderV4):
    """Carregador de dados com integração de custos REAIS (Despesify) + estimados"""

    def __init__(self,
                 santa_casa_dir='dados_vendas',
                 pos1_dir='/home/jorge/Documentos/pos/pos_1',
                 pos2_dir='/home/jorge/Documentos/pos/pos_2',
                 custos_dir='dados_custos',
                 santa_casa_file='/home/jorge/Documentos/Santa casa/dados/dados_extracao.txt',
                 usar_despesify=True):
        # Inicializar classe pai
        super().__init__(santa_casa_dir, pos1_dir, pos2_dir)

        # Inicializar gestor de custos v2 (com Despesify)
        self.cost_manager = CostManagerV2(custos_dir, usar_despesify=usar_despesify)

        # Ficheiro da Santa Casa (formato do dashboard original)
        self.santa_casa_file = Path(santa_casa_file)

    def carregar_santa_casa_extracao(self):
        """
        Carrega dados do ficheiro dados_extracao.txt da Santa Casa
        (Formato usado no dashboard original da porta 8501)
        """
        if not self.santa_casa_file.exists():
            print(f"Ficheiro Santa Casa não encontrado: {self.santa_casa_file}")
            return pd.DataFrame()

        try:
            # Lendo o arquivo
            try:
                text = self.santa_casa_file.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    text = self.santa_casa_file.read_text(encoding='cp1252')
                except UnicodeDecodeError:
                    text = self.santa_casa_file.read_text(encoding='latin-1')

            data = text.splitlines()
            records = []

            # Regex para extrair dados
            pattern = r'^(.+?):\s*(\d+\.\d+)\s*\(Data de Emiss[ãa]o:\s*(\d{2}-\d{2}-\d{4})\)'

            for line in data:
                line = line.strip()
                if not line:
                    continue

                match = re.match(pattern, line)
                if match:
                    jogo = match.group(1).strip()
                    valor = float(match.group(2))
                    data_emissao = match.group(3)

                    # Renomear jogos específicos
                    if 'Subtotal (LI)' in jogo:
                        jogo = 'Lotaria Instantânea'
                    elif 'Subtotal (LP)' in jogo:
                        jogo = 'Lotaria Popular'
                    elif 'Subtotal (LC)' in jogo:
                        jogo = 'Lotaria Clássica'

                    records.append({
                        'Produto': jogo,
                        'Valor': valor,
                        'Data_Emissao': data_emissao
                    })

            # Criar DataFrame
            df = pd.DataFrame(records)
            if df.empty:
                return df

            df['Data_Emissao'] = pd.to_datetime(df['Data_Emissao'], format='%d-%m-%Y')

            # Adicionar +2 dias a todas as datas (formato da Santa Casa)
            df['Data'] = df['Data_Emissao'] + pd.Timedelta(days=2)

            # Adicionar metadados
            df['Fonte'] = 'Santa Casa'
            df['Categoria'] = 'Jogos Santa Casa'
            df['Subcategoria'] = df['Produto']  # Usar Produto como Subcategoria
            df['Qtd'] = 1.0  # Jogos Santa Casa são vendas totais, não unidades

            # Selecionar colunas finais
            df = df[['Data', 'Produto', 'Valor', 'Qtd', 'Fonte', 'Categoria', 'Subcategoria']].copy()

            print(f"✓ Carregados {len(df)} registos da Santa Casa")
            return df

        except Exception as e:
            print(f"Erro ao carregar dados Santa Casa: {e}")
            return pd.DataFrame()

    def carregar_tudo_integrado_com_custos(self):
        """
        Carrega todos os dados e adiciona informações de custos

        Returns:
            DataFrame completo com vendas e custos
        """
        # Carregar dados da Santa Casa (ficheiro único)
        print("Carregando dados Santa Casa...")
        df_santa_casa = self.carregar_santa_casa_extracao()

        # Carregar dados POS (café e outros)
        print("Carregando vendas de café...")
        df_cafe = self.carregar_vendas_cafe()

        print("Carregando outros produtos...")
        df_outros = self.carregar_outros_produtos()

        # Combinar todos os DataFrames
        dfs = []
        if not df_santa_casa.empty:
            dfs.append(df_santa_casa)
        if not df_cafe.empty:
            dfs.append(df_cafe)
        if not df_outros.empty:
            dfs.append(df_outros)

        if not dfs:
            return pd.DataFrame()

        df_vendas = pd.concat(dfs, ignore_index=True)
        df_vendas = df_vendas.sort_values('Data').reset_index(drop=True)

        # Adicionar colunas temporais
        df_vendas['Ano'] = df_vendas['Data'].dt.year
        df_vendas['Mes'] = df_vendas['Data'].dt.month
        df_vendas['Semana'] = df_vendas['Data'].dt.isocalendar().week
        df_vendas['Dia_Semana'] = df_vendas['Data'].dt.dayofweek
        df_vendas['Trimestre'] = df_vendas['Data'].dt.quarter

        # Adicionar informações de custos
        print("Calculando custos e comissões...")
        df_completo = self.cost_manager.calcular_custos_vendas(df_vendas)

        return df_completo

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
        # Carregar dados se não fornecido
        if df is None:
            df = self.carregar_tudo_integrado_com_custos()

        if df.empty:
            return {}

        # Filtrar por data se especificado
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

    def get_analise_break_even(self, df: pd.DataFrame = None) -> dict:
        """
        Retorna análise de break-even

        Args:
            df: DataFrame com dados (se None, carrega tudo)

        Returns:
            Dicionário com análise de break-even
        """
        # Carregar dados se não fornecido
        if df is None:
            df = self.carregar_tudo_integrado_com_custos()

        if df.empty:
            return {}

        # Calcular margem de contribuição média
        if 'Margem_Bruta_Pct' in df.columns:
            margem_media = df['Margem_Bruta_Pct'].mean()
        else:
            margem_media = 50.0  # Default

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

            # Dias para atingir break-even mensal
            if vendas_atuais_diarias > 0:
                break_even['dias_para_break_even'] = (
                    break_even['vendas_break_even_mensal'] / vendas_atuais_diarias
                )

        return break_even

    def get_produtos_margem_negativa(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Retorna produtos com margem negativa ou muito baixa

        Args:
            df: DataFrame com dados

        Returns:
            DataFrame com produtos problemáticos
        """
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

        # Calcular margem corretamente: (Lucro Total / Valor Total) × 100
        analise['Margem_Bruta_Pct'] = (analise['Lucro_Bruto'] / analise['Valor'] * 100).round(2)

        analise = analise.sort_values('Margem_Bruta_Pct')

        return analise

    def get_produtos_estrela(self, df: pd.DataFrame = None, top_n: int = 10) -> pd.DataFrame:
        """
        Retorna produtos estrela (alta margem + alto volume)

        Args:
            df: DataFrame com dados
            top_n: Número de produtos a retornar

        Returns:
            DataFrame com produtos estrela
        """
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

        # Calcular margem corretamente: (Lucro Total / Valor Total) × 100
        analise['Margem_Bruta_Pct'] = (analise['Lucro_Bruto'] / analise['Valor'] * 100).round(2)

        # Filtrar alta margem (>50%) e alto lucro
        estrelas = analise[
            (analise['Margem_Bruta_Pct'] > 50) &
            (analise['Lucro_Bruto'] > analise['Lucro_Bruto'].quantile(0.5))
        ].copy()

        # Calcular score
        estrelas['Score'] = (
            estrelas['Lucro_Bruto'] * estrelas['Margem_Bruta_Pct']
        )

        estrelas = estrelas.sort_values('Score', ascending=False)

        return estrelas.head(top_n)

    def get_analise_por_categoria(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """
        Retorna análise financeira por categoria

        Args:
            df: DataFrame com dados

        Returns:
            DataFrame com análise por categoria
        """
        if df is None:
            df = self.carregar_tudo_integrado_com_custos()

        return self.cost_manager.analisar_rentabilidade_categorias(df)

    def comparar_periodo(self, df_atual: pd.DataFrame, df_anterior: pd.DataFrame) -> dict:
        """
        Compara métricas entre dois períodos

        Args:
            df_atual: DataFrame do período atual
            df_anterior: DataFrame do período anterior

        Returns:
            Dicionário com comparações
        """
        if df_atual.empty or df_anterior.empty:
            return {}

        # Calcular datas e dias
        data_min_atual = df_atual['Data'].min().to_pydatetime()
        data_max_atual = df_atual['Data'].max().to_pydatetime()
        data_min_anterior = df_anterior['Data'].min().to_pydatetime()
        data_max_anterior = df_anterior['Data'].max().to_pydatetime()

        dias_atual = (data_max_atual - data_min_atual).days + 1
        dias_anterior = (data_max_anterior - data_min_anterior).days + 1

        # Métricas dos dois períodos (com datas para Despesify)
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


# Função auxiliar
def carregar_dados_completos_v5():
    """Função conveniente para carregar dados v5"""
    loader = DataLoaderV5()
    return loader.carregar_tudo_integrado_com_custos()


if __name__ == '__main__':
    print("=== Teste do DataLoaderV5 ===\n")
    loader = DataLoaderV5()

    # Carregar dados
    print("Carregando dados com custos...")
    df = loader.carregar_tudo_integrado_com_custos()

    print(f"\nTotal de registos: {len(df)}")

    if not df.empty:
        print(f"\nColunas disponíveis:")
        print(df.columns.tolist())

        print(f"\nPrimeiras linhas:")
        print(df[['Data', 'Produto', 'Categoria', 'Valor', 'Custo_Unitario', 'Lucro_Bruto', 'Margem_Bruta_Pct']].head())

        # Resumo financeiro
        print("\n=== Resumo Financeiro ===")
        resumo = loader.get_resumo_financeiro(df)
        for chave, valor in resumo.items():
            if isinstance(valor, float):
                print(f"{chave}: €{valor:,.2f}" if 'pct' not in chave else f"{chave}: {valor:.2f}%")

        # Break-even
        print("\n=== Análise Break-Even ===")
        be = loader.get_analise_break_even(df)
        print(f"Vendas diárias necessárias para break-even: €{be.get('vendas_break_even_diaria', 0):,.2f}")

    print("\n✅ DataLoaderV5 funcionando corretamente!")
