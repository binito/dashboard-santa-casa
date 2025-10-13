"""
Script de teste para validar o Dashboard v3 e o data_loader_v3
"""

import sys
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("TESTE DO DASHBOARD V3 - VALIDAÇÃO DE DADOS")
print("=" * 70)
print()

# Testar importação do módulo
print("1. Testando importação do data_loader_v3...")
try:
    from data_loader_v3 import DataLoaderV3
    print("   ✓ Importação bem-sucedida")
except Exception as e:
    print(f"   ✗ Erro na importação: {e}")
    sys.exit(1)

print()

# Criar instância do loader
print("2. Criando instância do DataLoaderV3...")
try:
    loader = DataLoaderV3()
    print("   ✓ Instância criada com sucesso")
except Exception as e:
    print(f"   ✗ Erro ao criar instância: {e}")
    sys.exit(1)

print()

# Verificar existência dos diretórios
print("3. Verificando diretórios de dados...")
dirs = {
    'Santa Casa': loader.santa_casa_dir,
    'POS 1 (Café)': loader.pos1_dir,
    'POS 2 (Outros)': loader.pos2_dir
}

for nome, caminho in dirs.items():
    if caminho.exists():
        print(f"   ✓ {nome}: {caminho} (encontrado)")
    else:
        print(f"   ⚠ {nome}: {caminho} (não encontrado)")

print()

# Carregar dados
print("4. Carregando dados de todas as fontes...")
try:
    dados = loader.carregar_todos_dados()
    print("   ✓ Dados carregados com sucesso")
except Exception as e:
    print(f"   ✗ Erro ao carregar dados: {e}")
    sys.exit(1)

print()

# Validar cada fonte
print("5. Validando dados carregados...")
print()

sources = {
    'Santa Casa': dados['santa_casa'],
    'Café': dados['cafe'],
    'Outros': dados['outros']
}

resultados = {}

for fonte, df in sources.items():
    print(f"   {fonte}:")

    if len(df) == 0:
        print(f"      ⚠ Nenhum dado encontrado")
        resultados[fonte] = {'status': 'vazio', 'registos': 0}
        print()
        continue

    # Estatísticas básicas
    registos = len(df)
    periodo_inicio = df['Data'].min()
    periodo_fim = df['Data'].max()
    total_vendas = df['Valor'].sum()
    media_diaria = df.groupby('Data')['Valor'].sum().mean()

    print(f"      ✓ Registos: {registos:,}")
    print(f"      ✓ Período: {periodo_inicio.strftime('%Y-%m-%d')} a {periodo_fim.strftime('%Y-%m-%d')}")
    print(f"      ✓ Total de vendas: €{total_vendas:,.2f}")
    print(f"      ✓ Média diária: €{media_diaria:,.2f}")

    resultados[fonte] = {
        'status': 'ok',
        'registos': registos,
        'periodo': (periodo_inicio, periodo_fim),
        'total': total_vendas,
        'media_diaria': media_diaria
    }

    print()

print()

# Testar resumo
print("6. Testando método get_resumo_dados()...")
try:
    resumo = loader.get_resumo_dados()
    print("   ✓ Resumo gerado com sucesso")
    print()
    for fonte, info in resumo.items():
        print(f"   {fonte}:")
        print(f"      Registos: {info['registos']}")
        print(f"      Período: {info['periodo']}")
        print(f"      Total: €{info['total']:.2f}")
except Exception as e:
    print(f"   ✗ Erro ao gerar resumo: {e}")

print()

# Resumo final
print("=" * 70)
print("RESUMO DO TESTE")
print("=" * 70)
print()

total_registos = sum(r['registos'] for r in resultados.values())
total_vendas_geral = sum(r.get('total', 0) for r in resultados.values())

fontes_ok = sum(1 for r in resultados.values() if r['status'] == 'ok')
fontes_vazias = sum(1 for r in resultados.values() if r['status'] == 'vazio')

print(f"Fontes com dados: {fontes_ok}/3")
print(f"Fontes vazias: {fontes_vazias}/3")
print(f"Total de registos: {total_registos:,}")
print(f"Total de vendas: €{total_vendas_geral:,.2f}")
print()

if fontes_ok > 0:
    print("✓ TESTE PASSOU - Dashboard v3 está funcional!")
    print()
    print("Para iniciar o dashboard:")
    print("   streamlit run dashboard_v3.py")
    print()
    if fontes_vazias > 0:
        print("Nota: Algumas fontes não têm dados ainda, mas o sistema está pronto para recebê-los.")
else:
    print("⚠ AVISO - Nenhuma fonte de dados disponível!")
    print()
    print("Verifique os caminhos dos ficheiros:")
    print("   - /home/jorge/Documentos/pos/pos_1/*.xlsx")
    print("   - /home/jorge/Documentos/pos/pos_2/*.csv")

print()
print("=" * 70)
print(f"Teste executado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
