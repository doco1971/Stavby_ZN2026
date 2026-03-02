import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding: 0.5rem !important; }
    .custom-head { font-size: 1.1rem; font-weight: bold; margin-bottom: 0.5rem; }
    
    /* TABULKA KONTEJNER - 16 ŘÁDKŮ */
    .table-container { height: 400px; overflow: auto; border: 1px solid #000; }
    
    /* MASIVNÍ POSUVNÍK */
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

# --- 2. DATA (PŘESNĚ 23 SLOUPCŮ) ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=5, header=None, engine='openpyxl')
        df = df.iloc[:, :23] # Vezmeme přesně 23 sloupců
        df = df.replace({np.nan: '', 'nan': '', 'NaT': '', 'None': ''})
        return df
    except: return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # Horní lišta
    c_h1, c_h2 = st.columns([1, 4])
    with c_h1: st.markdown('<div class="custom-head">Evidence 2026</div>', unsafe_allow_html=True)
    with c_h2: hledat = st.text_input("", placeholder="Hledat...", label_visibility="collapsed")

    df = df_raw.copy()
    if hledat:
        df = df[df.apply(lambda r: hledat.lower() in str(r.values).lower(), axis=1)]

    # --- 3. HTML TABULKA S COLGROUP (ŠÍŘKY) ---
    html = '<div class="table-container"><table class="html-table">'
    
    # Definice šířek (PS, SNK, BO mají 90px)
    html += '<colgroup>'
    html += '<col style="width:40px"><col style="width:100px">' # poř, firma
    html += '<col style="width:90px"><col style="width:90px"><col style="width:90px">' # Kat I
    html += '<col style="width:90px"><col style="width:90px"><col style="width:90px">' # Kat II
    html += '<col style="width:90px"><col style="width:250px">' # č.stavby, název
    html += '<col style="width:100px"><col style="width:100px"><col style="width:100px">' # nabídka, rozdíl, vyfakt
    html += '<col style="width:80px"><col style="width:80px"><col style="width:80px"><col style="width:80px"><col style="width:100px"><col style="width:100px"><col style="width:100px"><col style="width:100px"><col style="width:100px"><col style="width:100px">'
    html += '</colgroup>'

    # Hlavička (Dvouúrovňová)
    html += '<thead><tr>'
    html += '<th rowspan="2">poř.č.</th><th rowspan="2">firma</th>'
    html += '<th colspan="3">kategorie i</th><th colspan="3">kategorie ii</th>'
    html += '<th rowspan="2">č.stavby</th><th rowspan="2">název stavby</th><th rowspan="2">nabídka</th><th rowspan="2">rozdíl</th><th rowspan="2">vyfaktur.</th>'
    html += '<th rowspan="2">ukončení</th><th rowspan="2">zrealiz.</th><th rowspan="2">SOD</th><th rowspan="2">ze dne</th><th rowspan="2">objednatel</th><th rowspan="2">stavbyved.</th><th rowspan="2">nabídková c.</th><th rowspan="2">č.faktury</th><th rowspan="2">bez DPH</th><th rowspan="2">splatná</th>'
    html += '</tr><tr>'
    html += '<th>PS</th><th>SNK</th><th>BO</th><th>PS</th><th>BO</th><th>poruch</th>'
    html += '</tr></thead><tbody>'

    # Data
    for _, row in df.iterrows():
        html += '<tr>'
        for i in range(23):
            val = row[i]
            td_cls = ""
            
            # Formát peněz (sloupce 2-7, 10-12, 19, 21)
            if i in [2,3,4,5,6,7,10,11,12,19,21]:
                try:
                    n = float(val)
                    val = f"{n:,.2f}".replace(",", " ")
                    td_cls = ' class="num-align"'
                    if i == 11 and n < 0: td_cls = ' class="red-bold"'
                except: pass
            # Formát dat (13, 14, 16, 22)
            elif i in [13, 14, 16, 22]:
                try: val = pd.to_datetime(val).strftime('%d.%m.%Y')
                except: pass

            html += f'<td{td_cls}>{val}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)
else:
    st.error("Data nenalezena.")
