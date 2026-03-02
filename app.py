import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A KOMPAKTNÍ STYL ---
st.set_page_config(page_title="Stavby ZN 2026", layout="wide")

st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    h3 { margin-bottom: 0.5rem; font-size: 1.2rem; color: #1e3a5f; font-weight: 800; }
    .stMetric { padding: 2px 10px; border: 1px solid #eee; border-radius: 5px; background: white; }
    div[data-testid="stMetricValue"] { font-size: 1.0rem !important; font-weight: 700; }
    div[data-testid="stMetricLabel"] { font-size: 0.75rem !important; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Chyba při načítání Excelu: {e}")
        return pd.DataFrame()

df_all = load_data()

if not df_all.empty:
    # Identifikace sloupců
    cols = df_all.columns.tolist()
    col_nabidka = next((c for c in cols if 'nabídka' in c.lower() or 'cena' in c.lower()), None)
    col_stav = next((c for c in cols if 'stav' in c.lower()), None)
    col_vedouci = next((c for c in cols if 'vedoucí' in c.lower() or 'stavbyved' in c.lower()), None)

    # Převod nabídky na čísla
    if col_nabidka:
        df_all[col_nabidka] = pd.to_numeric(df_all[col_nabidka], errors='coerce').fillna(0)

    # --- 3. FILTRY (Kompaktní) ---
    st.markdown("### 🏗️ Evidence zakázek 2026")
    
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat kdekoli (stavba, firma...)...")
    with f2:
        # Ošetření TypeError v sorted: převedeme na str a vyfiltrujeme unikátní
        v_opt = ["Všichni vedoucí"]
        if col_vedouci:
            unique_v = sorted([str(x) for x in df_all[col_vedouci].dropna().unique()])
            v_opt.extend(unique_v)
        sel_v = st.selectbox("Vedoucí", v_opt, label_visibility="collapsed")
    with f3:
        s_opt = ["Všechny stavy"]
        if col_stav:
            unique_s = sorted([str(x) for x in df_all[col_stav].dropna().unique()])
            s_opt.extend(unique_s)
        sel_s = st.selectbox("Stav", s_opt, label_visibility="collapsed")

    # Aplikace filtrů
    df_f = df_all.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
    if col_vedouci and sel_v != "Všichni vedoucí":
        df_f = df_f[df_f[col_vedouci].astype(str) == sel_v]
    if col_stav and sel_s != "Všechny stavy":
        df_f = df_f[df_f[col_stav].astype(str) == sel_s]

    # --- 4. SOUČTY (Kompaktní metriky) ---
    if col_nabidka:
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Celkem", f"{df_f[col_nabidka].sum():,.0f} Kč".replace(',', ' '))
        
        # Filtrované součty podle klíčových slov v Excelu
        def sum_by_status(keyword):
            if col_stav:
                return df_f[df_f[col_stav].astype(str).str.contains(keyword, case=False, na=False)][col_nabidka].sum()
            return 0

        m2.metric("Hotovo", f"{sum_by_status('hotov'):,.0f} Kč".replace(',', ' '))
        m3.metric("Fakturace", f"{sum_by_status('faktur'):,.0f} Kč".replace(',', ' '))
        m4.metric("Probíhá", f"{sum_by_status('probíh'):,.0f} Kč".replace(',', ' '))
        m5.metric("Počet staveb", len(df_f))

    # --- 5. TABULKA (Maximální prostor) ---
    st.dataframe(df_f, use_container_width=True, height=700)
    
else:
    st.warning("Excel soubor nebyl nalezen nebo je prázdný.")
