import streamlit as st
import pandas as pd
import sqlite3
import os

# --- 1. KONFIGURACE (Široké rozvržení pro tabulku) ---
st.set_page_config(page_title="Stavby ZN 2026", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main-title { color: #1e3a5f; font-size: 2rem; font-weight: 800; margin-bottom: 20px; }
    /* Styl pro vylepšení tabulky */
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABÁZE ---
DB_NAME = 'database_table_v1.db'

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

if not os.path.exists(DB_NAME):
    conn = get_conn()
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.iloc[:, :10]
        df.columns = ['Firma', 'Číslo stavby', 'Název stavby', 'Nabídka (Kč)', 'Termín nabídka', 'Termín ukončení', 'Stavbyvedoucí', 'Smlouva', 'Faktura', 'Poznámka']
        df['Stav'] = 'V přípravě'
        # Vyčištění dat - odstranění prázdných řádků v názvu
        df = df.dropna(subset=['Název stavby'])
        df.to_sql('zakazky', conn, if_exists='replace', index=False)
        conn.commit()
    except Exception as e:
        st.error(f"Chyba při načítání: {e}")
    conn.close()

conn = get_conn()
df_all = pd.read_sql('SELECT rowid as ID, * FROM zakazky', conn)

# --- 3. HLAVNÍ PLOCHA ---
st.markdown('<div class="main-title">🏗️ Přehled zakázek 2026</div>', unsafe_allow_html=True)

# Horní lišta s filtry (roztažená)
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    hledat = st.text_input("🔍 Vyhledat v tabulce...", placeholder="Napište název, číslo nebo firmu...")
with col2:
    vedouci_opt = ["Všichni"] + sorted(df_all['Stavbyvedoucí'].dropna().unique().tolist())
    sel_vedouci = st.selectbox("Vedoucí", vedouci_opt)
with col3:
    stav_opt = ["Vše", "V přípravě", "Probíhá", "Hotovo", "Fakturace"]
    sel_stav = st.selectbox("Stav", stav_opt)

# Filtrování
df_display = df_all.copy()
if hledat:
    df_display = df_display[df_display.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
if sel_vedouci != "Všichni":
    df_display = df_display[df_display['Stavbyvedoucí'] == sel_vedouci]
if sel_stav != "Vše":
    df_display = df_display[df_display['Stav'] == sel_stav]

# --- 4. ZOBRAZENÍ TABULKY (Moderní Data Editor) ---
# Formátování čísel pro zobrazení
st.data_editor(
    df_display.drop(columns=['ID']),
    use_container_width=True,
    height=500,
    disabled=True, # Tabulka je pro čtení, měníme přes panel
    column_config={
        "Nabídka (Kč)": st.column_config.NumberColumn("Cena", format="%d Kč"),
        "Termín ukončení": st.
