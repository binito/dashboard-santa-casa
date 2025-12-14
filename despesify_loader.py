"""
Módulo de Integração com Despesify - Dashboard v7
Carrega despesas reais da base de dados MariaDB do Despesify
"""

import pandas as pd
import mysql.connector
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')


class DespesifyLoader:
    """Carregador de despesas reais do Despesify (MariaDB)"""

    # Configuração da base de dados
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'cathie',
        'database': 'despesify'
    }

    # Mapeamento de categorias Despesify para categorias do Dashboard
    MAPEAMENTO_CATEGORIAS = {
        # 621 - Serviços especializados
        '621 Serviços especializados': 'Serviços Especializados',
        '6211 Subcontratos': 'Serviços Especializados',
        '6212 Conservação e reparação': 'Manutenção e Reparações',
        '6213 Publicidade': 'Marketing e Publicidade',
        '6214 Deslocações e estadas': 'Deslocações',
        '6215 Comunicações': 'Comunicações',
        '6216 Honorários': 'Serviços Especializados',
        '6217 Seguros': 'Seguros',
        '6218 Outros serviços especializados': 'Serviços Especializados',

        # 622 - Fornecimentos e serviços de terceiros
        '622 Fornecimentos e serviços de terceiros': 'Fornecimentos Gerais',
        '6221 Energia': 'Energia e Água',
        '6222 Água': 'Energia e Água',
        '6223 Combustíveis': 'Combustíveis',
        '6224 Ferramentas e utensílios': 'Ferramentas e Utensílios',
        '6225 Material de escritório': 'Material de Escritório',
        '6226 Artigos de desgaste rápido': 'Consumíveis',
        '6227 Higiene e limpeza': 'Higiene e Limpeza',
        '6228 Outros fornecimentos e serviços de terceiros': 'Fornecimentos Gerais',

        # 623-629 - Outros
        '623 Rendas e alugueres': 'Rendas',
        '624 Trabalho especializado': 'Serviços Especializados',
        '625 Transportes': 'Transportes',
        '626 Deslocações e estadas': 'Deslocações',
        '626 – Representação': 'Representação',
        '627 Ajudas de custo': 'Deslocações',
        '628 Serviços bancários e similares': 'Serviços Bancários',
        '629 Outros fornecimentos e serviços externos': 'Outros FSE',

        # 63 - Custos com pessoal
        '63 Custos com o pessoal': 'Pessoal',
        '631 Remunerações': 'Remunerações',
        '6311 Remunerações do pessoal': 'Remunerações',
        '6312 Remunerações dos órgãos sociais': 'Remunerações',
        '632 Encargos sobre remunerações': 'Encargos Sociais',
        '6321 Segurança social': 'Segurança Social',
        '6322 Seguros de acidentes de trabalho': 'Seguros',
        '6323 Outros encargos sobre remunerações': 'Encargos Sociais',
        '633 Indemnizações': 'Indemnizações',
        '634 Formação': 'Formação',
        '635 Outros custos com pessoal': 'Outros Custos Pessoal',

        # 611 - Compras (estas são CUSTOS DE PRODUTOS, não operacionais!)
        '611 – Compras de mercadorias': 'COMPRAS_MERCADORIAS'
    }

    def __init__(self):
        """Inicializa o carregador"""
        self.connection = None
        self.categorias = None

    def _conectar(self):
        """Estabelece conexão com a base de dados"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**self.DB_CONFIG)
            return True
        except mysql.connector.Error as e:
            print(f"Erro ao conectar à base de dados Despesify: {e}")
            return False

    def _desconectar(self):
        """Fecha conexão com a base de dados"""
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def _carregar_categorias(self) -> pd.DataFrame:
        """Carrega tabela de categorias do Despesify"""
        if not self._conectar():
            return pd.DataFrame()

        try:
            query = "SELECT id, name, color FROM categories"
            df_categorias = pd.read_sql(query, self.connection)
            return df_categorias
        except Exception as e:
            print(f"Erro ao carregar categorias: {e}")
            return pd.DataFrame()

    def carregar_despesas(self, data_inicio: Optional[datetime] = None,
                         data_fim: Optional[datetime] = None) -> pd.DataFrame:
        """
        Carrega despesas do Despesify num período

        Args:
            data_inicio: Data inicial (None = desde 1/12/2025)
            data_fim: Data final (None = hoje)

        Returns:
            DataFrame com despesas
        """
        if not self._conectar():
            return pd.DataFrame()

        try:
            # Carregar categorias se ainda não carregou
            if self.categorias is None:
                self.categorias = self._carregar_categorias()

            # Definir período padrão
            if data_inicio is None:
                data_inicio = datetime(2025, 12, 1)
            if data_fim is None:
                data_fim = datetime.now()

            # Query para carregar despesas
            query = """
                SELECT
                    e.id,
                    e.description,
                    e.amount,
                    e.expense_date,
                    e.payment_method,
                    e.notes,
                    e.vat_percentage,
                    e.vat_amount,
                    e.nif_emitente,
                    e.nif_adquirente,
                    e.numero_documento,
                    e.base_tributavel,
                    e.category_id,
                    c.name as category_name,
                    c.color as category_color
                FROM expenses e
                LEFT JOIN categories c ON e.category_id = c.id
                WHERE e.expense_date BETWEEN %s AND %s
                ORDER BY e.expense_date DESC
            """

            df = pd.read_sql(query, self.connection,
                           params=(data_inicio.strftime('%Y-%m-%d'),
                                  data_fim.strftime('%Y-%m-%d')))

            # Processar dados
            if not df.empty:
                # Converter datas
                df['expense_date'] = pd.to_datetime(df['expense_date'])

                # Mapear categorias
                df['Categoria_Dashboard'] = df['category_name'].map(
                    self.MAPEAMENTO_CATEGORIAS
                ).fillna('Outros')

                # Identificar se é compra de mercadoria (custo de produto) ou despesa operacional
                df['Tipo_Custo'] = df['category_name'].apply(
                    lambda x: 'PRODUTO' if x == '611 – Compras de mercadorias' else 'OPERACIONAL'
                )

                # Calcular base tributável se não existir
                df['base_tributavel'] = df.apply(
                    lambda row: row['base_tributavel'] if pd.notna(row['base_tributavel'])
                    else row['amount'] - (row['vat_amount'] if pd.notna(row['vat_amount']) else 0),
                    axis=1
                )

                # Renomear colunas para padrão do dashboard
                df.rename(columns={
                    'expense_date': 'Data',
                    'description': 'Descrição',
                    'amount': 'Valor_Total',
                    'vat_amount': 'IVA',
                    'base_tributavel': 'Valor_Sem_IVA',
                    'category_name': 'Categoria_POC',
                    'payment_method': 'Metodo_Pagamento',
                    'notes': 'Notas',
                    'nif_emitente': 'NIF_Fornecedor'
                }, inplace=True)

            return df

        except Exception as e:
            print(f"Erro ao carregar despesas: {e}")
            return pd.DataFrame()
        finally:
            self._desconectar()

    def get_resumo_despesas(self, data_inicio: Optional[datetime] = None,
                           data_fim: Optional[datetime] = None) -> Dict:
        """
        Retorna resumo das despesas por categoria

        Args:
            data_inicio: Data inicial
            data_fim: Data final

        Returns:
            Dicionário com resumo
        """
        df = self.carregar_despesas(data_inicio, data_fim)

        if df.empty:
            return {
                'total_despesas': 0,
                'total_operacionais': 0,
                'total_produtos': 0,
                'por_categoria': pd.DataFrame(),
                'por_categoria_dashboard': pd.DataFrame()
            }

        # Separar por tipo de custo
        df_operacionais = df[df['Tipo_Custo'] == 'OPERACIONAL']
        df_produtos = df[df['Tipo_Custo'] == 'PRODUTO']

        # Resumo por categoria POC
        por_categoria = df.groupby('Categoria_POC').agg({
            'Valor_Total': 'sum',
            'IVA': 'sum',
            'Valor_Sem_IVA': 'sum'
        }).round(2).sort_values('Valor_Total', ascending=False)

        # Resumo por categoria Dashboard
        por_categoria_dash = df.groupby(['Tipo_Custo', 'Categoria_Dashboard']).agg({
            'Valor_Total': 'sum',
            'IVA': 'sum',
            'Valor_Sem_IVA': 'sum'
        }).round(2).sort_values('Valor_Total', ascending=False)

        return {
            'total_despesas': df['Valor_Total'].sum(),
            'total_operacionais': df_operacionais['Valor_Total'].sum(),
            'total_produtos': df_produtos['Valor_Total'].sum(),
            'total_iva': df['IVA'].sum(),
            'num_despesas': len(df),
            'por_categoria': por_categoria,
            'por_categoria_dashboard': por_categoria_dash,
            'df_completo': df
        }

    def get_despesas_operacionais_periodo(self, data_inicio: datetime,
                                         data_fim: datetime) -> Tuple[float, pd.DataFrame]:
        """
        Retorna despesas operacionais reais de um período

        Args:
            data_inicio: Data inicial
            data_fim: Data final

        Returns:
            Tuple (total, dataframe_detalhado)
        """
        df = self.carregar_despesas(data_inicio, data_fim)

        if df.empty:
            return 0.0, pd.DataFrame()

        # Filtrar apenas operacionais (excluir compras de mercadorias)
        df_operacionais = df[df['Tipo_Custo'] == 'OPERACIONAL'].copy()

        total = df_operacionais['Valor_Total'].sum()

        return total, df_operacionais

    def get_despesas_mensais_por_categoria(self, mes: int, ano: int) -> pd.DataFrame:
        """
        Retorna despesas de um mês específico agrupadas por categoria

        Args:
            mes: Mês (1-12)
            ano: Ano

        Returns:
            DataFrame com despesas por categoria
        """
        from calendar import monthrange

        data_inicio = datetime(ano, mes, 1)
        ultimo_dia = monthrange(ano, mes)[1]
        data_fim = datetime(ano, mes, ultimo_dia)

        df = self.carregar_despesas(data_inicio, data_fim)

        if df.empty:
            return pd.DataFrame()

        # Filtrar apenas operacionais
        df_operacionais = df[df['Tipo_Custo'] == 'OPERACIONAL'].copy()

        # Agrupar por categoria
        resumo = df_operacionais.groupby('Categoria_Dashboard').agg({
            'Valor_Total': 'sum',
            'IVA': 'sum',
            'Valor_Sem_IVA': 'sum'
        }).round(2).sort_values('Valor_Total', ascending=False)

        return resumo

    def validar_conexao(self) -> bool:
        """
        Testa conexão com a base de dados

        Returns:
            True se conexão OK
        """
        return self._conectar()

    def pesquisar_fatura(self, numero_documento: str = None,
                        nif_fornecedor: str = None,
                        descricao: str = None) -> pd.DataFrame:
        """
        Pesquisa faturas por número de documento, NIF ou descrição

        Args:
            numero_documento: Número do documento (ex: "FS 2025021701A/80387")
            nif_fornecedor: NIF do fornecedor
            descricao: Descrição/nome do fornecedor

        Returns:
            DataFrame com faturas encontradas
        """
        if not self._conectar():
            return pd.DataFrame()

        try:
            # Construir query dinamicamente
            conditions = []
            params = []

            if numero_documento:
                conditions.append("e.numero_documento LIKE %s")
                params.append(f"%{numero_documento}%")

            if nif_fornecedor:
                conditions.append("e.nif_emitente = %s")
                params.append(nif_fornecedor)

            if descricao:
                conditions.append("e.description LIKE %s")
                params.append(f"%{descricao}%")

            if not conditions:
                # Se não há filtros, retornar vazio
                return pd.DataFrame()

            where_clause = " OR ".join(conditions)

            query = f"""
                SELECT
                    e.id,
                    e.description,
                    e.amount,
                    e.expense_date,
                    e.payment_method,
                    e.notes,
                    e.vat_percentage,
                    e.vat_amount,
                    e.nif_emitente,
                    e.nif_adquirente,
                    e.numero_documento,
                    e.atcud,
                    e.base_tributavel,
                    e.qr_data,
                    e.category_id,
                    c.name as category_name
                FROM expenses e
                LEFT JOIN categories c ON e.category_id = c.id
                WHERE {where_clause}
                ORDER BY e.expense_date DESC
                LIMIT 50
            """

            df = pd.read_sql(query, self.connection, params=params)

            if not df.empty:
                df['expense_date'] = pd.to_datetime(df['expense_date'])

            return df

        except Exception as e:
            print(f"Erro ao pesquisar fatura: {e}")
            return pd.DataFrame()
        finally:
            self._desconectar()

    def get_detalhes_fatura(self, numero_documento: str) -> Dict:
        """
        Retorna detalhes completos de uma fatura incluindo dados do QR Code

        Args:
            numero_documento: Número do documento

        Returns:
            Dicionário com todos os detalhes da fatura
        """
        if not self._conectar():
            return {}

        try:
            query = """
                SELECT
                    e.*,
                    c.name as category_name,
                    c.color as category_color
                FROM expenses e
                LEFT JOIN categories c ON e.category_id = c.id
                WHERE e.numero_documento = %s
                LIMIT 1
            """

            df = pd.read_sql(query, self.connection, params=(numero_documento,))

            if df.empty:
                return {}

            fatura = df.iloc[0].to_dict()

            # Parse QR data se existir
            if fatura.get('qr_data'):
                import json
                try:
                    qr_data = json.loads(fatura['qr_data'])
                    fatura['qr_data_parsed'] = qr_data

                    # Extrair linhas de IVA se existirem
                    if 'raw_qr_data' in qr_data and 'linhas_iva' in qr_data['raw_qr_data']:
                        fatura['linhas_iva'] = qr_data['raw_qr_data']['linhas_iva']
                    else:
                        fatura['linhas_iva'] = []

                except json.JSONDecodeError:
                    fatura['qr_data_parsed'] = {}
                    fatura['linhas_iva'] = []
            else:
                fatura['qr_data_parsed'] = {}
                fatura['linhas_iva'] = []

            return fatura

        except Exception as e:
            print(f"Erro ao obter detalhes da fatura: {e}")
            return {}
        finally:
            self._desconectar()

    def get_todas_faturas(self, limite: int = 100) -> pd.DataFrame:
        """
        Retorna todas as faturas (mais recentes primeiro)

        Args:
            limite: Número máximo de faturas a retornar

        Returns:
            DataFrame com faturas
        """
        df = self.carregar_despesas(
            datetime(2020, 1, 1),  # Data antiga para pegar todas
            datetime.now()
        )

        if df.empty:
            return pd.DataFrame()

        return df.head(limite)


# Função auxiliar para uso rápido
def carregar_despesas_periodo(data_inicio: datetime, data_fim: datetime) -> pd.DataFrame:
    """Função conveniente para carregar despesas de um período"""
    loader = DespesifyLoader()
    return loader.carregar_despesas(data_inicio, data_fim)


if __name__ == '__main__':
    # Teste do módulo
    print("=== Teste do DespesifyLoader ===\n")

    loader = DespesifyLoader()

    # Testar conexão
    if loader.validar_conexao():
        print("✅ Conexão com Despesify OK\n")

        # Carregar despesas desde 1/12/2025
        data_inicio = datetime(2025, 12, 1)
        data_fim = datetime.now()

        resumo = loader.get_resumo_despesas(data_inicio, data_fim)

        print(f"📊 RESUMO DE DESPESAS ({data_inicio.strftime('%d/%m/%Y')} - {data_fim.strftime('%d/%m/%Y')})")
        print(f"   Total Geral: €{resumo['total_despesas']:.2f}")
        print(f"   • Despesas Operacionais: €{resumo['total_operacionais']:.2f}")
        print(f"   • Compras de Mercadorias: €{resumo['total_produtos']:.2f}")
        print(f"   • IVA Total: €{resumo['total_iva']:.2f}")
        print(f"   • Número de Despesas: {resumo['num_despesas']}\n")

        print("📦 POR CATEGORIA DASHBOARD:")
        print(resumo['por_categoria_dashboard'])

        print("\n✅ DespesifyLoader funcionando corretamente!")
    else:
        print("❌ Erro ao conectar com Despesify")
