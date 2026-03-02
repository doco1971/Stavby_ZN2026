import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 0.5rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    .stApp { background-color: #f4f6f8; }
    
    /* ŠIROKÝ A VIDITELNÝ POSUVNÍK */
    ::-webkit-scrollbar { width: 14px; height: 14px; }
    ::-webkit-scrollbar-thumb { background: #888; border-radius: 10px; border: 3px solid #f4f6f8; }
    ::-webkit-scrollbar-track { background: #eee; }

    /* KOMPAKTNÍ METRIKY */
    div[data-testid="stMetric"] { 
        border: 1px solid #e2e8f0; background-color: white; padding: 5px !important; border-radius: 4px; height: 50px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 1rem !important; font-weight: 700 !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ A PŘÍSNÁ ÚPRAVA DAT ---
@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        df = df[df[df.columns[0]].notna()]
        
        # PŘEVOD FINANCÍ NA TEXT (STRIKTNÍ 2 DESETINY)
        money_cols = [c for c in df.columns if any(x in c.lower() for x in ['nabídka', 'rozdíl', 'bez dph', 'vyfaktur', 'ps', 'snk', 'bo', 'poruchy'])]
        
        for c in money_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            # Tady vytváříme finální řetězec, se kterým Streamlit už nehne
            df[c] = df[c].apply(lambda x: f"{x:.2f}")
            
        return df, money_cols
    except:
        return pd.DataFrame(), []

df_raw, money_cols = load_data()

if not df_raw.empty:
    col_stav = next((c for c in df_raw.columns if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_rozdil = next((c for c in df_raw.columns if 'rozdíl' in c.lower()), None)

    # --- 3. LIŠTA A FILTR ---
    c1, c2 = st.columns([1, 3])
    with c1: st.markdown("#### 🏗️ Evidence 2026")
    with c2: hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat...")

    df_f = df_raw.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    # --- 4. SOUČTY (Výpočet z textových hodnot) ---
    def get_sum(kw):
        col_n = next((c for c in money_cols if 'nabídka' in c.lower()), None)
        if col_stav and col_n:
            return df_f[df_f[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_n].astype(float).sum()
        return 0

    m1, m2, m3, m4, m5 = st.columns(5)
    total_val = df_f[next(c for c in money_cols if 'nabídka' in c.lower())].astype(float).sum()
    
    m1.metric("CELKEM", f"{total_val:,.2f}".replace(",", " ").replace(".", ",") + " Kč")
    m2.metric("HOTOVO", f"{get_sum('hotov'):,.2f}".replace(",", " ").replace(".", ",") + " Kč")
    m3.metric("FAKTURACE", f"{get_sum('faktur'):,.2f}".replace(",", " ").replace(".", ",") + " Kč")
    m4.metric("PROBÍHÁ", f"{get_sum('probíh'):,.2f}".replace(",", " ").replace(".", ",") + " Kč")
    m5.metric("ZAKÁZEK", len(df_f))

    # --- 5. STYLING A TABULKA ---
    def style_row(row):
        styles = [''] * len(row)
        if col_stav:
            s = str(row[col_stav]).lower()
            color = ''
            if 'hotov' in s: color = 'background-color: #f1fcf4'
            elif 'probíh' in s: color = 'background-color: #fffdf2'
            elif 'faktur' in s: color = 'background-color: #f0f7ff'
            styles = [color] * len(row)
        
        if col_rozdil:
            idx = row.index.get_loc(col_rozdil)
            if float(row[col_rozdil]) < 0:
                styles[idx] += '; color: #d00000; font-weight: bold;'
        return styles

    # Formátování dat na DD.MM.RRRR
    for c in df_f.columns:
        if any(x in c.lower() for x in ['dne', 'ukončení']):
            df_f[c] = pd.to_datetime(df_f[c], errors='coerce').dt.strftime('%d.%m.%Y').replace('NaT', '')

    st.dataframe(
        df_f.style.apply(style_row, axis=1),
        use_container_width=True, 
        height=575, # Nastaveno tak, aby při 16 řádcích naskočil posuvník
        hide_index=True
    )
    
else:
    st.error("Data nebyla nalezena.")
