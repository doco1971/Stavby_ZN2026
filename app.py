import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A POSUVNÍK ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding-top: 0.5rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    
    /* STYL TABULKY - ČISTÉ HTML */
    .table-container {
        height: 500px; /* VÝŠKA PRO CCA 16 ŘÁDKŮ */
        overflow-y: scroll;
        display: block;
        border: 1px solid #e2e8f0;
    }
    table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 13px; }
    th { position: sticky; top: 0; background: #f8fafc; padding: 8px; border-bottom: 2px solid #cbd5e1; text-align: left; z-index: 10; }
    td { padding: 6px 8px; border-bottom: 1px solid #e2e8f0; }
    
    /* ŠIROKÝ POSUVNÍK */
    .table-container::-webkit-scrollbar { width: 16px; height: 16px; }
    .table-container::-webkit-scrollbar-thumb { background: #888; border-radius: 4px; border: 3px solid #fff; }
    .table-container::-webkit-scrollbar-track { background: #f1f1f1; }

    /* METRIKY */
    .metric-box { border: 1px solid #e2e8f0; background: white; padding: 5px 10px; border-radius: 4px; margin-bottom: 10px; }
    .metric-label { font-size: 0.7rem; color: #64748b; }
    .metric-value { font-size: 1rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ A FORMÁT ---
@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        df = df[df[df.columns[0]].notna()]
        return df
    except: return pd.DataFrame()

df = load_data()

if not df.empty:
    # Identifikace sloupců
    money_cols = [c for c in df.columns if any(x in c.lower() for x in ['nabídka', 'rozdíl', 'bez dph', 'vyfaktur'])]
    col_stav = next((c for c in df.columns if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_rozdil = next((c for c in df.columns if 'rozdíl' in c.lower()), None)

    # HLAVNÍ FORMÁTOVÁNÍ - Tady vzniká ten text 00 000 000.00
    def format_money(val):
        try:
            return f"{float(val):,.2True}".replace(",", " ")
        except: return val

    # HLEDÁNÍ
    c1, c2 = st.columns([1, 3])
    with c1: st.markdown("#### 🏗️ Evidence 2026")
    with c2: hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat...")

    if hledat:
        df = df[df.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    # SOUČTY
    m1, m2, m3, m4, m5 = st.columns(5)
    def get_s(kw):
        col_n = next((c for c in money_cols if 'nabídka' in c.lower()), money_cols[0])
        return pd.to_numeric(df[df[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_n], errors='coerce').sum()

    m1.metric("CELKEM", f"{pd.to_numeric(df[money_cols[0]], errors='coerce').sum():,.2f}".replace(",", " ") + " Kč")
    m2.metric("HOTOVO", f"{get_s('hotov'):,.2f}".replace(",", " ") + " Kč")
    m3.metric("FAKTURACE", f"{get_s('faktur'):,.2f}".replace(",", " ") + " Kč")
    m4.metric("PROBÍHÁ", f"{get_s('probíh'):,.2f}".replace(",", " ") + " Kč")
    m5.metric("ZAKÁZEK", len(df))

    # --- 3. GENEROVÁNÍ HTML TABULKY ---
    html = '<div class="table-container"><table><thead><tr>'
    for c in df.columns:
        html += f'<th>{c}</th>'
    html += '</tr></thead><tbody>'

    for _, row in df.iterrows():
        # Barva řádku podle stavu
        bg = ""
        st_val = str(row[col_stav]).lower() if col_stav else ""
        if 'hotov' in st_val: bg = 'style="background-color: #f1fcf4"'
        elif 'probíh' in st_val: bg = 'style="background-color: #fffdf2"'
        elif 'faktur' in st_val: bg = 'style="background-color: #f0f7ff"'
        
        html += f'<tr {bg}>'
        for col_name in df.columns:
            val = row[col_name]
            style = ""
            
            # Formátování čísel a červená barva pro mínus
            if col_name in money_cols:
                try:
                    num_val = float(val)
                    if col_name == col_rozdil and num_val < 0:
                        style = 'style="color: #d00000; font-weight: bold;"'
                    val = f"{num_val:,.2f}".replace(",", " ")
                except: pass
            
            # Datum
            if any(x in col_name.lower() for x in ['dne', 'ukončení']):
                try: val = pd.to_datetime(val).strftime('%d.%m.%Y')
                except: pass

            html += f'<td {style}>{val}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)

else:
    st.error("Data nebyla nalezena.")
