import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A KOMPAKTNÍ STYL ---
st.set_page_config(page_title="Stavby ZN 2026", layout="wide")

st.markdown("""
<style>
    /* Zmenšení mezer a písem */
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h3 { margin-bottom: 0.5rem; font-size: 1.2rem; color: #1e3a5f; }
    .stMetric { padding: 5px; border: 1px solid #eee; border-radius: 5px; background: white; }
    div[data-testid="stMetricValue"] { font-size: 1.1rem !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
    .small-font { font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Chyba: {e}")
        return pd.DataFrame()

df_all = load_data()

if not df_all.empty:
    # Dynamická identifikace sloupců
    cols = df_all.columns.tolist()
    col_nabidka = next((c for c in cols if 'nabídka' in c.lower() or 'cena' in c.lower()), None)
    col_stav = next((c for c in cols if 'stav' in c.lower()), None)
    col_vedouci = next((c for c in cols if 'vedoucí' in c.lower() or 'stavbyved' in c.lower()), None)

    # Převod na čísla pro výpočty
    if col_nabidka:
        df_all[col_nabidka] = pd.to_numeric(df_all[col_nabidka], errors='coerce').fillna(0)

    # --- 3. FILTRY (Kompaktní řádek) ---
    st.markdown("### 🏗️ Evidence zakázek 2026")
    
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        hledat = st.text_input("🔍 Hledat...", label_visibility="collapsed", placeholder="Hledat kdekoli...")
    with f2:
        v_list = ["Všichni vedoucí"] + sorted(df_all[col_vedouci].dropna().unique().tolist()) if col_vedouci else ["Všichni"]
        sel_v = st.selectbox("Vedoucí", v_list, label_visibility="collapsed")
    with f3:
        s_list = ["Všechny stavy"] + sorted(df_all[col_stav].dropna().unique().tolist()) if col_stav else ["Vše"]
        sel_s = st.selectbox("Stav", s_list, label_visibility="collapsed")

    # Aplikace filtrů
    df_f = df_all.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
    if col_vedouci and sel_v != "Všichni vedoucí":
        df_f = df_f[df_f[col_vedouci] == sel_v]
    if col_stav and sel_s != "Všechny stavy":
        df_f = df_f[df_f[col_stav] == sel_s]

    # --- 4. SOUČTY (Více informací na méně místě) ---
    if col_nabidka and col_stav:
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Celkem", f"{df_f[col_nabidka].sum():,.0f} Kč".replace(',', ' '))
        
        # Součty podle stavů (přizpůsobte názvy stavů dle vašeho Excelu)
        hotovo = df_f[df_f[col_stav].str.contains('hotovo', case=False, na=False)][col_nabidka].sum()
        faktura = df_f[df_f[col_stav].str.contains('faktur', case=False, na=False)][col_nabidka].sum()
        probiha = df_f[df_f[col_stav].str.contains('probíhá', case=False, na=False)][col_nabidka].sum()
        
        m2.metric("Hotovo", f"{hotovo:,.0f} Kč".replace(',', ' '))
        m3.metric("Fakturace", f"{faktura:,.0f} Kč".replace(',', ' '))
        m4.metric("Probíhá", f"{probiha:,.0f} Kč".replace(',', ' '))
        m5.metric("Počet", len(df_f))

    # --- 5. TABULKA ---
    st.dataframe(df_f, use_container_width=True, height=650)
    
else:
    st.warning("Data nebyla načtena.")
