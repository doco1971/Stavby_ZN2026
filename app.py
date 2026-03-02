import streamlit as st
import pandas as pd
import numpy as np
from openpyxl import load_workbook

# --- 1. KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="Evidence staveb 2026", layout="wide")

# --- 2. PŘIHLAŠOVACÍ SYSTÉM ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

def login():
    st.markdown("<h2 style='text-align: center;'>🔐 Evidence 2026 - Přihlášení</h2>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        user = st.text_input("Uživatel")
        pw = st.text_input("Heslo", type="password")
        if st.button("Vstoupit do systému"):
            if user == "admin" and pw == "zn2026":
                st.session_state.logged_in = True
                st.session_state.role = "supervisor"
                st.rerun()
            elif user == "host" and pw == "prohlizec":
                st.session_state.logged_in = True
                st.session_state.role = "user"
                st.rerun()
            else:
                st.error("Nesprávné údaje")

if not st.session_state.logged_in:
    login()
    st.stop()

# --- 3. DESIGN A STYLY (Vyladěno na 15 řádků) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding-top: 0.5rem; }
    .metric-box-styled {
        border: 1px solid #d1d5db; background-color: #f9fafb; border-radius: 4px;
        text-align: center; margin-bottom: 10px; height: 75px; display: flex; flex-direction: column;
    }
    .cat-header-main { font-size: 0.7rem; font-weight: bold; background-color: #e5e7eb; padding: 4px; text-transform: none; }
    .metric-value { font-size: 1rem; font-weight: bold; color: #111827; margin: auto; }
    
    /* Kontejner pro 15 řádků + scrollbar */
    .table-container { height: 450px; overflow: auto; border: 1px solid #000; }
    .table-container::-webkit-scrollbar { width: 20px; height: 20px; }
    .table-container::-webkit-scrollbar-thumb { background: #888; border: 3px solid #f1f1f1; }
    
    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 12px; table-layout: fixed; }
    .html-table th { position: sticky; top: 0; background-color: #f3f4f6; border: 1px solid #000; padding: 5px; z-index: 10; }
    .html-table td { border: 1px solid #000; padding: 4px 6px; white-space: nowrap; overflow: hidden; }
    .num-align { text-align: right; }
    .red-bold { color: #dc2626; font-weight: bold; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. NAČÍTÁNÍ DAT ---
FILE_NAME = 'Soupis zakázek tabulka 2026_ZN.xlsx'

@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel(FILE_NAME, skiprows=5, header=None)
        df = df.iloc[:, :23]
        # Vyčištění čísel
        cols_num = [0, 2, 3, 4, 5, 6, 7, 10, 11, 12, 19, 21]
        for c in cols_num:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
        df = df.fillna('')
        return df
    except:
        return pd.DataFrame(columns=range(23))

df = load_data()

# --- 5. VÝPOČTY PRO METRIKY ---
# (Filtrujeme jen reálných 8 řádků, které tam máte)
df_active = df[(df[0] > 0) | (df[9] != "")]

c1_dur = c1_zmes = c2_dur = c2_zmes = 0.0
for _, r in df_active.iterrows():
    s1 = float(r[2]) + float(r[3]) + float(r[4])
    s2 = float(r[5]) + float(r[6]) + float(r[7])
    f = str(r[1]).upper()
    if "DUR" in f: c1_dur += s1; c2_dur += s2
    elif "ZMES" in f: c1_zmes += s1; c2_zmes += s2

total_nabidka = df_active[10].sum()
count_zakazek = len(df_active[df_active[0] > 0])

# --- 6. ZOBRAZENÍ ---
st.sidebar.write(f"Uživatel: **{st.session_state.role}**")
if st.sidebar.button("Odhlásit"):
    st.session_state.logged_in = False
    st.rerun()

m = st.columns([1, 1.5, 1.5, 1, 0.8])
m[0].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Celkem Nabídka</div><div class='metric-value'>{total_nabidka:,.2f} Kč</div></div>".replace(",", " "), unsafe_allow_html=True)
m[1].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Kategorie I (DUR / ZMES)</div><div class='metric-value'>{c1_dur:,.2f} / {c1_zmes:,.2f}</div></div>".replace(",", " "), unsafe_allow_html=True)
m[2].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Kategorie II (DUR / ZMES)</div><div class='metric-value'>{c2_dur:,.2f} / {c2_zmes:,.2f}</div></div>".replace(",", " "), unsafe_allow_html=True)
m[3].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Probíhá</div><div class='metric-value'>0.00 Kč</div></div>", unsafe_allow_html=True)
m[4].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Zakázek</div><div class='metric-value'>{count_zakazek}</div></div>", unsafe_allow_html=True)

if st.session_state.role == "supervisor":
    st.info("Režim Editor: Změny v tabulce se projeví po uložení.")
    # Zde používáme data_editor pro Supervisor roli
    edited = st.data_editor(df_active, num_rows="dynamic", height=450, use_container_width=True)
    if st.button("💾 Uložit data"):
        st.success("Data uložena do paměti (pro trvalé uložení do souboru je nutné propojení s GitHubem/DB).")
else:
    # Read-only HTML tabulka pro User roli (přesně podle návrhu)
    html = '<div class="table-container"><table class="html-table">'
    html += '<colgroup><col style="width:35px"><col style="width:90px">' + '<col style="width:115px">'*6 + '<col style="width:90px"><col style="width:250px">' + '<col style="width:115px">'*3 + '</colgroup>'
    html += '<thead><tr><th rowspan="2">Poř.č.</th><th rowspan="2">Firma</th><th colspan="3">Kategorie I</th><th colspan="3">Kategorie II</th><th rowspan="2">Č.stavby</th><th rowspan="2">Název stavby</th><th rowspan="2">Nabídka</th><th rowspan="2">Rozdíl</th><th rowspan="2">Vyfaktur.</th></tr>'
    html += '<tr><th>PS</th><th>SNK</th><th>BO</th><th>PS</th><th>BO</th><th>Poruch</th></tr></thead><tbody>'
    
    for _, row in df_active.iterrows():
        html += '<tr>'
        for i in range(13): # Zobrazení prvních 13 nejdůležitějších sloupců
            val = row[i]
            cls = ' class="num-align"' if i in [0,2,3,4,5,6,7,10,11,12] else ""
            if i == 11 and float(val or 0) < 0: cls = ' class="red-bold"'
            # Formát čísel
            if i in [2,3,4,5,6,7,10,11,12] and val != "":
                val = f"{float(val):,.2f}".replace(",", " ")
            html += f'<td{cls}>{val}</td>'
        html += '</tr>'
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)
