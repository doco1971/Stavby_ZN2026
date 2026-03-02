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
    
    .custom-head { font-size: 1.2rem; font-weight: bold; margin: 0.5rem 0; }

    /* Součty v rámečcích */
    .metric-box {
        border: 1px solid #d1d5db;
        background-color: #f9fafb;
        padding: 5px 10px;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-label { font-size: 0.7rem; color: #6b7280; text-transform: uppercase; }
    .metric-value { font-size: 0.9rem; font-weight: bold; color: #111827; }

    /* TABULKA KONTEJNER */
    .table-container {
        height: 500px; 
        overflow-y: scroll;
        overflow-x: auto;
        border: 1px solid #000;
    }
    
    /* POSUVNÍK */
    .table-container::-webkit-scrollbar { width: 35px; height: 35px; }
    .table-container::-webkit-scrollbar-track { background: #f1f1f1; }
    .table-container::-webkit-scrollbar-thumb { background: #888; border: 5px solid #f1f1f1; }

    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 13px; table-layout: fixed; }
    
    /* ZÁHLAVÍ */
    .html-table th { 
        position: sticky; top: 0; 
        background-color: #f3f4f6; border: 1px solid #000;
        padding: 6px; z-index: 10; text-align: center;
        overflow: hidden;
    }
    /* Shodná šířka kategorií a jejich sloupců */
    .cat-header { width: 180px; font-weight: bold; text-transform: lowercase; font-size: 15px; }
    .cat-i { background-color: #ffff00 !important; } 
    .cat-ii { background-color: #00ffff !important; }
    .col-sub { width: 60px; font-weight: bold; }

    .html-table td { padding: 5px; border: 1px solid #000; white-space: nowrap; overflow: hidden; }
    .red-bold { color: #dc2626; font-weight: bold; text-align: right; }
    .num-align { text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=1)
def load_data():
    try:
        # Čteme data od řádku 6 (pod hlavičkami)
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=5, header=None, engine='openpyxl')
        df = df.dropna(how='all')
        # Totální vyčištění nan/NaT
        df = df.replace({np.nan: '', 'nan': '', 'NaT': '', 'None': ''})
        return df
    except: return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # Horní lišta: Nadpis + Hledání
    c_h1, c_h2 = st.columns([1, 4])
    with c_h1: st.markdown('<div class="custom-head">Evidence 2026</div>', unsafe_allow_html=True)
    with c_h2: hledat = st.text_input("", placeholder="Hledat...", label_visibility="collapsed")

    # Filtrování
    df = df_raw.copy()
    if hledat:
        df = df[df.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    # --- 3. SOUČTY (METRIKY) ---
    def get_sum(col_idx):
        vals = pd.to_numeric(df[col_idx], errors='coerce').fillna(0)
        return vals.sum()

    m = st.columns(5)
    # Předpokládané indexy sloupců: 10=nabídka, 21=částka bez DPH
    # Uprav indexy [10] podle potřeby, pokud součty nesedí
    celkem_val = get_sum(10) 
    zakazek_cnt = len(df[df[0] != '']) # Počet řádků kde je poř.č.
    
    m_labels = ["CELKEM", "HOTOVO", "FAKTURACE", "PROBÍHÁ", "ZAKÁZEK"]
    m_vals = [f"{celkem_val:,.2f}".replace(",", " ") + " Kč", "0.00 Kč", "0.00 Kč", "0.00 Kč", str(zakazek_cnt)]
    
    for i in range(5):
        m[i].markdown(f'<div class="metric-box"><div class="metric-label">{m_labels[i]}</div><div class="metric-value">{m_vals[i]}</div></div>', unsafe_allow_html=True)

    # --- 4. HTML TABULKA S PŘESNÝM ZÁHLAVÍM ---
    html = '<div class="table-container"><table class="html-table">'
    
    # Definice šířek ostatních sloupců
    html += '<colgroup>'
    html += '<col style="width:40px"><col style="width:100px">' # poř, firma
    html += '<col style="width:60px"><col style="width:60px"><col style="width:60px">' # Kat I (3x60=180)
    html += '<col style="width:60px"><col style="width:60px"><col style="width:60px">' # Kat II (3x60=180)
    html += '<col style="width:90px"><col style="width:250px">' # č.stavby, název
    html += '<col style="width:90px"><col style="width:90px"><col style="width:90px">' # nabídka, rozdíl, vyfakt
    html += '</colgroup>'

    # Hlavička - Řádek 1
    html += '<thead><tr>'
    html += '<th rowspan="2" style="width:40px">poř.č.</th>'
    html += '<th rowspan="2" style="width:80px">firma</th>'
    html += '<th colspan="3" class="cat-header cat-i">kategorie I</th>'
    html += '<th colspan="3" class="cat-header cat-ii">kategorie II</th>'
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
    
    # Hlavička - Řádek 2
    html += '<tr>'
    html += '<th class="col-sub">PS</th><th class="col-sub">SNK</th><th class="col-sub">BO</th>'
    html += '<th class="col-sub">PS</th><th class="col-sub">BO</th><th class="col-sub">poruch</th>'
    html += '</tr></thead><tbody>'

    # Výpis dat
    for _, row in df.iterrows():
        html += '<tr>'
        for i, val in enumerate(row):
            if i > 18: break # Omezení na sloupce definované v hlavičce
            
            td_cls = ""
            v_str = str(val)

            # Formátování čísel
            if i in [2,3,4,5,6,7,10,11,12]:
                try:
                    n = float(val)
                    v_str = f"{n:.2f}"
                    td_cls = ' class="num-align"'
                    if i == 11 and n < 0: td_cls = ' class="red-bold"'
                except: pass
            
            # Formátování dat (ukončení, zrealizováno, ze dne)
            elif i in [13, 14, 16]:
                try: v_str = pd.to_datetime(val).strftime('%d.%m.%Y')
                except: pass

            html += f'<td{td_cls}>{v_str}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)
else:
    st.error("Soubor nenalezen nebo je prázdný.")
