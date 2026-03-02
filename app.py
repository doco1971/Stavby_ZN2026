import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="Evidence zakázek", layout="wide")

def get_connection():
    return sqlite3.connect('zakazky_data.db', check_same_thread=False)

# Inicializace DB
if not os.path.exists('zakazky_data.db'):
    conn = get_connection()
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        # Vyčištění názvů sloupců - nahradíme vše problémové podtržítkem
        df.columns = [str(c).strip().replace(' ', '_').replace('.', '_').replace('/', '_') for c in df.columns]
        df = df.dropna(subset=[df.columns[2]]) # Filtrujeme podle 3. sloupce (Název stavby)
        
        if 'stav' not in df.columns:
            df['stav'] = 'V přípravě'
            
        df.to_sql('zakazky', conn, if_exists='replace', index=False)
        conn.commit()
    except Exception as e:
        st.error(f"Chyba při načítání: {e}")
    conn.close()

conn = get_connection()
df_display = pd.read_sql('SELECT rowid as ID, * FROM zakazky', conn)

st.title("📋 Evidence zakázek 2026")

# TADY JSOU TY FILTRY
hledat = st.text_input("🔍 Rychlé hledání")
if hledat:
    mask = df_display.apply(lambda row: hledat.lower() in row.astype(str).str.lower().values, axis=1)
    df_display = df_display[mask]

st.dataframe(df_display.drop(columns=['ID']), use_container_width=True)

# OPRAVENÝ BOČNÍ PANEL
st.sidebar.header("📝 Správa zakázky")
if not df_display.empty:
    # Použijeme druhý sloupec (číslo stavby) bez ohledu na to, jak se přesně jmenuje
    col_cislo_stavby = df_display.columns[2] 
    col_nazev_stavby = df_display.columns[3]
    
    vybrane_cislo = st.sidebar.selectbox("Vyberte stavbu", df_display[col_cislo_stavby].tolist())
    radek = df_display[df_display[col_cislo_stavby] == vybrane_cislo].iloc[0]
    
    st.sidebar.info(f"Vybráno: {radek[col_nazev_stavby]}")
    
    novy_stav = st.sidebar.selectbox("Změnit stav", ["V přípravě", "Probíhá", "Hotovo", "Fakturace"])
    
    if st.sidebar.button("Uložit změny"):
        conn.execute('UPDATE zakazky SET stav = ? WHERE rowid = ?', (novy_stav, int(radek['ID'])))
        conn.commit()
        st.sidebar.success("Uloženo!")
        st.rerun()

conn.close()
