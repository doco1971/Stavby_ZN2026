import streamlit as st
import pandas as pd
import os

# --- 1. KONFIGURACE ---
st.set_page_config(page_title="Stavby ZN 2026", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fc; }
    .main-title { color: #1e3a5f; font-size: 2.2rem; font-weight: 800; margin-bottom: 20px; text-align: center; }
    .metric-box {
        background-color: white; padding: 15px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;
        border-top: 5px solid #1e3a5f;
    }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: #1e3a5f; }
    .metric-label { font-size: 0.9rem; color: #666; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT PŘÍMO Z EXCELU ---
@st.cache_data(ttl=60) # Data se obnoví každou minutu
def load_data():
    try:
        # Čteme od 5. řádku (skiprows=4)
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        # Odstraníme prázdné řádky na konci
        df = df.dropna(how='all')
        # Vyčistíme názvy sloupců od mezer
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Nepodařilo se načíst Excel: {e}")
        return pd.DataFrame()

df_all = load_data()

if not df_all.empty:
    # Dynamické hledání sloupců pro součty a filtry
    cols = df_all.columns.tolist()
    
    # Najdeme sloupec s nabídkou (hledáme slovo 'nabídka' nebo 'cena' bez ohledu na velikost písmen)
    col_nabidka = next((c for c in cols if 'nabídka' in c.lower() or 'cena' in c.lower()), cols[4] if len(cols) > 4 else None)
    # Najdeme stavbyvedoucího
    col_vedouci = next((c for c in cols if 'vedoucí' in c.lower() or 'stavbyved' in c.lower()), cols[7] if len(cols) > 7 else None)
    
    # --- 3. HLAVNÍ PLOCHA ---
    st.markdown('<div class="main-title">🏗️ Evidence zakázek 2026</div>', unsafe_allow_html=True)

    # Filtry
    col1, col2 = st.columns([2, 1])
    with col1:
        hledat = st.text_input("🔍 Hledat kdekoli v tabulce...")
    with col2:
        if col_vedouci:
            vedouci_list = ["Všichni"] + sorted(df_all[col_vedouci].dropna().unique().tolist())
            sel_vedouci = st.selectbox("Filtr: Stavbyvedoucí", vedouci_list)
        else:
            sel_vedouci = "Všichni"

    # Filtrování
    df_f = df_all.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
    if sel_vedouci != "Všichni":
        df_f = df_f[df_f[col_vedouci] == sel_vedouci]

    # --- 4. SOUČTY ---
    if col_nabidka:
        total_val = pd.to_numeric(df_f[col_nabidka], errors='coerce').sum()
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="metric-box"><div class="metric-label">Počet staveb</div><div class="metric-value">{len(df_f)}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-box"><div class="metric-label">Celková hodnota</div><div class="metric-value">{total_val:,.0f} Kč'.replace(',', ' ') + '</div></div>', unsafe_allow_html=True)

    st.write("##")

    # --- 5. TABULKA (Všechny sloupce) ---
    st.dataframe(df_f, use_container_width=True, height=600)

    st.info("💡 Tip: Pro seřazení tabulky klikněte na název sloupce. Tabulka obsahuje všechny sloupce z vašeho Excelu.")

else:
    st.warning("Excel tabulka je prázdná nebo nebyla nalezena.")
