import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE A STYLY ---
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
    
    /* Metriky přesně podle screenshotu */
    .metric-row { display: flex; gap: 10px; margin-bottom: 10px; }
    .metric-box-styled {
        border: 1px solid #d1d5db;
        background-color: #ffffff;
        border-radius: 8px;
        flex: 1;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .cat-header-main {
        font-size: 0.75rem; font-weight: bold; background-color: #f3f4f6;
        border-bottom: 1px solid #d1d5db; padding: 6px 0; text-transform: uppercase;
        text-align: center; color: #374151;
    }
    .cat-content { display: flex; flex-grow: 1; align-items: center; padding: 8px 0; }
    .cat-sub-item { flex: 1; text-align: center; position: relative; }
    .metric-label { font-size: 0.65rem; color: #9ca3af; text-transform: uppercase; margin-bottom: 2px; }
    .metric-value { font-size: 1.25rem; font-weight: bold; color: #000000; }
    .v-line { position: absolute; right: 0; top: 20%; bottom: 20%; width: 1px; background-color: #d1d5db; }

    /* KONTEJNER TABULKY */
    .table-container { 
        height: 450px; 
        overflow: auto; 
        border: 1px solid #000;
        background-color: white;
    }
    
    .table-container::-webkit-scrollbar { width: 22px; height: 22px; }
    .table-container::-webkit-scrollbar-track { background: #f1f1f1; }
    .table-container::-webkit-scrollbar-thumb { background: #888; border: 4px solid #f1f1f1; }

    /* TABULKA - ČISTÁ MŘÍŽKA */
    .html-table { 
        width: 100%; 
        border-collapse: separate; 
        border-spacing: 0; 
        font-family: sans-serif; 
        font-size: 12px; 
        table-layout: fixed;
    }
    
    .html-table th, .html-table td {
        border-right: 1px solid #000;
        border-bottom: 1px solid #000;
        padding: 6px 8px;
        white-space: nowrap;
        overflow: hidden;
        background-color: white;
    }

    /* FIXNÍ HLAVIČKA */
    .html-table th { 
        position: sticky; 
        background-color: #f3f4f6 !important; 
        z-index: 10; 
        text-align: center;
        font-weight: bold;
    }

    .html-table thead tr:nth-child(1) th { top: 0; z-index: 20; }
    .html-table thead tr:nth-child(2) th { top: 31px; z-index: 20; } 
    
    /* ZAROVNÁNÍ */
    .num-align { text-align: right; }
    .txt-align { text-align: left; }
    .center-align { text-align: center; }
    .red-bold { color: #dc2626; font-weight: bold; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PŘIHLAŠOVACÍ SYSTÉM ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        st.markdown("### 🔐 Přihlášení do systému")
        u = st.text_input("Uživatel")
        p = st.text_input("Heslo", type="password")
        if st.button("Vstoupit", use_container_width=True):
            if u == "admin" and p == "zn2026":
                st.session_state.logged_in = True
                st.rerun()
            elif u == "host" and p == "prohlizec":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Nesprávné jméno nebo heslo")
    st.stop()

# --- 3. DATA ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=5, header=None, engine='openpyxl')
        df = df.iloc[:, :23]
        cols_to_fix = [0, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 19, 21]
        for col in cols_to_fix:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df = df.fillna('')
        return df
    except: return pd.DataFrame()

df_raw = load_data()

def reset_search():
    st.session_state.search_key = ""

if not df_raw.empty:
    c_h1, c_h2, c_h3 = st.columns([1, 3.5, 0.5])
    with c_h1: st.markdown('<div class="custom-head">Evidence 2026</div>', unsafe_allow_html=True)
    with c_h2: hledat = st.text_input("", placeholder="Hledat...", label_visibility="collapsed", key="search_key")
    with c_h3: st.button("❌", on_click=reset_search)

    df = df_raw.copy()
    df = df[(df[0] > 0) | (df[9].astype(str).str.strip() != "")]
    if hledat:
        df = df[df.apply(lambda r: hledat.lower() in str(list(r.values)).lower(), axis=1)]

    # --- 4. VÝPOČTY (Kat I: PS+SNK+BO | Kat II: PS+BO+Poruch) ---
    # Podle Saved Information: suma Kat I se přičítá k DUR nebo ZMES podle sloupce 'firma'
    cat1_dur = cat1_zmes = cat2_dur = cat2_zmes = 0.0
    for _, row in df.iterrows():
        s1 = float(row[2]) + float(row[3]) + float(row[4])
        s2 = float(row[5]) + float(row[6]) + float(row[7])
        f = str(row[1]).strip().upper()
        if "DUR" in f:
            cat1_dur += s1
            cat2_dur += s2
        elif "ZMES" in f:
            cat1_zmes += s1
            cat2_zmes += s2

    celkem_val = df[10].sum()
    zakazek_cnt = int((df[0] > 0).sum())

    # --- 5. METRIKY (Vzhled dle screenshotu) ---
    m1, m2, m3, m4, m5 = st.columns([1, 1.5, 1.5, 1, 0.8]) 
    
    m1.markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">Celkem Nabídka</div><div class="cat-content"><div class="cat-sub-item"><div class="metric-value">{celkem_val:,.2f}</div></div></div></div>'''.replace(",", " "), unsafe_allow_html=True)
    
    m2.markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">Kategorie I</div><div class="cat-content"><div class="cat-sub-item"><div class="metric-label">DUR</div><div class="metric-value">{cat1_dur:,.2f}</div><div class="v-line"></div></div><div class="cat-sub-item"><div class="metric-label">ZMES</div><div class="metric-value">{cat1_zmes:,.2f}</div></div></div></div>'''.replace(",", " "), unsafe_allow_html=True)
    
    m3.markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">Kategorie II</div><div class="cat-content"><div class="cat-sub-item"><div class="metric-label">DUR</div><div class="metric-value">{cat2_dur:,.2f}</div><div class="v-line"></div></div><div class="cat-sub-item"><div class="metric-label">ZMES</div><div class="metric-value">{cat2_zmes:,.2f}</div></div></div></div>'''.replace(",", " "), unsafe_allow_html=True)
    
    m4.markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">Probíhá</div><div class="cat-content"><div class="cat-sub-item"><div class="metric-value">0.00</div></div></div></div>''', unsafe_allow_html=True)
    
    m5.markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">Zakázek</div><div class="cat-content"><div class="cat-sub-item"><div class="metric-value">{zakazek_cnt}</div></div></div></div>''', unsafe_allow_html=True)

    # --- 6. HTML TABULKA ---
    html = '<div class="table-container"><table class="html-table">'
    html += '<colgroup>'
    html += '<col style="width:45px"><col style="width:95px">'
    html += '<col style="width:110px">'*6
    html += '<col style="width:90px"><col style="width:280px"><col style="width:115px">'*3
    html += '<col style="width:95px">'*4
    html += '<col style="width:130px">'*2
    html += '<col style="width:115px"><col style="width:100px"><col style="width:115px"><col style="width:100px">'
    html += '</colgroup>'

    html += '<thead><tr>'
    html += '<th rowspan="2">Poř.č.</th><th rowspan="2">Firma</th><th colspan="3">Kategorie I</th><th colspan="3">Kategorie II</th>'
    html += '<th rowspan="2">Č.stavby</th><th rowspan="2">Název stavby</th><th rowspan="2">Nabídka</th><th rowspan="2">Rozdíl</th><th rowspan="2">Vyfaktur.</th>'
    html += '<th rowspan="2">Ukončení</th><th rowspan="2">Zrealiz.</th><th rowspan="2">SOD</th><th rowspan="2">Ze dne</th><th rowspan="2">Objednatel</th>'
    html += '<th rowspan="2">Stavbyved.</th><th rowspan="2">Nabídková c.</th><th rowspan="2">Č.faktury</th><th rowspan="2">Bez DPH</th><th rowspan="2">Splatná</th>'
    html += '</tr><tr><th>PS</th><th>SNK</th><th>BO</th><th>PS</th><th>BO</th><th>Poruch</th></tr></thead><tbody>'

    # Zobrazení dat (15 řádků na stránku je zaručeno výškou kontejneru 450px)
    for _, row in df.iterrows():
        html += '<tr>'
        for i in range(23):
            val = row[i]
            if i in [0, 13, 14, 15, 16, 20, 22]: td_cls = ' class="center-align"'
            elif i in [1, 9, 17, 18]: td_cls = ' class="txt-align"'
            else: td_cls = ' class="num-align"'

            if i == 0: val = int(val) if val != 0 else ""
            elif i in [2,3,4,5,6,7,8,10,11,12,19,21]:
                try:
                    n = float(val)
                    val = f"{n:,.2f}".replace(",", " ") if n != 0 else ""
                    if i == 11 and n < 0: td_cls += " red-bold"
                except: val = ""
            elif i in [13, 14, 16, 22]:
                try: val = pd.to_datetime(val).strftime('%d.%m.%Y')
                except: val = ""
            
            if str(val).lower() in ["nan", "none"]: val = ""
            html += f'<td{td_cls}>{val}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)

    if st.sidebar.button("Odhlásit"):
        st.session_state.logged_in = False
        st.rerun()
else:
    st.error("Data nenalezena.")
