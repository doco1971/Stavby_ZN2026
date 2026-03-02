import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# --- KONFIGURACE A STYLING ---
st.set_page_config(page_title="Evidence zakázek 2026", layout="wide", page_icon="🏗️")

st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; font-family: 'Segoe UI', sans-serif; }
    h1 { color: #1a508b; text-align: center; font-weight: 700; }
    .zakazka-card {
        background-color: white; padding: 1.5rem; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1rem;
        border-left: 6px solid #ddd;
    }
    .stav-v-priprave { border-left-color: #6c757d; }
    .stav-probíhá { border-left-color: #f39c12; }
    .stav-hotovo { border-left-color: #2ecc71; }
    .stav-fakturace { border-left-color: #3498db; }
    .card-title { font-size: 1.2rem; font-weight: 600; color: #1a508b; margin-bottom: 8px; }
    .card-detail { font-size: 0.9rem; color: #555; margin-bottom: 4px; }
    .card-label { font-weight: 600; color: #333; margin-right: 5px; }
</style>
""", unsafe_allow_html=True)

# --- DATABÁZE ---
def get_connection():
    return sqlite3.connect('zakazky_data.db', check_same_thread=False)

# Inicializace (pokud DB neexistuje)
if not os.path.exists('zakazky_data.db'):
    conn = get_connection()
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df.columns = [str(c).strip().replace(' ', '_').replace('.', '_').replace('/', '_') for c in df.columns]
        df = df.dropna(subset=[df.columns[2]])
        if 'stav' not in df.columns:
            df['stav'] = 'V přípravě'
        df.to_sql('zakazky', conn, if_exists='replace', index=False)
        conn.commit()
    except Exception as e:
        st.error(f"Chyba při načítání: {e}")
    finally:
        conn.close()

conn = get_connection()
df_all = pd.read_sql('SELECT rowid as ID, * FROM zakazky', conn)

# --- FILTRY ---
st.title("🏗️ Evidence zakázek 2026")

with st.expander("🔍 Filtry a vyhledávání", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        hledat = st.text_input("Rychlé hledání")
    with col2:
        stavbyvedouci_list = ["Všichni"] + sorted(df_all['stavbyvedoucí'].dropna().unique().tolist())
        vybrany_stavbyvedouci = st.selectbox("Stavbyvedoucí", stavbyvedouci_list)
    with col3:
        vybrany_stav = st.selectbox("Stav", ["Všechny", "V přípravě", "Probíhá", "Hotovo", "Fakturace"])

# Logika filtrování (POZOR NA ODSZENÍ!)
df_display = df_all.copy()

if hledat:
    mask = df_display.apply(lambda row: hledat.lower() in row.astype(str).str.lower().values, axis=1)
    df_display = df_display[mask]

if vybrany_stavbyvedouci != "Všichni":
    df_display = df_display[df_display['stavbyvedoucí'] == vybrany_stavbyvedouci]

if vybrany_stav != "Všechny":
    df_display = df_display[df_display['stav'] == vybrany_stav]

# --- VÝPIS KARET ---
st.write(f"Zobrazeno {len(df_display)} zakázek")

for _, radek in df_display.iterrows():
    # Určení barvy podle stavu
    s = str(radek['stav']).lower()
    css_class = "v-priprave"
    if "probíhá" in s: css_class = "probíhá"
    elif "hotovo" in s: css_class = "hotovo"
    elif "fakturace" in s: css_class = "fakturace"

    st.markdown(f"""
    <div class="zakazka-card stav-{css_class}">
        <div class="card-title">{radek['název_stavby']}</div>
        <div class="card-detail"><span class="card-label">Číslo:</span>{radek['č_stavby']}</div>
        <div class="card-detail"><span class="card-label">Firma:</span>{radek['firma']}</div>
        <div class="card-detail"><span class="card-label">Stavbyvedoucí:</span>{radek['stavbyvedoucí']}</div>
        <div class="card-detail"><span class="card-label">Aktuální stav:</span><strong>{radek['stav']}</strong></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tlačítko pro rychlou úpravu
    with st.expander("Změnit stav"):
        novy_stav = st.selectbox("Nový stav", ["V přípravě", "Probíhá", "Hotovo", "Fakturace"], key=f"sel_{radek['ID']}")
        if st.button("Uložit", key=f"btn_{radek['ID']}"):
            conn.execute('UPDATE zakazky SET stav = ? WHERE rowid = ?', (novy_stav, int(radek['ID'])))
            conn.commit()
            st.rerun()

conn.close()
