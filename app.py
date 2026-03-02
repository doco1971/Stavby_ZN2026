import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A FIXACE VRCHNÍ ČÁSTI ---
st.set_page_config(page_title="ZN 2026", layout="wide")

st.markdown("""
    <style>
    /* Skrytí systémových prvků */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* FIXACE VRŠKU: Nadpis, Filtry a Metriky zůstanou nahoře */
    [data-testid="stVerticalBlock"] > div:first-child {
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 999;
        padding-top: 1rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f2f6;
    }

    .block-container { padding-top: 0rem; padding-bottom: 0rem; }
    h4 { margin: 0; padding: 5px 0; font-size: 1.2rem; color: #1e3a5f; font-weight: 800; }
    
    .stMetric { 
        padding: 2px 8px !important; 
        border: 1px solid #f0f2f6; 
        background: #f8f9fc;
        border-radius: 4px;
    }
    div[data-testid="stMetricValue"] { font-size: 0.9rem !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] { font-size: 0.65rem !important; }
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
    # Identifikace sloupců pro výpočty
    cols = df_all.columns.tolist()
    col_nabidka = next((c for c in cols if 'nabídka' in c.lower() or 'cena' in c.lower()), None)
    col_stav = next((c for c in cols if 'stav' in c.lower()), None)
    col_vedouci = next((c for c in cols if 'vedoucí' in c.lower() or 'stavbyved' in c.lower()), None)

    if col_nabidka:
        df_all[col_nabidka] = pd.to_numeric(df_all[col_nabidka], errors='coerce').fillna(0)

    # --- 3. PEVNÝ KONTEJNER (NADPIS, FILTRY, SOUČTY) ---
    # Vše v tomto bloku bude díky CSS nahoře "přilepené"
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

        # Součty (vždy pod filtry)
        if col_nabidka:
            m1, m2, m3, m4, m5 = st.columns(5)
            
            # Pomocná funkce pro součty (filtruje z aktuálního výběru)
            def get_sum(df_source, kw):
                if col_stav:
                    return df_source[df_source[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_nabidka].sum()
                return 0

            # Filtrování pro výpočet metrik
            df_temp = df_all.copy()
            if col_vedouci and sel_v != "Všichni vedoucí":
                df_temp = df_temp[df_temp[col_vedouci].astype(str) == sel_v]
            if col_stav and sel_s != "Všechny stavy":
                df_temp = df_temp[df_temp[col_stav].astype(str) == sel_s]
            if hledat:
                df_temp = df_temp[df_temp.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

            m1.metric("CELKEM", f"{df_temp[col_nabidka].sum():,.0f} Kč".replace(',', ' '))
            m2.metric("HOTOVO", f"{get_sum(df_temp, 'hotov'):,.0f} Kč".replace(',', ' '))
            m3.metric("FAKTURACE", f"{get_sum(df_temp, 'faktur'):,.0f} Kč".replace(',', ' '))
            m4.metric("PROBÍHÁ", f"{get_sum(df_temp, 'probíh'):,.0f} Kč".replace(',', ' '))
            m5.metric("STAVEB", len(df_temp))

    # --- 4. ROLOVACÍ TABULKA ---
    # Styling pro barevné řádky
    def style_rows(row):
        color = ''
        if col_stav:
            status = str(row[col_stav]).lower()
            if 'hotov' in status: color = 'background-color: #dcfce7'
            elif 'probíh' in status: color = 'background-color: #fef9c3'
            elif 'faktur' in status: color = 'background-color: #dbeafe'
        return [color] * len(row)

    # Zobrazení finální tabulky (používáme df_temp z filtrování výše)
    st.dataframe(df_temp.style.apply(style_rows, axis=1), use_container_width=True, height=1000)
    
else:
    st.error("Data nebyla nalezena.")
