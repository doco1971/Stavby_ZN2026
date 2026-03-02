import streamlit as st
import pandas as pd
import sqlite3
import os

# --- 1. NASTAVENÍ VZHLEDU (Moderní tmavě modrá / šedá) ---
st.set_page_config(page_title="Stavby ZN 2026", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f0f2f5; }
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 15px;
        border-left: 8px solid #1e3a5f;
    }
    .card-title { color: #1e3a5f; font-size: 1.2rem; font-weight: bold; margin-bottom: 10px; }
    .info-row { display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding: 5px 0; }
    .label { font-weight: 600; color: #666; }
    .status-v-priprave { border-left-color: #94a3b8; }
    .status-probiha { border-left-color: #f59e0b; }
    .status-hotovo { border-left-color: #10b981; }
    .status-fakturace { border-left-color: #3b82f6; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABÁZE (Čistý start) ---
DB_NAME = 'database_final.db' # Nový název pro čistý start

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

if not os.path.exists(DB_NAME):
    conn = get_conn()
    try:
        # Načtení Excelu - bereme jen data, nezajímají nás názvy sloupců
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        # Necháme jen prvních 10 sloupců a pojmenujeme je napevno
        df = df.iloc[:, :10]
        df.columns = ['firma', 'cislo', 'nazev', 'nabidka', 'termin_nabidka', 'termin_ukonceni', 'vedouci', 'smlouva', 'faktura', 'poznamka']
        df['stav'] = 'V přípravě'
        df.to_sql('zakazky', conn, if_exists='replace', index=False)
        conn.commit()
    except Exception as e:
        st.error(f"Chyba při startu: {e}")
    conn.close()

# --- 3. LOGIKA A FILTRY ---
conn = get_conn()
df_all = pd.read_sql('SELECT rowid as ID, * FROM zakazky', conn)

st.title("🏗️ Evidence zakázek ZN 2026")

col_search, col_filter = st.columns([2, 1])
with col_search:
    search = st.text_input("🔍 Hledat (název, firma, číslo...)")
with col_filter:
    vedouci_opt = ["Všichni"] + sorted(df_all['vedouci'].dropna().unique().tolist())
    sel_vedouci = st.selectbox("Stavbyvedoucí", vedouci_opt)

# Filtrování
df_view = df_all.copy()
if search:
    df_view = df_view[df_view.apply(lambda r: search.lower() in r.astype(str).str.lower().values, axis=1)]
if sel_vedouci != "Všichni":
    df_view = df_view[df_view['vedouci'] == sel_vedouci]

# --- 4. ZOBRAZENÍ KARET ---
for _, radek in df_view.iterrows():
    stav_slug = str(radek['stav']).lower().replace('í', 'i').replace('ě', 'e')
    css_status = "status-v-priprave"
    if "probiha" in stav_slug: css_status = "status-probiha"
    elif "hotovo" in stav_slug: css_status = "status-hotovo"
    elif "fakturace" in stav_slug: css_status = "status-fakturace"

    st.markdown(f"""
    <div class="card {css_status}">
        <div class="card-title">{radek['nazev']}</div>
        <div class="info-row"><span class="label">Číslo stavby:</span><span>{radek['cislo']}</span></div>
        <div class="info-row"><span class="label">Firma:</span><span>{radek['firma']}</span></div>
        <div class="info-row"><span class="label">Stavbyvedoucí:</span><span>{radek['vedouci']}</span></div>
        <div class="info-row"><span class="label">Aktuální stav:</span><strong>{radek['stav']}</strong></div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("⚙️ Změnit stav"):
        novy = st.selectbox("Vyberte stav", ["V přípravě", "Probíhá", "Hotovo", "Fakturace"], key=f"s_{radek['ID']}")
        if st.button("Uložit změnu", key=f"b_{radek['ID']}"):
            conn.execute("UPDATE zakazky SET stav = ? WHERE rowid = ?", (novy, int(radek['ID'])))
            conn.commit()
            st.rerun()

conn.close()
