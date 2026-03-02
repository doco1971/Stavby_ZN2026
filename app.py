import streamlit as st
import pandas as pd
import sqlite3
import os

# --- 1. KONFIGURACE ---
st.set_page_config(page_title="Stavby ZN 2026", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main-title { color: #1e3a5f; font-size: 2.2rem; font-weight: 800; margin-bottom: 20px; text-align: center; }
    .stDataFrame { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABÁZE ---
DB_NAME = 'database_v3.db'

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

if not os.path.exists(DB_NAME):
    conn = get_conn()
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.iloc[:, :10]
        df.columns = ['Firma', 'Cislo', 'Nazev', 'Nabidka', 'Termin_N', 'Termin_U', 'Vedouci', 'Smlouva', 'Faktura', 'Poznamka']
        df['Stav'] = 'V přípravě'
        df = df.dropna(subset=['Nazev'])
        df.to_sql('zakazky', conn, if_exists='replace', index=False)
        conn.commit()
    except Exception as e:
        st.error(f"Chyba importu: {e}")
    conn.close()

conn = get_conn()
df_all = pd.read_sql('SELECT rowid as ID, * FROM zakazky', conn)

# --- 3. HLAVNÍ PLOCHA ---
st.markdown('<div class="main-title">🏗️ Evidence zakázek 2026</div>', unsafe_allow_html=True)

# Filtry nahoře
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    hledat = st.text_input("🔍 Hledat v tabulce...", placeholder="Název, firma, číslo...")
with col2:
    vedouci_opt = ["Všichni"] + sorted(df_all['Vedouci'].dropna().unique().tolist())
    sel_vedouci = st.selectbox("Vedoucí", vedouci_opt)
with col3:
    stav_opt = ["Vše"] + ["V přípravě", "Probíhá", "Hotovo", "Fakturace"]
    sel_stav = st.selectbox("Stav", stav_opt)

# Filtrování
df_display = df_all.copy()
if hledat:
    df_display = df_display[df_display.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
if sel_vedouci != "Všichni":
    df_display = df_display[df_display['Vedouci'] == sel_vedouci]
if sel_stav != "Vše":
    df_display = df_display[df_display['Stav'] == sel_stav]

# --- 4. TABULKA ---
st.write(f"Zobrazeno {len(df_display)} řádků")
st.dataframe(
    df_display.drop(columns=['ID']),
    use_container_width=True,
    height=450
)

# --- 5. EDITACE (Pod tabulkou) ---
st.markdown("---")
st.subheader("📝 Rychlá aktualizace stavu")
c_sel, c_stav, c_btn = st.columns([2, 1, 1])

with c_sel:
    vyber = st.selectbox("Vyberte stavbu pro změnu:", df_display['Nazev'].tolist())
with c_stav:
    novy_stav = st.selectbox("Nový stav:", ["V přípravě", "Probíhá", "Hotovo", "Fakturace"])
with c_btn:
    st.write("##") # zarovnání tlačítka
    if st.button("💾 ULOŽIT ZMĚNU", use_container_width=True):
        id_update = int(df_display[df_display['Nazev'] == vyber]['ID'].iloc[0])
        conn.execute("UPDATE zakazky SET Stav = ? WHERE rowid = ?", (novy_stav, id_update))
        conn.commit()
        st.success(f"Uloženo: {vyber} -> {novy_stav}")
        st.rerun()

conn.close()
