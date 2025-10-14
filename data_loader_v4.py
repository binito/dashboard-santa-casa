"""
Módulo de carregamento de dados para Dashboard v4
Com categorização inteligente de produtos
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import warnings
from product_categorizer import ProductCategorizer

warnings.filterwarnings('ignore')


class DataLoaderV4:
    """Carregador de dados integrado com categorização automática"""

    def __init__(self,
                 santa_casa_dir='dados_vendas',
                 pos1_dir='/home/jorge/Documentos/pos/pos_1',
                 pos2_dir='/home/jorge/Documentos/pos/pos_2'):
        self.santa_casa_dir = Path(santa_casa_dir)
        self.pos1_dir = Path(pos1_dir)
        self.pos2_dir = Path(pos2_dir)
        self.categorizer = ProductCategorizer()

    def carregar_dados_santa_casa(self):
        """Carrega dados dos jogos Santa Casa"""
        dados_vendas = []

        if not self.santa_casa_dir.exists():
            return pd.DataFrame()

        for arquivo in sorted(self.santa_casa_dir.glob('*.txt')):
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()

                match_data = re.search(r'(\d{4})(\d{2})(\d{2})', arquivo.stem)
                if match_data:
                    ano, mes, dia = match_data.groups()
                    data = f"{ano}-{mes}-{dia}"
                else:
                    continue

                linhas = conteudo.strip().split('\n')
                jogo_atual = None

                for linha in linhas:
                    linha = linha.strip()

                    if linha and not any(c.isdigit() for c in linha.split(':')[0] if ':' in linha):
                        if linha not in ['', 'Vendas Diárias']:
                            jogo_atual = linha
                            continue

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
                                    'Fonte': 'Santa Casa',
                                    'Produto': jogo_atual
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
        
        # Categorizar jogos Santa Casa
        if not df.empty:
            df = self.categorizer.categorizar_dataframe(df, coluna_produto='Produto')
        
        return df

    def carregar_vendas_cafe(self):
        """Carrega vendas de café com categorização detalhada"""
        dados_cafe = []

        if not self.pos1_dir.exists():
            return pd.DataFrame()

        for arquivo in sorted(self.pos1_dir.glob('*.xlsx')):
            try:
                df = pd.read_excel(arquivo, skiprows=8)

                df = df.rename(columns={
                    'Valor Total': 'Valor',
                    'Quantidade': 'Qtd',
                    'Familia / Sub-Familia': 'Familia'
                })

                df = df[df['Data'].notna() & df['Valor'].notna()].copy()
                df = df[~df['Data'].astype(str).str.contains('Totais', na=False)].copy()

                df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
                df = df[df['Data'].notna()].copy()
                df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
                df['Qtd'] = pd.to_numeric(df['Qtd'], errors='coerce')

                df['Fonte'] = 'POS-Café'

                # Manter todas as colunas relevantes
                colunas = ['Data', 'Valor', 'Qtd', 'Fonte', 'Produto']
                if 'Familia' in df.columns:
                    colunas.append('Familia')
                
                df = df[colunas].copy()
                dados_cafe.append(df)

            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")
                continue

        if not dados_cafe:
            return pd.DataFrame()

        df_final = pd.concat(dados_cafe, ignore_index=True)
        df_final = df_final.sort_values('Data').reset_index(drop=True)

        # Aplicar categorização inteligente
        if not df_final.empty:
            if 'Familia' in df_final.columns:
                df_final = self.categorizer.categorizar_dataframe(
                    df_final, 
                    coluna_produto='Produto',
                    coluna_familia='Familia'
                )
            else:
                df_final = self.categorizer.categorizar_dataframe(df_final, coluna_produto='Produto')

        return df_final

    def carregar_outros_produtos(self, incluir_raspadinhas=False):
        """Carrega outros produtos dos CSV"""
        dados_outros = []

        if not self.pos2_dir.exists():
            return pd.DataFrame()

        for arquivo in sorted(self.pos2_dir.glob('*.csv')):
            try:
                df = pd.read_csv(arquivo,
                                sep=';',
                                encoding='latin1',
                                decimal=',',
                                thousands='.')

                df['Data'] = pd.to_datetime(df['Data'], format='%Y-%m-%d')

                df_filtrado = df[df['Codigo'] == 50010].copy()

                if incluir_raspadinhas:
                    df_rasp = df[df['Codigo'] < 50000].copy()
                    df_filtrado = pd.concat([df_filtrado, df_rasp]).drop_duplicates()

                df_filtrado = df_filtrado.rename(columns={
                    'Val.Total': 'Valor',
                    'Designação': 'Produto',
                    'Qtd': 'Qtd'
                })

                df_filtrado['Fonte'] = 'POS-Outros'

                # Renomear todos os produtos para "Outros"
                df_filtrado['Produto'] = 'Outros'

                df_filtrado = df_filtrado[['Data', 'Valor', 'Qtd', 'Fonte', 'Produto']].copy()
                dados_outros.append(df_filtrado)

            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")
                continue

        if not dados_outros:
            return pd.DataFrame()

        df_final = pd.concat(dados_outros, ignore_index=True)
        df_final = df_final.sort_values('Data').reset_index(drop=True)

        # Categorizar
        if not df_final.empty:
            df_final = self.categorizer.categorizar_dataframe(df_final, coluna_produto='Produto')

        return df_final

    def carregar_todos_dados(self, incluir_raspadinhas_pos2=False):
        """Carrega todos os dados com categorização"""
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

    def carregar_tudo_integrado(self):
        """Carrega e integra todos os dados num único DataFrame"""
        dados = self.carregar_todos_dados()
        
        dfs = []
        for fonte, df in dados.items():
            if not df.empty:
                dfs.append(df)
        
        if not dfs:
            return pd.DataFrame()
        
        df_completo = pd.concat(dfs, ignore_index=True)
        df_completo = df_completo.sort_values('Data').reset_index(drop=True)
        
        # Adicionar colunas temporais
        df_completo['Ano'] = df_completo['Data'].dt.year
        df_completo['Mes'] = df_completo['Data'].dt.month
        df_completo['Semana'] = df_completo['Data'].dt.isocalendar().week
        df_completo['Dia_Semana'] = df_completo['Data'].dt.dayofweek
        df_completo['Trimestre'] = df_completo['Data'].dt.quarter
        
        return df_completo


# Função auxiliar
def carregar_dados_completos():
    """Função conveniente"""
    loader = DataLoaderV4()
    return loader.carregar_tudo_integrado()


if __name__ == '__main__':
    print("=== Teste do DataLoaderV4 ===\n")
    loader = DataLoaderV4()
    df = loader.carregar_tudo_integrado()
    
    print(f"Total de registos: {len(df)}")
    print(f"\nCategorias encontradas:")
    print(df['Categoria'].value_counts())
    print(f"\nTotal por categoria:")
    print(df.groupby('Categoria')['Valor'].sum().round(2))
