import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURACE ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding-top: 1rem; }
    /* Styl pro tabulku, aby vypadala profesionálně */
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ A OPRAVA SLOUPCŮ ---
@st.cache_data(ttl=1)
def load_and_clean_data():
    try:
        # Načteme data od řádku 6 (kde začínají záznamy)
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=5, header=None, engine='openpyxl')
        
        # Tady definujeme VŠECH 23 SLOUPCŮ přesně podle tvého Excelu, aby nenastala chyba "Length mismatch"
        df.columns = [
            "poř.č.", "firma", 
            "PS (I)", "SNK (I)", "BO (I)", 
            "PS (II)", "BO (II)", "poruchy", 
            "č.stavby", "název stavby", 
            "nabídka", "rozdíl", "vyfaktur.", 
            "ukončení", "zrealizováno", "SOD", "ze dne", "objednatel", "stavbyvedoucí",
            "nabídková cena", "č.faktury", "částka bez DPH", "splatná"
        ]

        # Odstraníme úplně prázdné řádky
        df = df.dropna(subset=["poř.č.", "firma"], how='all')

        # Čištění peněžních sloupců - žádné nan, jen nuly nebo čísla
        money_cols = ["PS (I)", "SNK (I)", "BO (I)", "PS (II)", "BO (II)", "poruchy", 
                      "nabídka", "rozdíl", "vyfaktur.", "nabídková cena", "částka bez DPH"]
        for col in money_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # Čištění dat - žádné NaT, jen prázdno nebo datum
        date_cols = ["ukončení", "zrealizováno", "ze dne", "splatná"]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df[col] = df[col].dt.strftime('%d.%m.%Y').replace("NaT", "").replace("nan", "")

        # Vše ostatní (None) pryč
        df = df.fillna("")
        return df
    except Exception as e:
        st.error(f"Chyba při načítání: {e}")
        return pd.DataFrame()

df = load_and_clean_data()

# --- 3. ZOBRAZENÍ ---
if not df.empty:
    st.markdown("### Evidence 2026")
    
    # Vyhledávání
    search = st.text_input("", placeholder="Hledat zakázku (firma, název, stavba...)", label_visibility="collapsed")
    
    filtered_df = df.copy()
    if search:
        mask = filtered_df.apply(lambda r: search.lower() in str(r.values).lower(), axis=1)
        filtered_df = filtered_df[mask]

    # Dynamické metriky (Celkem a Počet)
    c1, c2, _ = st.columns([2, 1, 4])
    with c1:
        st.metric("CELKEM NABÍDKA", f"{filtered_df['nabídka'].sum():,.2f} Kč".replace(",", " "))
    with c2:
        st.metric("POČET ZAKÁZEK", len(filtered_df[filtered_df["poř.č."] != ""]))

    # Hlavní tabulka - teď už bez chyb v počtu sloupců
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=450, # Ideální výška pro tvých 16 řádků
        hide_index=True,
        column_config={
            "nabídka": st.column_config.NumberColumn("nabídka", format="%.2f Kč"),
            "rozdíl": st.column_config.NumberColumn("rozdíl", format="%.2f Kč"),
            "vyfaktur.": st.column_config.NumberColumn("vyfaktur.", format="%.2f Kč"),
            "částka bez DPH": st.column_config.NumberColumn("částka bez DPH", format="%.2f Kč"),
            "poř.č.": st.column_config.Column(width="small"),
            "firma": st.column_config.Column(width="medium"),
        }
    )
else:
    st.warning("Data nebyla nalezena. Zkontrolujte, zda je soubor v pořádku.")
