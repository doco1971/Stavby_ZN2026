import streamlit as st
import pandas as pd
import numpy as np

# --- KONFIGURACE ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

# Skrytí Streamlit menu a okrajů
st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    div[data-testid="stExpander"] { border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- NAČTENÍ A ÚPRAVA DAT ---
@st.cache_data(ttl=1)
def load_and_clean_data():
    try:
        # Načtení dat (přeskočíme hlavičky v Excelu a definujeme si vlastní)
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=5, header=None, engine='openpyxl')
        
        # Vlastní názvy sloupců (přesně podle tvého pořadí)
        df.columns = [
            "poř.č.", "firma", "PS (I)", "SNK (I)", "BO (I)", "PS (II)", "BO (II)", "poruchy", 
            "č.stavby", "název stavby", "nabídka", "rozdíl", "vyfaktur.", 
            "ukončení", "zrealizováno", "SOD", "ze dne", "objednatel", "stavbyvedoucí"
        ]

        # 1. Odstranění prázdných řádků na konci
        df = df.dropna(subset=["poř.č.", "firma", "název stavby"], how='all')

        # 2. Převedení peněz na čísla a formátování (aby tam nebylo nan)
        money_cols = ["PS (I)", "SNK (I)", "BO (I)", "PS (II)", "BO (II)", "poruchy", "nabídka", "rozdíl", "vyfaktur."]
        for col in money_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # 3. Formátování dat (datumy) - odstranění NaT
        date_cols = ["ukončení", "zrealizováno", "ze dne"]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            # Převedeme na string v českém formátu, prázdné necháme prázdné
            df[col] = df[col].dt.strftime('%d.%m.%Y').fillna("")

        # 4. Vše ostatní (None, nan) pryč
        df = df.fillna("")
        return df
    except Exception as e:
        st.error(f"Chyba: {e}")
        return pd.DataFrame()

df = load_and_clean_data()

# --- ZOBRAZENÍ ---
if not df.empty:
    st.subheader("Evidence 2026")
    
    # Hledání
    search = st.text_input("Hledat v tabulce...", placeholder="Zadejte název, firmu nebo číslo stavby")
    if search:
        df = df[df.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)]

    # Zobrazení tabulky pomocí moderního Streamlit Dataframe
    # Tenhle prvek je "neprůstřelný" - neřešíš HTML, funguje skvěle na šířku
    st.dataframe(
        df,
        use_container_width=True,
        height=580, # Fixní výška pro cca 16 řádků
        hide_index=True,
        column_config={
            "nabídka": st.column_config.NumberColumn(format="%.2f Kč"),
            "rozdíl": st.column_config.NumberColumn(format="%.2f Kč"),
            "vyfaktur.": st.column_config.NumberColumn(format="%.2f Kč"),
            "PS (I)": st.column_config.NumberColumn(format="%.2f"),
            "SNK (I)": st.column_config.NumberColumn(format="%.2f"),
            "BO (I)": st.column_config.NumberColumn(format="%.2f"),
        }
    )
    
    # Součty pod tabulkou pro kontrolu
    celkem = df["nabídka"].sum()
    st.write(f"**Celková hodnota zobrazených zakázek:** {celkem:,.2f} Kč".replace(",", " "))

else:
    st.info("Nahrajte soubor nebo zkontrolujte cestu k Excelu.")
