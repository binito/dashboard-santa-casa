"""
Módulo de carregamento de dados para Dashboard v3
Carrega dados de:
- Santa Casa (scraped data)
- POS 1: Vendas de café (Excel)
- POS 2: Outros produtos incluindo Totobola (CSV)
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class DataLoaderV3:
    """Carregador de dados integrado para todas as fontes"""

    def __init__(self,
                 santa_casa_dir='dados_vendas',
                 pos1_dir='/home/jorge/Documentos/pos/pos_1',
                 pos2_dir='/home/jorge/Documentos/pos/pos_2'):
        self.santa_casa_dir = Path(santa_casa_dir)
        self.pos1_dir = Path(pos1_dir)
        self.pos2_dir = Path(pos2_dir)

    # ==================== SANTA CASA ====================
    def carregar_dados_santa_casa(self):
        """Carrega dados dos jogos Santa Casa (método original)"""
        dados_vendas = []

        if not self.santa_casa_dir.exists():
            return pd.DataFrame()

        # Percorrer todos os ficheiros de texto
        for arquivo in sorted(self.santa_casa_dir.glob('*.txt')):
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()

                # Extrair data do nome do arquivo
                match_data = re.search(r'(\d{4})(\d{2})(\d{2})', arquivo.stem)
                if match_data:
                    ano, mes, dia = match_data.groups()
                    data = f"{ano}-{mes}-{dia}"
                else:
                    continue

                # Extrair dados do conteúdo
                linhas = conteudo.strip().split('\n')
                jogo_atual = None

                for linha in linhas:
                    linha = linha.strip()

                    # Identificar início de um jogo
                    if linha and not any(c.isdigit() for c in linha.split(':')[0] if ':' in linha):
                        if linha not in ['', 'Vendas Diárias']:
                            jogo_atual = linha
                            continue

                    # Extrair valores
                    if ':' in linha and jogo_atual:
                        partes = linha.split(':')
                        if len(partes) == 2:
                            descricao = partes[0].strip()
                            valor_str = partes[1].strip().replace('€', '').replace(',', '.').strip()

                            try:
                                valor = float(valor_str)
                                dados_vendas.append({
                                    'Data': data,
                                    'Jogo': jogo_atual,
                                    'Descricao': descricao,
                                    'Valor': valor,
                                    'Fonte': 'Santa Casa'
                                })
                            except ValueError:
                                continue

            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")
                continue

        if not dados_vendas:
            return pd.DataFrame()

        df = pd.DataFrame(dados_vendas)
        df['Data'] = pd.to_datetime(df['Data'])
        return df

    # ==================== POS 1 - CAFÉ ====================
    def carregar_vendas_cafe(self):
        """Carrega vendas de café dos ficheiros Excel (pos_1)"""
        dados_cafe = []

        if not self.pos1_dir.exists():
            return pd.DataFrame()

        # Processar cada ficheiro Excel (2023, 2024, 2025)
        for arquivo in sorted(self.pos1_dir.glob('*.xlsx')):
            try:
                # Ler Excel pulando as linhas de cabeçalho
                df = pd.read_excel(arquivo, skiprows=8)

                # Renomear colunas para facilitar
                df = df.rename(columns={
                    'Valor Total': 'Valor',
                    'Quantidade': 'Qtd'
                })

                # Filtrar linhas válidas (com data e valor)
                # Excluir linhas com "Totais" ou datas inválidas
                df = df[df['Data'].notna() & df['Valor'].notna()].copy()
                df = df[~df['Data'].astype(str).str.contains('Totais', na=False)].copy()

                # Converter tipos
                df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
                df = df[df['Data'].notna()].copy()  # Remove datas inválidas
                df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')

                # Adicionar metadados
                df['Fonte'] = 'Café'
                df['Categoria'] = 'Vendas Café'

                # Selecionar colunas relevantes
                df = df[['Data', 'Valor', 'Fonte', 'Categoria', 'Produto']].copy()

                dados_cafe.append(df)

            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")
                continue

        if not dados_cafe:
            return pd.DataFrame()

        # Combinar todos os anos
        df_final = pd.concat(dados_cafe, ignore_index=True)
        df_final = df_final.sort_values('Data').reset_index(drop=True)

        return df_final

    # ==================== POS 2 - OUTROS PRODUTOS ====================
    def carregar_outros_produtos(self, incluir_raspadinhas=False):
        """
        Carrega dados de outros produtos do CSV (pos_2)
        Por padrão, filtra apenas Totobola (código 50010)

        Args:
            incluir_raspadinhas: Se True, inclui raspadinhas (códigos < 50000)
        """
        dados_outros = []

        if not self.pos2_dir.exists():
            return pd.DataFrame()

        # Processar cada ficheiro CSV
        for arquivo in sorted(self.pos2_dir.glob('*.csv')):
            try:
                # Ler CSV com configurações corretas
                df = pd.read_csv(arquivo,
                                sep=';',
                                encoding='latin1',
                                decimal=',',
                                thousands='.')

                # Converter data
                df['Data'] = pd.to_datetime(df['Data'], format='%Y-%m-%d')

                # Filtrar apenas Totobola (código 50010)
                # Nota: Mesmo sendo Totobola, vamos categorizar como "Outros" conforme pedido
                df_filtrado = df[df['Codigo'] == 50010].copy()

                if incluir_raspadinhas:
                    # Incluir também raspadinhas (códigos < 50000, exceto 50010 já incluído)
                    df_rasp = df[df['Codigo'] < 50000].copy()
                    df_filtrado = pd.concat([df_filtrado, df_rasp]).drop_duplicates()

                # Renomear e adicionar metadados
                df_filtrado = df_filtrado.rename(columns={
                    'Val.Total': 'Valor',
                    'Designação': 'Produto'
                })

                df_filtrado['Fonte'] = 'Outros'
                df_filtrado['Categoria'] = 'Outros Produtos'

                # Selecionar colunas relevantes
                df_filtrado = df_filtrado[['Data', 'Valor', 'Fonte', 'Categoria', 'Produto']].copy()

                dados_outros.append(df_filtrado)

            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")
                continue

        if not dados_outros:
            return pd.DataFrame()

        # Combinar todos os ficheiros
        df_final = pd.concat(dados_outros, ignore_index=True)
        df_final = df_final.sort_values('Data').reset_index(drop=True)

        return df_final

    # ==================== CARREGAMENTO INTEGRADO ====================
    def carregar_todos_dados(self, incluir_raspadinhas_pos2=False):
        """
        Carrega e combina todos os dados de todas as fontes

        Returns:
            dict com 3 DataFrames: 'santa_casa', 'cafe', 'outros'
        """
        print("Carregando dados Santa Casa...")
        df_sc = self.carregar_dados_santa_casa()

        print("Carregando vendas de café...")
        df_cafe = self.carregar_vendas_cafe()

        print("Carregando outros produtos...")
        df_outros = self.carregar_outros_produtos(incluir_raspadinhas=incluir_raspadinhas_pos2)

        return {
            'santa_casa': df_sc,
            'cafe': df_cafe,
            'outros': df_outros
        }

    def get_resumo_dados(self):
        """Retorna um resumo dos dados carregados"""
        dados = self.carregar_todos_dados()

        resumo = {
            'Santa Casa': {
                'registos': len(dados['santa_casa']),
                'periodo': f"{dados['santa_casa']['Data'].min():%Y-%m-%d} a {dados['santa_casa']['Data'].max():%Y-%m-%d}" if len(dados['santa_casa']) > 0 else 'N/A',
                'total': dados['santa_casa']['Valor'].sum() if len(dados['santa_casa']) > 0 else 0
            },
            'Café': {
                'registos': len(dados['cafe']),
                'periodo': f"{dados['cafe']['Data'].min():%Y-%m-%d} a {dados['cafe']['Data'].max():%Y-%m-%d}" if len(dados['cafe']) > 0 else 'N/A',
                'total': dados['cafe']['Valor'].sum() if len(dados['cafe']) > 0 else 0
            },
            'Outros': {
                'registos': len(dados['outros']),
                'periodo': f"{dados['outros']['Data'].min():%Y-%m-%d} a {dados['outros']['Data'].max():%Y-%m-%d}" if len(dados['outros']) > 0 else 'N/A',
                'total': dados['outros']['Valor'].sum() if len(dados['outros']) > 0 else 0
            }
        }

        return resumo


# Função auxiliar para uso rápido
def carregar_dados_completos():
    """Função conveniente para carregar todos os dados"""
    loader = DataLoaderV3()
    return loader.carregar_todos_dados()


if __name__ == '__main__':
    # Teste do módulo
    print("=== Teste do DataLoaderV3 ===\n")

    loader = DataLoaderV3()
    resumo = loader.get_resumo_dados()

    print("Resumo dos dados carregados:\n")
    for fonte, info in resumo.items():
        print(f"{fonte}:")
        print(f"  Registos: {info['registos']}")
        print(f"  Período: {info['periodo']}")
        print(f"  Total: €{info['total']:.2f}")
        print()
