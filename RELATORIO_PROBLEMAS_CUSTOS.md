# 📊 Relatório de Problemas com Custos e Margens

## ⚠️ PROBLEMA PRINCIPAL

A margem global de **85.2%** está **INCORRETA** porque:

1. **Jogos Santa Casa** (79.7% das vendas) têm margem de 91.86%
   - ✅ Isto está CORRETO (comissões de 5-12.7%)

2. **Produtos com custos errados** que inflacionam o lucro negativamente

---

## 🔴 Produtos com PREJUÍZO (Margens Negativas)

### Margens mais problemáticas:

| Produto | Categoria | Vendas | Custos | Margem | Problema |
|---------|-----------|--------|--------|--------|----------|
| **PASTILHAS** | ALIMENTAÇÃO | €22.60 | €113.00 | **-400%** | Custo 5x maior que venda! |
| **Aguardente** | DIGESTIVOS | €379.80 | €1,540.00 | **-305%** | Custo 4x maior que venda! |
| **VINHO** | VINHOS | €929.40 | €2,060.17 | **-122%** | Preço venda €0.60 vs custo €1.33 |
| **GINJA** | APERITIVOS | €42.80 | €88.00 | **-106%** | Custo 2x maior |
| **KIR** | APERITIVOS | €188.00 | €380.00 | **-102%** | Custo 2x maior |
| **BRANDYS** | DIGESTIVOS | €511.80 | €920.00 | **-80%** | Custo quase 2x |
| **Moscatel** | APERITIVOS | €2,938.10 | €4,222.00 | **-44%** | Custo €2/unidade |
| **Martini com Cerveja** | APERITIVOS | €2,791.30 | €3,860.00 | **-38%** | Custo €2/unidade |
| **Ricard** | APERITIVOS | €688.90 | €920.00 | **-34%** | Custo €2/unidade |

---

## 🔍 Análise Detalhada: Caso VINHO

**Dados encontrados:**
- Preço de venda: **€0.60 por unidade**
- Custo atribuído: **€1.33 por copo** (do ficheiro custos_produtos.csv)
- Fonte: POS-Café

**Problema:**
- O sistema está a vender VINHO a €0.60, mas o custo é €1.33
- **Prejuízo de €0.73 por venda!**

**Causa provável:**
1. O preço nos dados POS está errado (deveria ser €2.50 como em custos_produtos.csv)
2. OU o produto "VINHO" nos POS é diferente de "Vinho Tinto" e precisa custo diferente

---

## 💡 SOLUÇÕES NECESSÁRIAS

### 1. Verificar Preços de Venda nos Ficheiros POS
- `/home/jorge/Documentos/pos/pos_1/*.xlsx`
- `/home/jorge/Documentos/pos/pos_2/*.csv`

Produtos a verificar:
- VINHO (deve ser ~€2.50, não €0.60)
- PASTILHAS (preço muito baixo?)
- Aguardente (preço muito baixo?)

### 2. Verificar/Corrigir Custos em `dados_custos/custos_produtos.csv`

Produtos que precisam de custos corretos:
- PASTILHAS
- Aguardente
- GINJA
- KIR
- BRANDYS
- Moscatel
- Martini com Cerveja
- Ricard

### 3. Verificar Correspondência de Nomes

Alguns produtos podem ter nomes diferentes entre POS e custos_produtos.csv:
- "VINHO" (POS) vs "Vinho Tinto" (custos)
- "PASTILHAS" vs ?
- "Aguardente" vs ?

---

## 📈 Impacto na Margem Global

**Cenário Atual (ERRADO):**
- Receita Total: €539,104
- Lucro Bruto: €453,370
- Margem: **84.10%** ❌ (inflacionada pelos Jogos SC)

**Análise Real por Categoria:**

| Categoria | Vendas | Margem Real |
|-----------|--------|-------------|
| JOGOS_SANTA_CASA | €429,423 (79.7%) | 91.86% ✅ |
| CERVEJAS | €34,112 | 68.86% ✅ |
| CAFETARIA | €25,734 | 61.55% ✅ |
| ÁGUAS | €1,952 | 74.74% ✅ |
| OUTROS | €35,112 | 64.01% ❓ |
| REFRIGERANTES | €1,925 | 57.23% ✅ |
| ALIMENTAÇÃO | €985 | 45.11% ❓ |
| **VINHOS** | €929 | **-121.67%** ❌ |
| **DIGESTIVOS** | €1,265 | **-132.57%** ❌ |
| **APERITIVOS** | €7,668 | **-40.44%** ❌ |

**Conclusão:**
- As margens negativas em VINHOS, DIGESTIVOS e APERITIVOS estão a **reduzir** o lucro
- Mas como estas categorias são pequenas (~2% das vendas), o impacto é minimizado
- A margem global é dominada pelos Jogos Santa Casa (79.7% das vendas)

---

## ✅ AÇÕES RECOMENDADAS

1. **URGENTE:** Corrigir preços de venda ou custos dos produtos com margens negativas
2. **Revisar** o ficheiro `custos_produtos.csv` e adicionar produtos em falta
3. **Verificar** dados brutos dos POS para confirmar preços corretos
4. **Depois das correções,** a margem global deve baixar para valores mais realistas (~88-92%)

---

*Relatório gerado automaticamente em 2025-10-15*
