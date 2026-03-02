import streamlit as st
import pandas as pd
import sqlite3
import os

# Nastavení stránky
st.set_page_config(page_title="Evidence zakázek", layout="wide")

# Funkce pro spojení s databází
def get_connection():
    return sqlite3.connect('zakazky_data.db', check_same_thread=False)

# Inicializace databáze z EXCELU
if not os.path.exists('zakazky_data.db'):
    conn = get_connection()
    try:
        # Čteme přímo XLSX, přeskakujeme první 4 řádky (hlavička je na 5. řádku)
        # Používáme openpyxl, což je standard pro Excel v Pythonu
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        
        # Vyčištění názvů sloupců pro SQL (odstranění teček, mezer a lomítek)
        df.columns = [str(c).replace(' ', '_').replace('.', '').replace('/', '_') for c in df.columns]
        
        # Odstranění úplně prázdných řádků
        df = df.dropna(subset=['název_stavby'])
        
        # Vytvoření sloupce 'stav', pokud v Excelu není
        if 'stav' not in df.columns:
            df['stav'] = 'V přípravě'
            
        # Uložení do SQL
        df.to_sql('zakazky', conn, if_exists='replace', index=False)
        conn.commit()
    except Exception as e:
        st.error(f"Chyba při načítání Excelu: {e}. Ujistěte se, že se soubor jmenuje přesně: Soupis zakázek tabulka 2026_ZN.xlsx")
    conn.close()

# Načtení dat pro zobrazení
conn = get_connection()
df_display = pd.read_sql('SELECT rowid as ID, * FROM zakazky', conn)

st.title("📋 Evidence zakázek 2026 (z Excelu)")

# Horní vyhledávání
hledat = st.text_input("🔍 Rychlé hledání v celé tabulce")
if hledat:
    mask = df_display.apply(lambda row: hledat.lower() in row.astype(str).str.lower().values, axis=1)
    df_display = df_display[mask]

# Zobrazení tabulky - skryjeme ID, které je jen pro databázi
st.dataframe(df_display.drop(columns=['ID']), use_container_width=True)

# Boční panel pro úpravy
st.sidebar.header("📝 Správa zakázky")
if not df_display.empty:
    # Vyhledání zakázky podle Čísla stavby nebo ID
    možnosti = df_display['čstavby'].tolist()
    vybrane_cislo = st.sidebar.selectbox("Vyberte číslo stavby", možnosti)
    
    radek = df_display[df_display['čstavby'] == vybrane_cislo].iloc[0]
    
    st.sidebar.info(f"Stavba: {radek['název_stavby']}")
    
    novy_stav = st.sidebar.selectbox(
        "Změnit stav realizace", 
        ["V přípravě", "Probíhá", "Hotovo", "Fakturace"],
        index=["V přípravě", "Probíhá", "Hotovo", "Fakturace"].index(radek['stav']) if 'stav' in radek else 0
    )
    
    if st.sidebar.button("Uložit změny"):
        curr_id = int(radek['ID'])
        conn.execute('UPDATE zakazky SET stav = ? WHERE rowid = ?', (novy_stav, curr_id))
        conn.commit()
        st.sidebar.success("Změna uložena!")
        st.rerun()

conn.close()
