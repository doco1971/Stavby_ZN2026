import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE (ZACHOVÁNO) ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 0rem !important; 
        padding-left: 1.5rem !important; 
        padding-right: 1.5rem !important;
        max-width: 100% !important;
    }
    .custom-head { font-size: 1.1rem; font-weight: bold; margin-bottom: 0.3rem; }
    
    /* Metriky */
    .metric-box {
        border: 1px solid #d1d5db;
        background-color: #f9fafb;
        padding: 5px 10px;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 10px;
    }
    .cat-label { font-size: 0.6rem; color: #1f2937; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }
    .metric-label { font-size: 0.7rem; color: #6b7280; text-transform: uppercase; }
    .metric-value { font-size: 1rem; font-weight: bold; color: #111827; }

    /* TABULKA (ZACHOVÁNO 400PX) */
    .table-container { height: 400px; overflow: auto; border: 1px solid #000; }
    .table-container::-webkit-scrollbar { width: 30px; height: 30px; }
    .table-container::-webkit-scrollbar-track { background: #f1f1f1; }
    .table-container::-webkit-scrollbar-thumb { background: #888; border: 5px solid #f1f1f1; }

    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 12px; table-layout: fixed; }
    .html-table th { position: sticky; top: 0; background-color: #f3f4f6; border: 1px solid #000; padding: 5px; z-index: 10; text-align: center; }
    .html-table td { border: 1px solid #000; padding: 4px 6px; white-space: nowrap; overflow: hidden; }
    
    .num-align { text-align: right; }
    .red-bold { color: #dc2626; font-weight: bold; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA (ZACHOVÁNO 23 SLOUPCŮ) ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=5, header=None, engine='openpyxl')
        df = df.iloc[:, :23]
        df = df.replace({np.nan: '', 'nan': '', 'NaT': '', 'None': ''})
        return df
    except: return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    c_h1, c_h2 = st.columns([1, 4])
    with c_h1: st.markdown('<div class="custom-head">Evidence 2026</div>', unsafe_allow_html=True)
    with c_h2: hledat = st.text_input("", placeholder="Hledat...", label_visibility="collapsed")

    df = df_raw.copy()
    if hledat:
        df = df[df.apply(lambda r: hledat.lower() in str(list(r.values)).lower(), axis=1)]

    # --- 3. SOUČTY (UPRAVENO DLE DOHODY) ---
    def get_sum(col_idx):
        return pd.to_numeric(df[col_idx], errors='coerce').fillna(0).sum()

    m = st.columns(6) # Rozšířeno na 6 sloupců pro nové boxy
    
    # Výpočty
    celkem_val = get_sum(10) # Nabídka
    dur_val = get_sum(3)    # Sloupec K v Excelu (index 3)
    zmes_val = get_sum(4)   # Sloupec L v Excelu (index 4)
    zakazek_cnt = len(df[df[0] != ''])

    # 1. Box: CELKEM
    m[0].markdown(f'<div class="metric-box"><div class="metric-label">CELKEM</div><div class="metric-value">{celkem_val:,.2f} Kč'.replace(",", " ")+'</div></div>', unsafe_allow_html=True)
    
    # 2. Box: DUR (Kategorie I)
    m[1].markdown(f'<div class="metric-box"><div class="cat-label">KATEGORIE I</div><div class="metric-label">DUR</div><div class="metric-value">{dur_val:,.2f}'.replace(",", " ")+'</div></div>', unsafe_allow_html=True)
    
    # 3. Box: ZMES (Kategorie I)
    m[2].markdown(f'<div class="metric-box"><div class="cat-label">KATEGORIE I</div><div class="metric-label">ZMES</div><div class="metric-value">{zmes_val:,.2f}'.replace(",", " ")+'</div></div>', unsafe_allow_html=True)
    
    # 4. Box: FAKTURACE
    m[3].markdown(f'<div class="metric-box"><div class="metric-label">FAKTURACE</div><div class="metric-value">0.00 Kč</div></div>', unsafe_allow_html=True)
    
    # 5. Box: PROBÍHÁ
    m[4].markdown(f'<div class="metric-box"><div class="metric-label">PROBÍHÁ</div><div class="metric-value">0.00 Kč</div></div>', unsafe_allow_html=True)
    
    # 6. Box: ZAKÁZEK
    m[5].markdown(f'<div class="metric-box"><div class="metric-label">ZAKÁZEK</div><div class="metric-value">{zakazek_cnt}</div></div>', unsafe_allow_html=True)

    # --- 4. HTML TABULKA (BEZ ZMĚN) ---
    html = '<div class="table-container"><table class="html-table">'
    html += '<colgroup>'
    html += '<col style="width:40px"><col style="width:100px">' 
    html += '<col style="width:90px"><col style="width:90px"><col style="width:90px">' 
    html += '<col style="width:90px"><col style="width:90px"><col style="width:90px">' 
    html += '<col style="width:90px"><col style="width:250px">' 
    html += '<col style="width:100px"><col style="width:100px"><col style="width:100px">' 
    html += '<col style="width:80px"><col style="width:80px"><col style="width:80px"><col style="width:80px"><col style="width:100px"><col style="width:100px"><col style="width:100px"><col style="width:100px"><col style="width:100px"><col style="width:100px">'
    html += '</colgroup>'

    html += '<thead><tr>'
    html += '<th rowspan="2">poř.č.</th><th rowspan="2">firma</th>'
    html += '<th colspan="3">kategorie i</th><th colspan="3">kategorie ii</th>'
    html += '<th rowspan="2">č.stavby</th><th rowspan="2">název stavby</th><th rowspan="2">nabídka</th><th rowspan="2">rozdíl</th><th rowspan="2">vyfaktur.</th>'
    html += '<th rowspan="2">ukončení</th><th rowspan="2">zrealiz.</th><th rowspan="2">SOD</th><th rowspan="2">ze dne</th><th rowspan="2">objednatel</th><th rowspan="2">stavbyved.</th><th rowspan="2">nabídková c.</th><th rowspan="2">č.faktury</th><th rowspan="2">bez DPH</th><th rowspan="2">splatná</th>'
    html += '</tr><tr>'
    html += '<th>PS</th><th>SNK</th><th>BO</th><th>PS</th><th>BO</th><th>poruch</th>'
    html += '</tr></thead><tbody>'

    for _, row in df.iterrows():
        html += '<tr>'
        for i in range(23):
            val = row[i]
            td_cls = ""
            if i in [2,3,4,5,6,7,10,11,12,19,21]:
                try:
                    n = float(val)
                    val = f"{n:,.2f}".replace(",", " ")
                    td_cls = ' class="num-align"'
                    if i == 11 and n < 0: td_cls = ' class="red-bold"'
                except: pass
            elif i in [13, 14, 16, 22]:
                try: val = pd.to_datetime(val).strftime('%d.%m.%Y')
                except: pass
            html += f'<td{td_cls}>{val}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)
else:
    st.error("Data nenalezena.")
