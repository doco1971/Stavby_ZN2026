import streamlit as st
import pandas as pd
import sqlite3
import os

# --- 1. KONFIGURACE ---
st.set_page_config(page_title="Stavby ZN 2026", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    .main-title { color: #1e3a5f; font-size: 2rem; font-weight: 800; margin-bottom: 20px; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABÁZE (Čistý start) ---
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

# Filtry
col1, col2 = st.columns([2, 1])
with col1:
    hledat = st.text_input("🔍 Rychlé hledání v tabulce...")
with col2:
    vedouci_opt = ["Všichni"] + sorted(df_all['Vedouci'].dropna().unique().tolist())
    sel_vedouci = st.selectbox("Filtr: Vedoucí", vedouci_opt)

# Filtrování dat
df_display = df_all.copy()
if hledat:
    df_display = df_display[df_display.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
if sel_vedouci != "Všichni":
    df_display = df_display[df_display['Vedouci'] == sel_vedouci]

# --- 4. TABULKA (Moderní styl) ---
st.dataframe(
    df_display.drop(columns=['ID']),
    use_container_width=True,
    height=5
