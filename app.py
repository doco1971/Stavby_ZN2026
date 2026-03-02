import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-left: 2rem; padding-right: 2rem; max-width: 100%; }
    .stApp { background-color: #f8fafc; }
    
    /* Karty se součty */
    div[data-testid="stMetric"] { 
        border: 1px solid #e2e8f0; 
        background-color: #ffffff;
        padding: 10px !important;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all').dropna(axis=1, how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

df_all = load_data()

if not df_all.empty:
    cols = df_all.columns.tolist()
    
    # Identifikace sloupců
    col_nabidka = next((c for c in cols if 'nabídka' in c.lower()), None)
    col_rozdil = next((c for c in cols if 'rozdíl' in c.lower()), None)
    col_stav = next((c for c in cols if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_vedouci = next((c for c in cols if 'vedoucí' in c.lower()), None)
    
    # Převod na čísla
    fin_cols = [c for c in [col_nabidka, col_rozdil] if c]
    for c in fin_cols:
        df_all[c] = pd.to_numeric(df_all[c], errors='coerce').fillna(0)

    # Čištění datumů (pouze textový formát pro stabilitu)
    for c in cols:
        if 'dne' in c.lower() or 'ukončení' in c.lower():
            df_all[c] = pd.to_datetime(df_all[c], errors='coerce').dt.strftime('%d.%m.%Y')
            df_all[c] = df_all[c].replace('NaT', '')

    # --- 3. FILTRY ---
    st.subheader("🏗️ Evidence zakázek 2026")
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1: hledat = st.text_input("Hledat", placeholder="Rychlé hledání...")
    with f2:
        v_opt = ["Všichni"] + sorted([str(x) for x in df_all[col_vedouci].dropna().unique()]) if col_vedouci else ["Všichni"]
        sel_v = st.selectbox("Vedoucí", v_opt)
    with f3:
        s_opt = ["Všechny stavy"] + sorted([str(x) for x in df_all[col_stav].dropna().unique()]) if col_stav else ["Všechny stavy"]
        sel_s = st.selectbox("Stav", s_opt)

    # Filtrování dat
    df_f = df_all.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
    if col_vedouci and sel_v != "Všichni":
        df_f = df_f[df_f[col_vedouci].astype(str) == sel_v]
    if col_stav and sel_s != "Všechny stavy":
        df_f = df_f[df_f[col_stav].astype(str) == sel_s]

    # --- 4. SOUČTY ---
    def fmt_num(val):
        return f"{val:,.2f}".replace(",", " ").replace(".", ",") + " Kč"

    m1, m2, m3, m4, m5 = st.columns(5)
    def get_sum(kw):
        return df_f[df_f[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_nabidka].sum() if col_stav and col_nabidka else 0

    m1.metric("CELKEM", fmt_num(df_f[col_nabidka].sum()) if col_nabidka else "0 Kč")
    m2.metric("HOTOVO", fmt_num(get_sum('hotov')))
    m3.metric("FAKTURACE", fmt_num(get_sum('faktur')))
    m4.metric("PROBÍHÁ", fmt_num(get_sum('probíh')))
    m5.metric("STAVEB", len(df_f))

    # --- 5. TABULKA (Styling) ---
    def apply_style(row):
        styles = [''] * len(row)
        if col_stav:
            s = str(row[col_stav]).lower()
            color = ''
            if 'hotov' in s: color = 'background-color: #f1fcf4'
            elif 'probíh' in s: color = 'background-color: #fffdf2'
            elif 'faktur' in s: color = 'background-color: #f0f7ff'
            styles = [color] * len(row)
        if col_rozdil:
            idx = row.index.get_loc(col_rozdil)
            if float(row[col_rozdil]) < 0:
                styles[idx] += '; color: #d00000; font-weight: bold;'
        return styles

    # Finální formát čísel pro tabulku
    format_map = {c: "{:,.2f}".format for c in fin_cols}

    st.dataframe(
        df_f.style.apply(apply_style, axis=1).format(format_map, thousands=" ", decimal="."),
        use_container_width=True, 
        height=550, # Snížená výška, aby byl posuvník hned vidět
        hide_index=True
    )
    
else:
    st.error("Data nebyla nalezena.")
