import streamlit as st
import pandas as pd

# --- 1. KOMPLETNÍ KONFIGURACE A STYLY ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding-top: 0.5rem; padding-left: 1.5rem; padding-right: 1.5rem; }
    
    /* NADPIS A PANEL VYHLEDÁVÁNÍ */
    .header-text { font-size: 1.4rem; font-weight: bold; margin-bottom: 0px; padding-bottom: 0px; }
    
    /* TABULKA: 450px VÝŠKA + 25px SCROLLBAR */
    .table-container { 
        height: 450px; 
        overflow: auto; 
        border: 2px solid black; 
        background-color: white;
    }
    .table-container::-webkit-scrollbar { width: 25px; height: 25px; }
    .table-container::-webkit-scrollbar-track { background: #f1f1f1; }
    .table-container::-webkit-scrollbar-thumb { background: #888; border: 3px solid #f1f1f1; }

    /* MŘÍŽKA DLE OBRÁZKU */
    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 13px; table-layout: fixed; }
    .html-table th { 
        position: sticky; top: 0; background-color: #f3f4f6; 
        border: 1px solid black !important; padding: 8px; z-index: 10; 
        color: black; font-weight: bold; text-align: left;
    }
    .html-table td { border: 1px solid black !important; padding: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

    .num-align { text-align: right; }
    .red-bold { color: #dc2626; font-weight: bold; text-align: right; }
    
    /* METRIKY */
    .metric-box-styled {
        border: 1px solid #d1d5db; background-color: #f9fafb; text-align: center; height: 85px; display: flex; flex-direction: column;
    }
    .cat-header-main { font-size: 0.75rem; font-weight: bold; background-color: #e5e7eb; padding: 5px; border-bottom: 1px solid #d1d5db; color: #374151; }
    .metric-value { font-size: 1.1rem; font-weight: bold; color: #111827; margin: auto; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGIKA PŘIHLÁŠENÍ ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        u = st.text_input("Uživatel")
        p = st.text_input("Heslo", type="password")
        if st.button("Vstoupit"):
            if u == "admin" and p == "zn2026":
                st.session_state.logged_in, st.session_state.role = True, "supervisor"
                st.rerun()
            elif u == "host" and p == "prohlizec":
                st.session_state.logged_in, st.session_state.role = True, "user"
                st.rerun()
    st.stop()

# --- 3. DATA ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=5, header=None).iloc[:, :23]
        for c in [0, 2, 3, 4, 5, 6, 7, 10, 11, 12]:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        return df.fillna('')
    except: return pd.DataFrame(columns=range(23))

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- 4. HORNÍ PANELY (METRIKY) ---
m = st.columns([1, 1.5, 1.5, 1, 0.8])
# Sumy se počítají z aktivních dat
df_sums = st.session_state.data[(st.session_state.data[0] > 0) | (st.session_state.data[9] != "")]

c1_dur = c1_zmes = c2_dur = c2_zmes = 0.0
for _, r in df_sums.iterrows():
    # Kat I = PS + SNK + BO
    s1 = float(r[2]) + float(r[3]) + float(r[4])
    # Kat II = PS + BO + Poruch
    s2 = float(r[5]) + float(r[6]) + float(r[7])
    
    f = str(r[1]).upper()
    if "DUR" in f: c1_dur += s1; c2_dur += s2
    elif "ZMES" in f: c1_zmes += s1; c2_zmes += s2

m[0].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Nabídka</div><div class='metric-value'>{df_sums[10].sum():,.2f}</div></div>".replace(",", " "), unsafe_allow_html=True)
m[1].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Kategorie I (DUR/ZMES)</div><div class='metric-value'>{c1_dur:,.2f} / {c1_zmes:,.2f}</div></div>".replace(",", " "), unsafe_allow_html=True)
m[2].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Kategorie II (DUR/ZMES)</div><div class='metric-value'>{c2_dur:,.2f} / {c2_zmes:,.2f}</div></div>".replace(",", " "), unsafe_allow_html=True)
m[3].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Probíhá</div><div class='metric-value'>0.00</div></div>", unsafe_allow_html=True)
m[4].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Zakázek</div><div class='metric-value'>{len(df_sums[df_sums[0]>0])}</div></div>", unsafe_allow_html=True)

# --- 5. NADPIS A VYHLEDÁVACÍ POLE (VRÁCENO ZPĚT) ---
st.write("")
col_n1, col_n2 = st.columns([1, 4])
with col_n1:
    st.markdown('<p class="header-text">Evidence 2026</p>', unsafe_allow_html=True)
with col_n2:
    hledat = st.text_input("", placeholder="🔍 Hledat v zakázkách...", label_visibility="collapsed")

# --- 6. FILTRACE A TABULKA ---
df_view = df_sums.copy()
if hledat:
    df_view = df_view[df_view.apply(lambda r: hledat.lower() in str(list(r.values)).lower(), axis=1)]

html = '<div class="table-container"><table class="html-table">'
# Definice šířek
html += '<colgroup><col style="width:40px"><col style="width:100px">' + '<col style="width:110px">'*6 + '<col style="width:110px"><col style="width:350px"><col style="width:120px"><col style="width:120px"><col style="width:120px"></colgroup>'
html += '<thead><tr><th>Poř.</th><th>Firma</th><th>K1 PS</th><th>K1 SNK</th><th>K1 BO</th><th>K2 PS</th><th>K2 BO</th><th>K2 Por.</th><th>Č.stavby</th><th>Název stavby</th><th>Nabídka</th><th>Rozdíl</th><th>Vyfakt.</th></tr></thead><tbody>'

for _, r in df_view.iterrows():
    html += '<tr>'
    for i in range(13):
        val = r[i]
        cls = ' class="num-align"' if i in [0,2,3,4,5,6,7,10,11,12] else ""
        if i == 11 and float(val or 0) < 0: cls = ' class="red-bold"'
        
        if i in [2,3,4,5,6,7,10,11,12] and val != 0:
            val = f"{float(val):,.2f}".replace(",", " ")
        elif val == 0 and i != 0: val = ""
        
        html += f'<td{cls}>{val}</td>'
    html += '</tr>'

html += '</tbody></table></div>'
st.markdown(html, unsafe_allow_html=True)

if st.sidebar.button("Odhlásit"):
    st.session_state.logged_in = False
    st.rerun()
