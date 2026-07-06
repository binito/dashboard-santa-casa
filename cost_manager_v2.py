"""
Módulo de Gestão de Custos v2 - Dashboard v7
Sistema HÍBRIDO: Despesas Reais (Despesify) + Custos Estimados (CSV) + Comissões Santa Casa
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime, timedelta
import warnings

from despesify_loader import DespesifyLoader

warnings.filterwarnings('ignore')


class CostManagerV2:
    """
    Gestor de custos HÍBRIDO que combina:
    1. Despesas REAIS do Despesify (desde 1/12/2025)
    2. Custos ESTIMADOS dos CSVs (antes de 1/12/2025 ou quando Despesify não tem dados)
    3. Comissões Santa Casa (cálculo automático)
    4. Custos de produtos (CSV - mantém-se)
    """

    # Percentagens de comissão dos jogos Santa Casa
    COMISSOES_SANTA_CASA = {
        'Euromilhões': 5.0,
        'EuroDreams': 5.0,
        'Totoloto': 7.0,
        'M1lhao': 5.0,
        'Totobola': 7.0,
        'Hípicas': 7.0,
        'Placard': 5.0,
        'Lotaria Instantânea': 10.0,
        'Raspadinha': 10.0,
        'Lotaria Popular': 12.5,
        'Lotaria Clássica': 12.7
    }

    # Data a partir da qual usa despesas REAIS do Despesify
    DATA_INICIO_DESPESIFY = datetime(2025, 12, 1)

    def __init__(self, custos_dir='dados_custos', usar_despesify=True):
        """
        Inicializa o gestor de custos

        Args:
            custos_dir: Diretório com ficheiros de custos estimados (CSV)
            usar_despesify: Se True, carrega despesas reais do Despesify
        """
        self.custos_dir = Path(custos_dir)
        self.usar_despesify = usar_despesify

        # Dados dos CSVs (custos estimados/históricos)
        self.custos_produtos = None
        self.custos_operacionais_estimados = None
        self.margens_categorias = None

        # Loader do Despesify (despesas reais)
        self.despesify_loader = None
        if usar_despesify:
            try:
                self.despesify_loader = DespesifyLoader()
                if not self.despesify_loader.validar_conexao():
                    print("⚠️ Aviso: Não foi possível conectar ao Despesify. Usando apenas custos estimados.")
                    self.despesify_loader = None
            except Exception as e:
                print(f"⚠️ Aviso: Erro ao inicializar Despesify: {e}")
                self.despesify_loader = None

        # Carregar dados dos CSVs
        self._carregar_custos_csv()

    def _carregar_custos_csv(self):
        """Carrega ficheiros de custos estimados (CSVs)"""
        try:
            # Custos de produtos (mantém-se sempre)
            arquivo_produtos = self.custos_dir / 'custos_produtos.csv'
            if arquivo_produtos.exists():
                self.custos_produtos = pd.read_csv(arquivo_produtos)
                if 'Margem_Bruta' in self.custos_produtos.columns:
                    self.custos_produtos['Margem_Bruta'] = self.custos_produtos['Margem_Bruta'].str.replace('%', '').astype(float)
            else:
                print(f"⚠️ Aviso: {arquivo_produtos} não encontrado")
                self.custos_produtos = pd.DataFrame()

            # Custos operacionais ESTIMADOS (fallback quando não há dados reais)
            arquivo_operacionais = self.custos_dir / 'custos_operacionais.csv'
            if arquivo_operacionais.exists():
                self.custos_operacionais_estimados = pd.read_csv(arquivo_operacionais)
            else:
                print(f"⚠️ Aviso: {arquivo_operacionais} não encontrado")
                self.custos_operacionais_estimados = pd.DataFrame()

            # Margens por categoria
            arquivo_margens = self.custos_dir / 'margens_categorias.csv'
            if arquivo_margens.exists():
                self.margens_categorias = pd.read_csv(arquivo_margens)
                if 'Margem_Objetivo' in self.margens_categorias.columns:
                    self.margens_categorias['Margem_Objetivo'] = self.margens_categorias['Margem_Objetivo'].str.replace('%', '').astype(float)
                if 'IVA_Aplicavel' in self.margens_categorias.columns:
                    self.margens_categorias['IVA_Aplicavel'] = self.margens_categorias['IVA_Aplicavel'].str.replace('%', '').astype(float)
            else:
                print(f"⚠️ Aviso: {arquivo_margens} não encontrado")
                self.margens_categorias = pd.DataFrame()

        except Exception as e:
            print(f"❌ Erro ao carregar custos CSV: {e}")
            self.custos_produtos = pd.DataFrame()
            self.custos_operacionais_estimados = pd.DataFrame()
            self.margens_categorias = pd.DataFrame()

    def get_total_custos_operacionais(self) -> float:
        """
        Retorna o total mensal de custos operacionais (estimado ou real)
        Por padrão, retorna a soma dos custos fixos estimados no CSV
        """
        if self.custos_operacionais_estimados is not None and not self.custos_operacionais_estimados.empty:
            return self.custos_operacionais_estimados['Valor'].sum()
        return 0.0

    def get_custo_produto(self, nome_produto: str, categoria: str = None) -> float:
        """
        Retorna o custo unitário de um produto (do CSV)

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

    def is_jogo_santa_casa(self, nome_produto: str, categoria: str = None) -> bool:
        """Verifica se é um jogo da Santa Casa"""
        if categoria == 'JOGOS_SANTA_CASA':
            return True

        nome_lower = str(nome_produto).lower()
        jogos_santa_casa = [jogo.lower() for jogo in self.COMISSOES_SANTA_CASA.keys()]
        return any(jogo in nome_lower for jogo in jogos_santa_casa)

    def get_comissao_santa_casa(self, nome_produto: str) -> float:
        """Retorna a percentagem de comissão de um jogo Santa Casa"""
        if nome_produto in self.COMISSOES_SANTA_CASA:
            return self.COMISSOES_SANTA_CASA[nome_produto]

        nome_lower = str(nome_produto).lower()
        for jogo, comissao in self.COMISSOES_SANTA_CASA.items():
            if jogo.lower() in nome_lower or nome_lower in jogo.lower():
                return comissao

        return 0.0

    def calcular_custo_ou_comissao(self, nome_produto: str, valor_venda: float,
                                   categoria: str = None, qtd: float = 1.0) -> Tuple[float, str]:
        """
        Calcula custo (produtos) ou comissão (Santa Casa)

        Args:
            nome_produto: Nome do produto
            valor_venda: Valor da venda
            categoria: Categoria do produto
            qtd: Quantidade vendida

        Returns:
            Tuple (custo_total, tipo) onde tipo é 'comissao' ou 'custo'
        """
        if self.is_jogo_santa_casa(nome_produto, categoria):
            percentagem = self.get_comissao_santa_casa(nome_produto)
            comissao = valor_venda * (percentagem / 100.0)
            return (comissao, 'comissao')
        else:
            custo_unitario = self.get_custo_produto(nome_produto, categoria)
            custo_total = custo_unitario * qtd
            return (custo_total, 'custo')

    def _calcular_custos_estimados_periodo(self, data_inicio: datetime, data_fim: datetime) -> Tuple[float, float]:
        """
        Calcula custos fixos e variáveis estimados do CSV para um período
        (usado para detectar se custos reais estão incompletos)

        Args:
            data_inicio: Data inicial
            data_fim: Data final

        Returns:
            Tuple (custos_fixos_total, custos_variaveis_total)
        """
        if self.custos_operacionais_estimados is None or self.custos_operacionais_estimados.empty:
            return (0.0, 0.0)

        # Separar custos fixos e variáveis
        df_custos = self.custos_operacionais_estimados[
            self.custos_operacionais_estimados['Tipo'] != 'Calculado'
        ].copy()

        custos_fixos = df_custos[df_custos['Tipo'] == 'Fixo']
        custos_variaveis = df_custos[df_custos['Tipo'] == 'Variável']

        # Calcular custos fixos mensais
        total_fixos_mensal = custos_fixos['Valor_Mensal'].sum()
        total_variaveis_mensal = custos_variaveis['Valor_Mensal'].sum()

        # Verificar quantos dias 28 estão no período
        meses_com_dia28 = []
        data_atual = data_inicio.replace(day=1)

        while data_atual <= data_fim:
            try:
                dia28 = data_atual.replace(day=28)
                if data_inicio <= dia28 <= data_fim:
                    meses_com_dia28.append(dia28)
            except ValueError:
                pass

            # Avançar para o próximo mês
            if data_atual.month == 12:
                data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
            else:
                data_atual = data_atual.replace(month=data_atual.month + 1)

        # Calcular totais
        custo_fixos_total = total_fixos_mensal * len(meses_com_dia28)
        dias_periodo = (data_fim - data_inicio).days + 1
        custo_variaveis_total = (total_variaveis_mensal / 30) * dias_periodo

        return (custo_fixos_total, custo_variaveis_total)

    def _criar_dataframe_hibrido(self, df_despesas_reais: pd.DataFrame,
                                 data_inicio: datetime, data_fim: datetime,
                                 custos_fixos_estimados: float) -> pd.DataFrame:
        """
        Cria DataFrame híbrido combinando despesas reais + custos fixos estimados

        Args:
            df_despesas_reais: DataFrame com despesas reais do Despesify
            data_inicio: Data inicial do período
            data_fim: Data final do período
            custos_fixos_estimados: Total de custos fixos estimados a adicionar

        Returns:
            DataFrame combinado
        """
        # Copiar despesas reais
        registros = []

        # Adicionar despesas reais (se houver)
        if not df_despesas_reais.empty:
            for _, row in df_despesas_reais.iterrows():
                registros.append({
                    'Categoria_Dashboard': row.get('Categoria_Dashboard', 'Outros'),
                    'Valor_Total': row.get('Valor_Total', 0),
                    'Tipo': 'Variável (Real)',
                    'Detalhes': 'Despesify - Real'
                })

        # Adicionar custos fixos estimados do CSV (agrupados)
        if custos_fixos_estimados > 0 and self.custos_operacionais_estimados is not None:
            df_custos = self.custos_operacionais_estimados[
                self.custos_operacionais_estimados['Tipo'] != 'Calculado'
            ].copy()
            custos_fixos = df_custos[df_custos['Tipo'] == 'Fixo']

            # Verificar quantos meses com dia 28 estão no período
            meses_com_dia28 = []
            data_atual = data_inicio.replace(day=1)

            while data_atual <= data_fim:
                try:
                    dia28 = data_atual.replace(day=28)
                    if data_inicio <= dia28 <= data_fim:
                        meses_com_dia28.append(dia28)
                except ValueError:
                    pass

                if data_atual.month == 12:
                    data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
                else:
                    data_atual = data_atual.replace(month=data_atual.month + 1)

            # Adicionar custos fixos por categoria
            if not custos_fixos.empty and len(meses_com_dia28) > 0:
                for categoria in custos_fixos['Categoria'].unique():
                    valor_cat = custos_fixos[custos_fixos['Categoria'] == categoria]['Valor_Mensal'].sum()
                    valor_total = valor_cat * len(meses_com_dia28)

                    registros.append({
                        'Categoria_Dashboard': f"{categoria} (Fixo Estimado)",
                        'Valor_Total': valor_total,
                        'Tipo': 'Fixo (Estimado)',
                        'Detalhes': f"{len(meses_com_dia28)}x dia 28 (CSV)"
                    })

        return pd.DataFrame(registros) if registros else pd.DataFrame({
            'Categoria_Dashboard': [],
            'Valor_Total': [],
            'Tipo': [],
            'Detalhes': []
        })

    def get_custos_operacionais_periodo(self, data_inicio: datetime, data_fim: datetime) -> Tuple[float, str, pd.DataFrame]:
        """
        Retorna custos operacionais de um período usando LÓGICA HÍBRIDA INTELIGENTE:
        - Despesas REAIS do Despesify (se disponível)
        - Se custos reais < 50% do esperado: ADICIONA custos fixos estimados do CSV
          (porque as despesas fixas como renda/ordenados só caem no dia 28)
        - Custos ESTIMADOS dos CSVs (fallback completo) com lógica:
          * Custos FIXOS: Lançados automaticamente no dia 28 de cada mês
          * Custos VARIÁVEIS: Proporcionais aos dias do período

        Args:
            data_inicio: Data inicial do período
            data_fim: Data final do período

        Returns:
            Tuple (custo_total, fonte, dataframe_detalhes)
            - fonte pode ser 'REAL', 'HÍBRIDO' ou 'ESTIMADO'
        """
        # Verificar se deve usar Despesify
        if self.despesify_loader and data_inicio >= self.DATA_INICIO_DESPESIFY:
            try:
                # Carregar despesas REAIS
                total_real, df_despesas_reais = self.despesify_loader.get_despesas_operacionais_periodo(
                    data_inicio, data_fim
                )

                # LÓGICA HÍBRIDA INTELIGENTE:
                # Calcular custos esperados do período para comparação
                custos_fixos_esperados, custos_variaveis_esperados = self._calcular_custos_estimados_periodo(
                    data_inicio, data_fim
                )
                total_esperado = custos_fixos_esperados + custos_variaveis_esperados

                # Se custos reais < 50% do esperado, significa que custos fixos ainda não foram lançados
                # (porque renda, ordenados, etc. só caem no dia 28)
                if total_real < (total_esperado * 0.5) and custos_fixos_esperados > 0:
                    # MODO HÍBRIDO: Custos reais variáveis + Custos fixos estimados
                    print(f"💡 Modo HÍBRIDO ativado: Custos reais (€{total_real:.2f}) < 50% do esperado (€{total_esperado:.2f})")
                    print(f"   Adicionando custos fixos estimados (€{custos_fixos_esperados:.2f}) aos custos reais")

                    # Criar DataFrame híbrido combinando reais + estimados fixos
                    df_hibrido = self._criar_dataframe_hibrido(
                        df_despesas_reais,
                        data_inicio,
                        data_fim,
                        custos_fixos_esperados
                    )

                    total_hibrido = total_real + custos_fixos_esperados
                    return (total_hibrido, 'HÍBRIDO (Reais + Fixos Estimados)', df_hibrido)
                else:
                    # Custos reais suficientes - usar apenas dados reais
                    return (total_real, 'REAL', df_despesas_reais)

            except Exception as e:
                print(f"⚠️ Erro ao carregar despesas reais: {e}. Usando estimativa.")

        # Fallback: usar custos estimados dos CSVs com lógica de regime de caixa
        if self.custos_operacionais_estimados is None or self.custos_operacionais_estimados.empty:
            df_vazio = pd.DataFrame({
                'Categoria_Dashboard': [],
                'Valor_Total': [],
                'Tipo': []
            })
            return (0.0, 'ESTIMADO', df_vazio)

        # Separar custos fixos e variáveis
        df_custos = self.custos_operacionais_estimados[
            self.custos_operacionais_estimados['Tipo'] != 'Calculado'
        ].copy()

        custos_fixos = df_custos[df_custos['Tipo'] == 'Fixo']
        custos_variaveis = df_custos[df_custos['Tipo'] == 'Variável']

        # Calcular total de custos fixos mensais
        total_fixos_mensal = custos_fixos['Valor_Mensal'].sum()
        total_variaveis_mensal = custos_variaveis['Valor_Mensal'].sum()

        # Verificar quantos dias 28 estão no período
        meses_com_dia28 = []
        data_atual = data_inicio.replace(day=1)  # Começar no dia 1 do mês inicial

        while data_atual <= data_fim:
            # Tentar criar data do dia 28 deste mês
            try:
                dia28 = data_atual.replace(day=28)
                # Verificar se o dia 28 está dentro do período
                if data_inicio <= dia28 <= data_fim:
                    meses_com_dia28.append(dia28)
            except ValueError:
                pass  # Mês não tem dia 28 (impossível, mas por segurança)

            # Avançar para o próximo mês
            if data_atual.month == 12:
                data_atual = data_atual.replace(year=data_atual.year + 1, month=1)
            else:
                data_atual = data_atual.replace(month=data_atual.month + 1)

        # Calcular custos fixos (apenas nos meses que têm dia 28 no período)
        custo_fixos_total = total_fixos_mensal * len(meses_com_dia28)

        # Calcular custos variáveis (proporcionais aos dias)
        dias_periodo = (data_fim - data_inicio).days + 1
        custo_variaveis_total = (total_variaveis_mensal / 30) * dias_periodo

        # Total
        custo_total = custo_fixos_total + custo_variaveis_total

        # Criar DataFrame detalhado
        registros = []

        # Adicionar custos fixos agrupados por categoria
        if not custos_fixos.empty and len(meses_com_dia28) > 0:
            for categoria in custos_fixos['Categoria'].unique():
                valor_cat = custos_fixos[custos_fixos['Categoria'] == categoria]['Valor_Mensal'].sum()
                valor_total = valor_cat * len(meses_com_dia28)

                registros.append({
                    'Categoria_Dashboard': f"{categoria} (Fixo)",
                    'Valor_Total': valor_total,
                    'Tipo': 'Fixo',
                    'Detalhes': f"{len(meses_com_dia28)}x dia 28"
                })

        # Adicionar custos variáveis agrupados por categoria
        if not custos_variaveis.empty:
            for categoria in custos_variaveis['Categoria'].unique():
                valor_cat = custos_variaveis[custos_variaveis['Categoria'] == categoria]['Valor_Mensal'].sum()
                valor_total = (valor_cat / 30) * dias_periodo

                registros.append({
                    'Categoria_Dashboard': f"{categoria} (Variável)",
                    'Valor_Total': valor_total,
                    'Tipo': 'Variável',
                    'Detalhes': f"{dias_periodo} dias"
                })

        df_estimado = pd.DataFrame(registros) if registros else pd.DataFrame({
            'Categoria_Dashboard': [],
            'Valor_Total': [],
            'Tipo': [],
            'Detalhes': []
        })

        return (custo_total, 'ESTIMADO', df_estimado)

    def get_custos_operacionais_mensais_estimados(self) -> float:
        """Retorna custos operacionais mensais ESTIMADOS do CSV"""
        if self.custos_operacionais_estimados is None or self.custos_operacionais_estimados.empty:
            return 0.0

        custos_mensais = self.custos_operacionais_estimados[
            self.custos_operacionais_estimados['Tipo'] != 'Calculado'
        ]['Valor_Mensal'].sum()

        return custos_mensais

    def get_margem_categoria(self, categoria: str) -> float:
        """Retorna a margem objetivo de uma categoria"""
        if self.margens_categorias is None or self.margens_categorias.empty:
            return 0.0

        filtro = self.margens_categorias['Categoria'] == categoria
        if filtro.any():
            return self.margens_categorias.loc[filtro, 'Margem_Objetivo'].iloc[0]

        return 0.0

    def get_iva_categoria(self, categoria: str) -> float:
        """Retorna a taxa de IVA aplicável a uma categoria"""
        if self.margens_categorias is None or self.margens_categorias.empty:
            return 23.0

        filtro = self.margens_categorias['Categoria'] == categoria
        if filtro.any():
            return self.margens_categorias.loc[filtro, 'IVA_Aplicavel'].iloc[0]

        return 23.0

    def calcular_custos_vendas(self, df_vendas: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona informações de custo/comissão ao DataFrame de vendas

        OTIMIZADO: Usa vectorização e lookup maps para performance máxima

        Args:
            df_vendas: DataFrame com vendas (deve ter colunas: Produto, Categoria, Valor, Qtd)

        Returns:
            DataFrame com colunas adicionais de custo/comissão
        """
        df = df_vendas.copy()

        if 'Produto' not in df.columns or 'Valor' not in df.columns:
            print("❌ Erro: DataFrame deve ter colunas 'Produto' e 'Valor'")
            return df

        # OTIMIZAÇÃO: Criar lookup maps para produtos únicos
        produtos_unicos = df['Produto'].unique()

        # Mapas para lookup rápido
        is_santa_casa_map = {}
        comissao_map = {}
        custo_unitario_map = {}

        for produto in produtos_unicos:
            if pd.isna(produto):
                is_santa_casa_map[produto] = False
                comissao_map[produto] = 0.0
                custo_unitario_map[produto] = 0.0
            else:
                # Verificar se é Santa Casa
                is_sc = self.is_jogo_santa_casa(produto)
                is_santa_casa_map[produto] = is_sc

                if is_sc:
                    comissao_map[produto] = self.get_comissao_santa_casa(produto)
                    custo_unitario_map[produto] = 0.0  # Santa Casa não tem custo unitário
                else:
                    comissao_map[produto] = 0.0
                    custo_unitario_map[produto] = self.get_custo_produto(produto)

        # Aplicar maps (vectorizado - muito rápido!)
        df['Is_Santa_Casa'] = df['Produto'].map(is_santa_casa_map).fillna(False)
        df['Percentagem_Comissao'] = df['Produto'].map(comissao_map).fillna(0.0)
        custo_unit = df['Produto'].map(custo_unitario_map).fillna(0.0)

        # Garantir que Qtd existe
        if 'Qtd' not in df.columns:
            df['Qtd'] = 1.0

        # Calcular custo total (vectorizado)
        # Para Santa Casa: custo = valor * (100 - comissao) / 100
        # Para produtos: custo = custo_unitario * qtd
        df['Custo_Total'] = np.where(
            df['Is_Santa_Casa'],
            df['Valor'] * ((100 - df['Percentagem_Comissao']) / 100.0),
            custo_unit * df['Qtd']
        )

        # Calcular custo unitário (vectorizado)
        df['Custo_Unitario'] = np.where(
            df['Qtd'] > 0,
            df['Custo_Total'] / df['Qtd'],
            0
        )

        # Calcular lucro bruto (vectorizado)
        df['Lucro_Bruto'] = df['Valor'] - df['Custo_Total']

        # Calcular margem bruta % (vectorizado)
        df['Margem_Bruta_Pct'] = np.where(
            df['Valor'] > 0,
            (df['Lucro_Bruto'] / df['Valor']) * 100,
            0
        )

        # Adicionar margem objetivo e IVA por categoria (vectorizado com maps)
        if 'Categoria' in df.columns:
            categorias_unicas = df['Categoria'].unique()
            margem_map = {cat: self.get_margem_categoria(cat) for cat in categorias_unicas if not pd.isna(cat)}
            iva_map = {cat: self.get_iva_categoria(cat) for cat in categorias_unicas if not pd.isna(cat)}

            df['Margem_Objetivo'] = df['Categoria'].map(margem_map).fillna(0.0)
            df['IVA_Aplicavel'] = df['Categoria'].map(iva_map).fillna(23.0)

            # Flag de margem abaixo do objetivo (vectorizado)
            df['Abaixo_Objetivo'] = df['Margem_Bruta_Pct'] < df['Margem_Objetivo']

        return df

    def calcular_metricas_financeiras(self, df_vendas: pd.DataFrame,
                                      data_inicio: datetime, data_fim: datetime) -> Dict:
        """
        Calcula métricas financeiras principais usando despesas REAIS ou ESTIMADAS

        Args:
            df_vendas: DataFrame com vendas e custos
            data_inicio: Data inicial do período
            data_fim: Data final do período

        Returns:
            Dicionário com métricas (inclui fonte de dados: REAL ou ESTIMADO)
        """
        if df_vendas.empty:
            return {}

        # Receitas e custos de produtos
        receita_total = df_vendas['Valor'].sum()
        cogs_total = df_vendas['Custo_Total'].sum() if 'Custo_Total' in df_vendas.columns else 0
        lucro_bruto = df_vendas['Lucro_Bruto'].sum() if 'Lucro_Bruto' in df_vendas.columns else 0

        # Separar comissões Santa Casa de custos de produtos
        if 'Is_Santa_Casa' in df_vendas.columns:
            comissoes_sc = df_vendas[df_vendas['Is_Santa_Casa'] == True]['Custo_Total'].sum()
            custos_produtos = df_vendas[df_vendas['Is_Santa_Casa'] == False]['Custo_Total'].sum()
        else:
            comissoes_sc = 0
            custos_produtos = cogs_total

        # Custos operacionais (REAIS ou ESTIMADOS)
        custos_ops, fonte_custos, df_custos_ops = self.get_custos_operacionais_periodo(
            data_inicio, data_fim
        )

        # Lucro líquido
        lucro_liquido = lucro_bruto - custos_ops

        # Margens
        margem_bruta_pct = (lucro_bruto / receita_total * 100) if receita_total > 0 else 0
        margem_liquida_pct = (lucro_liquido / receita_total * 100) if receita_total > 0 else 0

        # ROI
        roi = (lucro_liquido / custos_ops * 100) if custos_ops > 0 else 0

        dias_periodo = (data_fim - data_inicio).days + 1

        return {
            'receita_total': receita_total,
            'cogs_total': cogs_total,
            'comissoes_santa_casa': comissoes_sc,
            'custos_produtos': custos_produtos,
            'lucro_bruto': lucro_bruto,
            'custos_operacionais': custos_ops,
            'lucro_liquido': lucro_liquido,
            'margem_bruta_pct': margem_bruta_pct,
            'margem_liquida_pct': margem_liquida_pct,
            'roi_pct': roi,
            'custo_total': cogs_total + custos_ops,
            'dias_periodo': dias_periodo,
            'fonte_custos_operacionais': fonte_custos,  # 'REAL' ou 'ESTIMADO'
            'df_custos_operacionais': df_custos_ops
        }

    def get_resumo_custos_operacionais(self, data_inicio: datetime, data_fim: datetime) -> pd.DataFrame:
        """
        Retorna resumo dos custos operacionais por categoria (REAL ou ESTIMADO)

        Args:
            data_inicio: Data inicial
            data_fim: Data final

        Returns:
            DataFrame com resumo
        """
        custos_total, fonte, df_custos = self.get_custos_operacionais_periodo(data_inicio, data_fim)

        if fonte == 'REAL' and not df_custos.empty:
            # Agrupar despesas reais por categoria
            resumo = df_custos.groupby('Categoria_Dashboard').agg({
                'Valor_Total': 'sum'
            }).round(2)
            resumo.columns = ['Total_Periodo']
            resumo['Percentual'] = (resumo['Total_Periodo'] / resumo['Total_Periodo'].sum() * 100).round(1)
            resumo['Fonte'] = 'Real'
            resumo = resumo.sort_values('Total_Periodo', ascending=False)
            return resumo

        elif not df_custos.empty:
            # Usar custos estimados (já calculados com a nova lógica)
            resumo = df_custos.copy()
            resumo = resumo.set_index('Categoria_Dashboard')
            resumo['Total_Periodo'] = resumo['Valor_Total']
            resumo['Percentual'] = (resumo['Total_Periodo'] / resumo['Total_Periodo'].sum() * 100).round(1)
            resumo['Fonte'] = 'Estimado'
            resumo = resumo.sort_values('Total_Periodo', ascending=False)

            # Retornar com colunas: Total_Periodo, Percentual, Fonte, Detalhes
            return resumo[['Total_Periodo', 'Percentual', 'Fonte', 'Detalhes']]

        return pd.DataFrame()

    def calcular_break_even(self, margem_contribuicao_media: float, iva_medio: float = 18.0,
                          margem_seguranca_pct: float = 15.0,
                          usar_custos_reais: bool = True,
                          data_inicio: datetime = None,
                          data_fim: datetime = None) -> Dict:
        """
        Calcula o ponto de equilíbrio usando custos REAIS ou ESTIMADOS

        Args:
            margem_contribuicao_media: Margem de contribuição média (em %)
            iva_medio: Taxa média de IVA aplicável
            margem_seguranca_pct: Margem de segurança desejada
            usar_custos_reais: Se True, usa custos reais do último mês
            data_inicio: Data inicial para cálculo (se usar_custos_reais=True)
            data_fim: Data final para cálculo (se usar_custos_reais=True)

        Returns:
            Dicionário com informações de break-even
        """
        # Determinar custos fixos mensais
        custos_fixos_mensais = 0
        fonte_custos = 'ESTIMADO'

        if usar_custos_reais and self.despesify_loader:
            if data_inicio is None:
                # Usar último mês
                data_fim = datetime.now()
                data_inicio = data_fim - timedelta(days=30)

            custos_periodo, fonte, _ = self.get_custos_operacionais_periodo(data_inicio, data_fim)
            dias = (data_fim - data_inicio).days + 1
            custos_fixos_mensais = (custos_periodo / dias) * 30
            fonte_custos = fonte

        # Fallback para custos estimados se não houver dados reais
        if custos_fixos_mensais <= 0:
            custos_fixos_mensais = self.get_custos_operacionais_mensais_estimados()
            fonte_custos = 'ESTIMADO (fallback)'

        if margem_contribuicao_media <= 0:
            return {
                'custos_fixos': custos_fixos_mensais,
                'margem_contribuicao': 0,
                'vendas_break_even': 0,
                'vendas_diarias_break_even': 0,
                'erro': 'Margem de contribuição deve ser positiva',
                'fonte_custos': fonte_custos
            }

        # Cálculos de break-even
        vendas_break_even_simples = custos_fixos_mensais / (margem_contribuicao_media / 100)

        iva_pct_efetivo = iva_medio / 100
        margem_efetiva = (margem_contribuicao_media / 100) - iva_pct_efetivo

        if margem_efetiva <= 0:
            vendas_break_even_com_iva = float('inf')
        else:
            vendas_break_even_com_iva = custos_fixos_mensais / margem_efetiva

        vendas_break_even_realista = vendas_break_even_com_iva * (1 + margem_seguranca_pct / 100)

        vendas_diarias_simples = vendas_break_even_simples / 30
        vendas_diarias_com_iva = vendas_break_even_com_iva / 30 if vendas_break_even_com_iva != float('inf') else float('inf')
        vendas_diarias_realista = vendas_break_even_realista / 30 if vendas_break_even_realista != float('inf') else float('inf')

        iva_mensal_estimado = vendas_break_even_realista * iva_pct_efetivo
        lucro_minimo = (vendas_break_even_realista * (margem_contribuicao_media / 100)) - custos_fixos_mensais - iva_mensal_estimado

        return {
            'custos_fixos_mensais': custos_fixos_mensais,
            'margem_contribuicao_pct': margem_contribuicao_media,
            'iva_medio_pct': iva_medio,
            'margem_seguranca_pct': margem_seguranca_pct,
            'vendas_break_even_mensal_simples': vendas_break_even_simples,
            'vendas_break_even_diaria_simples': vendas_diarias_simples,
            'vendas_break_even_mensal_com_iva': vendas_break_even_com_iva if vendas_break_even_com_iva != float('inf') else 0,
            'vendas_break_even_diaria_com_iva': vendas_diarias_com_iva if vendas_diarias_com_iva != float('inf') else 0,
            'vendas_break_even_mensal': vendas_break_even_realista if vendas_break_even_realista != float('inf') else 0,
            'vendas_break_even_diaria': vendas_diarias_realista if vendas_diarias_realista != float('inf') else 0,
            'custos_fixos_diarios': custos_fixos_mensais / 30,
            'iva_mensal_estimado': iva_mensal_estimado,
            'margem_efetiva_apos_iva': margem_efetiva * 100,
            'lucro_minimo_esperado': lucro_minimo,
            'fonte_custos': fonte_custos  # Indica se usou custos REAIS ou ESTIMADOS
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


# Função auxiliar para uso rápido
def adicionar_custos_vendas(df_vendas: pd.DataFrame) -> pd.DataFrame:
    """Função conveniente para adicionar custos às vendas"""
    manager = CostManagerV2()
    return manager.calcular_custos_vendas(df_vendas)


if __name__ == '__main__':
    # Teste do módulo
    print("=== Teste do CostManagerV2 (Sistema Híbrido) ===\n")

    manager = CostManagerV2(usar_despesify=True)

    # Testar custos operacionais REAIS
    data_inicio = datetime(2025, 12, 1)
    data_fim = datetime.now()

    print("📊 CUSTOS OPERACIONAIS:")
    custos, fonte, df_custos = manager.get_custos_operacionais_periodo(data_inicio, data_fim)
    print(f"   Período: {data_inicio.strftime('%d/%m/%Y')} - {data_fim.strftime('%d/%m/%Y')}")
    print(f"   Total: €{custos:.2f}")
    print(f"   Fonte: {fonte} {'✅' if fonte == 'REAL' else '⚠️'}\n")

    if fonte == 'REAL' and not df_custos.empty:
        print("📦 DETALHES DAS DESPESAS REAIS:")
        resumo = manager.get_resumo_custos_operacionais(data_inicio, data_fim)
        print(resumo)
    else:
        print("⚠️ Usando custos estimados (sem dados reais no Despesify)")

    print("\n✅ CostManagerV2 funcionando corretamente!")
