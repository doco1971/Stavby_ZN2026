import streamlit as st
import pandas as pd
import sqlite3
import os

# --- KONFIGURACE A STYLING ---
st.set_page_config(page_title="Evidence zakázek 2026", layout="wide", page_icon="🏗️")

st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; font-family: 'Segoe UI', sans-serif; }
    h1 { color: #1a508b; text-align: center; font-weight: 700; margin-bottom: 20px; }
    .zakazka-card {
        background-color: white; padding: 1.5rem; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1rem;
        border-left: 8px solid #ddd;
    }
    .stav-v-priprave { border-left-color: #6c757d; }
    .stav-probíhá { border-left-color: #f39c12; }
    .stav-hotovo { border-left-color: #2ecc71; }
    .stav-fakturace { border-left-color: #3498db; }
    .card-title { font-size: 1.3rem; font-weight: 700; color: #1a508b; margin-bottom: 10px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    .card-detail { font-size: 1rem; color: #444; margin-bottom: 5px; }
    .card-label { font-weight: 700; color: #1a508b; min-width: 120px; display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- DATABÁZE ---
def get_connection():
    return sqlite3.connect('zakazky_data.db', check_same_thread=False)

# Smazání staré DB a vytvoření nové při změně struktury (pro jistotu)
if not os.path.exists('zakazky_data.db'):
    conn = get_connection()
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        # Vyčistíme názvy sloupců
        df.columns = [str(c).strip().replace(' ', '_').replace('.', '_').replace('/', '_') for c in df.columns]
        # Odstraníme řádky bez názvu stavby (sloupec index 2)
        df = df.dropna(subset=[df.columns[2]])
        
        if 'stav' not in df.columns:
            df['stav'] = 'V přípravě'
            
        df.to_sql('zakazky', conn, if_exists='replace', index=False)
        conn.commit()
    except Exception as e:
        st.error(f"Chyba při importu: {e}")
    finally:
        conn.close()

conn = get_connection()
df_all = pd.read_sql('SELECT rowid as ID, * FROM zakazky', conn)

# --- DYNAMICKÉ URČENÍ SLOUPCŮ ---
# Abychom se vyhnuli KeyError, najdeme názvy sloupců podle pozice
cols = df_all.columns.tolist()
# indexy: 0=ID, 1=firma, 2=č_stavby, 3=název
