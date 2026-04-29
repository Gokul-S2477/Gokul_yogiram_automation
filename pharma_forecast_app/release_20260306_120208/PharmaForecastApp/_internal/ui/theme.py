import streamlit as st


PALETTES = {
    "light": {
        "bg": "linear-gradient(160deg, #eef6ff 0%, #f6fff8 55%, #fbfdff 100%)",
        "surface": "#ffffff",
        "surface_alt": "#f7fbff",
        "sidebar": "#f4f9ff",
        "text": "#0f172a",
        "muted": "#475569",
        "border": "#d5e6fb",
        "input_bg": "#ffffff",
        "input_border": "#bad4ff",
        "input_bg_hover": "#f0f7ff",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "download": "#16a34a",
        "download_hover": "#15803d",
        "button_text": "#ffffff",
        "shadow": "0 12px 30px rgba(15, 23, 42, 0.10)",
    },
    "dark": {
        "bg": "linear-gradient(165deg, #0c1320 0%, #0d1924 58%, #101a2a 100%)",
        "surface": "#131f30",
        "surface_alt": "#18263a",
        "sidebar": "#111b2b",
        "text": "#e2e8f0",
        "muted": "#9fb2c8",
        "border": "#31455f",
        "input_bg": "#0f1827",
        "input_border": "#425a78",
        "input_bg_hover": "#162235",
        "accent": "#60a5fa",
        "accent_hover": "#3b82f6",
        "download": "#22c55e",
        "download_hover": "#16a34a",
        "button_text": "#ffffff",
        "shadow": "0 14px 32px rgba(2, 6, 23, 0.62)",
    },
}


def apply_app_theme(mode="light"):
    p = PALETTES.get(mode, PALETTES["light"])

    st.markdown(
        f"""
        <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {{
            background: {p["bg"]} !important;
            color: {p["text"]} !important;
            font-family: 'Segoe UI', Arial, sans-serif !important;
        }}

        [data-testid="stHeader"] {{
            background: transparent !important;
        }}

        [data-testid="stMain"] > div {{
            max-width: 1280px;
            padding-top: 0.8rem;
        }}

        [data-testid="stSidebar"] > div {{
            background: {p["sidebar"]} !important;
            border-right: 1px solid {p["border"]};
        }}

        .hub-hero, .forecast-hero {{
            background: {p["surface"]};
            border: 1px solid {p["border"]};
            border-radius: 20px;
            padding: 1.15rem 1.2rem;
            box-shadow: {p["shadow"]};
        }}

        .hub-title, .forecast-title {{
            font-size: 1.65rem;
            font-weight: 800;
            color: {p["text"]};
            margin-bottom: 0.2rem;
            line-height: 1.2;
        }}

        .hub-subtitle, .forecast-subtitle {{
            font-size: 0.95rem;
            color: {p["muted"]};
            line-height: 1.45;
            margin-bottom: 0;
        }}

        .module-card {{
            background: {p["surface"]};
            border: 1px solid {p["border"]};
            border-radius: 16px;
            box-shadow: {p["shadow"]};
            padding: 0.95rem 1rem;
            margin-bottom: 0.55rem;
        }}

        .module-status {{
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 700;
            padding: 0.2rem 0.56rem;
            border-radius: 999px;
            margin-bottom: 0.45rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .status-live {{
            color: #14532d;
            background: rgba(34, 197, 94, 0.18);
            border: 1px solid rgba(34, 197, 94, 0.36);
        }}

        .status-coming {{
            color: #92400e;
            background: rgba(245, 158, 11, 0.20);
            border: 1px solid rgba(245, 158, 11, 0.36);
        }}

        .module-name {{
            color: {p["text"]};
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }}

        .module-desc {{
            color: {p["muted"]};
            font-size: 0.9rem;
            line-height: 1.4;
        }}

        div.stButton > button {{
            border: 0 !important;
            border-radius: 11px !important;
            background: {p["accent"]} !important;
            color: {p["button_text"]} !important;
            font-weight: 700 !important;
            border: 1px solid {p["accent"]} !important;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.22) !important;
            transition: transform 120ms ease, filter 120ms ease;
        }}

        div.stButton > button * {{
            color: {p["button_text"]} !important;
            fill: {p["button_text"]} !important;
        }}

        div.stButton > button:hover {{
            background: {p["accent_hover"]} !important;
            border-color: {p["accent_hover"]} !important;
            transform: translateY(-1px);
            filter: saturate(1.04);
        }}

        div.stButton > button:disabled {{
            background: #b3bfce !important;
            color: #f8fafc !important;
            border-color: #b3bfce !important;
            box-shadow: none !important;
        }}

        div.stButton > button:disabled * {{
            color: #f8fafc !important;
            fill: #f8fafc !important;
        }}

        div.stDownloadButton > button {{
            border: 1px solid {p["download"]} !important;
            border-radius: 11px !important;
            background: {p["download"]} !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            box-shadow: 0 8px 20px rgba(22, 163, 74, 0.25) !important;
            transition: transform 120ms ease, filter 120ms ease;
        }}

        div.stDownloadButton > button * {{
            color: #ffffff !important;
            fill: #ffffff !important;
        }}

        div.stDownloadButton > button:hover {{
            background: {p["download_hover"]} !important;
            border-color: {p["download_hover"]} !important;
            transform: translateY(-1px);
            filter: saturate(1.04);
        }}

        [data-testid="stFileUploaderDropzone"] {{
            background: {p["input_bg"]} !important;
            border: 2px dashed {p["input_border"]} !important;
            border-radius: 14px !important;
        }}

        [data-testid="stFileUploaderDropzone"]:hover {{
            background: {p["input_bg_hover"]} !important;
            border-color: {p["accent"]} !important;
        }}

        [data-testid="stFileUploaderDropzone"] * {{
            color: {p["text"]} !important;
        }}

        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div,
        [data-testid="stDateInput"] > div > div,
        [data-testid="stTextInput"] > div > div,
        [data-testid="stNumberInput"] > div > div,
        textarea {{
            background: {p["input_bg"]} !important;
            border: 1px solid {p["input_border"]} !important;
            border-radius: 12px !important;
            color: {p["text"]} !important;
            box-shadow: none !important;
        }}

        [data-baseweb="select"] * {{
            color: {p["text"]} !important;
        }}

        input, textarea {{
            color: {p["text"]} !important;
        }}

        [data-baseweb="input"] > div:focus-within,
        [data-baseweb="select"] > div:focus-within,
        [data-testid="stDateInput"] > div > div:focus-within {{
            border-color: {p["accent"]} !important;
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.18) !important;
        }}

        label, p, h1, h2, h3, h4, h5, h6 {{
            color: {p["text"]} !important;
        }}

        [data-testid="stMarkdownContainer"] p {{
            color: {p["muted"]} !important;
        }}

        [data-testid="stAlert"] {{
            border-radius: 12px !important;
            border: 1px solid {p["border"]} !important;
            background: {p["surface"]} !important;
        }}

        [data-testid="stDataFrame"] {{
            border: 1px solid {p["border"]} !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            background: {p["surface"]} !important;
            box-shadow: {p["shadow"]};
        }}

        [data-testid="stDataFrame"] * {{
            color: {p["text"]} !important;
        }}

        hr {{
            border-top: 1px solid {p["border"]} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
