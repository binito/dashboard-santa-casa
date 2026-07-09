"""Standalone web dashboard for Cafe Martins.

This server intentionally avoids Streamlit. It serves a static dashboard UI and a
small JSON API backed by the existing dashboard data loaders.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import mimetypes
import os
import secrets
import time
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import bcrypt
import pandas as pd
import yaml

ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
CONFIG_PATH = ROOT_DIR / "config.yaml"
CACHE_TTL_SECONDS = int(os.getenv("CM_WEB_CACHE_TTL", "600"))
SESSION_COOKIE = "cm_dashboard_session"

import sys

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data_loader_v9 import DataLoaderV9  # noqa: E402


DATA_CACHE: dict[str, Any] = {
    "loaded_at": 0.0,
    "df": None,
    "loader": None,
    "cost_manager": None,
}
SESSIONS: dict[str, dict[str, Any]] = {}
FICHAS_PATH = ROOT_DIR / "fichas_tecnicas.csv"
OP_COSTS_PATH = ROOT_DIR / "dados_custos" / "custos_operacionais.csv"
MARGIN_MANUAL_COSTS_PATH = ROOT_DIR / "custos_margens_reais.csv"
PRODUCT_MAPPING_PATH = ROOT_DIR / "mapeamento_produtos.csv"
NOVADIS_UNIT_MAPPING_PATH = ROOT_DIR / "mapeamento_unidades_novadis.csv"


CSV_SCHEMAS: dict[Path, list[str]] = {
    FICHAS_PATH: [
        "Produto_POS",
        "Preco_Compra",
        "Qtd_Compra",
        "Unidade_Compra",
        "Qtd_Dose",
        "Unidade_Dose",
        "Custo_Dose",
    ],
    OP_COSTS_PATH: ["Categoria", "Subcategoria", "Valor_Mensal", "Tipo", "Notas"],
    MARGIN_MANUAL_COSTS_PATH: ["Produto", "Custo_Manual"],
    PRODUCT_MAPPING_PATH: ["Produto_POS", "Produto_Custo", "Multiplicador"],
    NOVADIS_UNIT_MAPPING_PATH: ["produto_novadis", "unidades_por_caixa"],
}


def json_default(value: Any) -> Any:
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if hasattr(value, "item"):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def read_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_data(force: bool = False) -> tuple[pd.DataFrame, DataLoaderV9, Any]:
    now = time.time()
    if (
        not force
        and DATA_CACHE["df"] is not None
        and (now - float(DATA_CACHE["loaded_at"])) < CACHE_TTL_SECONDS
    ):
        return DATA_CACHE["df"], DATA_CACHE["loader"], DATA_CACHE["cost_manager"]

    loader = DataLoaderV9()
    df = loader.carregar_tudo_integrado_com_custos()
    if df.empty:
        raise RuntimeError("Sem dados carregados do DataLoaderV9")

    df = df.copy()
    df["Data"] = pd.to_datetime(df["Data"]).dt.normalize()

    DATA_CACHE.update(
        {
            "loaded_at": now,
            "df": df,
            "loader": loader,
            "cost_manager": loader.cost_manager,
        }
    )
    return df, loader, loader.cost_manager


def sign_session(token: str) -> str:
    cfg = read_config()
    key = str(cfg.get("cookie", {}).get("key", "dashboard-web")).encode("utf-8")
    signature = hmac.new(key, token.encode("utf-8"), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")


def make_session_cookie(token: str) -> str:
    return f"{token}.{sign_session(token)}"


def verify_session_cookie(cookie_value: str | None) -> dict[str, Any] | None:
    if not cookie_value or "." not in cookie_value:
        return None
    token, signature = cookie_value.rsplit(".", 1)
    if not hmac.compare_digest(signature, sign_session(token)):
        return None
    session = SESSIONS.get(token)
    if not session:
        return None
    if session["expires_at"] < time.time():
        SESSIONS.pop(token, None)
        return None
    return session


def authenticate(username: str, password: str) -> dict[str, str] | None:
    cfg = read_config()
    users = cfg.get("credentials", {}).get("usernames", {})
    user = users.get(username)
    if not user:
        return None
    password_hash = str(user.get("password", "")).encode("utf-8")
    if not bcrypt.checkpw(password.encode("utf-8"), password_hash):
        return None
    return {"username": username, "name": str(user.get("name", username))}


def periodo_anterior(data_inicio: pd.Timestamp, data_fim: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp]:
    dias = (data_fim - data_inicio).days + 1
    fim_anterior = data_inicio - pd.Timedelta(days=1)
    inicio_anterior = fim_anterior - pd.Timedelta(days=dias - 1)
    return inicio_anterior.normalize(), fim_anterior.normalize()


def produto_executivo(nome_produto: Any) -> str:
    nome = str(nome_produto or "").strip()
    nome_lower = nome.lower()
    if nome_lower.startswith("raspadinha"):
        return "Raspadinha"
    if "euromilhões" in nome_lower or "euromilhoes" in nome_lower:
        return "Euromilhões"
    if nome_lower.startswith("lotaria instantânea") or nome_lower.startswith("lotaria instantanea"):
        return "Lotaria Instantânea"
    return nome


def parse_list(params: dict[str, list[str]], key: str) -> list[str]:
    raw = params.get(key, [""])[0]
    return [item for item in raw.split(",") if item]


def resolve_period(params: dict[str, list[str]], df: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp, str]:
    data_min = pd.Timestamp(df["Data"].min()).normalize()
    data_max = pd.Timestamp(df["Data"].max()).normalize()
    preset = params.get("preset", ["YTD"])[0]

    if preset == "MTD":
        inicio = data_max.replace(day=1)
        fim = data_max
    elif preset == "30D":
        inicio = data_max - pd.Timedelta(days=29)
        fim = data_max
    elif preset == "PREV_MONTH":
        ref = data_max.replace(day=1) - pd.Timedelta(days=1)
        inicio = ref.replace(day=1)
        fim = ref
    elif preset == "YEAR":
        try:
            ano = int(params.get("year", [str(data_max.year)])[0])
        except ValueError:
            ano = data_max.year
        df_ano = df[df["Data"].dt.year == ano]
        if df_ano.empty:
            inicio = pd.Timestamp(year=data_max.year, month=1, day=1)
            fim = data_max
        else:
            inicio = pd.Timestamp(year=ano, month=1, day=1)
            fim = pd.Timestamp(df_ano["Data"].max()).normalize()
    elif preset == "ALL":
        inicio = data_min
        fim = data_max
    elif preset == "CUSTOM":
        inicio = pd.Timestamp(params.get("start", [data_min.date().isoformat()])[0])
        fim = pd.Timestamp(params.get("end", [data_max.date().isoformat()])[0])
    else:
        preset = "YTD"
        inicio = pd.Timestamp(year=data_max.year, month=1, day=1)
        fim = data_max

    inicio = max(inicio.normalize(), data_min)
    fim = min(fim.normalize(), data_max)
    if inicio > fim:
        inicio = fim
    return inicio, fim, preset


def filter_df(
    df: pd.DataFrame,
    data_inicio: pd.Timestamp,
    data_fim: pd.Timestamp,
    categorias: list[str],
    fontes: list[str],
    subcategorias: list[str],
    excluir_domingos: bool,
) -> pd.DataFrame:
    mask = (df["Data"] >= data_inicio) & (df["Data"] <= data_fim)
    if categorias and "Categoria" in df.columns:
        mask &= df["Categoria"].isin(categorias)
    if fontes and "Fonte" in df.columns:
        mask &= df["Fonte"].isin(fontes)
    if subcategorias and "Subcategoria" in df.columns:
        mask &= df["Subcategoria"].fillna("").astype(str).isin(subcategorias)
    if excluir_domingos:
        mask &= df["Data"].dt.dayofweek < 6
    return df[mask].copy()


def safe_sum(df: pd.DataFrame, column: str) -> float:
    return float(df[column].sum()) if column in df.columns and not df.empty else 0.0


def read_csv_schema(path: Path) -> pd.DataFrame:
    columns = CSV_SCHEMAS[path]
    if path.exists():
        df = pd.read_csv(path)
        for col in columns:
            if col not in df.columns:
                df[col] = pd.NA
        return df[columns].copy()
    return pd.DataFrame(columns=columns)


def write_csv_atomic(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = CSV_SCHEMAS.get(path, list(df.columns))
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            out[col] = pd.NA
    out = out[columns]
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    out.to_csv(tmp_path, index=False)
    tmp_path.replace(path)


def body_str(body: dict[str, Any], key: str, default: str = "") -> str:
    return str(body.get(key, default) or "").strip()


def body_float(body: dict[str, Any], key: str, default: float = 0.0) -> float:
    value = body.get(key, default)
    if value in ("", None):
        return default
    return float(value)


def reset_data_cache() -> None:
    DATA_CACHE.update({"loaded_at": 0.0, "df": None, "loader": None, "cost_manager": None})


def upsert_by_key(path: Path, row: dict[str, Any], key: str) -> pd.DataFrame:
    df = read_csv_schema(path)
    key_value = str(row[key])
    if not df.empty and key in df.columns:
        df = df[df[key].astype(str) != key_value]
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    write_csv_atomic(path, df)
    return df


def delete_by_key(path: Path, key: str, value: str) -> pd.DataFrame:
    df = read_csv_schema(path)
    if not df.empty and key in df.columns:
        df = df[df[key].astype(str) != str(value)]
    write_csv_atomic(path, df)
    return df


def clean_value(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat() if value.time().isoformat() == "00:00:00" else value.isoformat()
    if hasattr(value, "item"):
        value = value.item()
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, float) and (value == float("inf") or value == float("-inf")):
        return None
    return value


def table_records(df: pd.DataFrame, limit: int | None = None) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []
    out = df.copy()
    if limit is not None:
        out = out.head(limit)
    out = out.replace([float("inf"), float("-inf")], pd.NA)
    for col in out.columns:
        if pd.api.types.is_datetime64_any_dtype(out[col]):
            out[col] = out[col].dt.strftime("%Y-%m-%d")
    return [{str(key): clean_value(value) for key, value in row.items()} for row in out.to_dict(orient="records")]


def first_existing(columns: list[str], candidates: list[str]) -> str | None:
    available = set(columns)
    return next((candidate for candidate in candidates if candidate in available), None)


def group_sales(df: pd.DataFrame, by: str, top: int | None = None) -> pd.DataFrame:
    if df.empty or by not in df.columns:
        return pd.DataFrame(columns=[by, "Vendas", "Qtd", "Registos", "Lucro_Bruto", "Margem_Bruta_Pct", "Ticket", "Share"])

    agg: dict[str, tuple[str, str]] = {
        "Vendas": ("Valor", "sum"),
        "Registos": ("Valor", "count"),
    }
    if "Qtd" in df.columns:
        agg["Qtd"] = ("Qtd", "sum")
    if "Lucro_Bruto" in df.columns:
        agg["Lucro_Bruto"] = ("Lucro_Bruto", "sum")

    grouped = df.groupby(by, dropna=False).agg(**agg).reset_index()
    if "Qtd" not in grouped.columns:
        grouped["Qtd"] = grouped["Registos"]
    if "Lucro_Bruto" not in grouped.columns:
        grouped["Lucro_Bruto"] = grouped["Vendas"]
    total = float(grouped["Vendas"].sum())
    grouped["Margem_Bruta_Pct"] = grouped.apply(
        lambda row: (row["Lucro_Bruto"] / row["Vendas"] * 100) if row["Vendas"] else 0.0,
        axis=1,
    )
    grouped["Ticket"] = grouped.apply(lambda row: (row["Vendas"] / row["Qtd"]) if row["Qtd"] else 0.0, axis=1)
    grouped["Share"] = grouped["Vendas"] / total * 100 if total else 0.0
    grouped[by] = grouped[by].fillna("N/D").astype(str)
    grouped = grouped.sort_values("Vendas", ascending=False)
    return grouped.head(top) if top else grouped


def add_previous_delta(current: pd.DataFrame, previous: pd.DataFrame, key: str) -> pd.DataFrame:
    if current.empty:
        return current
    result = current.copy()
    if previous.empty or key not in previous.columns:
        result["Anterior"] = 0.0
        result["Delta_Pct"] = None
        return result
    previous_totals = previous.groupby(key)["Valor"].sum().rename("Anterior")
    result = result.merge(previous_totals, left_on=key, right_index=True, how="left")
    result["Anterior"] = result["Anterior"].fillna(0.0)
    result["Delta_Pct"] = result.apply(lambda row: delta_pct(float(row["Vendas"]), float(row["Anterior"])), axis=1)
    return result


def rows_for_columns(df: pd.DataFrame, columns: list[str], limit: int = 200) -> list[dict[str, Any]]:
    selected = [col for col in columns if col in df.columns]
    if not selected:
        return []
    return table_records(df[selected], limit=limit)


def resumo_periodo(df_periodo: pd.DataFrame, cost_manager: Any, data_inicio: pd.Timestamp, data_fim: pd.Timestamp) -> dict[str, Any]:
    if df_periodo.empty:
        return {
            "total": 0.0,
            "qtd": 0.0,
            "ticket": 0.0,
            "media_diaria": 0.0,
            "dias_com_venda": 0,
            "lucro_bruto": 0.0,
            "margem_bruta": 0.0,
            "custos_ops": 0.0,
            "lucro_liquido": 0.0,
            "margem_liquida": 0.0,
            "concentracao_top5": 0.0,
            "fonte_lider": "N/D",
            "categoria_lider": "N/D",
            "fonte_custos": "N/D",
        }

    total = safe_sum(df_periodo, "Valor")
    qtd = safe_sum(df_periodo, "Qtd")
    lucro_bruto = safe_sum(df_periodo, "Lucro_Bruto") or total
    dias_com_venda = int(df_periodo.groupby("Data")["Valor"].sum().gt(0).sum())
    dias_periodo = max(1, (data_fim - data_inicio).days + 1)
    custos_ops = 0.0
    fonte_custos = "N/D"
    try:
        custos_ops, fonte_custos, _ = cost_manager.get_custos_operacionais_periodo(
            data_inicio.to_pydatetime(),
            data_fim.to_pydatetime(),
        )
        custos_ops = float(custos_ops or 0.0)
    except Exception as exc:
        print(f"Aviso: custos operacionais indisponíveis: {exc}")

    top_prod = df_periodo.groupby("Produto")["Valor"].sum().sort_values(ascending=False)
    concentracao_top5 = (float(top_prod.head(5).sum()) / total * 100) if total else 0.0
    fonte_lider = str(df_periodo.groupby("Fonte")["Valor"].sum().idxmax()) if "Fonte" in df_periodo.columns else "N/D"
    categoria_lider = str(df_periodo.groupby("Categoria")["Valor"].sum().idxmax()) if "Categoria" in df_periodo.columns else "N/D"
    lucro_liquido = lucro_bruto - custos_ops

    return {
        "total": total,
        "qtd": qtd,
        "ticket": (total / qtd) if qtd else 0.0,
        "media_diaria": total / dias_periodo,
        "dias_com_venda": dias_com_venda,
        "lucro_bruto": lucro_bruto,
        "margem_bruta": (lucro_bruto / total * 100) if total else 0.0,
        "custos_ops": custos_ops,
        "lucro_liquido": lucro_liquido,
        "margem_liquida": (lucro_liquido / total * 100) if total else 0.0,
        "concentracao_top5": concentracao_top5,
        "fonte_lider": fonte_lider,
        "categoria_lider": categoria_lider,
        "fonte_custos": fonte_custos,
    }


def delta_pct(atual: float, anterior: float) -> float | None:
    if anterior == 0:
        return None
    return (atual - anterior) / anterior * 100


def calcular_operacionais(df_filtrado: pd.DataFrame, loader: DataLoaderV9, atual: dict[str, Any], data_inicio: pd.Timestamp, data_fim: pd.Timestamp) -> dict[str, Any]:
    if df_filtrado.empty:
        return {
            "projecao_mensal": 0.0,
            "break_even_diario": 0.0,
            "cobertura_break_even": 0.0,
            "volatilidade_diaria": 0.0,
            "linhas_abaixo_objetivo": 0,
            "dias_sem_venda": 0,
        }

    data_ref = pd.Timestamp(data_fim).normalize()
    inicio_mes = data_ref.replace(day=1)
    fim_mes = inicio_mes + pd.offsets.MonthEnd(0)
    dias_operacao_mes = max(1, sum(1 for dia in pd.date_range(inicio_mes, fim_mes, freq="D") if dia.weekday() < 6))
    projecao_mensal = atual["media_diaria"] * dias_operacao_mes

    try:
        break_even = loader.get_analise_break_even(df_filtrado)
        break_even_diario = float(break_even.get("vendas_break_even_diaria") or 0)
    except Exception as exc:
        print(f"Aviso: break-even indisponível: {exc}")
        break_even_diario = 0.0

    diario = df_filtrado.groupby("Data")["Valor"].sum()
    volatilidade = float(diario.std() / diario.mean() * 100) if len(diario) > 1 and diario.mean() else 0.0
    dias_periodo = pd.date_range(data_inicio, data_fim, freq="D")
    dias_sem_venda = max(0, len(dias_periodo) - int(diario.gt(0).sum()))
    abaixo = int(df_filtrado["Abaixo_Objetivo"].fillna(False).sum()) if "Abaixo_Objetivo" in df_filtrado.columns else 0

    return {
        "projecao_mensal": projecao_mensal,
        "break_even_diario": break_even_diario,
        "cobertura_break_even": (atual["media_diaria"] / break_even_diario * 100) if break_even_diario else 0.0,
        "volatilidade_diaria": volatilidade,
        "linhas_abaixo_objetivo": abaixo,
        "dias_sem_venda": dias_sem_venda,
    }


def calcular_decisao(df_filtrado: pd.DataFrame, df_completo: pd.DataFrame, cost_manager: Any, data_fim: pd.Timestamp) -> dict[str, Any]:
    vazio = {
        "margem_liquida_projetada": 0.0,
        "lucro_liquido_projetado": 0.0,
        "vendas_mes_projetadas": 0.0,
        "gap_objetivo_mensal": 0.0,
        "objetivo_mensal": 0.0,
        "objetivo_mensal_label": "mês anterior",
        "vendas_dia_util_necessarias": 0.0,
        "dias_uteis_restantes": 0,
        "vendas_margem_risco": 0.0,
        "pct_vendas_margem_risco": 0.0,
        "impacto_margem_risco": 0.0,
    }
    if df_filtrado.empty:
        return vazio

    data_ref = pd.Timestamp(data_fim).normalize()
    inicio_mes = data_ref.replace(day=1)
    fim_mes = inicio_mes + pd.offsets.MonthEnd(0)
    df_mes = df_filtrado[(df_filtrado["Data"] >= inicio_mes) & (df_filtrado["Data"] <= data_ref)].copy()
    if df_mes.empty:
        return vazio

    dias_decorridos = pd.date_range(inicio_mes, data_ref, freq="D")
    dias_operacao_decorridos = max(1, sum(1 for dia in dias_decorridos if dia.weekday() < 6))
    dias_operacao_mes = max(
        dias_operacao_decorridos,
        sum(1 for dia in pd.date_range(inicio_mes, fim_mes, freq="D") if dia.weekday() < 6),
    )
    dias_uteis_restantes = max(
        0,
        sum(1 for dia in pd.date_range(data_ref + pd.Timedelta(days=1), fim_mes, freq="D") if dia.weekday() < 6),
    )

    vendas_mtd = safe_sum(df_mes, "Valor")
    lucro_bruto_mtd = safe_sum(df_mes, "Lucro_Bruto") or vendas_mtd
    fator = dias_operacao_mes / dias_operacao_decorridos
    vendas_mes_projetadas = vendas_mtd * fator
    lucro_bruto_projetado = lucro_bruto_mtd * fator

    custos_ops_mes = 0.0
    try:
        custos_ops_mes, _, _ = cost_manager.get_custos_operacionais_periodo(
            inicio_mes.to_pydatetime(),
            fim_mes.to_pydatetime(),
        )
        custos_ops_mes = float(custos_ops_mes or 0)
    except Exception as exc:
        print(f"Aviso: custos mensais indisponíveis: {exc}")

    lucro_liquido_projetado = lucro_bruto_projetado - custos_ops_mes
    margem_liquida_projetada = (lucro_liquido_projetado / vendas_mes_projetadas * 100) if vendas_mes_projetadas else 0.0

    df_scope = df_completo.copy()
    for col in ("Categoria", "Fonte"):
        if col in df_filtrado.columns and col in df_scope.columns:
            values = set(df_filtrado[col].dropna().unique())
            if values:
                df_scope = df_scope[df_scope[col].isin(values)]
    if "Subcategoria" in df_filtrado.columns and "Subcategoria" in df_scope.columns:
        values = set(df_filtrado["Subcategoria"].dropna().astype(str).unique())
        if values:
            df_scope = df_scope[df_scope["Subcategoria"].fillna("").astype(str).isin(values)]

    fim_mes_anterior = inicio_mes - pd.Timedelta(days=1)
    inicio_mes_anterior = fim_mes_anterior.replace(day=1)
    df_mes_anterior = df_scope[(df_scope["Data"] >= inicio_mes_anterior) & (df_scope["Data"] <= fim_mes_anterior)]
    objetivo_mensal = safe_sum(df_mes_anterior, "Valor")
    objetivo_mensal_label = "mês anterior"
    if objetivo_mensal <= 0:
        inicio_ano_anterior = inicio_mes - pd.DateOffset(years=1)
        fim_ano_anterior = fim_mes - pd.DateOffset(years=1)
        df_mes_ano_anterior = df_scope[(df_scope["Data"] >= inicio_ano_anterior) & (df_scope["Data"] <= fim_ano_anterior)]
        objetivo_mensal = safe_sum(df_mes_ano_anterior, "Valor")
        objetivo_mensal_label = "mesmo mês ano passado"

    gap_objetivo_mensal = objetivo_mensal - vendas_mtd if objetivo_mensal > 0 else 0.0
    vendas_dia_util_necessarias = max(gap_objetivo_mensal, 0.0) / dias_uteis_restantes if dias_uteis_restantes else 0.0

    if "Abaixo_Objetivo" in df_filtrado.columns:
        df_risco = df_filtrado[df_filtrado["Abaixo_Objetivo"].fillna(False)].copy()
    elif {"Margem_Bruta_Pct", "Margem_Objetivo"}.issubset(df_filtrado.columns):
        df_risco = df_filtrado[df_filtrado["Margem_Bruta_Pct"] < df_filtrado["Margem_Objetivo"]].copy()
    else:
        df_risco = pd.DataFrame()
    vendas_margem_risco = safe_sum(df_risco, "Valor")
    impacto = 0.0
    if not df_risco.empty and {"Margem_Bruta_Pct", "Margem_Objetivo", "Valor"}.issubset(df_risco.columns):
        diff = (df_risco["Margem_Objetivo"] - df_risco["Margem_Bruta_Pct"]).clip(lower=0)
        impacto = float((df_risco["Valor"] * diff / 100).sum())
    vendas_periodo = safe_sum(df_filtrado, "Valor")

    return {
        "margem_liquida_projetada": margem_liquida_projetada,
        "lucro_liquido_projetado": lucro_liquido_projetado,
        "vendas_mes_projetadas": vendas_mes_projetadas,
        "gap_objetivo_mensal": gap_objetivo_mensal,
        "objetivo_mensal": objetivo_mensal,
        "objetivo_mensal_label": objetivo_mensal_label,
        "vendas_dia_util_necessarias": vendas_dia_util_necessarias,
        "dias_uteis_restantes": dias_uteis_restantes,
        "vendas_margem_risco": vendas_margem_risco,
        "pct_vendas_margem_risco": (vendas_margem_risco / vendas_periodo * 100) if vendas_periodo else 0.0,
        "impacto_margem_risco": impacto,
    }


def carregar_fornecedores(loader: DataLoaderV9, data_inicio: pd.Timestamp, data_fim: pd.Timestamp) -> dict[str, Any]:
    resultado = {
        "novadis_total": 0.0,
        "novadis_pedidos": 0,
        "delta_total": 0.0,
        "delta_faturas": 0,
    }
    try:
        df_novadis = loader.carregar_novadis_processado(data_inicio, data_fim)
        if not df_novadis.empty:
            resultado["novadis_total"] = float(df_novadis["custo_total"].sum())
            resultado["novadis_pedidos"] = int(df_novadis["numero_pedido"].nunique())
    except Exception as exc:
        print(f"Aviso: Novadis indisponível: {exc}")
    try:
        df_delta = loader.carregar_delta(data_inicio, data_fim)
        if not df_delta.empty:
            resultado["delta_total"] = float(df_delta["Total_EUR"].sum())
            resultado["delta_faturas"] = int(df_delta["Numero_Fatura"].nunique())
    except Exception as exc:
        print(f"Aviso: Delta indisponível: {exc}")
    return resultado


def gerar_prioridades(atual: dict[str, Any], deltas: dict[str, Any], operacionais: dict[str, Any], fornecedores: dict[str, Any]) -> list[dict[str, str]]:
    prioridades: list[dict[str, str]] = []
    delta_total = deltas.get("total")
    if delta_total is not None and delta_total < -5:
        prioridades.append({"level": "high", "text": f"Vendas abaixo do período anterior ({delta_total:.1f}%). Rever categorias em queda.", "target": "Comercial > Comparação"})
    elif delta_total is not None and delta_total > 5:
        prioridades.append({"level": "low", "text": f"Vendas em crescimento ({delta_total:.1f}%). Garantir stock dos produtos com maior tração.", "target": "Operação > Forecast"})

    if atual["margem_bruta"] < 35:
        prioridades.append({"level": "high", "text": f"Margem bruta baixa ({atual['margem_bruta']:.1f}%). Rever preço/custo nos produtos de maior volume.", "target": "Rentabilidade > Margens"})
    elif atual["margem_bruta"] < 50:
        prioridades.append({"level": "medium", "text": f"Margem bruta moderada ({atual['margem_bruta']:.1f}%). Afinar custos e fichas técnicas.", "target": "Rentabilidade"})

    if atual["concentracao_top5"] > 45:
        prioridades.append({"level": "medium", "text": f"Top 5 produtos concentram {atual['concentracao_top5']:.1f}% das vendas. Monitorizar dependência.", "target": "Comercial > Produtos"})

    total_fornecedores = fornecedores["novadis_total"] + fornecedores["delta_total"]
    if total_fornecedores > 0 and atual["total"] > 0 and total_fornecedores / atual["total"] > 0.35:
        prioridades.append({"level": "medium", "text": f"Compras Novadis/Delta equivalem a {total_fornecedores / atual['total'] * 100:.1f}% das vendas.", "target": "Operação > Encomendas"})

    if operacionais["linhas_abaixo_objetivo"]:
        prioridades.append({"level": "medium", "text": f"{operacionais['linhas_abaixo_objetivo']} linhas abaixo da margem objetivo.", "target": "Rentabilidade > Margens"})

    if not prioridades:
        prioridades.append({"level": "low", "text": "Indicadores principais equilibrados. Manter acompanhamento diário.", "target": "Painel"})
    return prioridades[:5]


def chart_series(df_filtrado: pd.DataFrame, df_anterior: pd.DataFrame) -> dict[str, Any]:
    diario = df_filtrado.groupby("Data")["Valor"].sum().reset_index()
    diario["Media_7d"] = diario["Valor"].rolling(7, min_periods=1).mean()

    mix = df_filtrado.groupby(["Fonte", "Categoria"], as_index=False)["Valor"].sum() if not df_filtrado.empty else pd.DataFrame(columns=["Fonte", "Categoria", "Valor"])

    df_rank = df_filtrado.copy()
    if not df_rank.empty:
        df_rank["Produto_Executivo"] = df_rank["Produto"].map(produto_executivo)
        top = (
            df_rank.groupby("Produto_Executivo")
            .agg(
                Vendas=("Valor", "sum"),
                Qtd=("Qtd", "sum"),
                Lucro=("Lucro_Bruto", "sum") if "Lucro_Bruto" in df_rank.columns else ("Valor", "sum"),
            )
            .reset_index()
            .sort_values("Vendas", ascending=False)
            .head(10)
        )
        top["Margem"] = top.apply(lambda row: (row["Lucro"] / row["Vendas"] * 100) if row["Vendas"] else 0.0, axis=1)
        top = top.rename(columns={"Produto_Executivo": "Produto"})
    else:
        top = pd.DataFrame(columns=["Produto", "Vendas", "Qtd", "Lucro", "Margem"])

    movers_up: list[dict[str, Any]] = []
    movers_down: list[dict[str, Any]] = []
    if not df_anterior.empty and not df_filtrado.empty:
        df_mov_atual = df_filtrado.copy()
        df_mov_anterior = df_anterior.copy()
        df_mov_atual["Produto_Executivo"] = df_mov_atual["Produto"].map(produto_executivo)
        df_mov_anterior["Produto_Executivo"] = df_mov_anterior["Produto"].map(produto_executivo)
        atual_prod = df_mov_atual.groupby("Produto_Executivo")["Valor"].sum()
        anterior_prod = df_mov_anterior.groupby("Produto_Executivo")["Valor"].sum()
        movimentos = pd.concat([atual_prod, anterior_prod], axis=1).fillna(0)
        movimentos.columns = ["Atual", "Anterior"]
        movimentos["Diferença"] = movimentos["Atual"] - movimentos["Anterior"]
        movimentos = movimentos.reset_index().rename(columns={"Produto_Executivo": "Produto"})
        movers_up = movimentos.sort_values("Diferença", ascending=False).head(8).to_dict(orient="records")
        movers_down = movimentos.sort_values("Diferença", ascending=True).head(8).to_dict(orient="records")

    return {
        "daily": [
            {"date": row["Data"].date().isoformat(), "value": float(row["Valor"]), "ma7": float(row["Media_7d"])}
            for _, row in diario.iterrows()
        ],
        "mix": mix.to_dict(orient="records"),
        "top_products": top.to_dict(orient="records"),
        "movers_up": movers_up,
        "movers_down": movers_down,
    }


def build_performance(df_filtrado: pd.DataFrame, df_scope: pd.DataFrame) -> dict[str, Any]:
    if df_filtrado.empty:
        return {}

    data_ref = pd.Timestamp(df_filtrado["Data"].max()).normalize()

    def period_sum(start: pd.Timestamp, end: pd.Timestamp) -> float:
        mask = (df_scope["Data"] >= start.normalize()) & (df_scope["Data"] <= end.normalize())
        return safe_sum(df_scope[mask], "Valor")

    week_start = data_ref - pd.Timedelta(days=6)
    prev_week_end = week_start - pd.Timedelta(days=1)
    prev_week_start = prev_week_end - pd.Timedelta(days=6)
    last_year_week_start = week_start - pd.DateOffset(years=1)
    last_year_week_end = data_ref - pd.DateOffset(years=1)

    month_start = data_ref.replace(day=1)
    days_mtd = (data_ref - month_start).days + 1
    prev_month_end = month_start - pd.Timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)
    prev_month_same_day = min(prev_month_start + pd.Timedelta(days=days_mtd - 1), prev_month_end)
    smly_start = month_start - pd.DateOffset(years=1)
    smly_end = data_ref - pd.DateOffset(years=1)

    year_start = data_ref.replace(month=1, day=1)
    ytd_last_year_start = year_start - pd.DateOffset(years=1)
    ytd_last_year_end = data_ref - pd.DateOffset(years=1)
    last_year_full_end = ytd_last_year_start.replace(month=12, day=31)

    values = {
        "semana_atual": period_sum(week_start, data_ref),
        "semana_anterior": period_sum(prev_week_start, prev_week_end),
        "semana_ano_passado": period_sum(last_year_week_start, last_year_week_end),
        "mes_atual": period_sum(month_start, data_ref),
        "mes_anterior_mtd": period_sum(prev_month_start, prev_month_same_day),
        "smly": period_sum(smly_start, smly_end),
        "ano_atual_ytd": period_sum(year_start, data_ref),
        "ano_anterior_ytd": period_sum(ytd_last_year_start, ytd_last_year_end),
        "ano_anterior_total": period_sum(ytd_last_year_start, last_year_full_end),
    }
    values.update(
        {
            "var_semana_vs_anterior": delta_pct(values["semana_atual"], values["semana_anterior"]),
            "var_semana_vs_ano_passado": delta_pct(values["semana_atual"], values["semana_ano_passado"]),
            "var_mes_vs_anterior": delta_pct(values["mes_atual"], values["mes_anterior_mtd"]),
            "var_mes_vs_ano_passado": delta_pct(values["mes_atual"], values["smly"]),
            "var_ano_vs_ano_anterior": delta_pct(values["ano_atual_ytd"], values["ano_anterior_ytd"]),
            "dias_mtd": days_mtd,
            "data_atualizacao": data_ref.date().isoformat(),
        }
    )
    return values


def build_commercial(
    df_filtrado: pd.DataFrame,
    df_anterior: pd.DataFrame,
    df_homologo: pd.DataFrame,
    df_scope: pd.DataFrame,
    atual: dict[str, Any],
    data_inicio: pd.Timestamp,
    data_fim: pd.Timestamp,
) -> dict[str, Any]:
    if df_filtrado.empty:
        return {}

    categories = add_previous_delta(group_sales(df_filtrado, "Categoria"), df_anterior, "Categoria")
    subcategories = group_sales(df_filtrado, "Subcategoria", top=18)
    sources = group_sales(df_filtrado, "Fonte")

    homologo_categories = add_previous_delta(group_sales(df_filtrado, "Categoria"), df_homologo, "Categoria")
    homologo_categories = homologo_categories.rename(columns={"Delta_Pct": "Delta_Homologo_Pct", "Anterior": "Homologo"})

    produtos = group_sales(df_filtrado, "Produto")
    produtos["Produto_Executivo"] = produtos["Produto"].map(produto_executivo)
    produtos_exec = (
        produtos.groupby("Produto_Executivo", as_index=False)
        .agg(
            Vendas=("Vendas", "sum"),
            Qtd=("Qtd", "sum"),
            Registos=("Registos", "sum"),
            Lucro_Bruto=("Lucro_Bruto", "sum"),
        )
        .sort_values("Vendas", ascending=False)
    )
    produtos_exec["Margem_Bruta_Pct"] = produtos_exec.apply(
        lambda row: (row["Lucro_Bruto"] / row["Vendas"] * 100) if row["Vendas"] else 0.0,
        axis=1,
    )
    produtos_exec["Share"] = produtos_exec["Vendas"] / produtos_exec["Vendas"].sum() * 100 if not produtos_exec.empty else 0.0

    pareto = produtos_exec.copy().sort_values("Vendas", ascending=False)
    pareto["Acumulado_Pct"] = pareto["Vendas"].cumsum() / pareto["Vendas"].sum() * 100 if not pareto.empty else 0.0
    produtos_80 = int((pareto["Acumulado_Pct"] <= 80).sum()) if not pareto.empty else 0
    if not pareto.empty and produtos_80 == 0:
        produtos_80 = 1
    total_produtos = int(len(produtos_exec))
    hhi = float(((produtos_exec["Vendas"] / produtos_exec["Vendas"].sum()) ** 2).sum() * 10000) if not produtos_exec.empty and produtos_exec["Vendas"].sum() else 0.0

    diario = df_filtrado.groupby("Data")["Valor"].sum().reset_index()
    mensal = df_filtrado.assign(Mes_Ano=df_filtrado["Data"].dt.to_period("M").astype(str)).groupby("Mes_Ano", as_index=False)["Valor"].sum()
    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    weekday = df_filtrado.copy()
    weekday["Dia"] = weekday["Data"].dt.dayofweek.map(lambda i: dias_semana[int(i)])
    weekday_totals = weekday.groupby("Dia", as_index=False)["Valor"].sum()
    weekday_totals["Ordem"] = weekday_totals["Dia"].map({day: idx for idx, day in enumerate(dias_semana)})
    weekday_totals = weekday_totals.sort_values("Ordem").drop(columns=["Ordem"])

    scatter = (
        df_filtrado.groupby("Categoria", as_index=False)
        .agg(Vendas=("Valor", "count"), Media=("Valor", "mean"), Total=("Valor", "sum"), Qtd=("Qtd", "sum") if "Qtd" in df_filtrado.columns else ("Valor", "count"))
        .sort_values("Total", ascending=False)
    )

    detail_cols = [
        "Data",
        "Produto",
        "Categoria",
        "Subcategoria",
        "Fonte",
        "Qtd",
        "Valor",
        "Custo_Total",
        "Lucro_Bruto",
        "Margem_Bruta_Pct",
        "Abaixo_Objetivo",
    ]
    details = df_filtrado.sort_values("Valor", ascending=False)

    return {
        "kpis": {
            "total_vendas": atual["total"],
            "media_diaria": atual["media_diaria"],
            "ticket_medio": atual["ticket"],
            "projecao_30d": atual["media_diaria"] * 30,
            "produtos": total_produtos,
            "categorias": int(df_filtrado["Categoria"].nunique()) if "Categoria" in df_filtrado.columns else 0,
            "transacoes": int(len(df_filtrado)),
            "hhi": hhi,
            "produtos_80": produtos_80,
            "pct_catalogo_80": (produtos_80 / total_produtos * 100) if total_produtos else 0.0,
        },
        "performance": build_performance(df_filtrado, df_scope),
        "categories": table_records(categories),
        "categories_homologo": table_records(homologo_categories),
        "subcategories": table_records(subcategories),
        "sources": table_records(sources),
        "top_products": table_records(produtos_exec.rename(columns={"Produto_Executivo": "Produto"}).head(20)),
        "bottom_products": table_records(produtos.sort_values("Vendas", ascending=True).head(20)),
        "pareto": table_records(pareto.rename(columns={"Produto_Executivo": "Produto"}).head(50)),
        "daily": table_records(diario),
        "monthly": table_records(mensal),
        "weekday": table_records(weekday_totals),
        "scatter": table_records(scatter),
        "details": rows_for_columns(details, detail_cols, limit=350),
        "period": {"start": data_inicio.date().isoformat(), "end": data_fim.date().isoformat()},
    }


def build_margin_real(df_filtrado: pd.DataFrame, loader: DataLoaderV9) -> dict[str, Any]:
    df_pos = df_filtrado[df_filtrado["Fonte"].eq("POS-Café")].copy() if "Fonte" in df_filtrado.columns else pd.DataFrame()
    if df_pos.empty:
        return {"summary": {}, "top": [], "low": [], "missing": [], "details": [], "mapping": []}

    vendas = (
        df_pos.groupby(["Produto", "Categoria"], as_index=False)
        .agg(Qtd=("Qtd", "sum"), Valor=("Valor", "sum"))
        .sort_values("Valor", ascending=False)
    )
    vendas["PVP_Medio"] = vendas.apply(lambda row: (row["Valor"] / row["Qtd"]) if row["Qtd"] else 0.0, axis=1)

    data_fim = pd.Timestamp(df_filtrado["Data"].max())
    data_inicio_custos = data_fim - pd.Timedelta(days=180)
    try:
        df_novadis = loader.carregar_novadis_processado(data_inicio_custos, data_fim)
    except Exception as exc:
        print(f"Aviso: margens reais sem Novadis: {exc}")
        df_novadis = pd.DataFrame()

    if not df_novadis.empty and {"produto_pos", "custo_unitario"}.issubset(df_novadis.columns):
        custos_novadis = df_novadis.groupby("produto_pos", as_index=False)["custo_unitario"].mean()
        custos_novadis.columns = ["Produto", "Custo_Novadis"]
    else:
        custos_novadis = pd.DataFrame(columns=["Produto", "Custo_Novadis"])

    custos_manuais_path = ROOT_DIR / "custos_margens_reais.csv"
    if custos_manuais_path.exists():
        custos_manuais = pd.read_csv(custos_manuais_path)
    else:
        custos_manuais = pd.DataFrame(columns=["Produto", "Custo_Manual"])

    fichas_path = ROOT_DIR / "fichas_tecnicas.csv"
    if fichas_path.exists():
        fichas = pd.read_csv(fichas_path)
        if {"Produto_POS", "Custo_Dose"}.issubset(fichas.columns):
            custos_fichas = fichas[["Produto_POS", "Custo_Dose"]].copy()
            custos_fichas.columns = ["Produto", "Custo_Ficha"]
        else:
            custos_fichas = pd.DataFrame(columns=["Produto", "Custo_Ficha"])
    else:
        custos_fichas = pd.DataFrame(columns=["Produto", "Custo_Ficha"])

    map_path = ROOT_DIR / "mapeamento_produtos.csv"
    mapping = pd.read_csv(map_path) if map_path.exists() else pd.DataFrame(columns=["Produto_POS", "Produto_Custo", "Multiplicador"])
    if not mapping.empty and not custos_novadis.empty and {"Produto_POS", "Produto_Custo"}.issubset(mapping.columns):
        if "Multiplicador" not in mapping.columns:
            mapping["Multiplicador"] = 1.0
        dict_custos = dict(zip(custos_novadis["Produto"], custos_novadis["Custo_Novadis"]))
        mapped_costs = []
        for _, row in mapping.iterrows():
            base = dict_custos.get(row["Produto_Custo"])
            if base is not None:
                mapped_costs.append(
                    {
                        "Produto": row["Produto_POS"],
                        "Custo_Novadis": float(base) * float(row.get("Multiplicador", 1.0) or 1.0),
                    }
                )
        if mapped_costs:
            custos_novadis = pd.concat([custos_novadis, pd.DataFrame(mapped_costs)], ignore_index=True)
            custos_novadis = custos_novadis.drop_duplicates(subset=["Produto"], keep="last")

    margens = vendas.merge(custos_novadis, on="Produto", how="left")
    margens = margens.merge(custos_manuais, on="Produto", how="left")
    margens = margens.merge(custos_fichas, on="Produto", how="left")
    margens["Custo_Final"] = margens["Custo_Ficha"].combine_first(margens["Custo_Manual"]).combine_first(margens["Custo_Novadis"])
    missing = margens[margens["Custo_Final"].isna()].sort_values("Valor", ascending=False)
    analysis = margens[margens["Custo_Final"].notna()].copy()

    if analysis.empty:
        return {
            "summary": {"produtos_analisados": 0, "produtos_sem_custo": int(len(missing))},
            "top": [],
            "low": [],
            "missing": table_records(missing[["Produto", "Categoria", "Qtd", "Valor", "PVP_Medio"]], 50),
            "details": [],
            "mapping": table_records(mapping, 200),
        }

    analysis["Custo_Total_Real"] = analysis["Custo_Final"] * analysis["Qtd"]
    analysis["Lucro_Bruto_Real"] = analysis["Valor"] - analysis["Custo_Total_Real"]
    analysis["Margem_Real_Pct"] = analysis.apply(
        lambda row: (row["Lucro_Bruto_Real"] / row["Valor"] * 100) if row["Valor"] else 0.0,
        axis=1,
    )

    total_vendas = float(analysis["Valor"].sum())
    total_custo = float(analysis["Custo_Total_Real"].sum())
    lucro = total_vendas - total_custo
    return {
        "summary": {
            "produtos_analisados": int(len(analysis)),
            "produtos_sem_custo": int(len(missing)),
            "vendas_analisadas": total_vendas,
            "custos_produtos": total_custo,
            "lucro_bruto_real": lucro,
            "margem_global": (lucro / total_vendas * 100) if total_vendas else 0.0,
        },
        "top": table_records(analysis.sort_values("Lucro_Bruto_Real", ascending=False).head(15)),
        "low": table_records(analysis.sort_values("Margem_Real_Pct", ascending=True).head(15)),
        "missing": table_records(missing[["Produto", "Categoria", "Qtd", "Valor", "PVP_Medio"]], 50),
        "details": table_records(analysis.sort_values("Lucro_Bruto_Real", ascending=False), 250),
        "mapping": table_records(mapping, 200),
    }


def build_profitability(
    df_filtrado: pd.DataFrame,
    loader: DataLoaderV9,
    cost_manager: Any,
    data_inicio: pd.Timestamp,
    data_fim: pd.Timestamp,
) -> dict[str, Any]:
    if df_filtrado.empty:
        return {}

    dt_inicio = data_inicio.to_pydatetime()
    dt_fim = data_fim.to_pydatetime()
    try:
        metrics = cost_manager.calcular_metricas_financeiras(df_filtrado, dt_inicio, dt_fim)
    except Exception as exc:
        print(f"Aviso: métricas financeiras indisponíveis: {exc}")
        metrics = {}

    breakdown = [
        {"Tipo": "Comissões Santa Casa", "Valor": float(metrics.get("comissoes_santa_casa", 0) or 0)},
        {"Tipo": "Custos de produtos", "Valor": float(metrics.get("custos_produtos", 0) or 0)},
        {"Tipo": "Custos operacionais", "Valor": float(metrics.get("custos_operacionais", 0) or 0)},
    ]

    try:
        op_costs = cost_manager.get_resumo_custos_operacionais(dt_inicio, dt_fim)
    except Exception as exc:
        print(f"Aviso: resumo de custos indisponível: {exc}")
        op_costs = pd.DataFrame()
    if not op_costs.empty:
        op_costs = op_costs.reset_index().rename(columns={"index": "Categoria"})
        if "Categoria_Dashboard" in op_costs.columns:
            op_costs = op_costs.rename(columns={"Categoria_Dashboard": "Categoria"})

    try:
        rent_cat = cost_manager.analisar_rentabilidade_categorias(df_filtrado)
    except Exception as exc:
        print(f"Aviso: rentabilidade por categoria indisponível: {exc}")
        rent_cat = pd.DataFrame()
    if not rent_cat.empty:
        rent_cat = rent_cat.reset_index()

    product_cols = ["Produto", "Categoria"]
    agg: dict[str, tuple[str, str]] = {
        "Vendas": ("Valor", "sum"),
        "Qtd": ("Qtd", "sum"),
    }
    if "Custo_Total" in df_filtrado.columns:
        agg["Custo_Total"] = ("Custo_Total", "sum")
    if "Lucro_Bruto" in df_filtrado.columns:
        agg["Lucro_Bruto"] = ("Lucro_Bruto", "sum")
    products = df_filtrado.groupby(product_cols, as_index=False).agg(**agg)
    if "Custo_Total" not in products.columns:
        products["Custo_Total"] = 0.0
    if "Lucro_Bruto" not in products.columns:
        products["Lucro_Bruto"] = products["Vendas"] - products["Custo_Total"]
    products["Margem_Bruta_Pct"] = products.apply(lambda row: (row["Lucro_Bruto"] / row["Vendas"] * 100) if row["Vendas"] else 0.0, axis=1)
    products["PVP_Medio"] = products.apply(lambda row: (row["Vendas"] / row["Qtd"]) if row["Qtd"] else 0.0, axis=1)
    products["Custo_Medio"] = products.apply(lambda row: (row["Custo_Total"] / row["Qtd"]) if row["Qtd"] else 0.0, axis=1)

    if "Abaixo_Objetivo" in df_filtrado.columns:
        alerts_base = df_filtrado[df_filtrado["Abaixo_Objetivo"].fillna(False)].copy()
    elif {"Margem_Bruta_Pct", "Margem_Objetivo"}.issubset(df_filtrado.columns):
        alerts_base = df_filtrado[df_filtrado["Margem_Bruta_Pct"] < df_filtrado["Margem_Objetivo"]].copy()
    else:
        alerts_base = pd.DataFrame()
    if not alerts_base.empty:
        alerts = (
            alerts_base.groupby(["Produto", "Categoria"], as_index=False)
            .agg(
                Vendas=("Valor", "sum"),
                Linhas=("Valor", "count"),
                Margem_Bruta_Pct=("Margem_Bruta_Pct", "mean"),
                Margem_Objetivo=("Margem_Objetivo", "mean"),
            )
            .sort_values("Vendas", ascending=False)
        )
        alerts["Gap_Pontos"] = alerts["Margem_Bruta_Pct"] - alerts["Margem_Objetivo"]
    else:
        alerts = pd.DataFrame()

    try:
        break_even = loader.get_analise_break_even(df_filtrado)
    except Exception as exc:
        print(f"Aviso: break-even indisponível: {exc}")
        break_even = {}

    expenses = metrics.get("df_custos_operacionais")
    if isinstance(expenses, pd.DataFrame) and not expenses.empty:
        expense_cols = [
            "Data",
            "Descrição",
            "Categoria_Dashboard",
            "Valor_Total",
            "IVA",
            "Valor_Sem_IVA",
            "NIF_Fornecedor",
        ]
        expenses_records = rows_for_columns(expenses, expense_cols, limit=120)
    else:
        expenses_records = []

    return {
        "metrics": {str(key): clean_value(value) for key, value in metrics.items() if not isinstance(value, pd.DataFrame)},
        "cost_breakdown": breakdown,
        "op_costs": table_records(op_costs, 80),
        "expenses": expenses_records,
        "categories": table_records(rent_cat, 80),
        "top_products": table_records(products.sort_values("Lucro_Bruto", ascending=False), 30),
        "bottom_products": table_records(products.sort_values("Lucro_Bruto", ascending=True), 30),
        "margin_alerts": table_records(alerts, 80),
        "break_even": {str(key): clean_value(value) for key, value in break_even.items()},
        "real_margins": build_margin_real(df_filtrado, loader),
        "editable": {
            "op_costs_csv": table_records(read_csv_schema(OP_COSTS_PATH), 200),
            "manual_costs": table_records(read_csv_schema(MARGIN_MANUAL_COSTS_PATH), 300),
            "product_mappings": table_records(read_csv_schema(PRODUCT_MAPPING_PATH), 300),
        },
    }


def simple_forecast(df_filtrado: pd.DataFrame, cost_manager: Any, dias_analise: int = 60) -> pd.DataFrame:
    if df_filtrado.empty:
        return pd.DataFrame()
    data_max = pd.Timestamp(df_filtrado["Data"].max())
    data_min = data_max - pd.Timedelta(days=dias_analise - 1)
    base = df_filtrado[df_filtrado["Data"] >= data_min].copy()
    if base.empty:
        return pd.DataFrame()

    rows = []
    for produto, df_produto in base.groupby("Produto"):
        if len(df_produto) < 3:
            continue
        categoria = str(df_produto["Categoria"].iloc[0]) if "Categoria" in df_produto.columns else "Outros"
        dias_com_venda = int(df_produto.groupby("Data")["Qtd"].sum().gt(0).sum()) if "Qtd" in df_produto.columns else int(df_produto["Data"].nunique())
        if dias_com_venda < 3:
            continue
        qtd_diaria = df_produto.groupby("Data")["Qtd"].sum() if "Qtd" in df_produto.columns else df_produto.groupby("Data")["Valor"].count()
        media_diaria = float(qtd_diaria.mean())
        desvio = float(qtd_diaria.std() or 0.0)
        cv = (desvio / media_diaria * 100) if media_diaria else 0.0
        split = data_max - pd.Timedelta(days=14)
        qtd_recente = safe_sum(df_produto[df_produto["Data"] > split], "Qtd")
        qtd_antiga = safe_sum(df_produto[df_produto["Data"] <= split], "Qtd")
        tendencia_pct = delta_pct(qtd_recente, qtd_antiga) or 0.0
        if tendencia_pct > 5:
            tendencia = "crescimento"
        elif tendencia_pct < -5:
            tendencia = "queda"
        else:
            tendencia = "estavel"
        try:
            custo_unitario = float(cost_manager.get_custo_produto(produto, categoria) or 0.0)
        except Exception:
            custo_unitario = 0.0
        qtd_semanal = media_diaria * 7
        qtd_mensal = media_diaria * 30
        rows.append(
            {
                "Produto": produto,
                "Categoria": categoria,
                "Media_Diaria": media_diaria,
                "Qtd_Semanal": qtd_semanal,
                "Qtd_Mensal": qtd_mensal,
                "Stock_Seguranca": max(desvio * 1.5, media_diaria * 0.2),
                "Custo_Unitario": custo_unitario,
                "Valor_Encomenda_Semanal": qtd_semanal * custo_unitario,
                "Valor_Encomenda_Mensal": qtd_mensal * custo_unitario,
                "Tendencia_Percent": tendencia_pct,
                "Tendencia_Direcao": tendencia,
                "CV": cv,
                "Dias_Com_Venda": dias_com_venda,
            }
        )
    return pd.DataFrame(rows).sort_values("Valor_Encomenda_Mensal", ascending=False) if rows else pd.DataFrame()


def carregar_santa_casa_file(data_inicio: pd.Timestamp, data_fim: pd.Timestamp) -> pd.DataFrame:
    data_file = Path(os.getenv("SANTA_CASA_CSV", "/home/jorge/Documentos/Santa casa/dados/dados.csv"))
    if not data_file.exists():
        return pd.DataFrame()
    try:
        df = pd.read_csv(data_file, sep=";", encoding="utf-8")
    except Exception as exc:
        print(f"Aviso: ficheiro Santa Casa indisponível: {exc}")
        return pd.DataFrame()
    if "Data" not in df.columns:
        return pd.DataFrame()
    df["Data"] = pd.to_datetime(df["Data"], format="%d-%m-%Y", errors="coerce")
    df = df[df["Data"].notna()].copy()
    if "Categoria" in df.columns:
        df = df[df["Categoria"] != "PRESTAÇÃO DE CONTAS"].copy()
    numeric_cols = ["Qt Maços", "Vendas ilíquidas (€)", "Remunerações (€)", "Prémios (€)", "Valor (€)"]
    for col in numeric_cols:
        if col in df.columns:
            series = df[col].astype(str).str.strip()
            mask = series.str.contains(",", na=False)
            series.loc[mask] = series.loc[mask].str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(series, errors="coerce").fillna(0.0)
    df = df[(df["Data"] >= data_inicio.normalize()) & (df["Data"] <= data_fim.normalize())].copy()
    if not df.empty:
        df["Ano_Mes"] = df["Data"].dt.to_period("M").astype(str)
        df["Semana"] = df["Data"].dt.strftime("%Y-W%V")
    return df.sort_values("Data")


def get_cost_references(loader: DataLoaderV9) -> pd.DataFrame:
    refs: list[pd.DataFrame] = []
    data_fim = pd.Timestamp.today().normalize()
    data_inicio = data_fim - pd.Timedelta(days=180)
    try:
        df_novadis = loader.carregar_novadis_processado(data_inicio, data_fim)
    except Exception as exc:
        print(f"Aviso: referências Novadis indisponíveis: {exc}")
        df_novadis = pd.DataFrame()
    if not df_novadis.empty and {"produto_pos", "custo_unitario"}.issubset(df_novadis.columns):
        novadis_refs = df_novadis.groupby("produto_pos", as_index=False)["custo_unitario"].mean()
        novadis_refs.columns = ["Produto", "Custo"]
        novadis_refs["Tipo"] = "Novadis"
        refs.append(novadis_refs)

    fichas = read_csv_schema(FICHAS_PATH)
    if not fichas.empty:
        ficha_refs = fichas[["Produto_POS", "Custo_Dose"]].copy()
        ficha_refs.columns = ["Produto", "Custo"]
        ficha_refs["Tipo"] = "Ficha"
        refs.append(ficha_refs)

    if not refs:
        return pd.DataFrame(columns=["Produto", "Custo", "Tipo"])
    out = pd.concat(refs, ignore_index=True)
    out["Produto"] = out["Produto"].astype(str)
    out["Custo"] = pd.to_numeric(out["Custo"], errors="coerce").fillna(0.0)
    out = out.sort_values(["Produto", "Tipo"]).drop_duplicates(subset=["Produto", "Tipo"], keep="last")
    return out


def build_operation(
    df_filtrado: pd.DataFrame,
    loader: DataLoaderV9,
    cost_manager: Any,
    data_inicio: pd.Timestamp,
    data_fim: pd.Timestamp,
) -> dict[str, Any]:
    santa = df_filtrado[df_filtrado["Is_Santa_Casa"].fillna(False)].copy() if "Is_Santa_Casa" in df_filtrado.columns else pd.DataFrame()
    if santa.empty and "Fonte" in df_filtrado.columns:
        santa = df_filtrado[df_filtrado["Fonte"].astype(str).str.contains("Santa", case=False, na=False)].copy()

    santa_file = carregar_santa_casa_file(data_inicio, data_fim)
    if not santa_file.empty and {"Jogo", "Vendas ilíquidas (€)"}.issubset(santa_file.columns):
        santa_products = (
            santa_file.groupby("Jogo", as_index=False)
            .agg(
                Vendas=("Vendas ilíquidas (€)", "sum"),
                Lucro_Bruto=("Remunerações (€)", "sum") if "Remunerações (€)" in santa_file.columns else ("Vendas ilíquidas (€)", "sum"),
                Premios=("Prémios (€)", "sum") if "Prémios (€)" in santa_file.columns else ("Vendas ilíquidas (€)", "sum"),
                Semanas=("Data", "nunique"),
            )
            .sort_values("Vendas", ascending=False)
            .rename(columns={"Jogo": "Produto"})
        )
        total_sc = float(santa_products["Vendas"].sum())
        santa_products["Share"] = santa_products["Vendas"] / total_sc * 100 if total_sc else 0.0
        if "Categoria" in santa_file.columns:
            santa_categories = (
                santa_file.groupby("Categoria", as_index=False)
                .agg(Vendas=("Vendas ilíquidas (€)", "sum"), Jogos=("Jogo", "nunique"))
                .sort_values("Vendas", ascending=False)
            )
        else:
            santa_categories = pd.DataFrame()
        santa_weekly = santa_file.groupby("Semana", as_index=False)["Vendas ilíquidas (€)"].sum().rename(columns={"Vendas ilíquidas (€)": "Valor"})
        santa_summary = {
            "vendas": safe_sum(santa_file, "Vendas ilíquidas (€)"),
            "lucro_bruto": safe_sum(santa_file, "Remunerações (€)"),
            "comissoes": safe_sum(santa_file, "Remunerações (€)"),
            "premios": safe_sum(santa_file, "Prémios (€)"),
            "valor_liquido": safe_sum(santa_file, "Valor (€)"),
            "jogos": int(santa_file["Jogo"].nunique()) if "Jogo" in santa_file.columns else 0,
            "registos": int(len(santa_file)),
            "fonte": "ficheiro_santa_casa",
        }
    elif not santa.empty:
        santa_products = group_sales(santa, "Produto", top=25)
        santa_categories = group_sales(santa, "Categoria", top=20)
        santa_weekly = santa.assign(Semana=santa["Data"].dt.strftime("%Y-W%V")).groupby("Semana", as_index=False)["Valor"].sum()
        santa_summary = {
            "vendas": safe_sum(santa, "Valor"),
            "lucro_bruto": safe_sum(santa, "Lucro_Bruto"),
            "comissoes": safe_sum(santa, "Custo_Total"),
            "premios": 0.0,
            "valor_liquido": safe_sum(santa, "Lucro_Bruto"),
            "jogos": int(santa["Produto"].nunique()) if "Produto" in santa.columns else 0,
            "registos": int(len(santa)),
            "fonte": "vendas_integradas",
        }
    else:
        santa_products = pd.DataFrame()
        santa_categories = pd.DataFrame()
        santa_weekly = pd.DataFrame()
        santa_summary = {
            "vendas": 0.0,
            "lucro_bruto": 0.0,
            "comissoes": 0.0,
            "premios": 0.0,
            "valor_liquido": 0.0,
            "jogos": 0,
            "registos": 0,
            "fonte": "N/D",
        }

    forecast = simple_forecast(df_filtrado, cost_manager)
    forecast_trends = forecast.groupby("Tendencia_Direcao", as_index=False)["Produto"].count().rename(columns={"Produto": "Produtos"}) if not forecast.empty else pd.DataFrame()

    try:
        novadis = loader.carregar_novadis_processado(data_inicio, data_fim)
    except Exception as exc:
        print(f"Aviso: Novadis indisponível na operação: {exc}")
        novadis = pd.DataFrame()
    if not novadis.empty:
        novadis_products = (
            novadis.groupby("produto_pos", as_index=False)
            .agg(
                custo_total=("custo_total", "sum"),
                unidades_vendaveis=("unidades_vendaveis", "sum"),
                encomendas=("numero_pedido", "nunique"),
            )
            .sort_values("custo_total", ascending=False)
        )
        novadis_monthly = novadis.assign(Mes=novadis["data"].dt.to_period("M").astype(str)).groupby("Mes", as_index=False)["custo_total"].sum()
    else:
        novadis_products = pd.DataFrame()
        novadis_monthly = pd.DataFrame()

    try:
        delta = loader.carregar_delta(data_inicio, data_fim)
    except Exception as exc:
        print(f"Aviso: Delta indisponível na operação: {exc}")
        delta = pd.DataFrame()
    if not delta.empty:
        delta_monthly = delta.assign(Mes=delta["Data_Fatura"].dt.to_period("M").astype(str)).groupby("Mes", as_index=False)["Total_EUR"].sum()
    else:
        delta_monthly = pd.DataFrame()

    try:
        delta_items = loader.carregar_delta_itens()
    except Exception as exc:
        print(f"Aviso: itens Delta indisponíveis: {exc}")
        delta_items = pd.DataFrame()
    if not delta_items.empty and not delta.empty and "Numero_Fatura" in delta_items.columns:
        wanted = set(delta["Numero_Fatura"].astype(str))
        delta_items["Numero_Fatura"] = delta_items["Numero_Fatura"].astype(str)
        delta_items = delta_items[delta_items["Numero_Fatura"].isin(wanted)]

    fichas_path = ROOT_DIR / "fichas_tecnicas.csv"
    fichas = pd.read_csv(fichas_path) if fichas_path.exists() else pd.DataFrame()
    if not fichas.empty:
        fichas["Custo_Dose"] = pd.to_numeric(fichas.get("Custo_Dose"), errors="coerce").fillna(0.0)
        fichas_summary = {
            "total": int(len(fichas)),
            "custo_medio_dose": float(fichas["Custo_Dose"].mean()),
            "custo_total_referencia": float(fichas["Custo_Dose"].sum()),
        }
    else:
        fichas_summary = {"total": 0, "custo_medio_dose": 0.0, "custo_total_referencia": 0.0}

    return {
        "santa_casa": {
            "summary": santa_summary,
            "products": table_records(santa_products, 30),
            "categories": table_records(santa_categories, 20),
            "weekly": table_records(santa_weekly, 120),
        },
        "forecast": {
            "summary": {
                "produtos": int(len(forecast)),
                "encomenda_semanal": safe_sum(forecast, "Valor_Encomenda_Semanal"),
                "encomenda_mensal": safe_sum(forecast, "Valor_Encomenda_Mensal"),
                "produtos_crescimento": int((forecast["Tendencia_Direcao"] == "crescimento").sum()) if not forecast.empty else 0,
            },
            "rows": table_records(forecast, 180),
            "trends": table_records(forecast_trends),
        },
        "novadis": {
            "summary": {
                "total": safe_sum(novadis, "custo_total"),
                "encomendas": int(novadis["numero_pedido"].nunique()) if not novadis.empty and "numero_pedido" in novadis.columns else 0,
                "unidades": safe_sum(novadis, "unidades_vendaveis"),
                "custo_medio_pedido": (safe_sum(novadis, "custo_total") / int(novadis["numero_pedido"].nunique())) if not novadis.empty and int(novadis["numero_pedido"].nunique()) else 0.0,
            },
            "products": table_records(novadis_products, 60),
            "monthly": table_records(novadis_monthly),
            "unit_mappings": table_records(read_csv_schema(NOVADIS_UNIT_MAPPING_PATH), 300),
            "rows": rows_for_columns(
                novadis.sort_values("data", ascending=False) if not novadis.empty else novadis,
                ["data", "numero_pedido", "produto_novadis", "quantidade_encomendada", "preco_unitario_com_iva", "custo_total", "produto_pos", "unidades_vendaveis", "custo_unitario"],
                180,
            ),
        },
        "delta": {
            "summary": {
                "total": safe_sum(delta, "Total_EUR"),
                "faturas": int(delta["Numero_Fatura"].nunique()) if not delta.empty and "Numero_Fatura" in delta.columns else 0,
                "itens": int(len(delta_items)),
            },
            "monthly": table_records(delta_monthly),
            "rows": rows_for_columns(delta, ["Data_Fatura", "Numero_Fatura", "Total_EUR", "Arquivo", "NIF_Cliente"], 120),
            "items": table_records(delta_items, 180),
        },
        "fichas": {
            "summary": fichas_summary,
            "rows": table_records(fichas.sort_values("Custo_Dose", ascending=False) if not fichas.empty else fichas, 180),
        },
    }


def build_meta() -> dict[str, Any]:
    df, loader, _ = load_data()
    cost_refs = get_cost_references(loader)
    return {
        "data_min": pd.Timestamp(df["Data"].min()).date().isoformat(),
        "data_max": pd.Timestamp(df["Data"].max()).date().isoformat(),
        "produtos": sorted(str(v) for v in df["Produto"].dropna().unique()) if "Produto" in df.columns else [],
        "categorias": sorted(str(v) for v in df["Categoria"].dropna().unique()) if "Categoria" in df.columns else [],
        "fontes": sorted(str(v) for v in df["Fonte"].dropna().unique()) if "Fonte" in df.columns else [],
        "subcategorias": sorted(str(v) for v in df["Subcategoria"].dropna().astype(str).unique()) if "Subcategoria" in df.columns else [],
        "anos": sorted(int(v) for v in df["Data"].dt.year.dropna().unique()),
        "cost_refs": table_records(cost_refs, 600),
        "loaded_at": DATA_CACHE["loaded_at"],
    }


def build_cockpit(params: dict[str, list[str]]) -> dict[str, Any]:
    df, loader, cost_manager = load_data()
    data_inicio, data_fim, preset = resolve_period(params, df)
    categorias = parse_list(params, "categorias")
    fontes = parse_list(params, "fontes")
    subcategorias = parse_list(params, "subcategorias")
    excluir_domingos = params.get("exclude_sundays", ["0"])[0] == "1"

    df_filtrado = filter_df(df, data_inicio, data_fim, categorias, fontes, subcategorias, excluir_domingos)
    ant_inicio, ant_fim = periodo_anterior(data_inicio, data_fim)
    df_anterior = filter_df(df, ant_inicio, ant_fim, categorias, fontes, subcategorias, excluir_domingos)
    data_min = pd.Timestamp(df["Data"].min()).normalize()
    data_max = pd.Timestamp(df["Data"].max()).normalize()
    df_scope = filter_df(df, data_min, data_max, categorias, fontes, subcategorias, excluir_domingos)
    df_homologo = filter_df(
        df,
        data_inicio - pd.DateOffset(years=1),
        data_fim - pd.DateOffset(years=1),
        categorias,
        fontes,
        subcategorias,
        excluir_domingos,
    )

    atual = resumo_periodo(df_filtrado, cost_manager, data_inicio, data_fim)
    anterior = resumo_periodo(df_anterior, cost_manager, ant_inicio, ant_fim)
    deltas = {
        key: delta_pct(atual[key], anterior[key])
        for key in ("total", "media_diaria", "ticket", "lucro_bruto", "lucro_liquido")
    }
    operacionais = calcular_operacionais(df_filtrado, loader, atual, data_inicio, data_fim)
    decisao = calcular_decisao(df_filtrado, df, cost_manager, data_fim)
    fornecedores = carregar_fornecedores(loader, data_inicio, data_fim)
    prioridades = gerar_prioridades(atual, deltas, operacionais, fornecedores)

    delta_total = deltas["total"] if deltas["total"] is not None else 0.0
    score = 50
    score += max(min(delta_total, 20), -20) * 0.8
    score += max(min(atual["margem_bruta"] - 45, 20), -20) * 0.7
    score += max(min(atual["margem_liquida"], 15), -15) * 0.8
    score -= max(atual["concentracao_top5"] - 35, 0) * 0.35
    score = int(max(0, min(100, round(score))))
    estado = "Forte" if score >= 78 else "Estável" if score >= 58 else "Atenção" if score >= 40 else "Crítico"

    return {
        "period": {
            "preset": preset,
            "start": data_inicio.date().isoformat(),
            "end": data_fim.date().isoformat(),
            "previous_start": ant_inicio.date().isoformat(),
            "previous_end": ant_fim.date().isoformat(),
        },
        "filters": {
            "categorias": categorias,
            "fontes": fontes,
            "subcategorias": subcategorias,
            "exclude_sundays": excluir_domingos,
        },
        "counts": {
            "filtered": int(len(df_filtrado)),
            "total": int(len(df)),
            "days": int((data_fim - data_inicio).days + 1),
        },
        "status": {"score": score, "label": estado},
        "atual": atual,
        "anterior": anterior,
        "deltas": deltas,
        "operacionais": operacionais,
        "decisao": decisao,
        "fornecedores": fornecedores,
        "prioridades": prioridades,
        "charts": chart_series(df_filtrado, df_anterior),
        "commercial": build_commercial(df_filtrado, df_anterior, df_homologo, df_scope, atual, data_inicio, data_fim),
        "profitability": build_profitability(df_filtrado, loader, cost_manager, data_inicio, data_fim),
        "operation": build_operation(df_filtrado, loader, cost_manager, data_inicio, data_fim),
    }


def api_save_ficha(body: dict[str, Any]) -> dict[str, Any]:
    produto = body_str(body, "Produto_POS")
    if not produto:
        raise ValueError("Produto_POS é obrigatório")
    preco_compra = body_float(body, "Preco_Compra")
    qtd_compra = body_float(body, "Qtd_Compra", 1.0)
    qtd_dose = body_float(body, "Qtd_Dose", 1.0)
    if preco_compra <= 0 or qtd_compra <= 0 or qtd_dose <= 0:
        raise ValueError("Preço, quantidade de compra e dose têm de ser maiores que zero")
    custo_dose = round((preco_compra / qtd_compra) * qtd_dose, 4)
    row = {
        "Produto_POS": produto,
        "Preco_Compra": preco_compra,
        "Qtd_Compra": qtd_compra,
        "Unidade_Compra": body_str(body, "Unidade_Compra", "Unidade"),
        "Qtd_Dose": qtd_dose,
        "Unidade_Dose": body_str(body, "Unidade_Dose", body_str(body, "Unidade_Compra", "Unidade")),
        "Custo_Dose": custo_dose,
    }
    upsert_by_key(FICHAS_PATH, row, "Produto_POS")
    reset_data_cache()
    return {"ok": True, "row": row}


def api_delete_ficha(body: dict[str, Any]) -> dict[str, Any]:
    produto = body_str(body, "Produto_POS")
    if not produto:
        raise ValueError("Produto_POS é obrigatório")
    delete_by_key(FICHAS_PATH, "Produto_POS", produto)
    reset_data_cache()
    return {"ok": True}


def api_save_composite(body: dict[str, Any]) -> dict[str, Any]:
    produto = body_str(body, "Produto_POS")
    ingredientes = body.get("ingredientes", [])
    if not produto:
        raise ValueError("Produto_POS é obrigatório")
    if not isinstance(ingredientes, list) or not ingredientes:
        raise ValueError("Adicione pelo menos um ingrediente")

    _, loader, _ = load_data()
    refs = get_cost_references(loader)
    ref_costs = dict(zip(refs["Produto"].astype(str), refs["Custo"])) if not refs.empty else {}
    total = 0.0
    normalized = []
    for item in ingredientes:
        if not isinstance(item, dict):
            continue
        ingrediente = str(item.get("Ingrediente", "")).strip()
        qtd = float(item.get("Qtd", 0) or 0)
        custo_unit = item.get("Custo_Unit")
        if custo_unit in ("", None):
            custo_unit = ref_costs.get(ingrediente, 0.0)
        custo_unit = float(custo_unit or 0)
        if not ingrediente or qtd <= 0 or custo_unit < 0:
            continue
        custo_total = qtd * custo_unit
        total += custo_total
        normalized.append(
            {
                "Ingrediente": ingrediente,
                "Qtd": qtd,
                "Custo_Unit": custo_unit,
                "Custo_Total": custo_total,
            }
        )
    if not normalized:
        raise ValueError("Ingredientes inválidos")
    row = {
        "Produto_POS": produto,
        "Preco_Compra": round(total, 4),
        "Qtd_Compra": 1.0,
        "Unidade_Compra": "Unid",
        "Qtd_Dose": 1.0,
        "Unidade_Dose": "Unid",
        "Custo_Dose": round(total, 4),
    }
    upsert_by_key(FICHAS_PATH, row, "Produto_POS")
    reset_data_cache()
    return {"ok": True, "row": row, "ingredientes": normalized}


def api_save_manual_cost(body: dict[str, Any]) -> dict[str, Any]:
    produto = body_str(body, "Produto")
    custo = body_float(body, "Custo_Manual")
    if not produto:
        raise ValueError("Produto é obrigatório")
    if custo <= 0:
        raise ValueError("Custo_Manual tem de ser maior que zero")
    row = {"Produto": produto, "Custo_Manual": custo}
    upsert_by_key(MARGIN_MANUAL_COSTS_PATH, row, "Produto")
    reset_data_cache()
    return {"ok": True, "row": row}


def api_delete_manual_cost(body: dict[str, Any]) -> dict[str, Any]:
    produto = body_str(body, "Produto")
    if not produto:
        raise ValueError("Produto é obrigatório")
    delete_by_key(MARGIN_MANUAL_COSTS_PATH, "Produto", produto)
    reset_data_cache()
    return {"ok": True}


def api_save_product_mapping(body: dict[str, Any]) -> dict[str, Any]:
    produto_pos = body_str(body, "Produto_POS")
    produto_custo = body_str(body, "Produto_Custo")
    multiplicador = body_float(body, "Multiplicador", 1.0)
    if not produto_pos or not produto_custo:
        raise ValueError("Produto_POS e Produto_Custo são obrigatórios")
    if multiplicador <= 0:
        raise ValueError("Multiplicador tem de ser maior que zero")
    row = {"Produto_POS": produto_pos, "Produto_Custo": produto_custo, "Multiplicador": multiplicador}
    upsert_by_key(PRODUCT_MAPPING_PATH, row, "Produto_POS")
    reset_data_cache()
    return {"ok": True, "row": row}


def api_delete_product_mapping(body: dict[str, Any]) -> dict[str, Any]:
    produto = body_str(body, "Produto_POS")
    if not produto:
        raise ValueError("Produto_POS é obrigatório")
    delete_by_key(PRODUCT_MAPPING_PATH, "Produto_POS", produto)
    reset_data_cache()
    return {"ok": True}


def api_save_novadis_unit_mapping(body: dict[str, Any]) -> dict[str, Any]:
    produto = body_str(body, "produto_novadis")
    unidades = body_float(body, "unidades_por_caixa")
    if not produto:
        raise ValueError("produto_novadis é obrigatório")
    if unidades <= 0:
        raise ValueError("unidades_por_caixa tem de ser maior que zero")
    row = {"produto_novadis": produto, "unidades_por_caixa": int(round(unidades))}
    upsert_by_key(NOVADIS_UNIT_MAPPING_PATH, row, "produto_novadis")
    reset_data_cache()
    return {"ok": True, "row": row}


def api_save_op_costs(body: dict[str, Any]) -> dict[str, Any]:
    rows = body.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError("rows deve ser uma lista")
    normalized = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        categoria = str(item.get("Categoria", "")).strip()
        subcategoria = str(item.get("Subcategoria", "")).strip()
        if not categoria or not subcategoria:
            continue
        valor = float(item.get("Valor_Mensal", 0) or 0)
        if valor < 0:
            raise ValueError("Valor_Mensal não pode ser negativo")
        normalized.append(
            {
                "Categoria": categoria,
                "Subcategoria": subcategoria,
                "Valor_Mensal": valor,
                "Tipo": str(item.get("Tipo", "Fixo") or "Fixo").strip(),
                "Notas": str(item.get("Notas", "") or "").strip(),
            }
        )
    if not normalized:
        raise ValueError("Nenhum custo operacional válido")
    df = pd.DataFrame(normalized)
    write_csv_atomic(OP_COSTS_PATH, df)
    reset_data_cache()
    return {"ok": True, "rows": table_records(df)}


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "CafeMartinsWeb/0.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"{self.address_string()} - {fmt % args}")

    def get_session(self) -> dict[str, Any] | None:
        cookie_header = self.headers.get("Cookie")
        if not cookie_header:
            return None
        cookie = SimpleCookie(cookie_header)
        morsel = cookie.get(SESSION_COOKIE)
        return verify_session_cookie(morsel.value if morsel else None)

    def require_auth(self) -> bool:
        if self.get_session():
            return True
        self.send_json({"error": "unauthorized"}, HTTPStatus.UNAUTHORIZED)
        return False

    def send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK, headers: dict[str, str] | None = None) -> None:
        data = json.dumps(payload, default=json_default, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        data = path.read_bytes()
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if path.name == "index.html":
            content_type = "text/html; charset=utf-8"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def read_json_body(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            if path == "/":
                self.send_file(STATIC_DIR / "index.html")
            elif path == "/favicon.ico":
                self.send_response(HTTPStatus.NO_CONTENT)
                self.end_headers()
            elif path == "/assets/plotly.min.js":
                import plotly

                plotly_path = Path(plotly.__file__).parent / "package_data" / "plotly.min.js"
                self.send_file(plotly_path)
            elif path.startswith("/static/"):
                self.send_file(STATIC_DIR / path.removeprefix("/static/"))
            elif path == "/api/session":
                session = self.get_session()
                self.send_json({"authenticated": bool(session), "name": session.get("name") if session else None})
            elif path == "/api/meta":
                if self.require_auth():
                    self.send_json(build_meta())
            elif path == "/api/cockpit":
                if self.require_auth():
                    self.send_json(build_cockpit(parse_qs(parsed.query)))
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
        except Exception as exc:
            print(f"Erro GET {path}: {exc}")
            self.send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/":
            head_path = STATIC_DIR / "index.html"
            content_type = "text/html; charset=utf-8"
        elif path.startswith("/static/"):
            head_path = STATIC_DIR / path.removeprefix("/static/")
            content_type = mimetypes.guess_type(str(head_path))[0] or "application/octet-stream"
        elif path == "/favicon.ico":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return
        else:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if not head_path.exists() or not head_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        data_size = head_path.stat().st_size
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(data_size))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/login":
                body = self.read_json_body()
                user = authenticate(str(body.get("username", "")), str(body.get("password", "")))
                if not user:
                    self.send_json({"error": "Credenciais inválidas"}, HTTPStatus.UNAUTHORIZED)
                    return
                token = secrets.token_urlsafe(32)
                SESSIONS[token] = {
                    "username": user["username"],
                    "name": user["name"],
                    "expires_at": time.time() + 30 * 24 * 60 * 60,
                }
                cookie = make_session_cookie(token)
                self.send_json(
                    {"authenticated": True, "name": user["name"]},
                    headers={
                        "Set-Cookie": f"{SESSION_COOKIE}={cookie}; Path=/; HttpOnly; SameSite=Lax; Max-Age={30 * 24 * 60 * 60}",
                    },
                )
            elif path == "/api/logout":
                session_cookie = SimpleCookie(self.headers.get("Cookie", "")).get(SESSION_COOKIE)
                if session_cookie and "." in session_cookie.value:
                    token = session_cookie.value.rsplit(".", 1)[0]
                    SESSIONS.pop(token, None)
                self.send_json({"ok": True}, headers={"Set-Cookie": f"{SESSION_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax"})
            elif path == "/api/refresh":
                if self.require_auth():
                    load_data(force=True)
                    self.send_json({"ok": True, "loaded_at": DATA_CACHE["loaded_at"]})
            elif path == "/api/fichas/save":
                if self.require_auth():
                    self.send_json(api_save_ficha(self.read_json_body()))
            elif path == "/api/fichas/delete":
                if self.require_auth():
                    self.send_json(api_delete_ficha(self.read_json_body()))
            elif path == "/api/fichas/composite":
                if self.require_auth():
                    self.send_json(api_save_composite(self.read_json_body()))
            elif path == "/api/margins/manual-cost/save":
                if self.require_auth():
                    self.send_json(api_save_manual_cost(self.read_json_body()))
            elif path == "/api/margins/manual-cost/delete":
                if self.require_auth():
                    self.send_json(api_delete_manual_cost(self.read_json_body()))
            elif path == "/api/margins/mapping/save":
                if self.require_auth():
                    self.send_json(api_save_product_mapping(self.read_json_body()))
            elif path == "/api/margins/mapping/delete":
                if self.require_auth():
                    self.send_json(api_delete_product_mapping(self.read_json_body()))
            elif path == "/api/novadis/unit-map/save":
                if self.require_auth():
                    self.send_json(api_save_novadis_unit_mapping(self.read_json_body()))
            elif path == "/api/custos-operacionais/save":
                if self.require_auth():
                    self.send_json(api_save_op_costs(self.read_json_body()))
            else:
                self.send_error(HTTPStatus.NOT_FOUND)
        except Exception as exc:
            print(f"Erro POST {path}: {exc}")
            self.send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8504)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), DashboardHandler)
    print(f"Cafe Martins web dashboard listening on http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
