import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A ŠIROKÝ POSUVNÍK ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 0.5rem !important; padding-left: 1rem !important; padding-right: 1rem !important; max-width: 100% !important; }
    .stApp { background-color: #f4f6f8; }
    
    /* ŠIRŠÍ A STÁLE VIDITELNÝ POSUVNÍK */
    ::-webkit-scrollbar {
        width: 14px !important;
        height: 14px !important;
        display: block !important;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #888 !important;
        border-radius: 5px !important;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555 !important;
    }
    
    /* Kompaktní metriky */
    div[data-testid="stMetric"] { 
        border: 1px solid #e2e8f0; 
        background-color: #ffffff;
        padding: 4px 8px !important;
        border-radius: 4px;
        height: 48px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 0.95rem !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        # Ponechat jen řádky s ID
        df = df[df[df.columns[0]].notna()]
        return df
    except:
        return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    cols = df_raw.columns.tolist()
    # Najít sloupce (Nabídka, Rozdíl, Bez DPH atd.)
    fin_cols = [c for c in cols if any(x in c.lower() for x in ['nabídka', 'rozdíl', 'bez dph', 'vyfaktur'])]
    col_stav = next((c for c in cols if 'stav' in c.lower() and 'název' not in c.lower()), None)

    # Převod na čísla
    for c in fin_cols:
        df_raw[c] = pd.to_numeric(df_raw[c], errors='coerce').fillna(0)

    # Formátování dat (text)
    for c in cols:
        if any(x in c.lower() for x in ['dne', 'ukončení']):
            df_raw[c] = pd.to_datetime(df_raw[c], errors='coerce').dt.strftime('%d.%m.%Y').replace('NaT', '')

    # --- 3. LIŠTA A FILTR ---
    c1, c2 = st.columns([1, 3])
    with c1: st.markdown("#### 🏗️ Evidence 2026")
    with c2: hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat...")

    df_f = df_raw.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    # --- 4. SOUČTY ---
    def fmt_num(val):
        return f"{val:,.2f}".replace(",", " ").replace(".", ",") + " Kč"

    m1, m2, m3, m4, m5 = st.columns(5)
    col_n = next((c for c in fin_cols if 'nabídka' in c.lower()), fin_cols[0] if fin_cols else None)
    
    def get_sum(kw):
        if col_stav and col_n:
            return df_f[df_f[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_n].sum()
        return 0

    m1.metric("CELKEM", fmt_num(df_f[col_n].sum()) if col_n else "0 Kč")
    m2.metric("HOTOVO", fmt_num(get_sum('hotov')))
    m3.metric("FAKTURACE", fmt_num(get_sum('faktur')))
    m4.metric("PROBÍHÁ", fmt_num(get_sum('probíh')))
    m5.metric("ZAKÁZEK", len(df_f))

    # --- 5. TABULKA (Klíčová část) ---
    def style_row(row):
        styles = [''] * len(row)
        if col_stav:
            s = str(row[col_stav]).lower()
            color = ''
            if 'hotov' in s: color = 'background-color: #f1fcf4'
            elif 'probíh' in s: color = 'background-color: #fffdf2'
            elif 'faktur' in s: color = 'background-color: #f0f7ff'
            styles = [color] * len(row)
        
        # Červený rozdíl
        col_r = next((c for c in fin_cols if 'rozdíl' in c.lower()), None)
        if col_r:
            idx = row.index.get_loc(col_r)
            if float(row[col_r]) < 0:
                styles[idx] += '; color: #d00000; font-weight: bold;'
        return styles

    # KONFIGURACE SLOUPCŮ - Tady vynutíme formátování
    # format="%.2f" je jediný způsob, jak zastavit 6 desetinných míst
    column_config = {
        c: st.column_config.NumberColumn(format="%.2f") for c in fin_cols
    }

    st.dataframe(
        df_f.style.apply(style_row, axis=1),
        use_container_width=True, 
        height=455, # Cca 16 řádků
        hide_index=True,
        column_config=column_config
    )
    
else:
    st.error("Data nebyla nalezena.")
