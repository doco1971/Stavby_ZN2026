import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE A STYLY (PŘESNĚ PODLE TVÉHO PŮVODNÍHO) ---
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

    .table-container { 
        height: 450px; 
        overflow-y: auto; 
        border: 1px solid #000; 
    }
    .table-container::-webkit-scrollbar { width: 25px; height: 25px; }
    .table-container::-webkit-scrollbar-track { background: #f1f1f1; }
    .table-container::-webkit-scrollbar-thumb { background: #888; border: 4px solid #f1f1f1; }

    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 12px; table-layout: fixed; }
    .html-table th { 
        position: sticky; 
        top: 0; 
        background-color: #f3f4f6; 
        border: 1px solid #000; 
        padding: 5px; 
        z-index: 10; 
        text-align: center;
        text-transform: none;
    }
    .html-table td { border: 1px solid #000; padding: 4px 6px; white-space: nowrap; overflow: hidden; }
    
    .num-align { text-align: right; }
    .red-bold { color: #dc2626; font-weight: bold; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PŘIHLAŠOVACÍ SYSTÉM (S PŘÍKAZEM STOP) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        st.write("")
        st.markdown("### 🔐 Přihlášení do systému")
        u = st.text_input("Uživatel")
        p = st.text_input("Heslo", type="password")
        if st.button("Vstoupit", use_container_width=True):
            if u == "admin" and p == "zn2026":
                st.session_state.logged_in = True
                st.session_state.role = "supervisor"
                st.rerun()
            elif u == "host" and p == "prohlizec":
                st.session_state.logged_in = True
                st.session_state.role = "user"
                st.rerun()
            else:
                st.error("Nesprávné jméno nebo heslo")
    st.stop()  # Tady se kód zastaví a nepustí nikoho k datům bez hesla

# --- 3. DATA (TVÁ PŮVODNÍ LOGIKA) ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=5, header=None, engine='openpyxl')
        df = df.iloc[:, :23]
        cols_to_fix = [0, 2, 3, 4, 5, 6, 7, 10, 11, 12, 19, 21]
        for col in cols_to_fix:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df = df.fillna('')
        return df
    except:
        return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # Horní lišta: Nadpis a Hledání
    c_h1, c_h2 = st.columns([1, 4])
    with c_h1: st.markdown('<div class="custom-head">Evidence 2026</div>', unsafe_allow_html=True)
    with c_h2: hledat = st.text_input("", placeholder="Hledat...", label_visibility="collapsed")

    df = df_raw.copy()
    # Filtrace prázdných řádků
    df = df[(df[0] > 0) | (df[9].astype(str).str.strip() != "")]

    if hledat:
        df = df[df.apply(lambda r: hledat.lower() in str(list(r.values)).lower(), axis=1)]

    # --- 4. VÝPOČTY (PS + SNK + BO) ---
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
    zakazek_cnt = int((df[0] > 0).sum())

    # --- 5. METRIKY (TVÉ PŮVODNÍ) ---
    m = st.columns([1, 1.5, 1.5, 1, 0.8]) 
    m[0].markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">Celkem Nabídka</div><div class="cat-content"><div class="metric-value">{celkem_val:,.2f} Kč</div></div></div>'''.replace(",", " "), unsafe_allow_html=True)
    m[1].markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">Kategorie I</div><div class="cat-content"><div class="cat-sub-item"><div class="metric-label">DUR</div><div class="metric-value">{cat1_dur:,.2f}</div></div><div class="cat-sub-item" style="border-left: 1px solid #d1d5db;"><div class="metric-label">ZMES</div><div class="metric-value">{cat1_zmes:,.2f}</div></div></div></div>'''.replace(",", " "), unsafe_allow_html=True)
    m[2].markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">Kategorie II</div><div class="cat-content"><div class="cat-sub-item"><div class="metric-label">DUR</div><div class="metric-value">{cat2_dur:,.2f}</div></div><div class="cat-sub-item" style="border-left: 1px solid #d1d5db;"><div class="metric-label">ZMES</div><div class="metric-value">{cat2_zmes:,.2f}</div></div></div></div>'''.replace(",", " "), unsafe_allow_html=True)
    m[3].markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">Probíhá</div><div class="cat-content"><div class="metric-value">0.00 Kč</div></div></div>''', unsafe_allow_html=True)
    m[4].markdown(f'''<div class="metric-box-styled"><div class="cat-header-main">Zakázek</div><div class="cat-content"><div class="metric-value">{zakazek_cnt}</div></div></div>''', unsafe_allow_html=True)

    # --- 6. FORMULÁŘ (POUZE PRO ADMINA) ---
    if st.session_state.role == "supervisor":
        with st.expander("➕ NOVÝ ZÁZNAM"):
            st.info("Zde budeme brzy přidávat nové zakázky.")

    # --- 7. HTML TABULKA (MŘÍŽKA, SCROLLBAR, 23 SLOUPCŮ) ---
    html = '<div class="table-container"><table class="html-table">'
    html += '<colgroup>'
    html += '<col style="width:35px"><col style="width:90px">'
    html += '<col style="width:115px">'*6
    html += '<col style="width:90px"><col style="width:250px"><col style="width:115px">'
    html += '<col style="width:115px">'*3 + '<col style="width:85px">'*4
    html += '<col style="width:110px">'*2 + '<col style="width:115px"><col style="width:100px"><col style="width:115px"><col style="width:100px">'
    html += '</colgroup>'

    html += '<thead>'
    html += '<tr><th rowspan="2">Poř.č.</th><th rowspan="2">Firma</th><th colspan="3">Kategorie I</th><th colspan="3">Kategorie II</th><th rowspan="2">Č.stavby</th><th rowspan="2">Název stavby</th><th rowspan="2">Nabídka</th><th rowspan="2">Rozdíl</th><th rowspan="2">Vyfaktur.</th><th rowspan="2">Ukončení</th><th rowspan="2">Zrealiz.</th><th rowspan="2">SOD</th><th rowspan="2">Ze dne</th><th rowspan="2">Objednatel</th><th rowspan="2">Stavbyved.</th><th rowspan="2">Nabídková c.</th><th rowspan="2">Č.faktury</th><th rowspan="2">Bez DPH</th><th rowspan="2">Splatná</th></tr>'
    html += '<tr><th>PS</th><th>SNK</th><th>BO</th><th>PS</th><th>BO</th><th>Poruch</th></tr>'
    html += '</thead><tbody>'

    for _, row in df.iterrows():
        html += '<tr>'
        for i in range(23):
            val = row[i]
            td_cls = ""
            if i == 0:
                td_cls = ' class="num-align"'
                val = int(val) if val != 0 else ""
            elif i in [2,3,4,5,6,7,10,11,12,19,21]:
                td_cls = ' class="num-align"'
                try:
                    n = float(val)
                    val = f"{n:,.2f}".replace(",", " ") if n != 0 else ""
                    if i == 11 and n < 0: td_cls = ' class="red-bold"'
                except: val = ""
            elif i in [13, 14, 16, 22]:
                try: val = pd.to_datetime(val).strftime('%d.%m.%Y')
                except: val = ""
            if str(val).lower() in ["nan", "none"]: val = ""
            html += f'<td{td_cls}>{val}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)

    # Tlačítko pro odhlášení
    if st.sidebar.button("Odhlásit"):
        st.session_state.logged_in = False
        st.rerun()
else:
    st.error("Data nenalezena.")
