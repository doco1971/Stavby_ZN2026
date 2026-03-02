import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE A STYLY (Vyladěno za 3 hodiny) ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding-top: 0.5rem; padding-left: 1.5rem; padding-right: 1.5rem; }
    .metric-box-styled {
        border: 1px solid #d1d5db; background-color: #f9fafb; border-radius: 4px;
        text-align: center; margin-bottom: 10px; height: 80px; display: flex; flex-direction: column;
    }
    .cat-header-main { font-size: 0.75rem; font-weight: bold; background-color: #e5e7eb; padding: 5px; border-bottom: 1px solid #d1d5db; }
    .metric-value { font-size: 1.1rem; font-weight: bold; color: #111827; margin: auto; }
    
    /* Kontejner pro 15 řádků + scrollbar (pamatuji si!) */
    .table-container { height: 450px; overflow: auto; border: 1px solid #000; margin-top: 10px; }
    .table-container::-webkit-scrollbar { width: 25px; height: 25px; }
    .table-container::-webkit-scrollbar-thumb { background: #888; border: 5px solid #f1f1f1; }
    
    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 12px; table-layout: fixed; }
    .html-table th { position: sticky; top: 0; background-color: #f3f4f6; border: 1px solid #000; padding: 5px; z-index: 10; }
    .html-table td { border: 1px solid #000; padding: 4px 6px; white-space: nowrap; overflow: hidden; }
    .num-align { text-align: right; }
    .red-bold { color: #dc2626; font-weight: bold; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PŘIHLAŠOVACÍ SYSTÉM ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>🔐 Vstup do systému Evidence 2026</h2>", unsafe_allow_html=True)
    _, col_m, _ = st.columns([1, 1, 1])
    with col_m:
        u = st.text_input("Uživatel")
        p = st.text_input("Heslo", type="password")
        if st.button("Přihlásit se"):
            if u == "admin" and p == "zn2026":
                st.session_state.logged_in, st.session_state.role = True, "supervisor"
                st.rerun()
            elif u == "host" and p == "prohlizec":
                st.session_state.logged_in, st.session_state.role = True, "user"
                st.rerun()
            else: st.error("Chyba přihlášení")
    st.stop()

# --- 3. DATA ---
FILE_NAME = 'Soupis zakázek tabulka 2026_ZN.xlsx'

@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel(FILE_NAME, skiprows=5, header=None)
        df = df.iloc[:, :23]
        cols_fix = [0, 2, 3, 4, 5, 6, 7, 10, 11, 12, 19, 21]
        for c in cols_fix: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        return df.fillna('')
    except: return pd.DataFrame(columns=range(23))

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- 4. VÝPOČTY (Dle vaší logiky DUR/ZMES) ---
df_active = st.session_state.data[(st.session_state.data[0] > 0) | (st.session_state.data[9] != "")]
c1_dur = c1_zmes = c2_dur = c2_zmes = 0.0

for _, r in df_active.iterrows():
    s1 = float(r[2]) + float(r[3]) + float(r[4])
    s2 = float(r[5]) + float(r[6]) + float(r[7])
    f = str(r[1]).strip().upper()
    if "DUR" in f: c1_dur += s1; c2_dur += s2
    elif "ZMES" in f: c1_zmes += s1; c2_zmes += s2

# --- 5. ZOBRAZENÍ METRIK ---
st.sidebar.write(f"Role: **{st.session_state.role}**")
if st.sidebar.button("Odhlásit"):
    st.session_state.logged_in = False
    st.rerun()

m = st.columns([1, 1.5, 1.5, 1, 0.8])
m[0].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Celkem Nabídka</div><div class='metric-value'>{df_active[10].sum():,.2f} Kč</div></div>".replace(",", " "), unsafe_allow_html=True)
m[1].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Kategorie I (DUR / ZMES)</div><div class='metric-value'>{c1_dur:,.2f} / {c1_zmes:,.2f}</div></div>".replace(",", " "), unsafe_allow_html=True)
m[2].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Kategorie II (DUR / ZMES)</div><div class='metric-value'>{c2_dur:,.2f} / {c2_zmes:,.2f}</div></div>".replace(",", " "), unsafe_allow_html=True)
m[3].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Probíhá</div><div class='metric-value'>0.00 Kč</div></div>", unsafe_allow_html=True)
m[4].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Zakázek</div><div class='metric-value'>{len(df_active[df_active[0]>0])}</div></div>", unsafe_allow_html=True)

# --- 6. FORMULÁŘ (Jen pro Supervisor) ---
if st.session_state.role == "supervisor":
    with st.expander("➕ FORMULÁŘ PRO NOVOU STAVBU"):
        with st.form("add_form", clear_on_submit=True):
            f1, f2, f3 = st.columns(3)
            with f1:
                firma = st.selectbox("Firma", ["DUR plus", "ZMES"])
                nazev = st.text_input("Název stavby")
                c_stavby = st.text_input("Číslo stavby")
            with f2:
                k1_ps = st.number_input("Kat I - PS", 0.0)
                k2_ps = st.number_input("Kat II - PS", 0.0)
                nabidka = st.number_input("Nabídková cena", 0.0)
            with f3:
                stavbyved = st.text_input("Stavbyvedoucí")
                termin = st.date_input("Termín ukončení")
            
            if st.form_submit_button("ULOŽIT DO DATABÁZE"):
                # Logika přidání řádku do session_state
                new_data = [len(st.session_state.data)+1, firma, k1_ps, 0, 0, k2_ps, 0, 0, c_stavby, nazev, nabidka, -nabidka, 0] + [""]*10
                st.session_state.data.loc[len(st.session_state.data)] = new_data
                st.success("Uloženo!")
                st.rerun()

# --- 7. TABULKA (15 řádků + barvy) ---
html = '<div class="table-container"><table class="html-table">'
html += '<colgroup><col style="width:40px"><col style="width:90px">' + '<col style="width:115px">'*6 + '<col style="width:90px"><col style="width:250px">' + '<col style="width:115px">'*3 + '</colgroup>'
html += '<thead><tr><th>Poř.č.</th><th>Firma</th><th>K1 PS</th><th>K1 SNK</th><th>K1 BO</th><th>K2 PS</th><th>K2 BO</th><th>K2 Poruch</th><th>Č.stavby</th><th>Název stavby</th><th>Nabídka</th><th>Rozdíl</th><th>Vyfaktur.</th></tr></thead><tbody>'

for _, r in df_active.iterrows():
    html += '<tr>'
    for i in range(13):
        val = r[i]
        td_cls = ' class="num-align"' if i in [0,2,3,4,5,6,7,10,11,12] else ""
        if i == 11 and float(val or 0) < 0: td_cls = ' class="red-bold"'
        if i in [2,3,4,5,6,7,10,11,12] and val != 0: 
            val = f"{float(val):,.2f}".replace(",", " ")
        elif val == 0: val = ""
        html += f'<td{td_cls}>{val}</td>'
    html += '</tr>'
html += '</tbody></table></div>'
st.markdown(html, unsafe_allow_html=True)
