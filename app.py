import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

# --- 2. TOTÁLNÍ STYLING (OPRAVA MEZER A RÁMEČKŮ) ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Odstranění prázdného místa nahoře */
    .block-container { 
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important; 
    }

    /* Nadpis a hledání v jedné lince */
    .custom-head { 
        font-size: 1.2rem; 
        font-weight: bold; 
        margin-bottom: 0.5rem; 
        margin-top: 0.5rem;
    }

    /* Součty v rámečcích */
    .metric-box {
        border: 1px solid #d1d5db;
        background-color: #f9fafb;
        padding: 5px 10px;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-label { font-size: 0.7rem; color: #6b7280; text-transform: uppercase; }
    .metric-value { font-size: 0.9rem; font-weight: bold; color: #111827; }

    /* TABULKA A POSUVNÍK - LIMIT 16 ŘÁDKŮ */
    .table-container {
        height: 520px; /* Pevná výška pro cca 16 řádků */
        overflow-y: scroll;
        overflow-x: auto;
        border: 1px solid #e5e7eb;
    }

    .table-container::-webkit-scrollbar { width: 30px !important; height: 30px !important; }
    .table-container::-webkit-scrollbar-track { background: #f1f1f1 !important; }
    .table-container::-webkit-scrollbar-thumb { background: #888 !important; border: 5px solid #f1f1f1; }

    .html-table { width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 13px; }
    .html-table th { 
        position: sticky; top: 0; 
        background-color: #f3f4f6; color: #374151; 
        padding: 8px; border: 1px solid #e5e7eb; z-index: 10;
    }
    .html-table td { padding: 6px; border: 1px solid #e5e7eb; white-space: nowrap; }
    
    /* Barvy */
    .row-hotovo { background-color: #f0fdf4 !important; }
    .row-probiha { background-color: #fffbeb !important; }
    .red-bold { color: #dc2626; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    # Horní lišta: Nadpis + Hledání
    c_h1, c_h2 = st.columns([1, 4])
    with c_h1: st.markdown('<div class="custom-head">Evidence 2026</div>', unsafe_allow_html=True)
    with c_h2: hledat = st.text_input("", placeholder="Hledat...", label_visibility="collapsed")

    # Filtrování
    df = df_raw.copy()
    if hledat:
        df = df[df.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    # Sloupce
    money_cols = [c for c in df.columns if any(x in c.lower() for x in ['nabídka', 'rozdíl', 'bez dph', 'vyfaktur', 'ps', 'snk', 'bo', 'poruchy'])]
    col_stav = next((c for c in df.columns if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_nabidka = next((c for c in money_cols if 'nabídka' in c.lower()), money_cols[0] if money_cols else None)

    # --- 4. SOUČTY V RÁMEČCÍCH ---
    def get_val(kw=None):
        if not col_nabidka: return 0
        d = df.copy()
        d[col_nabidka] = pd.to_numeric(d[col_nabidka], errors='coerce').fillna(0)
        if kw and col_stav:
            return d[d[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_nabidka].sum()
        return d[col_nabidka].sum()

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

    # --- 5. TABULKA (HTML) ---
    html = '<div class="table-container"><table class="html-table"><thead><tr>'
    for c in df.columns: html += f'<th>{c}</th>'
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
            val_str = str(v) if pd.notna(v) else ""
            td_cls = ""

            if c in money_cols:
                try:
                    n = float(v)
                    val_str = f"{n:.2f}"
                    if 'rozdíl' in c.lower() and n < 0: td_cls = ' class="red-bold"'
                except: pass
            elif any(x in c.lower() for x in ['dne', 'ukončení']):
                try: val_str = pd.to_datetime(v).strftime('%d.%m.%Y')
                except: pass

            html += f'<td{td_cls}>{val_str}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)
else:
    st.error("Data nenalezena.")
