import streamlit as st
import pandas as pd

# --- 1. EXTRÉMNĚ KOMPAKTNÍ STYL ---
st.set_page_config(page_title="ZN 2026", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0rem; }
    h4 { margin: 0; padding: 0; font-size: 1.1rem; color: #1e3a5f; }
    .stMetric { 
        padding: 0px 5px !important; 
        margin: 0 !important;
        border: 1px solid #f0f2f6; 
        background: #f8f9fc;
    }
    div[data-testid="stMetricValue"] { font-size: 0.95rem !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    div[data-testid="stExpander"] { border: none !important; }
    .stSelectbox, .stTextInput { margin-bottom: -10px; }
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

    # --- 3. JEDEN ŘÁDEK: NADPIS A FILTRY ---
    st.markdown("#### 🏗️ Evidence 2026")
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat...")
    with c2:
        v_opt = ["Všichni"] + sorted([str(x) for x in df_all[col_vedouci].dropna().unique()]) if col_vedouci else ["Všichni"]
        sel_v = st.selectbox("Vedoucí", v_opt, label_visibility="collapsed")
    with c3:
        s_opt = ["Vše"] + sorted([str(x) for x in df_all[col_stav].dropna().unique()]) if col_stav else ["Vše"]
        sel_s = st.selectbox("Stav", s_opt, label_visibility="collapsed")

    # Filtrování
    df_f = df_all.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
    if col_vedouci and sel_v != "Všichni":
        df_f = df_f[df_f[col_vedouci].astype(str) == sel_v]
    if col_stav and sel_s != "Vše":
        df_f = df_f[df_f[col_stav].astype(str) == sel_s]

    # --- 4. SOUČTY (V jednom řádku pod filtry) ---
    if col_nabidka:
        m1, m2, m3, m4, m5 = st.columns(5)
        
        def get_sum(kw):
            return df_f[df_f[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_nabidka].sum() if col_stav else 0

        m1.metric("CELKEM", f"{df_f[col_nabidka].sum():,.0f} Kč".replace(',', ' '))
        m2.metric("HOTOVO", f"{get_sum('hotov'):,.0f} Kč".replace(',', ' '))
        m3.metric("FAKTURACE", f"{get_sum('faktur'):,.0f} Kč".replace(',', ' '))
        m4.metric("PROBÍHÁ", f"{get_sum('probíh'):,.0f} Kč".replace(',', ' '))
        m5.metric("STAVEB", len(df_f))

    # --- 5. TABULKA (Teď zabírá zbytek obrazovky) ---
    st.dataframe(df_f, use_container_width=True, height=750)
    
else:
    st.error("Soubor nenalezen.")
