import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { 
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important; 
        padding-left: 0.5rem !important; 
        padding-right: 0.5rem !important;
        max-width: 100% !important;
    }
    .custom-head { font-size: 1.1rem; font-weight: bold; margin-top: 0.3rem; margin-bottom: 0.3rem; }
    .metric-box {
        border: 1px solid #d1d5db;
        background-color: #f9fafb;
        padding: 3px 8px;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 5px;
    }
    .metric-label { font-size: 0.65rem; color: #6b7280; text-transform: uppercase; }
    .metric-value { font-size: 0.85rem; font-weight: bold; color: #111827; }

    /* TABULKA - VÝŠKA NA 16 ŘÁDKŮ */
    .table-container {
        height: 400px; 
        overflow-y: scroll;
        overflow-x: auto;
        border: 1px solid #e5e7eb;
    }
    /* MASIVNÍ POSUVNÍK */
    .table-container::-webkit-scrollbar { width: 35px !important; height: 35px !important; }
    .table-container::-webkit-scrollbar-track { background: #f1f1f1 !important; }
    .table-container::-webkit-scrollbar-thumb { background: #888 !important; border: 5px solid #f1f1f1; }

    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 12px; }
    .html-table th { 
        position: sticky; top: 0; 
        background-color: #f3f4f6; color: #374151; 
        padding: 6px; border: 1px solid #e5e7eb; z-index: 10;
        text-align: left;
    }
    .html-table td { padding: 4px 6px; border: 1px solid #e5e7eb; white-space: nowrap; }
    .row-hotovo { background-color: #f0fdf4 !important; }
    .row-probiha { background-color: #fffbeb !important; }
    .red-bold { color: #dc2626; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ A PŘESNÉ POŘADÍ SLOUPCŮ ---
@st.cache_data(ttl=1)
def load_data():
    try:
        # Čteme data od řádku 4 (kde jsou názvy jako poř.č., firma...)
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        
        # DEFINICE PŘESNÝCH NÁZVŮ PODLE TVÉHO OBRÁZKU (bez .1, .2 atd.)
        # Toto přepíše to, co Pandas načte špatně ze sloučených buněk
        custom_headers = [
            "poř.č.", "firma", "PS", "SNK", "BO", "PS", "BO", "poruchy", 
            "č.stavby", "název stavby", "nabídka", "rozdíl", "vyfaktur.", 
            "ukončení", "zrealizováno", "SOD", "ze dne", "objednatel", 
            "stavbyvedoucí", "nabídková cena", "č.faktury", "částka bez DPH", "splatná"
        ]
        
        # Ořízneme DataFrame na počet definovaných sloupců, pokud jich je v Excelu víc/míň
        df = df.iloc[:, :len(custom_headers)]
        df.columns = custom_headers
        
        # Likvidace nan/NaT
        df = df.replace({np.nan: '', 'nan': '', 'NaT': '', 'None': ''})
        return df
    except Exception as e:
        st.error(f"Chyba při načítání: {e}")
        return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # Horní lišta
    c_h1, c_h2 = st.columns([1, 5])
    with c_h1: st.markdown('<div class="custom-head">Evidence 2026</div>', unsafe_allow_html=True)
    with c_h2: hledat = st.text_input("", placeholder="Hledat...", label_visibility="collapsed")

    df = df_raw.copy()
    if hledat:
        df = df[df.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    # Seznamy pro formátování
    money_cols = ["PS", "SNK", "BO", "poruchy", "nabídka", "rozdíl", "vyfaktur.", "nabídková cena", "částka bez DPH"]
    date_cols = ["ukončení", "zrealizováno", "ze dne", "splatná"]
    
    # Hledáme sloupec se stavem (pravděpodobně 'firma' nebo jiný, pokud v Excelu není explicitní 'stav')
    # Pokud máš v Excelu sloupec "stav", kód ho použije pro barvy
    col_stav = next((c for c in df.columns if 'stav' in str(c).lower()), None)

    # --- 3. SOUČTY ---
    def get_val(kw=None):
        col_n = "nabídka" if "nabídka" in df.columns else df.columns[10]
        nums = pd.to_numeric(df[col_n], errors='coerce').fillna(0)
        if kw and col_stav:
            mask = df[col_stav].astype(str).str.contains(kw, case=False, na=False)
            return nums[mask].sum()
        return nums.sum()

    m = st.columns(5)
    labels = ["CELKEM", "HOTOVO", "FAKTURACE", "PROBÍHÁ", "ZAKÁZEK"]
    vals = [
        f"{get_val():,.2f}".replace(",", " ") + " Kč",
        f"{get_val('hotov'):,.2f}".replace(",", " ") + " Kč",
        f"{get_val('faktur'):,.2f}".replace(",", " ") + " Kč",
        f"{get_val('probíh'):,.2f}".replace(",", " ") + " Kč",
        str(len(df))
    ]
    for i in range(5):
        m[i].markdown(f'<div class="metric-box"><div class="metric-label">{labels[i]}</div><div class="metric-value">{vals[i]}</div></div>', unsafe_allow_html=True)

    # --- 4. TABULKA (HTML) ---
    html = '<div class="table-container"><table class="html-table"><thead><tr>'
    for c in df.columns: 
        html += f'<th>{c}</th>'
    html += '</tr></thead><tbody>'

    for _, row in df.iterrows():
        tr_cls = ""
        if col_stav:
            s = str(row[col_stav]).lower()
            if 'hotov' in s: tr_cls = ' class="row-hotovo"'
            elif 'probíh' in s: tr_cls = ' class="row-probiha"'
        
        html += f'<tr{tr_cls}>'
        for i, (col_name, v) in enumerate(row.items()):
            td_cls = ""
            val_str = ""
            
            if v is not None and str(v).strip().lower() not in ['nan', 'nat', 'none', '']:
                # Formát peněz
                if col_name in money_cols:
                    try:
                        n = float(v)
                        val_str = f"{n:.2f}"
                        if col_name == "rozdíl" and n < 0: td_cls = ' class="red-bold"'
                    except: val_str = str(v)
                # Formát data
                elif col_name in date_cols:
                    try:
                        val_str = pd.to_datetime(v).strftime('%d.%m.%Y')
                        if "1900" in val_str: val_str = ""
                    except: val_str = str(v)
                else:
                    val_str = str(v)

            html += f'<td{td_cls}>{val_str}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)
else:
    st.error("Data nenalezena.")
