#!/usr/bin/env python3
"""
Teste da Lógica Híbrida de Custos
"""
from datetime import datetime
from cost_manager_v2 import CostManagerV2

# Inicializar o gestor de custos
print("🔧 Inicializando CostManagerV2...")
cost_manager = CostManagerV2(custos_dir='dados_custos', usar_despesify=True)

# Testar período de Janeiro 2026 (1/01 a 28/01)
print("\n" + "="*80)
print("📅 TESTE 1: Período 1/01/2026 a 28/01/2026 (INCLUI dia 28)")
print("="*80)

data_inicio = datetime(2026, 1, 1)
data_fim = datetime(2026, 1, 28)

total, fonte, df_detalhes = cost_manager.get_custos_operacionais_periodo(data_inicio, data_fim)

print(f"\n💰 Total Custos Operacionais: €{total:,.2f}")
print(f"📊 Fonte: {fonte}")
print(f"\n📋 Detalhes:")
if not df_detalhes.empty:
    print(df_detalhes.to_string(index=False))
else:
    print("   (vazio)")

# Testar período de Fevereiro 2026 (1/02 a 03/02)
print("\n" + "="*80)
print("📅 TESTE 2: Período 1/02/2026 a 03/02/2026 (NÃO INCLUI dia 28)")
print("="*80)

data_inicio = datetime(2026, 2, 1)
data_fim = datetime(2026, 2, 3)

total, fonte, df_detalhes = cost_manager.get_custos_operacionais_periodo(data_inicio, data_fim)

print(f"\n💰 Total Custos Operacionais: €{total:,.2f}")
print(f"📊 Fonte: {fonte}")
print(f"\n📋 Detalhes:")
if not df_detalhes.empty:
    print(df_detalhes.to_string(index=False))
else:
    print("   (vazio)")

# Testar ano completo 2026 (1/01 a 03/02)
print("\n" + "="*80)
print("📅 TESTE 3: Período 1/01/2026 a 03/02/2026 (ano 2026 completo até hoje)")
print("="*80)

data_inicio = datetime(2026, 1, 1)
data_fim = datetime(2026, 2, 3)

total, fonte, df_detalhes = cost_manager.get_custos_operacionais_periodo(data_inicio, data_fim)

print(f"\n💰 Total Custos Operacionais: €{total:,.2f}")
print(f"📊 Fonte: {fonte}")
print(f"\n📋 Detalhes:")
if not df_detalhes.empty:
    print(df_detalhes.to_string(index=False))
else:
    print("   (vazio)")

print("\n" + "="*80)
print("✅ Teste concluído!")
print("="*80)
