import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE A STYLING ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding: 0rem 0.5rem !important; max-width: 100% !important; }
    
    .custom-head { font-size: 1.1rem; font-weight: bold; margin: 0.3rem 0; }

    /* Součty v rámečcích */
    .metric-box {
        border: 1px solid #d1d5db;
        background-color: #f9fafb;
        padding: 4px 8px;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 5px;
    }
    .metric-label { font-size: 0.65rem; color: #6b7280; text-transform: uppercase; }
    .metric-value { font-size: 0.85rem; font-weight: bold; color: #111827; }

    /* TABULKA KONTEJNER - OMEZENO NA 16 ŘÁDKŮ */
    .table-container {
        height: 400px; 
        overflow-y: scroll;
        overflow-x: auto;
        border: 1px solid #000;
    }
    
    /* POSUVNÍK */
    .table-container::-webkit-scrollbar { width: 35px; height: 35px; }
    .table-container::-webkit-scrollbar-track { background: #f1f1f1; }
    .table-container::-webkit-scrollbar-thumb { background: #888; border: 5px solid #f1f1f1; }

    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 12px; table-layout: fixed; }
    
    /* ZÁHLAVÍ - ŠEDÉ DLE PŘÁNÍ */
    .html-table th { 
        position: sticky; top: 0; 
        background-color: #f3f4f6; border: 1px solid #000;
        padding: 5px; z-index: 10; text-align: center;
    }
    .cat-header { font-weight: bold; text-transform: lowercase; font-size: 13px; }
    
    /* Širší podsloupce pro čísla */
    .col-sub { width: 90px; font-weight: bold; }

    .html-table td { padding: 4px 6px; border: 1px solid #000; white-space: nowrap; overflow: hidden; }
    .red-bold { color: #dc2626; font-weight: bold; text-align: right; }
    .num-align { text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=5, header=None, engine='openpyxl')
        df = df.dropna(how='all')
        # Likvidace NaT a nan
        df = df.replace({np.nan: '', 'nan': '', 'NaT': '', 'None': ''})
        return df
    except: return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # Horní lišta
    c_h1, c_h2 = st.columns([1, 5])
    with c_h1: st.markdown('<div class="custom-head">Evidence 2026</div>', unsafe_allow_html=True)
    with c_h2: hledat = st.text_input("", placeholder="Hledat...", label_visibility="collapsed")

    # Filtrování
    df = df_raw.copy()
    if hledat:
        df = df[df.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    # --- 3. SOUČTY ---
    def get_sum(col_idx):
        vals = pd.to_numeric(df[col_idx], errors='coerce').fillna(0)
        return vals.sum()

    m = st.columns(5)
    celkem_val = get_sum(10) # Sloupec 'nabídka'
    zakazek_cnt = len(df[df[0] != ''])
    
    m_labels = ["CELKEM", "HOTOVO", "FAKTURACE", "PROBÍHÁ", "ZAKÁZEK"]
    m_vals = [f"{celkem_val:,.2f}".replace(",", " ") + " Kč", "0.00 Kč", "0.00 Kč", "0.00 Kč", str(zakazek_cnt)]
    
    for i in range(5):
        m[i].markdown(f'<div class="metric-box"><div class="metric-label">{m_labels[i]}</div><div class="metric-value">{m_vals[i]}</div></div>', unsafe_allow_html=True)

    # --- 4. HTML TABULKA ---
    html = '<div class="table-container"><table class="html-table">'
    
    # Nastavení šířek sloupců (colgroup) - PS, SNK, BO rozšířeny na 90px
    html += '<colgroup>'
    html += '<col style="width:40px"><col style="width:100px">' # poř, firma
    html += '<col style="width:90px"><col style="width:90px"><col style="width:90px">' # Kategorie I
    html += '<col style="width:90px"><col style="width:90px"><col style="width:90px">' # Kategorie II
    html += '<col style="width:90px"><col style="width:250px">' # č.stavby, název
    html += '<col style="width:100px"><col style="width:100px"><col style="width:100px">' # nabídka, rozdíl, vyfakt
    html += '</colgroup>'

    # Hlavička
    html += '<thead><tr>'
    html += '<th rowspan="2">poř.č.</th>'
    html += '<th rowspan="2">firma</th>'
    html += '<th colspan="3" class="cat-header">kategorie I</th>'
    html += '<th colspan="3" class="cat-header">kategorie II</th>'
    html += '<th rowspan="2">č.stavby</th>'
    html += '<th rowspan="2">název stavby</th>'
    html += '<th rowspan="2">nabídka</th>'
    html += '<th rowspan="2">rozdíl</th>'
    html += '<th rowspan="2">vyfaktur.</th>'
    html += '<th rowspan="2">ukončení</th>'
    html += '<th rowspan="2">zrealizováno</th>'
    html += '<th rowspan="2">SOD</th>'
    html += '<th rowspan="2">ze dne</th>'
    html += '<th rowspan="2">objednatel</th>'
    html += '<th rowspan="2">stavbyvedoucí</th>'
    html += '</tr>'
    
    html += '<tr>'
    html += '<th class="col-sub">PS</th><th class="col-sub">SNK</th><th class="col-sub">BO</th>'
    html += '<th class="col-sub">PS</th><th class="col-sub">BO</th><th class="col-sub">poruch</th>'
    html += '</tr></thead><tbody>'

    # Výpis dat
    for _, row in df.iterrows():
        html += '<tr>'
        for i, val in enumerate(row):
            if i > 18: break
            
            td_cls = ""
            v_str = str(val)

            # Čísla a peníze
            if i in [2,3,4,5,6,7,10,11,12]:
                try:
                    n = float(val)
                    v_str = f"{n:.2f}"
                    td_cls = ' class="num-align"'
                    if i == 11 and n < 0: td_cls = ' class="red-bold"'
                except: pass
            
            # Data
            elif i in [13, 14, 16]:
                try: v_str = pd.to_datetime(val).strftime('%d.%m.%Y')
                except: pass

            html += f'<td{td_cls}>{v_str}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)
else:
    st.error("Data nenalezena.")
