"""
Sistema de Categorização Inteligente de Produtos
Identifica automaticamente categorias e subcategorias
"""

import pandas as pd
import re
from typing import Dict, Tuple, List


class ProductCategorizer:
    """Categoriza produtos automaticamente com base em padrões e palavras-chave"""

    # Definição de categorias e palavras-chave
    CATEGORIAS = {
        'CAFETARIA': {
            'subcategorias': {
                'Café': ['café', 'galão', 'meia de leite', 'abatanado', 'expresso'],
                'Chá': ['chá', 'cha'],
                'Chocolate Quente': ['chocolate quente', 'chocolat quente']
            },
            'cor': '#8B4513',
            'icone': '☕'
        },
        'CERVEJAS': {
            'subcategorias': {
                'Cerveja': ['cerveja', 'imperial', 'heineken', 'super bock', 'sagres', 'caneca', 'panaché', 'panache', 'mini', 'media', 'média', 'especial', 'cidra', 'tango']
            },
            'cor': '#FFD700',
            'icone': '🍺'
        },
        'VINHOS': {
            'subcategorias': {
                'Vinho Tinto': ['vinho tinto'],
                'Vinho Branco': ['vinho branco'],
                'Vinho Verde': ['vinho verde'],
                'Vinho Geral': ['vinho'],
                'Porto': ['porto'],
                'Moscatel': ['moscatel']
            },
            'cor': '#722F37',
            'icone': '🍷'
        },
        'APERITIVOS': {
            'subcategorias': {
                'Martini': ['martini'],
                'Kir': ['kir'],
                'Ricard': ['ricard'],
                'Outros Aperitivos': ['aperitivo']
            },
            'cor': '#FF6347',
            'icone': '🍸'
        },
        'DIGESTIVOS': {
            'subcategorias': {
                'Aguardente': ['aguardente'],
                'Brandy': ['brandy', 'brandys'],
                'Whisky': ['whisky', 'whiskey'],
                'Licores': ['licor beirão', 'licor', 'ginja', 'amêndoa amarga'],
                'Outros Digestivos': ['são domingos', 'aliança']
            },
            'cor': '#8B0000',
            'icone': '🥃'
        },
        'REFRIGERANTES': {
            'subcategorias': {
                'Refrigerantes': ['refrigerante', 'coca-cola', 'pepsi', 'fanta'],
                'Sumos': ['compal', 'sumol'],
                'Ice Tea': ['icetea', 'ice tea'],
                'Energéticos': ['red bull', 'monster']
            },
            'cor': '#FF1493',
            'icone': '🥤'
        },
        'ÁGUAS': {
            'subcategorias': {
                'Água Natural': ['agua mineral', 'água mineral', 'água 0.5'],
                'Água com Gás': ['agua c/gás', 'água c/gás', 'aguas c/gas'],
                'Água com Sabor': ['agua c/sabor', 'água c/sabor', 'aguas c/sabor']
            },
            'cor': '#4169E1',
            'icone': '💧'
        },
        'ALIMENTAÇÃO': {
            'subcategorias': {
                'Pastelaria': ['pastelaria', 'bolos', 'bolo'],
                'Batatas Fritas': ['batata frita', 'batatas fritas'],
                'Chocolates': ['chocolate', 'trident', 'snickers', 'mars'],
                'Pastilhas': ['pastilha', 'halls', 'mentos'],
                'Outros Snacks': ['snack']
            },
            'cor': '#FFA500',
            'icone': '🍰'
        },
        'JOGOS_SANTA_CASA': {
            'subcategorias': {
                'Euromilhões': ['euromilhões', 'euromilhoes'],
                'Totoloto': ['totoloto'],
                'Placard': ['placard'],
                'Raspadinhas': ['raspadinha', 'lotaria instantânea'],
                'Totobola': ['totobola'],
                'Outros Jogos': ['m1lhao', 'eurodreams', 'lotaria']
            },
            'cor': '#1f77b4',
            'icone': '🎲'
        },
        'OUTROS': {
            'subcategorias': {
                'Diversos': ['outros', 'outro']
            },
            'cor': '#808080',
            'icone': '📦'
        }
    }

    def __init__(self):
        """Inicializa o categorizador"""
        self._cache = {}

    def categorizar_produto(self, nome_produto: str, familia: str = None) -> Tuple[str, str]:
        """
        Categoriza um produto com base no nome e família

        Args:
            nome_produto: Nome do produto
            familia: Família do produto (opcional)

        Returns:
            Tuple[categoria, subcategoria]
        """
        if not nome_produto or pd.isna(nome_produto):
            return ('OUTROS', 'Diversos')

        # Cache para performance
        cache_key = f"{nome_produto}_{familia}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        nome_lower = str(nome_produto).lower().strip()
        familia_lower = str(familia).lower().strip() if familia else ""

        # Tentar categorizar pela família primeiro
        if familia:
            for categoria, info in self.CATEGORIAS.items():
                if any(key.lower() in familia_lower for key in [categoria.lower()]):
                    # Para cervejas, usar o nome do produto como subcategoria
                    if categoria == 'CERVEJAS':
                        resultado = (categoria, str(nome_produto).strip())
                        self._cache[cache_key] = resultado
                        return resultado
                    # Encontrar subcategoria dentro da categoria
                    for subcat, palavras in info['subcategorias'].items():
                        if any(palavra in nome_lower for palavra in palavras):
                            resultado = (categoria, subcat)
                            self._cache[cache_key] = resultado
                            return resultado
                    # Se não encontrou subcategoria, usar primeira
                    resultado = (categoria, list(info['subcategorias'].keys())[0])
                    self._cache[cache_key] = resultado
                    return resultado

        # Tentar categorizar pelo nome do produto
        for categoria, info in self.CATEGORIAS.items():
            for subcat, palavras in info['subcategorias'].items():
                if any(palavra in nome_lower for palavra in palavras):
                    # Para cervejas, usar o nome do produto como subcategoria
                    if categoria == 'CERVEJAS':
                        resultado = (categoria, str(nome_produto).strip())
                        self._cache[cache_key] = resultado
                        return resultado
                    resultado = (categoria, subcat)
                    self._cache[cache_key] = resultado
                    return resultado

        # Padrão: OUTROS
        resultado = ('OUTROS', 'Diversos')
        self._cache[cache_key] = resultado
        return resultado

    def categorizar_dataframe(self, df: pd.DataFrame,
                            coluna_produto: str = 'Produto',
                            coluna_familia: str = 'Familia / Sub-Familia') -> pd.DataFrame:
        """
        Adiciona colunas de categoria e subcategoria a um DataFrame

        OTIMIZADO: Usa vectorização para performance máxima

        Args:
            df: DataFrame com produtos
            coluna_produto: Nome da coluna com produtos
            coluna_familia: Nome da coluna com família (opcional)

        Returns:
            DataFrame com colunas adicionais: Categoria, Subcategoria, Cor_Categoria, Icone_Categoria
        """
        df = df.copy()

        # Verificar se colunas existem
        if coluna_produto not in df.columns:
            raise ValueError(f"Coluna '{coluna_produto}' não encontrada no DataFrame")

        tem_familia = coluna_familia in df.columns

        # OTIMIZAÇÃO: Criar lookup de produtos únicos (muito mais rápido!)
        produtos_unicos = df[coluna_produto].unique()

        # Categorizar apenas produtos únicos
        categorias_map = {}
        subcategorias_map = {}

        for produto in produtos_unicos:
            if pd.isna(produto):
                categorias_map[produto] = 'OUTROS'
                subcategorias_map[produto] = 'Diversos'
            else:
                familia = None
                if tem_familia:
                    # Pegar primeira família associada ao produto (para cache)
                    mask = df[coluna_produto] == produto
                    familias = df.loc[mask, coluna_familia].dropna()
                    if len(familias) > 0:
                        familia = familias.iloc[0]

                cat, subcat = self.categorizar_produto(produto, familia)
                categorias_map[produto] = cat
                subcategorias_map[produto] = subcat

        # Mapear de volta para o DataFrame (vectorizado - muito rápido!)
        df['Categoria'] = df[coluna_produto].map(categorias_map)
        df['Subcategoria'] = df[coluna_produto].map(subcategorias_map)

        # Preencher valores nulos
        df['Categoria'] = df['Categoria'].fillna('OUTROS')
        df['Subcategoria'] = df['Subcategoria'].fillna('Diversos')

        # Criar mapas de cores e ícones (vectorizado)
        cores_map = {cat: info.get('cor', '#808080') for cat, info in self.CATEGORIAS.items()}
        icones_map = {cat: info.get('icone', '📦') for cat, info in self.CATEGORIAS.items()}

        df['Cor_Categoria'] = df['Categoria'].map(cores_map).fillna('#808080')
        df['Icone_Categoria'] = df['Categoria'].map(icones_map).fillna('📦')

        return df

    def get_resumo_categorias(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Retorna resumo estatístico por categoria

        Args:
            df: DataFrame com produtos categorizados (deve ter 'Categoria', 'Valor')

        Returns:
            DataFrame com resumo por categoria
        """
        if 'Categoria' not in df.columns or 'Valor' not in df.columns:
            raise ValueError("DataFrame deve ter colunas 'Categoria' e 'Valor'")

        resumo = df.groupby('Categoria').agg({
            'Valor': ['sum', 'mean', 'count', 'std']
        }).round(2)

        resumo.columns = ['Total (€)', 'Média (€)', 'Vendas', 'Desvio Padrão']
        resumo['% do Total'] = (resumo['Total (€)'] / resumo['Total (€)'].sum() * 100).round(1)

        # Adicionar ícones
        resumo['Ícone'] = resumo.index.map(
            lambda x: self.CATEGORIAS.get(x, {}).get('icone', '📦')
        )

        # Reordenar colunas
        resumo = resumo[['Ícone', 'Total (€)', '% do Total', 'Vendas', 'Média (€)', 'Desvio Padrão']]
        resumo = resumo.sort_values('Total (€)', ascending=False)

        return resumo

    def get_resumo_subcategorias(self, df: pd.DataFrame, categoria: str = None) -> pd.DataFrame:
        """
        Retorna resumo por subcategoria

        Args:
            df: DataFrame com produtos categorizados
            categoria: Filtrar por categoria específica (opcional)

        Returns:
            DataFrame com resumo por subcategoria
        """
        df_filtrado = df.copy()

        if categoria:
            df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria]

        if df_filtrado.empty:
            return pd.DataFrame()

        resumo = df_filtrado.groupby(['Categoria', 'Subcategoria']).agg({
            'Valor': ['sum', 'mean', 'count']
        }).round(2)

        resumo.columns = ['Total (€)', 'Média (€)', 'Vendas']
        resumo['% do Total'] = (resumo['Total (€)'] / df_filtrado['Valor'].sum() * 100).round(1)

        resumo = resumo.sort_values('Total (€)', ascending=False)

        return resumo

    def get_produtos_mais_vendidos(self, df: pd.DataFrame, top: int = 20,
                                  categoria: str = None) -> pd.DataFrame:
        """
        Retorna produtos mais vendidos

        Args:
            df: DataFrame com produtos
            top: Número de produtos a retornar
            categoria: Filtrar por categoria (opcional)

        Returns:
            DataFrame com top produtos
        """
        df_filtrado = df.copy()

        if categoria:
            df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria]

        if df_filtrado.empty:
            return pd.DataFrame()

        if 'Produto' not in df_filtrado.columns:
            return pd.DataFrame()

        # Agrupar por produto
        resumo = df_filtrado.groupby(['Produto', 'Categoria', 'Subcategoria']).agg({
            'Valor': ['sum', 'count']
        }).round(2)

        resumo.columns = ['Total (€)', 'Vendas']
        resumo = resumo.sort_values('Total (€)', ascending=False).head(top)

        return resumo


# Função auxiliar
def categorizar_vendas(df: pd.DataFrame) -> pd.DataFrame:
    """Função conveniente para categorizar um DataFrame de vendas"""
    categorizer = ProductCategorizer()
    return categorizer.categorizar_dataframe(df)


if __name__ == '__main__':
    # Teste do módulo
    print("=== Teste do ProductCategorizer ===\n")

    categorizer = ProductCategorizer()

    # Testes
    produtos_teste = [
        'CAFÉ',
        'CERVEJA MINI',
        'Imperial',
        'VINHO',
        'Aguardente',
        'REFRIGERANTES',
        'PASTELARIA',
        'Martini'
    ]

    print("Categorizando produtos de teste:\n")
    for produto in produtos_teste:
        cat, subcat = categorizer.categorizar_produto(produto)
        icone = categorizer.CATEGORIAS[cat]['icone']
        print(f"{icone} {produto:20s} → {cat:20s} / {subcat}")
