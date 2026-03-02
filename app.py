import streamlit as st
import pandas as pd
import sqlite3
import os

# --- KONFIGURACE ---
st.set_page_config(page_title="Evidence zakázek 2026", layout="wide", page_icon="🏗️")

# --- STYLING (Moderní karty) ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
    .zakazka-card {
        background-color: white; padding: 1.2rem; border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 1rem;
        border-left: 10px solid #dee2e6;
    }
    .stav-v-priprave { border-left-color: #adb5bd; }
    .stav-probiha { border-left-color: #fd7e14; }
    .stav-hotovo { border-left-color: #28a745; }
    .stav-fakturace { border-left-color: #007bff; }
    .card-title { font-size: 1.15rem; font-weight: 700; color: #1e3a5f; margin-bottom: 10px; }
    .card-row { display: flex; justify-content: space-between; margin-bottom: 4px; border-bottom: 1px solid #f1f1f1; padding-bottom: 2px; }
    .label { font-weight: 600; color: #495057; font-size: 0.9rem; }
    .value { color: #212529; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

def get_connection():
    return sqlite3.connect('zakazky_data_v2.db', check_same_thread=False)

# --- NAČTENÍ DAT ---
# Použijeme nový název DB zakazky_data_v2.db, aby se data načetla znovu čistě
if not os.path.exists('zakazky_data_v2.db'):
    conn = get_connection()
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        # Přejmenujeme sloupce na čísla pro jistotu, aby nás názvy netrápily
        df.columns = [f"col_{i}" for i in range(len(df.columns))]
        # Poslední sloupec bude náš "stav"
        df['stav'] = 'V přípravě'
        df.to_sql('zakazky', conn, if_exists='replace', index=False)
        conn.commit()
    except Exception as e:
        st.error(f"Chyba: {e}")
    conn.close()

conn = get_connection()
df_all = pd.read_sql('SELECT rowid as ID, * FROM zakazky', conn)

# Mapování sloupců podle pořadí v Excelu:
# 1=Firma, 2=Číslo, 3=Název, 7=Stavbyvedoucí
COL_FIRMA = "col_0"
COL_CISLO = "col_1"
COL_NAZEV = "col_2"
COL_VEDOUCI = "col_5" 

st.title("🏗️ Evidence zakázek 2026")

# --- FILTRY ---
with st.container():
    c1, c2 = st.columns([2, 1])
    with c1:
        hledat = st.text_input("🔍 Hledat stavbu, firmu nebo číslo...")
    with c2:
        seznam = ["Všichni"] + sorted(df_all[COL_VEDOUCI].dropna().unique().tolist())
        vybrany_v = st.selectbox("Filtrovat vedoucího", seznam)

# Filtrování dat
df_f = df_all.copy()
if hledat:
    df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
if vybrany_v != "Všichni":
    df_f = df_f[df_f[COL_VEDOUCI] == vybrany_v]

# --- VÝPIS KARET ---
for _, radek in df_f.iterrows():
    s = str(radek['stav']).lower()
    css = "v-priprave"
    if "probíhá" in s or "probiha" in s: css = "probiha"
    elif "hotovo" in s: css = "hotovo"
    elif "fakturace" in s: css = "fakturace"

    st.markdown(f"""
    <div class="zakazka-card stav-{css}">
        <div class="card-title">{radek[COL_NAZEV]}</div>
        <div class="card-row"><span class="label">Číslo stavby:</span><span class="value">{radek[COL_CISLO]}</span></div>
        <div class="card-row"><span class="label">Firma:</span><span class="value">{radek[COL_FIRMA]}</span></div>
        <div class="card-row"><span class="label">Stavbyvedoucí:</span><span class="value">{radek[COL_VEDOUCI]}</span></div>
        <div class="card-row"><span class="label">Aktuální stav:</span><span class="value"><strong>{radek['stav']}</strong></span></div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📝 Upravit stav"):
        novy = st.selectbox("Nový stav", ["V přípravě", "Probíhá", "Hotovo", "Fakturace"], key=f"s_{radek['ID']}")
        if st.button("Uložit", key=f"b_{radek['ID']}"):
            conn.execute("UPDATE zakazky SET stav = ? WHERE rowid = ?", (novy, int(radek['ID'])))
            conn.commit()
            st.rerun()

conn.close()
