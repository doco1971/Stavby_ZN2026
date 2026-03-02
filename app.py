import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# --- KONFIGURACE A STYLING (Moderní vzhled 2026) ---
st.set_page_config(page_title="Evidence zakázek 2026", layout="wide", page_icon="🏗️")

# Vlastní CSS pro moderní karty a prvky
st.markdown("""
<style>
    /* Hlavní pozadí a písmo */
    .stApp {
        background-color: #f4f7f6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Nadpis */
    h1 {
        color: #1a508b;
        font-weight: 700;
        margin-bottom: 1.5rem;
        text-align: center;
    }

    /* Styl pro karty zakázek */
    .zakazka-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s;
        border-left: 5px solid #ddd; /* Základní barva */
    }
    .zakazka-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Barevné označení podle stavu */
    .stav-v-priprave { border-left-color: #6c757d; } /* Šedá */
    .stav-probíhá { border-left-color: #f39c12; }    /* Oranžová */
    .stav-hotovo { border-left-color: #2ecc71; }      /* Zelená */
    .stav-fakturace { border-left-color: #3498db; }    /* Modrá */

    /* Nadpis na kartě (Název stavby) */
    .card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1a508b;
        margin-bottom: 0.5rem;
    }

    /* Detaily na kartě */
    .card-detail {
        font-size: 0.9rem;
        color: #555;
        margin-bottom: 0.25rem;
    }
    .card-label {
        font-weight: 600;
        color: #333;
        margin-right: 0.5rem;
    }

    /* Badge pro stav */
    .stav-badge {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 75%;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 10rem;
        color: white;
    }
    .badge-v-priprave { background-color: #6c757d; }
    .badge-probíhá { background-color: #f39c12; }
    .badge-hotovo { background-color: #2ecc71; }
    .badge-fakturace { background-color: #3498db; }

    /* Stylování filtrů */
    .stSelectbox label, .stTextInput label {
        font-weight: 600;
        color: #1a508b;
    }
    
    /* Skrytí standardní tabulky pro čistší vzhled */
    .stDataFrame {
        display: none;
    }
</style>
""", unsafe_allow_check_safe_true=True)

# --- FUNKCE PRO DATABÁZI (Zůstávají stejné) ---
def get_connection():
    return sqlite3.connect('zakazky_data.db', check_same_thread=False)

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
    conn.close()

conn = get_connection()
df_all = pd.read_sql('SELECT rowid as ID, * FROM zakazky', conn)

# --- POMOCNÉ FUNKCE PRO FORMÁTOVÁNÍ ---
def format_money(amount):
    try:
        return f"{amount:,.0f} Kč".replace(",", " ")
    except:
        return amount

def format_date(date_val):
    try:
        if pd.isna(date_val): return ""
        if isinstance(date_val, datetime):
            return date_val.strftime('%d.%m.%Y')
        return date_val
    except:
        return date_val

def get_stav_style(stav):
    stav_lower = str(stav).lower()
    if 'přípravě' in stav_lower: return 'v-priprave', 'V přípravě'
    if 'probíhá' in stav_lower: return 'probíhá', 'Probíhá'
    if 'hotovo' in stav_lower: return 'hotovo', 'Hotovo'
    if 'fakturace' in stav_lower: return 'fakturace', 'Fakturace'
    return '', stav

# --- HLAVNÍ STRÁNKA (Moderní layout) ---
st.title("🏗️ Evidence zakázek 2026")

# Sekce filtrů (Holeře, moderní vzhled)
with st.expander("🔍 Filtry a vyhledávání", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        hledat = st.text_input("Rychlé hledání (název, číslo stavby...)")
    with col2:
        stavbyvedouci_list = ["Všichni"] + sorted(df_all['stavbyvedoucí'].dropna().unique().tolist())
        vybrany_stavbyvedouci = st.selectbox("Filtrovat podle stavbyvedoucího", stavbyvedouci_list)
    with col3:
        stavy_list = ["Všechny stavy", "V přípravě", "Probíhá", "Hotovo", "Fakturace"]
        vybrany_stav = st.selectbox("Filtrovat podle stavu", stavy_list)

# Aplikace filtrů
df_display = df_all.copy()
if hledat:
    mask = df_display.apply(lambda row: hledat.lower() in row.astype(str).str.lower().values, axis=1)
    df_display = df_display[mask]
if vybrany_stavbyvedouci != "Všichni":
