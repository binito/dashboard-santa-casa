const state = {
  meta: null,
  dashboard: null,
  activeView: "cockpit",
  preset: "YTD",
  year: "",
  startDate: "",
  endDate: "",
  categorias: [],
  subcategorias: [],
  fontes: [],
  excludeSundays: false,
  compositeIngredients: [],
}

const viewMeta = {
  cockpit: { title: "Cockpit Operacional", eyebrow: "Dashboard executivo" },
  sales: { title: "Comercial", eyebrow: "Vendas, performance e dados" },
  margin: { title: "Rentabilidade", eyebrow: "Custos, margens e break-even" },
  ops: { title: "Operação", eyebrow: "Fornecedores, forecast e fichas" },
}

const els = {
  loginView: document.querySelector("#loginView"),
  appView: document.querySelector("#appView"),
  loginForm: document.querySelector("#loginForm"),
  loginError: document.querySelector("#loginError"),
  username: document.querySelector("#username"),
  password: document.querySelector("#password"),
  userName: document.querySelector("#userName"),
  logoutButton: document.querySelector("#logoutButton"),
  refreshButton: document.querySelector("#refreshButton"),
  resetButton: document.querySelector("#resetButton"),
  yearSelect: document.querySelector("#yearSelect"),
  startDate: document.querySelector("#startDate"),
  endDate: document.querySelector("#endDate"),
  categorySelect: document.querySelector("#categorySelect"),
  subcategorySelect: document.querySelector("#subcategorySelect"),
  sourceSelect: document.querySelector("#sourceSelect"),
  excludeSundays: document.querySelector("#excludeSundays"),
  presetButtons: document.querySelector("#presetButtons"),
  viewEyebrow: document.querySelector("#viewEyebrow"),
  viewTitle: document.querySelector("#viewTitle"),
  periodLabel: document.querySelector("#periodLabel"),
  recordsLabel: document.querySelector("#recordsLabel"),
  statusLabel: document.querySelector("#statusLabel"),
  statusScore: document.querySelector("#statusScore"),
  kpiGrid: document.querySelector("#kpiGrid"),
  decisionGrid: document.querySelector("#decisionGrid"),
  healthScore: document.querySelector("#healthScore"),
  healthText: document.querySelector("#healthText"),
  healthBar: document.querySelector("#healthBar"),
  healthFacts: document.querySelector("#healthFacts"),
  priorityList: document.querySelector("#priorityList"),
  topProducts: document.querySelector("#topProducts"),
  toast: document.querySelector("#toast"),
}

const money = new Intl.NumberFormat("pt-PT", { style: "currency", currency: "EUR", maximumFractionDigits: 0 })
const money2 = new Intl.NumberFormat("pt-PT", { style: "currency", currency: "EUR", minimumFractionDigits: 2, maximumFractionDigits: 2 })
const number = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 0 })
const number1 = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 1 })
const percent = new Intl.NumberFormat("pt-PT", { maximumFractionDigits: 1 })

function fmtMoney(value) {
  return money.format(Number(value || 0)).replace(/\s/g, "")
}

function fmtMoney2(value) {
  return money2.format(Number(value || 0)).replace(/\s/g, "")
}

function fmtNumber(value) {
  return number.format(Number(value || 0))
}

function fmtNumber1(value) {
  return number1.format(Number(value || 0))
}

function fmtPercent(value) {
  return `${percent.format(Number(value || 0))}%`
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;")
}

function showToast(message) {
  els.toast.textContent = message
  els.toast.classList.remove("hidden")
  window.setTimeout(() => els.toast.classList.add("hidden"), 3200)
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  })
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.error || `Erro ${response.status}`)
  }
  return data
}

function showLogin() {
  els.loginView.classList.remove("hidden")
  els.appView.classList.add("hidden")
}

function showApp(name) {
  els.userName.textContent = name || "Sessao ativa"
  els.loginView.classList.add("hidden")
  els.appView.classList.remove("hidden")
}

function optionList(select, values) {
  select.innerHTML = values.map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join("")
}

function optionListRows(select, rows, valueKey, labelFn) {
  select.innerHTML = rows
    .map((row) => {
      const value = row[valueKey]
      const label = labelFn ? labelFn(row) : value
      return `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`
    })
    .join("")
}

function selectedValues(select) {
  return Array.from(select.selectedOptions).map((option) => option.value)
}

function buildQuery() {
  const params = new URLSearchParams()
  params.set("preset", state.preset)
  if (state.preset === "YEAR" && state.year) params.set("year", state.year)
  if (state.preset === "CUSTOM") {
    if (state.startDate) params.set("start", state.startDate)
    if (state.endDate) params.set("end", state.endDate)
  }
  if (state.categorias.length) params.set("categorias", state.categorias.join(","))
  if (state.subcategorias.length) params.set("subcategorias", state.subcategorias.join(","))
  if (state.fontes.length) params.set("fontes", state.fontes.join(","))
  if (state.excludeSundays) params.set("exclude_sundays", "1")
  return params.toString()
}

async function loadMeta() {
  state.meta = await api("/api/meta")
  optionList(els.yearSelect, state.meta.anos || [])
  optionList(els.categorySelect, state.meta.categorias)
  optionList(els.subcategorySelect, state.meta.subcategorias)
  optionList(els.sourceSelect, state.meta.fontes)
  const produtos = state.meta.produtos || []
  const refs = state.meta.cost_refs || []
  ;["#fichaProduto", "#compositeProduto", "#manualCostProduct", "#mappingPos"].forEach((selector) => {
    const node = document.querySelector(selector)
    if (node) optionList(node, produtos)
  })
  ;["#compositeIngredient", "#mappingCost"].forEach((selector) => {
    const node = document.querySelector(selector)
    if (node) optionListRows(node, refs, "Produto", (row) => `${row.Produto} · ${fmtMoney2(row.Custo)} · ${row.Tipo}`)
  })
  state.year = state.year || String((state.meta.anos || []).at(-1) || "")
  els.yearSelect.value = state.year
  state.startDate = state.startDate || state.meta.data_min
  state.endDate = state.endDate || state.meta.data_max
  els.startDate.min = state.meta.data_min
  els.startDate.max = state.meta.data_max
  els.endDate.min = state.meta.data_min
  els.endDate.max = state.meta.data_max
  els.startDate.value = state.startDate
  els.endDate.value = state.endDate
}

