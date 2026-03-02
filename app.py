import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Evidence 2026", layout="wide")

# --- CSS STYLY (Čistý vzhled, šedé záhlaví, fixní výška) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding: 0.5rem !important; }
    .table-container { height: 450px; overflow: auto; border: 1px solid #000; }
    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 12px; }
    .html-table th { position: sticky; top: 0; background-color: #f3f4f6; border: 1px solid #000; padding: 4px; z-index: 10; }
    .html-table td { border: 1px solid #000; padding: 3px 6px; white-space: nowrap; }
    .num { text-align: right; }
    .red { color: red; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=1)
def load_data():
    try:
        # Načteme surová data od řádku 6
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=5, header=None, engine='openpyxl')
        # Ořízneme na 23 sloupců, aby to sedělo s hlavičkou
        df = df.iloc[:, :23]
        # Totální čistka nan/NaT hned při startu
        df = df.replace({np.nan: '', 'nan': '', 'NaT': '', 'None': ''})
        return df
    except: return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # Metriky (zjednodušené, aby nezabíraly místo)
    nabidka_sum = pd.to_numeric(df_raw[10], errors='coerce').sum()
    st.markdown(f"**CELKEM: {nabidka_sum:,.2f} Kč | ZAKÁZEK: {len(df_raw[df_raw[0]!=''])}**".replace(",", " "), unsafe_allow_html=True)
    
    hledat = st.text_input("", placeholder="Hledat...", label_visibility="collapsed")
    df = df_raw.copy()
    if hledat:
        df = df[df.apply(lambda r: hledat.lower() in str(r.values).lower(), axis=1)]

    # --- RUČNÍ STAVBA HTML (Přesně 23 sloupců) ---
    html = '<div class="table-container"><table class="html-table"><thead>'
    # 1. řádek hlavičky
    html += '<tr><th rowspan="2">poř.č.</th><th rowspan="2">firma</th>'
    html += '<th colspan="3">kategorie I</th><th colspan="3">kategorie II</th>'
    html += '<th rowspan="2">č.stavby</th><th rowspan="2">název stavby</th>'
    html += '<th rowspan="2">nabídka</th><th rowspan="2">rozdíl</th><th rowspan="2">vyfaktur.</th>'
    html += '<th rowspan="2">ukončení</th><th rowspan="2">zrealiz.</th><th rowspan="2">SOD</th>'
    html += '<th rowspan="2">ze dne</th><th rowspan="2">objednatel</th><th rowspan="2">stavbyved.</th>'
    html += '<th rowspan="2">nabídková c.</th><th rowspan="2">č.faktury</th><th rowspan="2">bez DPH</th><th rowspan="2">splatná</th></tr>'
    # 2. řádek hlavičky
    html += '<tr><th>PS</th><th>SNK</th><th>BO</th><th>PS</th><th>BO</th><th>poruch</th></tr></thead><tbody>'

    for _, row in df.iterrows():
        html += '<tr>'
        for i in range(23):
            val = row[i]
            cls = ""
            # Formátování čísel (sloupce s penězi)
            if i in [2,3,4,5,6,7,10,11,12,19,21]:
                try:
                    num = float(val)
                    val = f"{num:.2f}"
                    cls = ' class="num"'
                    if i == 11 and num < 0: cls = ' class="num red"'
                except: val = "" if str(val).lower() == 'nan' else val
            # Formátování dat
            elif i in [13,14,16,22]:
                try: val = pd.to_datetime(val).strftime('%d.%m.%Y')
                except: val = ""

            html += f'<td{cls}>{val}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)
