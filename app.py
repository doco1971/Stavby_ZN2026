import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE ---
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
    
    .metric-box-styled {
        border: 1px solid #d1d5db;
        background-color: #f9fafb;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 10px;
        width: 100%;
        height: 75px;
        display: flex;
        flex-direction: column;
    }
    .cat-header-main {
        font-size: 0.65rem;
        font-weight: bold;
        background-color: #e5e7eb;
        border-bottom: 1px solid #d1d5db;
        padding: 4px 0;
        text-transform: uppercase;
        flex-shrink: 0;
    }
    .cat-content {
        display: flex;
        justify-content: space-around;
        flex-grow: 1;
        align-items: center;
        padding: 2px 0;
    }
    .cat-sub-item { flex: 1; }
    
    .metric-label { font-size: 0.60rem; color: #6b7280; text-transform: uppercase; line-height: 1; }
    .metric-value { font-size: 0.95rem; font-weight: bold; color: #111827; }

    .table-container { height: 400px; overflow: auto; border: 1px solid #000; }
    .table-container::-webkit-scrollbar { width: 30px; height: 30px; }
    .table-container::-webkit-scrollbar-thumb { background: #888; border: 5px solid #f1f1f1; }

    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 12px; table-layout: fixed; }
    .html-table th { position: sticky; top: 0; background-color: #f3f4f6; border: 1px solid #000; padding: 5px; z-index: 10; text-align: center; }
    .html-table td { border: 1px solid #000; padding: 4px 6px; white-space: nowrap; overflow: hidden; }
    
    .num-align { text-align: right; }
    .red-bold { color: #dc2626; font-weight: bold; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=5, header=None, engine='openpyxl')
        df = df.iloc[:, :23]
        # Vyčistíme NaN hodnoty hned při načítání pro klíčové sloupce
        cols_to_fix = [0, 2, 3, 4, 5, 6, 7, 10, 11, 12, 19, 21]
        for col in cols_to_fix:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
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

    # --- 3. VÝPOČTY (KAT I i KAT II) ---
    cat1_dur, cat1_zmes = 0.0, 0.0
    cat2_dur, cat2_zmes = 0.0, 0.0

    for _, row in df.iterrows():
        sum1 = float(row[2]) + float(row[3]) + float(row[4])
        sum2 = float(row[5]) + float(row[6]) + float(row[7])
        
        firma = str(row[1]).strip().upper()
        if "DUR" in firma:
            cat1_dur += sum1
            cat2_dur += sum2
        elif "ZMES" in firma:
            cat1_zmes += sum1
            cat2_zmes += sum2

    celkem_val = df[10].sum()
    zakazek_cnt = len(df[df[0] > 0]) # Počet řádků, kde je poř.č. větší než 0

    # --- ZOBRAZENÍ METRIK ---
    m = st.columns([1, 1.5, 1.5, 1, 0.8]) 
    
    m[0].markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">CELKEM NABÍDKA</div><div class="cat-content"><div class="metric-value">{celkem_val:,.2f} Kč</div></div></div>'''.replace(",", " "), unsafe_allow_html=True)
    m[1].markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">KATEGORIE I</div><div class="cat-content"><div class="cat-sub-item"><div class="metric-label">DUR</div><div class="metric-value">{cat1_dur:,.2f}</div></div><div class="cat-sub-item" style="border-left: 1px solid #d1d5db;"><div class="metric-label">ZMES</div><div class="metric-value">{cat1_zmes:,.2f}</div></div></div></div>'''.replace(",", " "), unsafe_allow_html=True)
    m[2].markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">KATEGORIE II</div><div class="cat-content"><div class="cat-sub-item"><div class="metric-label">DUR</div><div class="metric-value">{cat2_dur:,.2f}</div></div><div class="cat-sub-item" style="border-left: 1px solid #d1d5db;"><div class="metric-label">ZMES</div><div class="metric-value">{cat2_zmes:,.2f}</div></div></div></div>'''.replace(",", " "), unsafe_allow_html=True)
    m[3].markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">PROBÍHÁ</div><div class="cat-content"><div class="metric-value">0.00 Kč</div></div></div>''', unsafe_allow_html=True)
    m[4].markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">ZAKÁZEK</div><div class="cat-content"><div class="metric-value">{zakazek_cnt}</div></div></div>''', unsafe_allow_html=True)

    # --- 4. HTML TABULKA (FIRMA 90PX + OPRAVA NAN) ---
    html = '<div class="table-container"><table class="html-table">'
    html += '<colgroup><col style="width:35px"><col style="width:90px"><col style="width:90px"><col style="width:90px"><col style="width:90px"><col style="width:90px"><col style="width:90px"><col style="width:90px"><col style="width:90px"><col style="width:250px"><col style="width:100px"><col style="width:100px"><col style="width:100px"><col style="width:80px"><col style="width:80px"><col style="width:80px"><col style="width:80px"><col style="width:100px"><col style="width:100px"><col style="width:100px"><col style="width:100px"><col style="width:100px"><col style="width:100px"></colgroup>'
    html += '<thead><tr><th rowspan="2">poř.č.</th><th rowspan="2">firma</th><th colspan="3">kategorie i</th><th colspan="3">kategorie ii</th><th rowspan="2">č.stavby</th><th rowspan="2">název stavby</th><th rowspan="2">nabídka</th><th rowspan="2">rozdíl</th><th rowspan="2">vyfaktur.</th><th rowspan="2">ukončení</th><th rowspan="2">zrealiz.</th><th rowspan="2">SOD</th><th rowspan="2">ze dne</th><th rowspan="2">objednatel</th><th rowspan="2">stavbyved.</th><th rowspan="2">nabídková c.</th><th rowspan="2">č.faktury</th><th rowspan="2">bez DPH</th><th rowspan="2">splatná</th></tr>'
    html += '<tr><th>PS</th><th>SNK</th><th>BO</th><th>PS</th><th>BO</th><th>poruch</th></tr></thead><tbody>'

    for _, row in df.iterrows():
        # Pokud je poř.č. 0, přeskočíme zobrazení prázdných řádků (volitelné, ale čistší)
        if row[0] == 0 and row[9] == "": continue
        
        html += '<tr>'
        for i in range(23):
            val = row[i]
            td_cls = ""
            
            if i == 0: # Poř. č.
                td_cls = ' class="num-align"'
                val = int(val) if val != 0 else ""
            elif i in [2,3,4,5,6,7,10,11,12,19,21]: # Číselné sloupce
                td_cls = ' class="num-align"'
                try:
                    n = float(val)
                    val = f"{n:,.2f}".replace(",", " ") if n != 0 else ""
                    if i == 11 and n < 0: td_cls = ' class="red-bold"'
                except: val = ""
            elif i in [13, 14, 16, 22]: # Datumy
                try: val = pd.to_datetime(val).strftime('%d.%m.%Y')
                except: val = ""
            
            # Ošetření zbytku proti NaN textu
            if val == "nan" or val == "NaN": val = ""
                
            html += f'<td{td_cls}>{val}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)
else:
    st.error("Data nenalezena.")