async function loadDashboard() {
  const data = await api(`/api/cockpit?${buildQuery()}`)
  state.dashboard = data
  renderDashboard(data)
}

function deltaText(value) {
  if (value === null || value === undefined) return ""
  const cls = value < 0 ? "negative" : ""
  const sign = value > 0 ? "+" : ""
  return `<div class="kpi-delta ${cls}">${sign}${fmtPercent(value)} vs período anterior</div>`
}

function card(label, value, delta, help) {
  return `
    <article class="kpi-card">
      <div class="kpi-label">${escapeHtml(label)}</div>
      <div class="kpi-value">${escapeHtml(value)}</div>
      ${deltaText(delta)}
      ${help ? `<div class="kpi-help">${escapeHtml(help)}</div>` : ""}
    </article>
  `
}

function decisionCard(label, value, help) {
  return `
    <article class="decision-card">
      <div class="kpi-label">${escapeHtml(label)}</div>
      <div class="kpi-value">${escapeHtml(value)}</div>
      <div class="kpi-help">${escapeHtml(help)}</div>
    </article>
  `
}

function miniMetric(label, value, help, tone = "") {
  return `
    <article class="mini-metric ${tone}">
      <span>${escapeHtml(label)}</span>
      <strong>${escapeHtml(value)}</strong>
      ${help ? `<small>${escapeHtml(help)}</small>` : ""}
    </article>
  `
}

function renderMiniGrid(id, cards) {
  const node = document.querySelector(`#${id}`)
  if (node) node.innerHTML = cards.join("")
}

function valueByType(value, type) {
  if (value === null || value === undefined || value === "") return "N/D"
  if (type === "money") return fmtMoney(value)
  if (type === "money2") return fmtMoney2(value)
  if (type === "percent") return fmtPercent(value)
  if (type === "number") return fmtNumber(value)
  if (type === "number1") return fmtNumber1(value)
  if (type === "bool") return value ? "Sim" : "Não"
  return String(value)
}

function renderTable(target, rows, columns, limit = 80) {
  const node = typeof target === "string" ? document.querySelector(`#${target}`) : target
  if (!node) return
  if (!rows || !rows.length) {
    node.innerHTML = `<div class="empty-state">Sem dados para o período selecionado.</div>`
    return
  }
  const shown = rows.slice(0, limit)
  node.innerHTML = `
    <table>
      <thead>
        <tr>${columns.map((col) => `<th>${escapeHtml(col.label)}</th>`).join("")}</tr>
      </thead>
      <tbody>
        ${shown.map((row) => `
          <tr>
            ${columns.map((col) => `<td>${escapeHtml(valueByType(row[col.key], col.type))}</td>`).join("")}
          </tr>
        `).join("")}
      </tbody>
    </table>
    ${rows.length > shown.length ? `<div class="table-caption">A mostrar ${shown.length} de ${rows.length} linhas.</div>` : ""}
  `
}

async function saveJson(path, payload, message = "Guardado") {
  await api(path, { method: "POST", body: JSON.stringify(payload) })
  showToast(message)
  await loadMeta()
  await loadDashboard()
}

function rowsToCsvText(rows, columns) {
  const header = columns.join(";")
  const lines = (rows || []).map((row) => columns.map((col) => String(row[col] ?? "").replaceAll(";", ",")).join(";"))
  return [header, ...lines].join("\n")
}

function csvTextToRows(text) {
  const lines = text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean)
  if (lines.length < 2) return []
  const header = lines[0].split(";").map((part) => part.trim())
  return lines.slice(1).map((line) => {
    const parts = line.split(";")
    const row = {}
    header.forEach((key, index) => {
      row[key] = parts[index] ?? ""
    })
    return row
  })
}

function renderIngredientList() {
  const node = document.querySelector("#ingredientList")
  if (!node) return
  if (!state.compositeIngredients.length) {
    node.innerHTML = `<div class="empty-state">Sem ingredientes adicionados.</div>`
    return
  }
  node.innerHTML = state.compositeIngredients.map((item, index) => `
    <div class="ingredient-chip">
      <span>${escapeHtml(item.Ingrediente)} · ${fmtNumber1(item.Qtd)} x ${fmtMoney2(item.Custo_Unit)} = ${fmtMoney2(item.Custo_Total)}</span>
      <button type="button" data-remove-ingredient="${index}">Remover</button>
    </div>
  `).join("")
}

