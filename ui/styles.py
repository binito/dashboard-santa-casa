"""Visual system for Dashboard v10."""

import streamlit as st


def apply_global_styles():
    """Apply the app visual theme."""
    st.markdown(
        """
        <style>
        :root {
            --cm-bg: #f8f8fb;
            --cm-bg-elevated: #f1eff7;
            --cm-panel: #ffffff;
            --cm-panel-soft: #f5f3fb;
            --cm-line: #e6e3ef;
            --cm-line-strong: #d8d3e7;
            --cm-ink: #0a0833;
            --cm-muted: #6f7688;
            --cm-faint: #9aa0aa;
            --cm-navy: #0a0833;
            --cm-plum: #403e68;
            --cm-lilac: #8f8bbc;
            --cm-orange: #fa5608;
            --cm-orange-soft: #fff0e9;
            --cm-blue: #4077c9;
            --cm-green: #1f8a5f;
            --cm-green-soft: #e8f7f0;
            --cm-red: #c43d32;
            --cm-red-soft: #fff0ef;
            --cm-gold: #b98220;
            --cm-gold-soft: #fff7e6;
            --cm-shadow: 0 16px 38px rgba(10, 8, 51, 0.08);
            --cm-shadow-soft: 0 8px 22px rgba(10, 8, 51, 0.06);
            color-scheme: light;
        }

        html,
        body,
        .stApp,
        .main,
        [data-testid="stAppViewContainer"] {
            background:
                linear-gradient(180deg, #ffffff 0, var(--cm-bg) 260px) !important;
            color: var(--cm-ink) !important;
        }

        [data-testid="stHeader"] {
            background: rgba(248, 248, 251, 0.88) !important;
            border-bottom: 1px solid rgba(230, 227, 239, 0.78) !important;
            backdrop-filter: blur(12px);
        }

        .main .block-container,
        [data-testid="stMainBlockContainer"],
        [data-testid="stAppViewBlockContainer"] {
            max-width: 1500px;
            padding-top: 1.2rem !important;
            padding-bottom: 3rem !important;
        }

        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] span,
        label,
        p,
        span {
            color: inherit;
        }

        h1, h2, h3, h4, h5, h6,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4 {
            color: var(--cm-ink) !important;
            letter-spacing: 0 !important;
        }

        section[data-testid="stSidebar"] {
            background: var(--cm-navy) !important;
            border-right: 0 !important;
            box-shadow: 18px 0 34px rgba(10, 8, 51, 0.08);
        }

        section[data-testid="stSidebar"] * {
            color: #f4f2ff;
        }

        section[data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.12) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
        section[data-testid="stSidebar"] label {
            color: rgba(244, 242, 255, 0.82) !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="select"] > div,
        section[data-testid="stSidebar"] [data-baseweb="input"] > div,
        section[data-testid="stSidebar"] textarea,
        section[data-testid="stSidebar"] input {
            background: rgba(255, 255, 255, 0.08) !important;
            border-color: rgba(255, 255, 255, 0.18) !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            box-shadow: none !important;
        }

        section[data-testid="stSidebar"] [data-baseweb="tag"] {
            background: rgba(250, 86, 8, 0.18) !important;
            border-color: rgba(250, 86, 8, 0.42) !important;
            color: #ffffff !important;
            border-radius: 999px !important;
        }

        .stButton > button,
        [data-testid="stSidebar"] button {
            border-radius: 8px !important;
            border: 1px solid var(--cm-line) !important;
            background: #ffffff !important;
            color: var(--cm-ink) !important;
            box-shadow: none !important;
            font-weight: 760 !important;
            transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
        }

        .stButton > button:hover {
            background: var(--cm-panel-soft) !important;
            border-color: var(--cm-lilac) !important;
            color: var(--cm-ink) !important;
            transform: none !important;
            box-shadow: var(--cm-shadow-soft) !important;
        }

        [data-testid="stSidebar"] button {
            background: rgba(255, 255, 255, 0.08) !important;
            border-color: rgba(255, 255, 255, 0.13) !important;
            color: rgba(255, 255, 255, 0.86) !important;
        }

        [data-testid="stSidebar"] button:hover {
            background: rgba(250, 86, 8, 0.18) !important;
            border-color: rgba(250, 86, 8, 0.55) !important;
            color: #ffffff !important;
            transform: none !important;
        }

        .stButton > button[kind="primary"],
        button[kind="primary"] {
            background: var(--cm-orange) !important;
            color: #ffffff !important;
            border-color: var(--cm-orange) !important;
            font-weight: 820 !important;
            box-shadow: 0 12px 22px rgba(250, 86, 8, 0.22) !important;
        }

        .v10-shell-brand,
        .v10-login-brand {
            background: #17143f !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            box-shadow: 0 18px 40px rgba(10, 8, 51, 0.24) !important;
        }

        .v10-shell-brand {
            padding: 17px 16px 15px 16px !important;
            margin: 4px 0 18px 0 !important;
            position: relative;
            overflow: hidden;
        }

        .v10-shell-brand::before,
        .v10-login-brand::before {
            content: "";
            position: absolute;
            inset: 0 auto 0 0;
            width: 4px;
            background: var(--cm-orange);
        }

        .v10-shell-brand-title,
        .v10-shell-brand-subtitle,
        .v10-login-brand * {
            color: #ffffff !important;
        }

        .v10-shell-brand-title {
            font-size: 1.24rem !important;
            font-weight: 880 !important;
            line-height: 1.1 !important;
        }

        .v10-shell-brand-subtitle {
            color: rgba(255, 255, 255, 0.66) !important;
            font-size: 0.82rem !important;
            margin-top: 5px !important;
        }

        .v10-topbar,
        .v10-kpi,
        .v10-panel,
        .v10-module,
        .metric-card,
        div[data-testid="stMetric"] {
            background: var(--cm-panel) !important;
            color: var(--cm-ink) !important;
            border: 1px solid var(--cm-line) !important;
            border-radius: 8px !important;
            box-shadow: var(--cm-shadow-soft) !important;
        }

        .v10-topbar {
            border: 0 !important;
            border-left: 5px solid var(--cm-orange) !important;
            padding: 20px 22px !important;
            margin-bottom: 14px !important;
            box-shadow: var(--cm-shadow) !important;
        }

        .v10-title {
            color: var(--cm-ink) !important;
            font-size: 2rem !important;
            line-height: 1.08 !important;
            font-weight: 880 !important;
            margin: 0 !important;
        }

        .v10-subtitle {
            margin-top: 8px !important;
            font-size: 0.96rem !important;
            line-height: 1.45 !important;
        }

        .v10-chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 13px;
        }

        .v10-subtitle,
        .v10-module-copy,
        .v10-score-label,
        .v10-kpi-label,
        div[data-testid="stMetricLabel"],
        div[data-testid="stMetricLabel"] *,
        div[data-testid="stMetricDelta"],
        div[data-testid="stMetricDelta"] * {
            color: var(--cm-muted) !important;
        }

        .v10-chip {
            display: inline-flex;
            align-items: center;
            background: var(--cm-panel-soft) !important;
            color: var(--cm-plum) !important;
            border: 1px solid var(--cm-line-strong) !important;
            border-radius: 999px !important;
            padding: 5px 11px !important;
            font-size: 0.78rem !important;
            font-weight: 780 !important;
            white-space: nowrap;
        }

        .v10-kpi {
            border-top: 3px solid var(--cm-orange) !important;
            min-height: 126px !important;
            padding: 16px 18px !important;
        }

        div[data-testid="column"]:nth-child(2n) .v10-kpi {
            border-top-color: var(--cm-lilac) !important;
        }

        div[data-testid="column"]:nth-child(3n) .v10-kpi {
            border-top-color: var(--cm-plum) !important;
        }

        .v10-section-label {
            color: var(--cm-plum) !important;
            font-size: 0.76rem !important;
            font-weight: 880 !important;
            letter-spacing: 0 !important;
            margin: 17px 0 8px 0 !important;
            text-transform: uppercase;
        }

        .v10-kpi-label {
            color: var(--cm-muted) !important;
            font-size: 0.73rem !important;
            text-transform: uppercase;
            font-weight: 820 !important;
            letter-spacing: 0 !important;
            margin-bottom: 9px !important;
        }

        .v10-kpi-value {
            font-size: 1.8rem !important;
            font-weight: 880 !important;
            line-height: 1.08 !important;
            margin-bottom: 8px !important;
        }

        .v10-kpi-delta {
            display: block;
            font-size: 0.86rem !important;
            font-weight: 800 !important;
            line-height: 1.35 !important;
            margin-bottom: 8px !important;
        }

        .v10-kpi-value,
        .v10-score-number,
        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            color: var(--cm-ink) !important;
        }

        .v10-positive,
        .v10-kpi .v10-positive,
        [data-testid="stMarkdownContainer"] span.v10-positive {
            color: var(--cm-green) !important;
        }

        .v10-negative,
        .v10-kpi .v10-negative,
        [data-testid="stMarkdownContainer"] span.v10-negative {
            color: var(--cm-red) !important;
        }

        .v10-neutral,
        .v10-kpi .v10-neutral,
        [data-testid="stMarkdownContainer"] span.v10-neutral {
            color: var(--cm-muted) !important;
        }

        .v10-module-map {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin: 7px 0 16px 0;
        }

        .v10-module {
            padding: 13px 14px !important;
            min-height: 94px;
            background: #ffffff !important;
        }

        .v10-module-kicker {
            color: var(--cm-orange) !important;
            font-size: 0.72rem !important;
            font-weight: 860 !important;
            text-transform: uppercase;
        }

        .v10-module-title,
        .v10-panel-title {
            color: var(--cm-ink) !important;
        }

        .v10-panel {
            padding: 16px 17px !important;
            min-height: 100%;
        }

        .v10-panel-title {
            font-size: 1rem !important;
            font-weight: 840 !important;
            margin-bottom: 10px !important;
        }

        .v10-score {
            display: flex;
            align-items: baseline;
            gap: 8px;
        }

        .v10-score-number {
            font-size: 2.28rem !important;
            font-weight: 880 !important;
            line-height: 1 !important;
        }

        .v10-score-label {
            font-size: 0.88rem !important;
        }

        .v10-score-bar {
            width: 100%;
            height: 8px;
            background: var(--cm-bg-elevated);
            border-radius: 999px;
            margin: 14px 0 16px 0;
            overflow: hidden;
        }

        .v10-score-bar span {
            display: block;
            height: 100%;
            background: var(--cm-orange);
            border-radius: 999px;
        }

        .v10-panel-note {
            color: var(--cm-muted) !important;
            font-size: 0.9rem !important;
            line-height: 1.45 !important;
            margin-top: 10px !important;
        }

        .v10-action {
            border: 1px solid var(--cm-line) !important;
            border-left: 4px solid var(--cm-plum) !important;
            background: #ffffff !important;
            color: var(--cm-ink) !important;
            padding: 11px 12px !important;
            margin: 9px 0 !important;
            border-radius: 8px !important;
            line-height: 1.5 !important;
            box-shadow: 0 8px 18px rgba(10, 8, 51, 0.04);
        }

        .v10-action-high {
            border-left-color: var(--cm-red) !important;
            background: var(--cm-red-soft) !important;
        }

        .v10-action-medium {
            border-left-color: var(--cm-gold) !important;
            background: var(--cm-gold-soft) !important;
        }

        .v10-action-low {
            border-left-color: var(--cm-green) !important;
            background: var(--cm-green-soft) !important;
        }

        .v10-action-destination {
            display: block;
            color: var(--cm-orange) !important;
            font-size: 0.76rem;
            font-weight: 860;
            margin-top: 6px;
            text-transform: uppercase;
        }

        .section-divider {
            border-top-color: var(--cm-line) !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            flex-wrap: wrap !important;
            border-bottom: 0 !important;
        }

        .stTabs [data-baseweb="tab"] {
            min-height: 43px;
            height: auto !important;
            background-color: #ffffff !important;
            color: var(--cm-muted) !important;
            border: 1px solid var(--cm-line) !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            font-weight: 780 !important;
            font-size: 13px !important;
            box-shadow: 0 6px 14px rgba(10, 8, 51, 0.035) !important;
        }

        .stTabs [aria-selected="true"] {
            background-color: var(--cm-navy) !important;
            color: #ffffff !important;
            border-color: var(--cm-navy) !important;
        }

        .info-box,
        .warning-box,
        .success-box {
            color: var(--cm-ink) !important;
            border-radius: 8px !important;
            border: 1px solid var(--cm-line) !important;
        }

        .info-box {
            background: #eef5ff !important;
            border-left-color: var(--cm-blue) !important;
        }

        .warning-box {
            background: var(--cm-gold-soft) !important;
            border-left-color: var(--cm-gold) !important;
        }

        .success-box {
            background: var(--cm-green-soft) !important;
            border-left-color: var(--cm-green) !important;
        }

        div[data-testid="stExpander"] {
            background: #ffffff !important;
            border: 1px solid var(--cm-line) !important;
            border-radius: 8px !important;
            box-shadow: 0 8px 18px rgba(10, 8, 51, 0.04) !important;
        }

        div[data-testid="stExpander"] details {
            border-color: transparent !important;
        }

        div[data-testid="stExpander"] summary {
            color: var(--cm-ink) !important;
            font-weight: 760 !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stExpander"] {
            background: rgba(255, 255, 255, 0.08) !important;
            border: 1px solid rgba(255, 255, 255, 0.14) !important;
            box-shadow: none !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stExpander"] summary,
        section[data-testid="stSidebar"] div[data-testid="stExpander"] summary * {
            color: #ffffff !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stExpander"] details {
            border-color: rgba(255, 255, 255, 0.12) !important;
        }

        div[data-testid="stMetric"] {
            border-top: 3px solid var(--cm-lilac) !important;
            padding: 13px 15px !important;
        }

        div[data-testid="stPlotlyChart"],
        div[data-testid="stDataFrame"] {
            background: #ffffff !important;
            border: 1px solid var(--cm-line) !important;
            border-radius: 8px !important;
            box-shadow: var(--cm-shadow-soft) !important;
            padding: 8px !important;
        }

        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrame"] * {
            color: var(--cm-ink);
        }

        div[data-testid="stProgress"] > div > div > div {
            background-color: var(--cm-orange) !important;
        }

        .v10-login-shell {
            max-width: 520px;
            margin: 5vh auto 1rem auto;
        }

        .v10-login-brand {
            padding: 22px 24px;
            margin-bottom: 14px;
            position: relative;
            overflow: hidden;
        }

        .v10-login-title {
            font-size: 1.58rem;
            font-weight: 880;
            line-height: 1.1;
        }

        .v10-login-subtitle {
            color: rgba(255, 255, 255, 0.72) !important;
            margin-top: 6px;
            font-size: 0.92rem;
        }

        .main .block-container:has(.v10-login-shell) {
            max-width: 620px !important;
            padding-top: 2rem !important;
        }

        .main .block-container:has(.v10-login-shell) div[data-testid="stForm"] {
            background: var(--cm-panel) !important;
            border: 1px solid var(--cm-line) !important;
            border-radius: 8px !important;
            padding: 18px 18px 12px 18px !important;
            box-shadow: var(--cm-shadow) !important;
        }

        @media (max-width: 900px) {
            .main .block-container,
            [data-testid="stMainBlockContainer"],
            [data-testid="stAppViewBlockContainer"] {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .v10-module-map {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .v10-title {
                font-size: 1.68rem !important;
            }
        }

        @media (max-width: 680px) {
            .main .block-container,
            [data-testid="stMainBlockContainer"],
            [data-testid="stAppViewBlockContainer"] {
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }

            .v10-module-map {
                grid-template-columns: 1fr;
            }

            .v10-kpi {
                min-height: 112px !important;
            }

            .v10-kpi-value {
                font-size: 1.55rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_login_brand():
    """Render a compact branded login header."""
    st.markdown(
        """
        <div class="v10-login-shell">
            <div class="v10-login-brand">
                <div class="v10-login-title">Café Martins</div>
                <div class="v10-login-subtitle">Dashboard operacional e rentabilidade</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
