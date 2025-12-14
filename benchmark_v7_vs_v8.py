#!/usr/bin/env python3
"""
Benchmark: Dashboard V7 (ficheiros) vs V8 (MariaDB)
Compara tempo de carregamento e performance
"""

import time
from datetime import datetime
from data_loader_v7 import DataLoaderV7
from data_loader_v8 import DataLoaderV8


def formatar_tempo(segundos):
    """Formata tempo em segundos para leitura humana"""
    if segundos < 1:
        return f"{segundos*1000:.0f}ms"
    return f"{segundos:.2f}s"


def benchmark_loader(nome, loader_func, repeticoes=3):
    """
    Executa benchmark de um loader

    Args:
        nome: Nome do loader (V7 ou V8)
        loader_func: Função que carrega os dados
        repeticoes: Número de repetições para média

    Returns:
        Dicionário com resultados
    """
    print(f"\n{'='*70}")
    print(f"🔄 TESTE: {nome}")
    print(f"{'='*70}")

    tempos = []
    df_final = None

    for i in range(repeticoes):
        print(f"\n▶️  Execução {i+1}/{repeticoes}...")

        inicio = time.time()
        df = loader_func()
        fim = time.time()

        tempo_decorrido = fim - inicio
        tempos.append(tempo_decorrido)

        print(f"   ⏱️  Tempo: {formatar_tempo(tempo_decorrido)}")
        print(f"   📊 Registos: {len(df):,}")

        if df_final is None:
            df_final = df

    # Calcular estatísticas
    tempo_medio = sum(tempos) / len(tempos)
    tempo_min = min(tempos)
    tempo_max = max(tempos)

    resultado = {
        'nome': nome,
        'tempos': tempos,
        'tempo_medio': tempo_medio,
        'tempo_min': tempo_min,
        'tempo_max': tempo_max,
        'num_registos': len(df_final) if df_final is not None else 0,
        'colunas': list(df_final.columns) if df_final is not None else []
    }

    return resultado


def main():
    print("="*70)
    print("🏁 BENCHMARK: Dashboard V7 (Ficheiros) vs V8 (MariaDB)")
    print("="*70)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔁 Repetições: 3 (para calcular média)")
    print("="*70)

    # Benchmark V7 (Ficheiros)
    print("\n\n")
    print("📂 V7: Carregamento de FICHEIROS (.xlsx, .csv, .txt)")
    print("   - Excel com skip rows e regex")
    print("   - CSV com encoding complexo")
    print("   - TXT com parsing manual")

    def carregar_v7():
        loader = DataLoaderV7(usar_despesify=False)  # Sem Despesify para comparação justa
        return loader.carregar_tudo_integrado_com_custos()

    resultado_v7 = benchmark_loader("V7 - Ficheiros", carregar_v7, repeticoes=3)

    # Benchmark V8 (MariaDB)
    print("\n\n")
    print("🗄️  V8: Carregamento de MARIADB")
    print("   - Queries SQL otimizadas")
    print("   - Índices em data, produto, codigo")
    print("   - Filtros aplicados na query (WHERE)")

    def carregar_v8():
        loader = DataLoaderV8(usar_despesify=False)  # Sem Despesify para comparação justa
        return loader.carregar_tudo_integrado_com_custos()

    resultado_v8 = benchmark_loader("V8 - MariaDB", carregar_v8, repeticoes=3)

    # Comparação
    print("\n\n")
    print("="*70)
    print("📊 RESULTADOS COMPARATIVOS")
    print("="*70)

    print(f"\n{'Métrica':<30} {'V7 (Ficheiros)':<20} {'V8 (MariaDB)':<20}")
    print("-"*70)

    print(f"{'Tempo Médio':<30} {formatar_tempo(resultado_v7['tempo_medio']):<20} {formatar_tempo(resultado_v8['tempo_medio']):<20}")
    print(f"{'Tempo Mínimo':<30} {formatar_tempo(resultado_v7['tempo_min']):<20} {formatar_tempo(resultado_v8['tempo_min']):<20}")
    print(f"{'Tempo Máximo':<30} {formatar_tempo(resultado_v7['tempo_max']):<20} {formatar_tempo(resultado_v8['tempo_max']):<20}")
    print(f"{'Registos Carregados':<30} {resultado_v7['num_registos']:,}".ljust(30) + f" {resultado_v8['num_registos']:,}")

    # Calcular ganho de performance
    melhoria_pct = ((resultado_v7['tempo_medio'] - resultado_v8['tempo_medio']) / resultado_v7['tempo_medio']) * 100
    fator_rapidez = resultado_v7['tempo_medio'] / resultado_v8['tempo_medio']

    print("\n" + "="*70)
    print("🚀 GANHO DE PERFORMANCE")
    print("="*70)
    print(f"✅ V8 é {melhoria_pct:.1f}% mais rápido que V7")
    print(f"⚡ V8 é {fator_rapidez:.1f}x mais rápido que V7")
    print(f"⏱️  Economia de tempo: {formatar_tempo(resultado_v7['tempo_medio'] - resultado_v8['tempo_medio'])}")

    # Análise detalhada
    print("\n" + "="*70)
    print("📝 ANÁLISE DETALHADA")
    print("="*70)

    print(f"\n🔴 V7 (Ficheiros):")
    print(f"   • Carregamento: {formatar_tempo(resultado_v7['tempo_medio'])}")
    print(f"   • Variação: {formatar_tempo(resultado_v7['tempo_min'])} - {formatar_tempo(resultado_v7['tempo_max'])}")
    print(f"   • Registos: {resultado_v7['num_registos']:,}")

    print(f"\n🟢 V8 (MariaDB):")
    print(f"   • Carregamento: {formatar_tempo(resultado_v8['tempo_medio'])}")
    print(f"   • Variação: {formatar_tempo(resultado_v8['tempo_min'])} - {formatar_tempo(resultado_v8['tempo_max'])}")
    print(f"   • Registos: {resultado_v8['num_registos']:,}")

    # Projeções
    print("\n" + "="*70)
    print("📈 PROJEÇÕES DE USO")
    print("="*70)

    cache_expira_minutos = 30
    carregamentos_por_dia = (24 * 60) / cache_expira_minutos

    tempo_v7_dia = resultado_v7['tempo_medio'] * carregamentos_por_dia
    tempo_v8_dia = resultado_v8['tempo_medio'] * carregamentos_por_dia
    economia_dia = tempo_v7_dia - tempo_v8_dia

    print(f"\nConsiderando cache de 30 minutos:")
    print(f"   • Carregamentos por dia: {carregamentos_por_dia:.0f}")
    print(f"   • Tempo total V7/dia: {formatar_tempo(tempo_v7_dia)}")
    print(f"   • Tempo total V8/dia: {formatar_tempo(tempo_v8_dia)}")
    print(f"   • ✅ Economia por dia: {formatar_tempo(economia_dia)}")
    print(f"   • ✅ Economia por mês: {formatar_tempo(economia_dia * 30)}")

    print("\n" + "="*70)
    print("✅ BENCHMARK CONCLUÍDO")
    print("="*70)
    print(f"⏰ Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    main()