function renderEditableFichas(rows) {
  const node = document.querySelector("#fichasTable")
  if (!node) return
  if (!rows || !rows.length) {
    node.innerHTML = `<div class="empty-state">Sem fichas técnicas configuradas.</div>`
    return
  }
  node.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Produto</th><th>Preço compra</th><th>Qtd compra</th><th>Dose</th><th>Custo dose</th><th></th>
        </tr>
      </thead>
      <tbody>
        ${rows.map((row) => `
          <tr>
            <td>${escapeHtml(row.Produto_POS)}</td>
            <td>${fmtMoney2(row.Preco_Compra)}</td>
            <td>${fmtNumber1(row.Qtd_Compra)} ${escapeHtml(row.Unidade_Compra)}</td>
            <td>${fmtNumber1(row.Qtd_Dose)} ${escapeHtml(row.Unidade_Dose)}</td>
            <td>${fmtMoney2(row.Custo_Dose)}</td>
            <td><button class="row-action" data-delete-ficha="${escapeHtml(row.Produto_POS)}">Apagar</button></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `
}

function fillFichaForm(produto = null) {
  const rows = state.dashboard?.operation?.fichas?.rows || []
  const selected = produto || document.querySelector("#fichaProduto")?.value
  const row = rows.find((item) => item.Produto_POS === selected)
  if (!row) {
    document.querySelector("#fichaPreco").value = ""
    document.querySelector("#fichaQtdCompra").value = ""
    document.querySelector("#fichaUnidadeCompra").value = "Unidade"
    document.querySelector("#fichaQtdDose").value = ""
    document.querySelector("#fichaUnidadeDose").value = "Unidade"
    return
  }
  document.querySelector("#fichaPreco").value = row.Preco_Compra ?? ""
  document.querySelector("#fichaQtdCompra").value = row.Qtd_Compra ?? ""
  document.querySelector("#fichaUnidadeCompra").value = row.Unidade_Compra || "Unidade"
  document.querySelector("#fichaQtdDose").value = row.Qtd_Dose ?? ""
  document.querySelector("#fichaUnidadeDose").value = row.Unidade_Dose || "Unidade"
}

function renderEditableMappings(rows) {
  const node = document.querySelector("#mappingTable")
  if (!node) return
  if (!rows || !rows.length) {
    node.innerHTML = `<div class="empty-state">Sem associações ativas.</div>`
    return
  }
  node.innerHTML = `
    <table>
      <thead><tr><th>Produto POS</th><th>Produto base</th><th>Mult.</th><th></th></tr></thead>
      <tbody>
        ${rows.map((row) => `
          <tr>
            <td>${escapeHtml(row.Produto_POS)}</td>
            <td>${escapeHtml(row.Produto_Custo)}</td>
            <td>${fmtNumber1(row.Multiplicador)}</td>
            <td><button class="row-action" data-delete-mapping="${escapeHtml(row.Produto_POS)}">Apagar</button></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `
}

function renderDashboard(data) {
  const a = data.atual
  els.periodLabel.textContent = `${data.period.start} a ${data.period.end} · ${data.counts.days} dias · ${fmtNumber(data.counts.filtered)} registos`
  els.statusLabel.textContent = data.status.label
  els.statusScore.textContent = `${data.status.score}/100`

  renderCockpit(data)
  renderCommercial(data.commercial || {})
  renderProfitability(data.profitability || {})
  renderOperation(data.operation || {})
  switchView(state.activeView, false)

  if (a.total <= 0) showToast("Sem vendas para os filtros selecionados")
}

function renderCockpit(data) {
  const a = data.atual
  const d = data.deltas
  const dec = data.decisao
  const op = data.operacionais
  const fornecedores = data.fornecedores

  els.recordsLabel.textContent = `${fmtNumber(data.counts.filtered)} registos`

  els.kpiGrid.innerHTML = [
    card("Vendas", fmtMoney(a.total), d.total, `${fmtNumber(a.qtd)} unidades`),
    card("Média diária", fmtMoney(a.media_diaria), d.media_diaria, `${a.dias_com_venda} dias com venda`),
    card("Ticket médio", fmtMoney(a.ticket), d.ticket, ""),
    card("Lucro bruto", fmtMoney(a.lucro_bruto), d.lucro_bruto, `margem ${fmtPercent(a.margem_bruta)}`),
    card("Lucro líquido", fmtMoney(a.lucro_liquido), d.lucro_liquido, `custos ops ${fmtMoney(a.custos_ops)}`),
  ].join("")

  let gapValue = "N/D"
  let gapHelp = "sem histórico mensal comparável"
  if (dec.objetivo_mensal > 0 && dec.gap_objetivo_mensal > 0) {
    gapValue = fmtMoney(dec.gap_objetivo_mensal)
    gapHelp = `para igualar ${dec.objetivo_mensal_label} (${fmtMoney(dec.objetivo_mensal)})`
  } else if (dec.objetivo_mensal > 0) {
    gapValue = "Batido"
    gapHelp = `${fmtMoney(Math.abs(dec.gap_objetivo_mensal))} acima de ${dec.objetivo_mensal_label}`
  }

  els.decisionGrid.innerHTML = [
    decisionCard("Margem líquida projetada", fmtPercent(dec.margem_liquida_projetada), `lucro mês ${fmtMoney(dec.lucro_liquido_projetado)}`),
    decisionCard("Gap objetivo mensal", gapValue, gapHelp),
    decisionCard("Venda/dia necessária", fmtMoney(dec.vendas_dia_util_necessarias), `${dec.dias_uteis_restantes} dias de venda restantes`),
    decisionCard("Margem em risco", fmtMoney(dec.vendas_margem_risco), `${fmtPercent(dec.pct_vendas_margem_risco)} vendas; impacto ${fmtMoney(dec.impacto_margem_risco)}`),
  ].join("")

  els.healthScore.textContent = data.status.score
  els.healthText.textContent = `/ 100 · ${data.status.label}`
  els.healthBar.style.width = `${data.status.score}%`
  els.healthFacts.innerHTML = `
    <div><dt>Concentração top 5</dt><dd>${fmtPercent(a.concentracao_top5)} das vendas</dd></div>
    <div><dt>Margem líquida</dt><dd>${fmtPercent(a.margem_liquida)}</dd></div>
    <div><dt>Cobertura break-even</dt><dd>${fmtPercent(op.cobertura_break_even)}</dd></div>
    <div><dt>Fornecedores</dt><dd>${fmtMoney((fornecedores.novadis_total || 0) + (fornecedores.delta_total || 0))}</dd></div>
  `

  els.priorityList.innerHTML = data.prioridades
    .map((item) => `
      <div class="priority ${escapeHtml(item.level)}">
        <p>${escapeHtml(item.text)}</p>
        <span>${escapeHtml(item.target)}</span>
      </div>
    `)
    .join("")

  els.topProducts.innerHTML = (data.charts.top_products || [])
    .map((row) => `
      <tr>
        <td>${escapeHtml(row.Produto)}</td>
        <td>${fmtMoney(row.Vendas)}</td>
        <td>${fmtPercent(row.Margem)}</td>
      </tr>
    `)
    .join("")
}

function renderCommercial(commercial) {
  const k = commercial.kpis || {}
  const p = commercial.performance || {}
  renderMiniGrid("commercialKpis", [
    card("Vendas", fmtMoney(k.total_vendas), null, `${fmtNumber(k.transacoes)} registos`),
    card("Média diária", fmtMoney(k.media_diaria), null, "ritmo do período"),
    card("Ticket médio", fmtMoney(k.ticket_medio), null, "valor por unidade"),
    card("Projeção 30 dias", fmtMoney(k.projecao_30d), null, "com ritmo atual"),
    card("Diversificação HHI", fmtNumber(k.hhi), null, `${fmtNumber(k.produtos_80)} produtos fazem 80%`),
  ])

  renderMiniGrid("performanceGrid", [
    miniMetric("Semana atual", fmtMoney(p.semana_atual), `${deltaLabel(p.var_semana_vs_anterior)} vs semana anterior`),
    miniMetric("Mes em curso", fmtMoney(p.mes_atual), `${deltaLabel(p.var_mes_vs_anterior)} vs mês anterior MTD`),
    miniMetric("Mesmo mês LY", fmtMoney(p.smly), `${deltaLabel(p.var_mes_vs_ano_passado)} vs SMLY`),
    miniMetric("Ano YTD", fmtMoney(p.ano_atual_ytd), `${deltaLabel(p.var_ano_vs_ano_anterior)} vs YTD anterior`),
    miniMetric("Catálogo 80/20", `${fmtPercent(k.pct_catalogo_80)}`, `${fmtNumber(k.produtos)} produtos agrupados`),
  ])

  renderTable("categoryTable", commercial.categories || [], [
    { key: "Categoria", label: "Categoria" },
    { key: "Vendas", label: "Vendas", type: "money" },
    { key: "Share", label: "Share", type: "percent" },
    { key: "Margem_Bruta_Pct", label: "Margem", type: "percent" },
    { key: "Delta_Pct", label: "Vs anterior", type: "percent" },
  ])
  renderTable("detailsTable", commercial.details || [], [
    { key: "Data", label: "Data" },
    { key: "Produto", label: "Produto" },
    { key: "Categoria", label: "Categoria" },
    { key: "Fonte", label: "Fonte" },
    { key: "Qtd", label: "Qtd", type: "number1" },
    { key: "Valor", label: "Vendas", type: "money" },
    { key: "Margem_Bruta_Pct", label: "Margem", type: "percent" },
  ], 160)
}

function deltaLabel(value) {
  if (value === null || value === undefined) return "N/D"
  const sign = value > 0 ? "+" : ""
  return `${sign}${fmtPercent(value)}`
}

function renderProfitability(profitability) {
  const m = profitability.metrics || {}
  renderMiniGrid("profitKpis", [
    card("Receita", fmtMoney(m.receita_total), null, "vendas filtradas"),
    card("COGS", fmtMoney(m.cogs_total), null, "produtos e comissões"),
    card("Lucro bruto", fmtMoney(m.lucro_bruto), null, `margem ${fmtPercent(m.margem_bruta_pct)}`),
    card("Lucro líquido", fmtMoney(m.lucro_liquido), null, `margem ${fmtPercent(m.margem_liquida_pct)}`),
    card("Custo total", fmtMoney(m.custo_total), null, `fonte ${m.fonte_custos_operacionais || "N/D"}`),
  ])

  const source = document.querySelector("#costSource")
  if (source) {
    const fonte = m.fonte_custos_operacionais || "N/D"
    source.textContent = fonte === "REAL"
      ? "Custos operacionais reais do Despesify aplicados neste período."
      : "Custos operacionais estimados ou híbridos aplicados neste período."
  }

  const be = profitability.break_even || {}
  renderMiniGrid("breakEvenGrid", [
    miniMetric("Custos fixos mensais", fmtMoney(be.custos_fixos_mensais), be.fonte_custos || ""),
    miniMetric("Break-even mensal", fmtMoney(be.vendas_break_even_mensal), "vendas necessárias"),
    miniMetric("Break-even diário", fmtMoney(be.vendas_break_even_diaria), "ritmo mínimo"),
    miniMetric("Vendas atuais/dia", fmtMoney(be.vendas_atuais_diarias), "média filtrada"),
    miniMetric("Margem segurança", fmtPercent(be.margem_seguranca_pct), "acima/abaixo do ponto equilíbrio"),
  ])

  renderTable("marginAlertTable", profitability.margin_alerts || [], [
    { key: "Produto", label: "Produto" },
    { key: "Categoria", label: "Categoria" },
    { key: "Vendas", label: "Vendas", type: "money" },
    { key: "Margem_Bruta_Pct", label: "Margem", type: "percent" },
    { key: "Margem_Objetivo", label: "Objetivo", type: "percent" },
    { key: "Gap_Pontos", label: "Gap", type: "percent" },
  ])

  renderTable("realMarginTable", profitability.real_margins?.details || [], [
    { key: "Produto", label: "Produto" },
    { key: "Categoria", label: "Categoria" },
    { key: "Qtd", label: "Qtd", type: "number1" },
    { key: "PVP_Medio", label: "PVP", type: "money2" },
    { key: "Custo_Final", label: "Custo", type: "money2" },
    { key: "Lucro_Bruto_Real", label: "Lucro", type: "money" },
    { key: "Margem_Real_Pct", label: "Margem", type: "percent" },
  ], 160)

  renderTable("opCostsTable", profitability.op_costs || [], [
    { key: "Categoria", label: "Categoria" },
    { key: "Total_Periodo", label: "Total", type: "money" },
    { key: "Percentual", label: "Peso", type: "percent" },
    { key: "Fonte", label: "Fonte" },
    { key: "Detalhes", label: "Detalhes" },
  ])

  renderTable("expensesTable", profitability.expenses || [], [
    { key: "Data", label: "Data" },
    { key: "Descrição", label: "Fornecedor" },
    { key: "Categoria_Dashboard", label: "Categoria" },
    { key: "Valor_Total", label: "Total", type: "money2" },
    { key: "IVA", label: "IVA", type: "money2" },
    { key: "NIF_Fornecedor", label: "NIF" },
  ], 100)

  renderTable("missingCostsTable", profitability.real_margins?.missing || [], [
    { key: "Produto", label: "Produto" },
    { key: "Categoria", label: "Categoria" },
    { key: "Qtd", label: "Qtd", type: "number1" },
    { key: "Valor", label: "Vendas", type: "money" },
    { key: "PVP_Medio", label: "PVP médio", type: "money2" },
  ], 120)

  const missing = profitability.real_margins?.missing || []
  const manualProduct = document.querySelector("#manualCostProduct")
  if (manualProduct) optionList(manualProduct, (missing.length ? missing.map((row) => row.Produto) : state.meta?.produtos || []))
  const mappingPos = document.querySelector("#mappingPos")
  if (mappingPos) optionList(mappingPos, (missing.length ? missing.map((row) => row.Produto) : state.meta?.produtos || []))
  const opEditor = document.querySelector("#opCostsEditor")
  if (opEditor) {
    opEditor.value = rowsToCsvText(profitability.editable?.op_costs_csv || [], ["Categoria", "Subcategoria", "Valor_Mensal", "Tipo", "Notas"])
  }
  renderEditableMappings(profitability.editable?.product_mappings || [])
}

function renderOperation(operation) {
  const sc = operation.santa_casa?.summary || {}
  const fc = operation.forecast?.summary || {}
  const nv = operation.novadis?.summary || {}
  const dl = operation.delta?.summary || {}
  const ft = operation.fichas?.summary || {}

  renderMiniGrid("operationKpis", [
    card("Santa Casa", fmtMoney(sc.vendas), null, `${fmtNumber(sc.jogos)} jogos · prémios ${fmtMoney(sc.premios)}`),
    card("Forecast mensal", fmtMoney(fc.encomenda_mensal), null, `${fmtNumber(fc.produtos)} produtos`),
    card("Novadis", fmtMoney(nv.total), null, `${fmtNumber(nv.encomendas)} encomendas`),
    card("Delta", fmtMoney(dl.total), null, `${fmtNumber(dl.faturas)} faturas`),
    card("Fichas técnicas", fmtNumber(ft.total), null, `custo dose médio ${fmtMoney2(ft.custo_medio_dose)}`),
  ])

  renderTable("santaTable", operation.santa_casa?.products || [], [
    { key: "Produto", label: "Jogo/Produto" },
    { key: "Vendas", label: "Vendas", type: "money" },
    { key: "Lucro_Bruto", label: "Remun.", type: "money" },
    { key: "Premios", label: "Prémios", type: "money" },
    { key: "Share", label: "Share", type: "percent" },
  ], 12)

  renderTable("forecastTable", operation.forecast?.rows || [], [
    { key: "Produto", label: "Produto" },
    { key: "Categoria", label: "Categoria" },
    { key: "Qtd_Mensal", label: "Qtd mês", type: "number1" },
    { key: "Valor_Encomenda_Mensal", label: "Valor mês", type: "money" },
    { key: "Tendencia_Direcao", label: "Tendência" },
  ], 14)

  renderTable("novadisTable", operation.novadis?.rows || [], [
    { key: "data", label: "Data" },
    { key: "numero_pedido", label: "Pedido" },
    { key: "produto_novadis", label: "Produto" },
    { key: "custo_total", label: "Total", type: "money2" },
    { key: "unidades_vendaveis", label: "Unid.", type: "number" },
  ], 12)

  renderTable("deltaTable", operation.delta?.rows || [], [
    { key: "Data_Fatura", label: "Data" },
    { key: "Numero_Fatura", label: "Fatura" },
    { key: "Total_EUR", label: "Total", type: "money2" },
    { key: "Arquivo", label: "Arquivo" },
  ], 12)

  renderMiniGrid("fichasKpis", [
    miniMetric("Total fichas", fmtNumber(ft.total), "produtos com dose configurada"),
    miniMetric("Custo médio dose", fmtMoney2(ft.custo_medio_dose), "média simples"),
    miniMetric("Custo referência", fmtMoney(ft.custo_total_referencia), "soma das doses"),
  ])

  const novadisProducts = Array.from(new Set((operation.novadis?.rows || []).map((row) => row.produto_novadis).filter(Boolean))).sort()
  const novadisSelect = document.querySelector("#novadisUnitProduct")
  if (novadisSelect) optionList(novadisSelect, novadisProducts)

  renderEditableFichas(operation.fichas?.rows || [])
  fillFichaForm()
}

function plotConfig() {
  return { responsive: true, displayModeBar: false }
}

function baseLayout(height, extra = {}) {
  return {
    height,
    margin: { l: 54, r: 20, t: 12, b: 44 },
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "#0b111b",
    font: { color: "#edfaff", family: "Inter, sans-serif" },
    xaxis: { gridcolor: "#1d2b3a", zerolinecolor: "#24394d", tickfont: { color: "#8fa0b8" } },
    yaxis: { gridcolor: "#1d2b3a", zerolinecolor: "#24394d", tickfont: { color: "#8fa0b8" } },
    legend: { orientation: "h", y: 1.16, x: 0, font: { color: "#edfaff" } },
    ...extra,
  }
}

function visibleChart(id) {
  const node = document.querySelector(`#${id}`)
  if (!node || node.closest(".hidden")) return null
  return node
}

function noPlot(id, text = "Sem dados") {
  const node = visibleChart(id)
  if (!node) return
  Plotly.react(node, [], baseLayout(300, {
    annotations: [{ text, x: 0.5, y: 0.5, xref: "paper", yref: "paper", showarrow: false, font: { color: "#8fa0b8" } }],
  }), plotConfig())
}

function plot(id, traces, layout) {
  const node = visibleChart(id)
  if (!node) return
  if (!traces.length) {
    noPlot(id)
    return
  }
  Plotly.react(node, traces, layout, plotConfig())
}

function renderChartsForView(view) {
  if (!state.dashboard) return
  if (view === "cockpit") renderCockpitCharts(state.dashboard)
  if (view === "sales") renderCommercialCharts(state.dashboard.commercial || {})
  if (view === "margin") renderProfitCharts(state.dashboard.profitability || {})
  if (view === "ops") renderOperationCharts(state.dashboard.operation || {})
  window.setTimeout(() => {
    document.querySelectorAll(".chart").forEach((node) => {
      if (!node.closest(".hidden")) Plotly.Plots.resize(node)
    })
  }, 60)
}

function renderCockpitCharts(data) {
  const daily = data.charts.daily || []
  plot("dailyChart", [
    {
      type: "bar",
      name: "Vendas",
      x: daily.map((d) => d.date),
      y: daily.map((d) => d.value),
      marker: { color: "#37f3ff", opacity: 0.62 },
    },
    {
      type: "scatter",
      mode: "lines",
      name: "Média 7d",
      x: daily.map((d) => d.date),
      y: daily.map((d) => d.ma7),
      line: { color: "#ff8a1f", width: 3 },
    },
  ], baseLayout(330))

  const mix = data.charts.mix || []
  const sourceTotals = new Map()
  mix.forEach((row) => sourceTotals.set(row.Fonte, (sourceTotals.get(row.Fonte) || 0) + Number(row.Valor || 0)))
  const sourceLabels = Array.from(sourceTotals.keys())
  const totalMix = Array.from(sourceTotals.values()).reduce((acc, value) => acc + value, 0)
  plot("mixChart", [
    {
      type: "treemap",
      labels: ["Total", ...sourceLabels, ...mix.map((row) => `${row.Fonte} · ${row.Categoria}`)],
      parents: ["", ...sourceLabels.map(() => "Total"), ...mix.map((row) => row.Fonte)],
      values: [totalMix, ...sourceLabels.map((source) => sourceTotals.get(source)), ...mix.map((row) => row.Valor)],
      branchvalues: "total",
      marker: { colorscale: [[0, "#111827"], [0.42, "#1d7385"], [0.72, "#37f3ff"], [1, "#7cff6b"]] },
      textfont: { color: "#edfaff" },
      textinfo: "label+value",
    },
  ], baseLayout(430, { margin: { l: 8, r: 8, t: 8, b: 8 } }))

  renderBar("upChart", data.charts.movers_up || [], "#7cff6b")
  renderBar("downChart", data.charts.movers_down || [], "#ff4d6d")
}

function renderBar(id, rows, color) {
  plot(id, [
    {
      type: "bar",
      orientation: "h",
      x: rows.map((row) => row.Diferença),
      y: rows.map((row) => row.Produto),
      marker: { color },
    },
  ], baseLayout(330, {
    margin: { l: 130, r: 18, t: 8, b: 38 },
    yaxis: { automargin: true, gridcolor: "#1d2b3a", zerolinecolor: "#24394d", tickfont: { color: "#8fa0b8" } },
  }))
}

function renderCommercialCharts(commercial) {
  const categories = commercial.categories || []
  const sources = commercial.sources || []
  const pareto = commercial.pareto || []
  const growth = commercial.categories_homologo || []
  const weekday = commercial.weekday || []
  const monthly = commercial.monthly || []

  plot("categoryChart", [{
    type: "bar",
    orientation: "h",
    x: categories.slice().reverse().map((row) => row.Vendas),
    y: categories.slice().reverse().map((row) => row.Categoria),
    marker: { color: "#37f3ff" },
  }], baseLayout(430, { margin: { l: 140, r: 18, t: 8, b: 38 }, yaxis: { automargin: true } }))

  plot("sourceChart", [{
    type: "pie",
    labels: sources.map((row) => row.Fonte),
    values: sources.map((row) => row.Vendas),
    hole: 0.58,
    marker: { colors: ["#37f3ff", "#7cff6b", "#ff8a1f", "#d96cff", "#ff4d6d"] },
  }], baseLayout(430, { margin: { l: 12, r: 12, t: 12, b: 12 }, showlegend: true }))

  plot("paretoChart", [
    {
      type: "bar",
      name: "Vendas",
      x: pareto.map((row, index) => index + 1),
      y: pareto.map((row) => row.Vendas),
      marker: { color: "#37f3ff", opacity: 0.7 },
    },
    {
      type: "scatter",
      name: "Acumulado",
      x: pareto.map((row, index) => index + 1),
      y: pareto.map((row) => row.Acumulado_Pct),
      yaxis: "y2",
      line: { color: "#ff8a1f", width: 3 },
    },
  ], baseLayout(430, {
    yaxis2: { overlaying: "y", side: "right", range: [0, 100], gridcolor: "rgba(0,0,0,0)", tickfont: { color: "#ff8a1f" } },
    shapes: [{ type: "line", xref: "paper", x0: 0, x1: 1, yref: "y2", y0: 80, y1: 80, line: { color: "#ff4d6d", dash: "dash" } }],
  }))

  plot("growthChart", [{
    type: "bar",
    x: growth.map((row) => row.Categoria),
    y: growth.map((row) => row.Delta_Homologo_Pct),
    marker: { color: growth.map((row) => Number(row.Delta_Homologo_Pct || 0) >= 0 ? "#7cff6b" : "#ff4d6d") },
  }], baseLayout(430))

  plot("weekdayChart", [{
    type: "bar",
    x: weekday.map((row) => row.Dia),
    y: weekday.map((row) => row.Valor),
    marker: { color: "#d96cff" },
  }], baseLayout(330))

  plot("monthlyChart", [{
    type: "scatter",
    mode: "lines+markers",
    x: monthly.map((row) => row.Mes_Ano),
    y: monthly.map((row) => row.Valor),
    line: { color: "#37f3ff", width: 3 },
    fill: "tozeroy",
    fillcolor: "rgba(55, 243, 255, 0.12)",
  }], baseLayout(330))
}

function renderProfitCharts(profitability) {
  const costs = profitability.cost_breakdown || []
  const categories = profitability.categories || []
  const be = profitability.break_even || {}
  const realLow = profitability.real_margins?.low || []

  plot("costsChart", [{
    type: "pie",
    labels: costs.map((row) => row.Tipo),
    values: costs.map((row) => row.Valor),
    hole: 0.56,
    marker: { colors: ["#37f3ff", "#ff8a1f", "#d96cff"] },
  }], baseLayout(430, { margin: { l: 12, r: 12, t: 12, b: 12 } }))

  plot("profitCategoryChart", [{
    type: "bar",
    x: categories.map((row) => row.Categoria),
    y: categories.map((row) => row.Margem_Bruta_Pct),
    marker: { color: categories.map((row) => Number(row.Diferenca_Objetivo || 0) >= 0 ? "#7cff6b" : "#ff4d6d") },
  }], baseLayout(430))

  const vendasBe = Number(be.vendas_break_even_mensal || 0)
  const margem = Number(be.margem_contribuicao_pct || 0)
  const custosFixos = Number(be.custos_fixos_mensais || 0)
  const maxSales = Math.max(vendasBe * 1.5, Number(be.vendas_atuais_diarias || 0) * 30 * 1.3, 1)
  const x = Array.from({ length: 24 }, (_, idx) => (maxSales / 23) * idx)
  plot("breakEvenChart", [
    {
      type: "scatter",
      mode: "lines",
      name: "Receita",
      x,
      y: x,
      line: { color: "#7cff6b", width: 3 },
    },
    {
      type: "scatter",
      mode: "lines",
      name: "Custos",
      x,
      y: x.map((value) => custosFixos + value * (1 - margem / 100)),
      line: { color: "#ff4d6d", width: 3 },
    },
    {
      type: "scatter",
      mode: "markers",
      name: "Break-even",
      x: [vendasBe],
      y: [vendasBe],
      marker: { color: "#ff8a1f", size: 14, symbol: "diamond" },
    },
  ], baseLayout(430))

  plot("realMarginChart", [{
    type: "bar",
    orientation: "h",
    x: realLow.slice().reverse().map((row) => row.Margem_Real_Pct),
    y: realLow.slice().reverse().map((row) => row.Produto),
    marker: { color: "#ff4d6d" },
  }], baseLayout(430, { margin: { l: 150, r: 18, t: 8, b: 38 }, yaxis: { automargin: true } }))
}

function renderOperationCharts(operation) {
  const santaWeekly = operation.santa_casa?.weekly || []
  const forecast = operation.forecast?.rows || []
  const novadis = operation.novadis?.monthly || []
  const delta = operation.delta?.monthly || []

  plot("santaChart", [{
    type: "scatter",
    mode: "lines+markers",
    x: santaWeekly.map((row) => row.Semana),
    y: santaWeekly.map((row) => row.Valor),
    line: { color: "#d96cff", width: 3 },
    fill: "tozeroy",
    fillcolor: "rgba(217, 108, 255, 0.12)",
  }], baseLayout(430))

  const topForecast = forecast.slice(0, 20).reverse()
  plot("forecastChart", [{
    type: "bar",
    orientation: "h",
    x: topForecast.map((row) => row.Valor_Encomenda_Mensal),
    y: topForecast.map((row) => row.Produto),
    marker: { color: topForecast.map((row) => row.Tendencia_Direcao === "crescimento" ? "#7cff6b" : row.Tendencia_Direcao === "queda" ? "#ff4d6d" : "#37f3ff") },
  }], baseLayout(430, { margin: { l: 150, r: 18, t: 8, b: 38 }, yaxis: { automargin: true } }))

  plot("novadisChart", [{
    type: "bar",
    x: novadis.map((row) => row.Mes),
    y: novadis.map((row) => row.custo_total),
    marker: { color: "#ff8a1f" },
  }], baseLayout(330))

  plot("deltaChart", [{
    type: "bar",
    x: delta.map((row) => row.Mes),
    y: delta.map((row) => row.Total_EUR),
    marker: { color: "#37f3ff" },
  }], baseLayout(330))
}

function switchView(view, scrollTop = true) {
  state.activeView = view
  document.querySelectorAll("[data-view-panel]").forEach((panel) => {
    panel.classList.toggle("hidden", panel.dataset.viewPanel !== view)
  })
  document.querySelectorAll(".nav-list button[data-view]").forEach((button) => {
    button.classList.toggle("active", button.dataset.view === view)
  })
  const meta = viewMeta[view] || viewMeta.cockpit
  els.viewEyebrow.textContent = meta.eyebrow
  els.viewTitle.textContent = meta.title
  if (scrollTop) document.querySelector(".workspace")?.scrollIntoView({ behavior: "smooth", block: "start" })
  renderChartsForView(view)
}

function resetFilters() {
  state.preset = "YTD"
  state.year = String((state.meta?.anos || []).at(-1) || "")
  state.startDate = state.meta?.data_min || ""
  state.endDate = state.meta?.data_max || ""
  state.categorias = []
  state.subcategorias = []
  state.fontes = []
  state.excludeSundays = false
  els.yearSelect.value = state.year
  els.startDate.value = state.startDate
  els.endDate.value = state.endDate
  els.categorySelect.selectedIndex = -1
  els.subcategorySelect.selectedIndex = -1
  els.sourceSelect.selectedIndex = -1
  els.excludeSundays.checked = false
  els.presetButtons.querySelectorAll("button").forEach((btn) => btn.classList.toggle("active", btn.dataset.preset === "YTD"))
}

function bindEvents() {
  els.loginForm.addEventListener("submit", async (event) => {
    event.preventDefault()
    els.loginError.textContent = ""
    try {
      const session = await api("/api/login", {
        method: "POST",
        body: JSON.stringify({ username: els.username.value, password: els.password.value }),
      })
      showApp(session.name)
      await loadMeta()
      await loadDashboard()
    } catch (error) {
      els.loginError.textContent = error.message
    }
  })

  els.logoutButton.addEventListener("click", async () => {
    await api("/api/logout", { method: "POST" })
    showLogin()
  })

  els.refreshButton.addEventListener("click", async () => {
    showToast("A atualizar dados...")
    await api("/api/refresh", { method: "POST" })
    await loadMeta()
    await loadDashboard()
    showToast("Dados atualizados")
  })

  els.resetButton.addEventListener("click", async () => {
    resetFilters()
    await loadDashboard()
  })

  els.presetButtons.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-preset]")
    if (!button) return
    state.preset = button.dataset.preset
    els.presetButtons.querySelectorAll("button").forEach((btn) => btn.classList.toggle("active", btn === button))
    await loadDashboard()
  })

  els.yearSelect.addEventListener("change", async () => {
    state.year = els.yearSelect.value
    state.preset = "YEAR"
    els.presetButtons.querySelectorAll("button").forEach((btn) => btn.classList.toggle("active", btn.dataset.preset === "YEAR"))
    await loadDashboard()
  })

  els.startDate.addEventListener("change", async () => {
    state.startDate = els.startDate.value
    state.preset = "CUSTOM"
    els.presetButtons.querySelectorAll("button").forEach((btn) => btn.classList.toggle("active", btn.dataset.preset === "CUSTOM"))
    await loadDashboard()
  })

  els.endDate.addEventListener("change", async () => {
    state.endDate = els.endDate.value
    state.preset = "CUSTOM"
    els.presetButtons.querySelectorAll("button").forEach((btn) => btn.classList.toggle("active", btn.dataset.preset === "CUSTOM"))
    await loadDashboard()
  })

  els.categorySelect.addEventListener("change", async () => {
    state.categorias = selectedValues(els.categorySelect)
    await loadDashboard()
  })

  els.subcategorySelect.addEventListener("change", async () => {
    state.subcategorias = selectedValues(els.subcategorySelect)
    await loadDashboard()
  })

  els.sourceSelect.addEventListener("change", async () => {
    state.fontes = selectedValues(els.sourceSelect)
    await loadDashboard()
  })

  els.excludeSundays.addEventListener("change", async () => {
    state.excludeSundays = els.excludeSundays.checked
    await loadDashboard()
  })

  document.querySelectorAll(".nav-list button[data-view]").forEach((button) => {
    button.addEventListener("click", () => switchView(button.dataset.view))
  })

  document.querySelector("#fichaForm")?.addEventListener("submit", async (event) => {
    event.preventDefault()
    await saveJson("/api/fichas/save", {
      Produto_POS: document.querySelector("#fichaProduto").value,
      Preco_Compra: document.querySelector("#fichaPreco").value,
      Qtd_Compra: document.querySelector("#fichaQtdCompra").value,
      Unidade_Compra: document.querySelector("#fichaUnidadeCompra").value,
      Qtd_Dose: document.querySelector("#fichaQtdDose").value,
      Unidade_Dose: document.querySelector("#fichaUnidadeDose").value,
    }, "Ficha técnica guardada")
  })

  document.querySelector("#fichaProduto")?.addEventListener("change", () => fillFichaForm())

  document.querySelector("#addIngredientButton")?.addEventListener("click", () => {
    const ingredient = document.querySelector("#compositeIngredient").value
    const qty = Number(document.querySelector("#compositeQtd").value || 0)
    const ref = (state.meta?.cost_refs || []).find((row) => row.Produto === ingredient)
    if (!ingredient || qty <= 0 || !ref) {
      showToast("Escolhe um ingrediente e quantidade válida")
      return
    }
    state.compositeIngredients.push({
      Ingrediente: ingredient,
      Qtd: qty,
      Custo_Unit: Number(ref.Custo || 0),
      Custo_Total: qty * Number(ref.Custo || 0),
    })
    renderIngredientList()
  })

  document.querySelector("#ingredientList")?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-remove-ingredient]")
    if (!button) return
    state.compositeIngredients.splice(Number(button.dataset.removeIngredient), 1)
    renderIngredientList()
  })

  document.querySelector("#compositeForm")?.addEventListener("submit", async (event) => {
    event.preventDefault()
    await saveJson("/api/fichas/composite", {
      Produto_POS: document.querySelector("#compositeProduto").value,
      ingredientes: state.compositeIngredients,
    }, "Produto composto guardado")
    state.compositeIngredients = []
    renderIngredientList()
  })

  document.querySelector("#fichasTable")?.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-delete-ficha]")
    if (!button) return
    await saveJson("/api/fichas/delete", { Produto_POS: button.dataset.deleteFicha }, "Ficha apagada")
  })

  document.querySelector("#manualCostForm")?.addEventListener("submit", async (event) => {
    event.preventDefault()
    await saveJson("/api/margins/manual-cost/save", {
      Produto: document.querySelector("#manualCostProduct").value,
      Custo_Manual: document.querySelector("#manualCostValue").value,
    }, "Custo manual guardado")
    document.querySelector("#manualCostValue").value = ""
  })

  document.querySelector("#mappingForm")?.addEventListener("submit", async (event) => {
    event.preventDefault()
    await saveJson("/api/margins/mapping/save", {
      Produto_POS: document.querySelector("#mappingPos").value,
      Produto_Custo: document.querySelector("#mappingCost").value,
      Multiplicador: document.querySelector("#mappingMultiplier").value,
    }, "Associação guardada")
  })

  document.querySelector("#mappingTable")?.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-delete-mapping]")
    if (!button) return
    await saveJson("/api/margins/mapping/delete", { Produto_POS: button.dataset.deleteMapping }, "Associação apagada")
  })

  document.querySelector("#saveOpCostsButton")?.addEventListener("click", async () => {
    const rows = csvTextToRows(document.querySelector("#opCostsEditor").value)
    await saveJson("/api/custos-operacionais/save", { rows }, "Custos operacionais guardados")
  })

  document.querySelector("#novadisUnitForm")?.addEventListener("submit", async (event) => {
    event.preventDefault()
    await saveJson("/api/novadis/unit-map/save", {
      produto_novadis: document.querySelector("#novadisUnitProduct").value,
      unidades_por_caixa: document.querySelector("#novadisUnitValue").value,
    }, "Unidades Novadis guardadas")
    document.querySelector("#novadisUnitValue").value = ""
  })

  window.addEventListener("resize", () => renderChartsForView(state.activeView))
}

async function boot() {
  bindEvents()
  const session = await api("/api/session")
  if (!session.authenticated) {
    showLogin()
    return
  }
  showApp(session.name)
  await loadMeta()
  await loadDashboard()
}

boot().catch((error) => {
  console.error(error)
  showToast(error.message)
  showLogin()
})
