import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE A STYLING ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding: 0rem 0.5rem !important; max-width: 100% !important; }
    
    .table-container {
        height: 450px; 
        overflow-y: scroll;
        overflow-x: auto;
        border: 1px solid #e5e7eb;
    }
    
    /* Široký posuvník pro snadné ovládání */
    .table-container::-webkit-scrollbar { width: 35px; height: 35px; }
    .table-container::-webkit-scrollbar-track { background: #f1f1f1; }
    .table-container::-webkit-scrollbar-thumb { background: #888; border: 5px solid #f1f1f1; }

    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 12px; }
    
    /* Styling hlavičky podle vzoru */
    .html-table th { 
        position: sticky; top: 0; 
        background-color: #f3f4f6; border: 1px solid #000;
        padding: 4px; z-index: 10; text-align: center;
    }
    .cat-i { background-color: #ffff00 !important; color: black; font-weight: bold; } /* Žlutá Kategorie I */
    .cat-ii { background-color: #00ffff !important; color: black; font-weight: bold; } /* Azurová Kategorie II */
    
    .html-table td { padding: 4px 6px; border: 1px solid #e5e7eb; white-space: nowrap; }
    .row-hotovo { background-color: #f0fdf4 !important; }
    .row-probiha { background-color: #fffbeb !important; }
    .red-bold { color: #dc2626; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=1)
def load_data():
    try:
        # Čteme data od řádku 5 (skutečná data začínají pod hlavičkami)
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=5, header=None, engine='openpyxl')
        df = df.dropna(how='all')
        # Vyčištění od nan/NaT
        df = df.replace({np.nan: '', 'nan': '', 'NaT': '', 'None': ''})
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Horní lišta a součty (zjednodušeno pro přehlednost)
    st.markdown('<div style="font-size: 1.2rem; font-weight: bold;">Evidence 2026</div>', unsafe_allow_html=True)
    
    # --- 3. RUČNÍ SESTAVENÍ HTML TABULKY S DVOUŘÁDKOVOU HLAVIČKOU ---
    html = '<div class="table-container"><table class="html-table">'
    
    # První řádek hlavičky (Kategorie)
    html += '<thead>'
    html += '<tr>'
    html += '<th rowspan="2">poř.č.</th>'
    html += '<th rowspan="2">firma</th>'
    html += '<th colspan="3" class="cat-i">kategorie I</th>'
    html += '<th colspan="3" class="cat-ii">kategorie II</th>'
    html += '<th rowspan="2">č.stavby</th>'
    html += '<th rowspan="2">název stavby</th>'
    html += '<th rowspan="2">nabídka</th>'
    html += '<th rowspan="2">rozdíl</th>'
    html += '<th rowspan="2">vyfaktur.</th>'
    html += '<th rowspan="2">ukončení</th>'
    html += '<th rowspan="2">zrealizováno</th>'
    html += '<th rowspan="2">SOD</th>'
    html += '<th rowspan="2">ze dne</th>'
    html += '<th rowspan="2">objednatel</th>'
    html += '<th rowspan="2">stavbyvedoucí</th>'
    html += '<th rowspan="2">nabídková cena</th>'
    html += '<th rowspan="2">č.faktury</th>'
    html += '<th rowspan="2">částka bez DPH</th>'
    html += '<th rowspan="2">splatná</th>'
    html += '</tr>'
    
    # Druhý řádek hlavičky (Podnázvy)
    html += '<tr>'
    html += '<th>PS</th><th>SNK</th><th>BO</th>' # Pod Kat I
    html += '<th>PS</th><th>BO</th><th>poruch</th>' # Pod Kat II
    html += '</tr></thead><tbody>'

    # --- 4. VÝPIS DAT ---
    for _, row in df.iterrows():
        # Logika pro barvy řádků (předpokládáme, že stav je v jednom ze sloupců)
        tr_cls = ""
        # Zde můžete přidat podmínku pro row[index] pro barvení
        
        html += f'<tr{tr_cls}>'
        for i, val in enumerate(row):
            if i >= 23: break # Omezení na počet sloupců v hlavičce
            
            td_cls = ""
            val_str = str(val)
            
            # Formátování čísel (sloupce 2-7 a 10-12 atd. jsou peněžní)
            if i in [2, 3, 4, 5, 6, 7, 10, 11, 12, 19, 21]:
                try:
                    n = float(val)
                    val_str = f"{n:.2f}"
                    if i == 11 and n < 0: td_cls = ' class="red-bold"' # Sloupec "rozdíl"
                except: pass
                
            # Formátování dat
            elif i in [13, 14, 16, 22]:
                try: val_str = pd.to_datetime(val).strftime('%d.%m.%Y')
                except: pass

            html += f'<td{td_cls}>{val_str}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)
else:
    st.error("Data nebyla načtena. Zkontrolujte název souboru.")
