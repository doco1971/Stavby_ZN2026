import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A ROZTAŽENÍ ---
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

    /* TABULKA - VÝŠKA PRO 16 ŘÁDKŮ */
    .table-container {
        height: 400px; 
        overflow-y: scroll;
        overflow-x: auto;
        border: 1px solid #e5e7eb;
    }

    .table-container::-webkit-scrollbar { width: 30px !important; height: 30px !important; }
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

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=1)
def load_data():
    try:
        # Načteme data - skiprows=4 zajistí, že čteme řádek s názvy sloupců (poř.č., firma, PS...)
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        
        # Očištění názvů sloupců od mezer
        df.columns = [str(c).strip() for c in df.columns]
        
        # Nahrazení 'nan' prázdným místem
        df = df.fillna('')
        return df
    except: return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # Horní lišta
    c_h1, c_h2 = st.columns([1, 5])
    with c_h1: st.markdown('<div class="custom-head">Evidence 2026</div>', unsafe_allow_html=True)
    with c_h2: hledat = st.text_input("", placeholder="Hledat...", label_visibility="collapsed")

    df = df_raw.copy()
    if hledat:
        df = df[df.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    # Definice peněžních sloupců podle tvého originálu
    money_cols = [
        'PS', 'SNK', 'BO', 'PS.1', 'BO.1', 'poruch', 'nabídka', 
        'rozdíl', 'vyfaktur', 'nabídková cena', 'částka bez DPH'
    ]
    # Najdeme sloupec se stavem pro barvení
    col_stav = next((c for c in df.columns if 'stav' in c.lower() and 'název' not in c.lower()), None)
    # Hlavní sloupec pro součty
    col_nabidka = next((c for c in df.columns if 'nabídka' in c.lower()), None)

    # --- 3. SOUČTY ---
    def get_val(kw=None):
        if not col_nabidka: return 0
        nums = pd.to_numeric(df[col_nabidka], errors='coerce').fillna(0)
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
        cls = ""
        if col_stav:
            s = str(row[col_stav]).lower()
            if 'hotov' in s: cls = ' class="row-hotovo"'
            elif 'probíh' in s: cls = ' class="row-probiha"'
        
        html += f'<tr{cls}>'
        for c in df.columns:
            v = row[c]
            val_str = str(v)
            td_cls = ""

            # Formátování peněz
            if any(m in c.lower() for m in money_cols) and v != '':
                try:
                    n = float(v)
                    val_str = f"{n:.2f}"
                    if 'rozdíl' in c.lower() and n < 0: td_cls = ' class="red-bold"'
                except: pass
            
            # Formátování dat
            elif any(x in c.lower() for x in ['dne', 'ukončení', 'splatná']) and v != '':
                try: val_str = pd.to_datetime(v).strftime('%d.%m.%Y')
                except: pass

            html += f'<td{td_cls}>{val_str}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)
else:
    st.error("Data nenalezena.")
