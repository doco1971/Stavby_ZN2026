import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE ---
st.set_page_config(page_title="Editor Evidence 2026", layout="wide")

# CSS zůstává podobné, ale st.data_editor má vlastní stylování, tak ho nebudeme omezovat příliš
st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding-top: 1rem; }
    .stButton>button { width: 100%; background-color: #059669; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNKCE PRO NAČÍTÁNÍ A UKLÁDÁNÍ ---
FILE_NAME = 'Soupis zakázek tabulka 2026_ZN.xlsx'

def load_data():
    try:
        # Načteme celý list, abychom při ukládání neponičili formátování (pokud možno)
        df = pd.read_excel(FILE_NAME, skiprows=5, header=None, engine='openpyxl')
        df = df.iloc[:, :23]
        # Přejmenujeme sloupce pro přehlednost v editoru
        df.columns = [
            "Poř.č.", "Firma", "Kat I PS", "Kat I SNK", "Kat I BO", 
            "Kat II PS", "Kat II BO", "Kat II Poruch", "Č.stavby", "Název stavby",
            "Nabídka", "Rozdíl", "Vyfaktur.", "Ukončení", "Zrealiz.", "SOD", "Ze dne",
            "Objednatel", "Stavbyved.", "Nabídková c.", "Č.faktury", "Bez DPH", "Splatná"
        ]
        return df
    except Exception as e:
        st.error(f"Chyba při načítání: {e}")
        return pd.DataFrame()

def save_data(df_to_save):
    try:
        # Načteme původní soubor, abychom zachovali prvních 5 řádků (hlavičky v Excelu)
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            # Zapíšeme data od 6. řádku (index 5 v Excelu)
            # header=False, protože hlavičky už v Excelu máte
            df_to_save.to_excel(writer, index=False, header=False, startrow=6)
        return True
    except Exception as e:
        st.error(f"Chyba při ukládání: {e}")
        return False

# --- 3. LOGIKA APLIKACE ---
st.title("📝 Editor databáze 2026")

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# Horní lišta s tlačítky
col_save, col_reload = st.columns([1, 1])

with col_reload:
    if st.button("🔄 Načíst znovu z Excelu (Zrušit změny)"):
        st.session_state.data = load_data()
        st.rerun()

# --- HLAVNÍ EDITOR ---
# num_rows="dynamic" umožňuje přidávat a mazat řádky
edited_df = st.data_editor(
    st.session_state.data, 
    num_rows="dynamic", 
    height=450, 
    use_container_width=True,
    column_config={
        "Ukončení": st.column_config.DateColumn(),
        "Zrealiz.": st.column_config.DateColumn(),
        "Ze dne": st.column_config.DateColumn(),
        "Splatná": st.column_config.DateColumn(),
    }
)

with col_save:
    if st.button("💾 ULOŽIT VŠECHNY ZMĚNY DO EXCELU"):
        if save_data(edited_df):
            st.success("Data byla úspěšně uložena do Excelu!")
            st.session_state.data = edited_df
        else:
            st.error("Nepodařilo se uložit data. Zkontrolujte, zda není Excel soubor otevřený!")

# --- 4. RYCHLÝ PŘEHLED (METRIKY) ---
# (Zde můžete nechat ty hezké boxíky z minula pro kontrolu součtů)
