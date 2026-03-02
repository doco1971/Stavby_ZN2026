import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-left: 1.5rem; padding-right: 1.5rem; max-width: 100%; }
    .stApp { background-color: #f8fafc; }
    
    /* Karty se součty - čistší vzhled */
    div[data-testid="stMetric"] { 
        border: 1px solid #e2e8f0; 
        background-color: #ffffff;
        padding: 10px !important;
        border-radius: 6px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricValue"] { font-size: 1.1rem !important; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ A PŘÍSNÉ ČIŠTĚNÍ DAT ---
@st.cache_data(ttl=5)
def load_data():
    try:
        # Načtení od 5. řádku
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        
        # 1. Odstranění úplně prázdných řádků
        df = df.dropna(how='all')
        
        # 2. Vyčištění názvů sloupců
        df.columns = [str(c).strip() for c in df.columns]
        
        # 3. PŘÍSNÉ FILTROVÁNÍ: Ponecháme jen řádky, kde je vyplněno pořadové číslo nebo název
        # Tím se zbavíme zbloudilých součtů zespodu Excelu, které nafukují CELKEM
        col_id = df.columns[0]
        df = df[df[col_id].notna()]
        
        return df
    except Exception as e:
        st.error(f"Chyba při načítání: {e}")
        return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # Identifikace sloupců
    cols = df_raw.columns.tolist()
    col_nabidka = next((c for c in cols if 'nabídka' in c.lower() or 'nabídková' in c.lower()), None)
    col_rozdil = next((c for c in cols if 'rozdíl' in c.lower()), None)
    col_stav = next((c for c in cols if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_vedouci = next((c for c in cols if 'vedoucí' in c.lower() or 'stavbyved' in c.lower()), None)
    
    # Sloupce s datem
    cols_date = [c for c in cols if 'dne' in c.lower() or 'ukončení' in c.lower()]

    # Převod financí na čistá čísla
    for c in [col_nabidka, col_rozdil]:
        if c:
            df_raw[c] = pd.to_numeric(df_raw[c], errors='coerce').fillna(0)

    # Formátování dat (odstranění času)
    for c in cols_date:
        df_raw[c] = pd.to_datetime(df_raw[c], errors='coerce').dt.strftime('%d.%m.%Y').replace('NaT', '')

    # --- 3. FILTRY ---
    st.markdown("#### 🏗️ Evidence zakázek 2026")
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1: hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat v zakázkách...")
    with f2:
        v_opt = ["Všichni vedoucí"] + sorted([str(x) for x in df_raw[col_vedouci].dropna().unique() if str(x).strip() != ''])
        sel_v = st.selectbox("Vedoucí", v_opt, label_visibility="collapsed")
    with f3:
        s_opt = ["Všechny stavy"] + sorted([str(x) for x in df_raw[col_stav].dropna().unique() if str(x).strip() != ''])
        sel_s = st.selectbox("Stav", s_opt, label_visibility="collapsed")

    # Aplikace filtrů na kopii dat
    df_f = df_raw.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
    if col_vedouci and sel_v != "Všichni vedoucí":
        df_f = df_f[df_f[col_vedouci].astype(str) == sel_v]
    if col_stav and sel_s != "Všechny stavy":
        df_f = df_f[df_f[col_stav].astype(str) == sel_s]

    # --- 4. SOUČTY (Přesné výpočty z vyfiltrovaných dat) ---
    def fmt_num(val):
        return f"{val:,.2f}".replace(",", " ").replace(".", ",") + " Kč"

    m1, m2, m3, m4, m5 = st.columns(5)
    
    total_val = df_f[col_nabidka].sum() if col_nabidka else 0
    
    def get_sum_status(keyword):
        if col_stav and col_nabidka:
            return df_f[df_f[col_stav].astype(str).str.contains(keyword, case=False, na=False)][col_nabidka].sum()
        return 0

    m1.metric("CELKEM", fmt_num(total_val))
    m2.metric("HOTOVO", fmt_num(get_sum_status('hotov')))
    m3.metric("FAKTURACE", fmt_num(get_sum_status('faktur')))
    m4.metric("PROBÍHÁ", fmt_num(get_sum_status('probíh')))
    m5.metric("ZAKÁZEK", len(df_f))

    # --- 5. TABULKA ---
    def style_row(row):
        styles = [''] * len(row)
        if col_stav:
            status = str(row[col_stav]).lower()
            color = ''
            if 'hotov' in status: color = 'background-color: #f1fcf4'
            elif 'probíh' in status: color = 'background-color: #fffdf2'
            elif 'faktur' in status: color = 'background-color: #f0f7ff'
            styles = [color] * len(row)
        
        if col_rozdil:
            idx = row.index.get_loc(col_rozdil)
            if float(row[col_rozdil]) < 0:
                styles[idx] += '; color: #d00000; font-weight: bold;'
        return styles

    # Finální formátování čísel pro zobrazení: 00 000 000.00
    format_map = {c: "{:,.2f}".format for c in [col_nabidka, col_rozdil] if c}

    st.dataframe(
        df_f.style.apply(style_row, axis=1).format(format_map, thousands=" ", decimal="."),
        use_container_width=True, 
        height=600,
        hide_index=True
    )
    
else:
    st.warning("Soubor je prázdný nebo nebyl nalezen.")
