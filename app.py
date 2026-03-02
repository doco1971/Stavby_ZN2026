import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE A STRIKTNÍ STYLY PRO TABULKU ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding-top: 0.5rem; padding-left: 1.5rem; padding-right: 1.5rem; }
    
    /* Kontejner s pevnou výškou 450px pro cca 15 řádků */
    .table-container { 
        height: 450px; 
        overflow-y: scroll; 
        overflow-x: auto; 
        border: 2px solid black; 
        margin-top: 10px;
    }
    
    /* Extrémně výrazný scrollbar (šířka 25px) */
    .table-container::-webkit-scrollbar { width: 25px; height: 25px; }
    .table-container::-webkit-scrollbar-track { background: #f1f1f1; }
    .table-container::-webkit-scrollbar-thumb { background: #888; border: 3px solid #f1f1f1; border-radius: 5px; }
    .table-container::-webkit-scrollbar-thumb:hover { background: #555; }

    /* Vynucené černé ohraničení pro celou tabulku */
    .html-table { 
        width: 100%; 
        border-collapse: collapse; 
        font-family: sans-serif; 
        font-size: 13px; 
        table-layout: fixed;
        border: 1px solid black;
    }
    
    /* Hlavička - fixní při skrollování */
    .html-table th { 
        position: sticky; 
        top: 0; 
        background-color: #f3f4f6; 
        border: 1px solid black !important; 
        padding: 8px; 
        z-index: 10;
        font-weight: bold;
    }
    
    /* Buňky - každá musí mít vlastní čáru */
    .html-table td { 
        border: 1px solid black !important; 
        padding: 6px; 
        white-space: nowrap; 
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .num-align { text-align: right; }
    .red-bold { color: #dc2626; font-weight: bold; text-align: right; }
    
    /* Styly pro metriky */
    .metric-box-styled {
        border: 1px solid #d1d5db; background-color: #f9fafb; border-radius: 4px;
        text-align: center; margin-bottom: 10px; height: 85px; display: flex; flex-direction: column;
    }
    .cat-header-main { font-size: 0.75rem; font-weight: bold; background-color: #e5e7eb; padding: 5px; border-bottom: 1px solid #d1d5db; }
    .metric-value { font-size: 1.1rem; font-weight: bold; color: #111827; margin: auto; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PŘIHLAŠOVACÍ SYSTÉM ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        st.title("🔐 Přihlášení")
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

# --- 3. DATA A FILTRACE ---
FILE_NAME = 'Soupis zakázek tabulka 2026_ZN.xlsx'

@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel(FILE_NAME, skiprows=5, header=None) # Čtení od 6. řádku
        df = df.iloc[:, :23]
        # Převod na čísla pro výpočty
        cols_to_fix = [0, 2, 3, 4, 5, 6, 7, 10, 11, 12]
        for c in cols_to_fix:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        return df.fillna('')
    except:
        return pd.DataFrame(columns=range(23))

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# Horní lišta: Nadpis a Hledání
c_h1, c_h2 = st.columns([1, 4])
with c_h1: st.subheader("Evidence 2026")
with c_h2: hledat = st.text_input("", placeholder="Hledat...", label_visibility="collapsed")

# Filtrace aktivních řádků
df_view = st.session_state.data[(st.session_state.data[0] > 0) | (st.session_state.data[9] != "")]
if hledat:
    df_view = df_view[df_view.apply(lambda r: hledat.lower() in str(list(r.values)).lower(), axis=1)]

# --- 4. OPRAVENÉ SOUČTY (Kategorie I a II) ---
c1_dur = c1_zmes = c2_dur = c2_zmes = 0.0
for _, r in df_view.iterrows():
    s1 = float(r[2]) + float(r[3]) + float(r[4]) # PS + SNK + BO
    s2 = float(r[5]) + float(r[6]) + float(r[7]) # PS + BO + Poruch
    f = str(r[1]).upper()
    if "DUR" in f: 
        c1_dur += s1; c2_dur += s2
    elif "ZMES" in f: 
        c1_zmes += s1; c2_zmes += s2

# --- 5. ZOBRAZENÍ BOXŮ ---
m = st.columns([1, 1.5, 1.5, 1, 0.8])
m[0].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Nabídka</div><div class='metric-value'>{df_view[10].sum():,.2f}</div></div>".replace(",", " "), unsafe_allow_html=True)
m[1].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Kategorie I (DUR/ZMES)</div><div class='metric-value'>{c1_dur:,.2f} / {c1_zmes:,.2f}</div></div>".replace(",", " "), unsafe_allow_html=True)
m[2].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Kategorie II (DUR/ZMES)</div><div class='metric-value'>{c2_dur:,.2f} / {c2_zmes:,.2f}</div></div>".replace(",", " "), unsafe_allow_html=True)
m[3].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Probíhá</div><div class='metric-value'>0.00</div></div>", unsafe_allow_html=True)
m[4].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Zakázek</div><div class='metric-value'>{len(df_view[df_view[0]>0])}</div></div>", unsafe_allow_html=True)

# --- 6. FORMULÁŘ (JEN PRO ADMINA) ---
if st.session_state.role == "supervisor":
    with st.expander("➕ NOVÝ ZÁZNAM"):
        with st.form("new_entry"):
            f1, f2, f3 = st.columns(3)
            with f1: f_firma = st.selectbox("Firma", ["DUR plus", "ZMES"]); f_nazev = st.text_input("Název")
            with f2: f_k1 = st.number_input("Kat I PS", 0.0); f_nab = st.number_input("Nabídka", 0.0)
            with f3: f_stavbyved = st.text_input("Stavbyvedoucí")
            if st.form_submit_button("Uložit"):
                st.success("Uloženo (zatím jen v této relaci)")

# --- 7. FINÁLNÍ TABULKA S OHRANIČENÍM ---
html = '<div class="table-container"><table class="html-table">'
# Definice šířek sloupců pro stabilitu
html += '<colgroup><col style="width:45px"><col style="width:100px">' + '<col style="width:110px">'*6 + '<col style="width:100px"><col style="width:300px"><col style="width:120px"><col style="width:120px"><col style="width:120px"></colgroup>'
html += '<thead><tr><th>Poř.</th><th>Firma</th><th>K1 PS</th><th>K1 SNK</th><th>K1 BO</th><th>K2 PS</th><th>K2 BO</th><th>K2 Por.</th><th>Č.stavby</th><th>Název stavby</th><th>Nabídka</th><th>Rozdíl</th><th>Vyfakt.</th></tr></thead><tbody>'

for _, r in df_view.iterrows():
    html += '<tr>'
    for i in range(13):
        val = r[i]
        cls = ' class="num-align"' if i in [0,2,3,4,5,6,7,10,11,12] else ""
        if i == 11 and float(val or 0) < 0: cls = ' class="red-bold"'
        
        # Formátování čísel
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
