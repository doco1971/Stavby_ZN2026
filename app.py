import streamlit as st
import pandas as pd

# --- 1. NASTAVENÍ A SKRYTÍ SYSTÉMOVÉ LIŠTY ---
st.set_page_config(page_title="ZN 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 0rem; padding-bottom: 0rem; }
    h4 { margin: 0; padding: 5px 0; font-size: 1.2rem; color: #1e3a5f; font-weight: 800; }
    .stMetric { 
        padding: 2px 8px !important; 
        margin: 0 !important;
        border: 1px solid #f0f2f6; 
        background: #f8f9fc;
        border-radius: 4px;
    }
    div[data-testid="stMetricValue"] { font-size: 0.9rem !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] { font-size: 0.65rem !important; }
    div[data-testid="stVerticalBlock"] > div { margin-top: -5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=20)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

df_all = load_data()

if not df_all.empty:
    cols = df_all.columns.tolist()
    col_nabidka = next((c for c in cols if 'nabídka' in c.lower() or 'cena' in c.lower()), None)
    col_stav = next((c for c in cols if 'stav' in c.lower()), None)
    col_vedouci = next((c for c in cols if 'vedoucí' in c.lower() or 'stavbyved' in c.lower()), None)

    if col_nabidka:
        df_all[col_nabidka] = pd.to_numeric(df_all[col_nabidka], errors='coerce').fillna(0)

    # --- 3. NADPIS A FILTRY ---
    st.markdown("#### 🏗️ Evidence zakázek 2026")
    
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Rychlé hledání...")
    with f2:
        v_opt = ["Všichni vedoucí"] + sorted([str(x) for x in df_all[col_vedouci].dropna().unique()]) if col_vedouci else ["Všichni"]
        sel_v = st.selectbox("Vedoucí", v_opt, label_visibility="collapsed")
    with f3:
        s_opt = ["Všechny stavy"] + sorted([str(x) for x in df_all[col_stav].dropna().unique()]) if col_stav else ["Vše"]
        sel_s = st.selectbox("Stav", s_opt, label_visibility="collapsed")

    # Filtrování
    df_f = df_all.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
    if col_vedouci and sel_v != "Všichni vedoucí":
        df_f = df_f[df_f[col_vedouci
