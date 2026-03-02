import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A ABSOLUTNÍ FIXACE VRŠKU ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    /* Skrytí systémových prvků */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* VYNUCENÁ FIXACE HORNÍHO PANELU */
    /* Zaměříme se na hlavní kontejner a první blok v něm */
    .stAppViewMain {
        overflow: hidden;
    }
    
    /* Tento blok vytvoří fixní zónu nahoře */
    [data-testid="stVerticalBlock"] > div:first-child {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        background-color: white;
        z-index: 999999;
        padding: 1rem 2rem;
        border-bottom: 2px solid #f0f2f6;
    }

    /* Odsazení pro zbytek obsahu, aby nezajížděl pod fixní vršek */
    [data-testid="stVerticalBlock"] > div:nth-child(2) {
        margin-top: 180px; /* Upravte podle výšky vašeho panelu */
    }

    .block-container { padding-top: 0rem; }
    h4 { margin: 0; padding-bottom: 5px; font-size: 1.2rem; color: #1e3a5f; font-weight: 800; }
    
    .stMetric { 
        border: 1px solid #e6e9ef; 
        background-color: #ffffff;
        padding: 5px !important;
        border-radius: 5px;
    }
    div[data-testid="stMetricValue"] { font-size: 1rem !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

df_all = load_data()

if not df_all.empty:
    cols = df_all.columns.tolist()
    col_nabidka = next((c for c in cols if 'nabídka' in c.lower() or 'cena' in c.lower()), None)
    col_stav = next((c for c in cols if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_vedouci = next((c for c in cols if 'vedoucí' in c.lower() or 'stavbyved' in c.lower()), None)

    if col_nabidka:
        df_all[col_nabidka] = pd.to_numeric(df_all[col_nabidka], errors='coerce').fillna(0)

    # --- 3. TENTO BLOK BUDE FIXNÍ (Díky CSS nth-child(1)) ---
    with st.container():
        st.markdown("#### 🏗️ Evidence zakázek 2026")
        
        f1, f2, f3 = st.columns([2, 1, 1])
        with f1:
            hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Rychlé hledání...")
        with f2:
            v_opt = ["Všichni vedoucí"] + sorted([str(x) for x in df_all[col_vedouci].dropna().unique()]) if col_vedouci else ["Všichni"]
            sel_v = st.selectbox("Vedoucí", v_opt, label_visibility="collapsed")
        with f3:
            s_opt = ["Všechny stavy"] + sorted([str(x) for x in df_all[col_stav].dropna().unique()]) if col_stav else ["Vše"]
            sel_s = st.selectbox("Stav", s_opt, label_visibility="collapsed")

        df_f = df_all.copy()
        if hledat:
            df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
        if col_vedouci and sel_v != "Všichni vedoucí":
            df_f = df_f[df_f[col_vedouci].astype(str) == sel_v]
        if col_stav and sel_s != "Všechny stavy":
            df_f = df_f[df_f[col_stav].astype(str) == sel_s]

        if col_nabidka:
            m1, m2, m3, m4, m5 = st.columns(5)
            def sum_kw(df, kw):
                return df[df[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_nabidka].sum() if col_stav else 0
            
            m1.metric("CELKEM", f"{df_f[col_nabidka].sum():,.0f} Kč".replace(',', ' '))
            m2.metric("HOTOVO", f"{sum_kw(df_f, 'hotov'):,.0f} Kč".replace(',', ' '))
            m3.metric("FAKTURACE", f"{sum_kw(df_f, 'faktur'):,.0f} Kč".replace(',', ' '))
            m4.metric("PROBÍHÁ", f"{sum_kw(df_f, 'probíh'):,.0f} Kč".replace(',', ' '))
            m5.metric("STAVEB", f"{len(df_f)}")

    # --- 4. TATO ČÁST BUDE ROLOVAT (Díky nth-child(2) marginu) ---
    def style_rows(row):
        color = ''
        if col_stav:
            status = str(row[col_stav]).lower()
            if 'hotov' in status: color = 'background-color: #dcfce7'
            elif 'probíh' in status: color = 'background-color: #fef9c3'
            elif 'faktur' in status: color = 'background-color: #dbeafe'
        return [color] * len(row)

    st.dataframe(df_f.style.apply(style_rows, axis=1), use_container_width=True, height=1500)
    
else:
    st.error("Data nebyla nalezena.")
