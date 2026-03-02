import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A AGRESIVNÍ CSS ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    /* Skrytí menu */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 0.5rem !important; }

    /* TOTÁLNÍ VYNUCENÍ POSUVNÍKU - ORANŽOVÁ PRO KONTROLU */
    html, body, [data-testid="stAppViewContainer"], .stDataFrame, div[data-testid="stDataTableVisualizer"] {
        scrollbar-width: auto !important; /* Pro Firefox */
        scrollbar-color: #ff4b4b #f1f1f1 !important;
    }

    ::-webkit-scrollbar {
        width: 35px !important; 
        height: 35px !important;
        display: block !important;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
        display: block !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #ff4b4b !important; /* Červeno-oranžová pro test, zda se změní */
        border-radius: 0px !important;
        border: 4px solid #f1f1f1 !important;
        display: block !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        
        # Peněžní sloupce na text (fix desetin)
        m_cols = [c for c in df.columns if any(x in c.lower() for x in ['nabídka', 'rozdíl', 'bez dph', 'vyfaktur', 'ps', 'snk', 'bo'])]
        for c in m_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).apply(lambda x: f"{x:.2f}")
            
        return df, m_cols
    except:
        return pd.DataFrame(), []

df_raw, money_cols = load_data()

if not df_raw.empty:
    col_stav = next((c for c in df_raw.columns if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_rozdil = next((c for c in df_raw.columns if 'rozdíl' in c.lower()), None)

    # --- 3. LIŠTA A SOUČTY ---
    c1, c2 = st.columns([1, 3])
    with c1: st.markdown("#### 🏗️ Evidence 2026")
    with c2: hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat...")

    df_f = df_raw.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    # Zobrazení metrik
    m1, m2, m3, m4, m5 = st.columns(5)
    def get_s(kw):
        cn = next((c for c in money_cols if 'nabídka' in c.lower()), money_cols[0])
        return df_f[df_f[col_stav].astype(str).str.contains(kw, case=False, na=False)][cn].astype(float).sum()

    m1.metric("CELKEM", f"{df_f[money_cols[0]].astype(float).sum():,.2f}".replace(",", " ") + " Kč")
    m2.metric("ZAKÁZEK", len(df_f))

    # --- 4. TABULKA (BRUTÁLNĚ SNÍŽENÁ VÝŠKA) ---
    def style_row(row):
        styles = [''] * len(row)
        if col_stav:
            s = str(row[col_stav]).lower()
            color = ''
            if 'hotov' in s: color = 'background-color: #f1fcf4'
            elif 'probíh' in s: color = 'background-color: #fffdf2'
            styles = [color] * len(row)
        if col_rozdil and "-" in str(row[col_rozdil]):
            styles[row.index.get_loc(col_rozdil)] = 'color: #d00000; font-weight: bold;'
        return styles

    # Datumy
    for c in df_f.columns:
        if any(x in c.lower() for x in ['dne', 'ukončení']):
            df_f[c] = pd.to_datetime(df_f[c], errors='coerce').dt.strftime('%d.%m.%Y').replace('NaT', '')

    # POKUD 530px BYLO 30 ŘÁDKŮ, DÁVÁM 280px PRO 16 ŘÁDKŮ
    st.dataframe(
        df_f.style.apply(style_row, axis=1),
        use_container_width=True, 
        height=280, 
        hide_index=True
    )
else:
    st.error("Data nenalezena.")
