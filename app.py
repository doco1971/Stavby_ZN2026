import streamlit as st
import pandas as pd
import sqlite3
import os

# --- 1. KONFIGURACE ---
st.set_page_config(page_title="Stavby ZN 2026", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fc; }
    .main-title { color: #1e3a5f; font-size: 2.2rem; font-weight: 800; margin-bottom: 20px; text-align: center; }
    .metric-box {
        background-color: white; padding: 15px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center;
        border-top: 5px solid #1e3a5f;
    }
    .metric-value { font-size: 1.5rem; font-weight: 700; color: #1e3a5f; }
    .metric-label { font-size: 0.9rem; color: #666; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATABÁZE ---
DB_NAME = 'database_v3.db'

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# Pokud DB neexistuje, vytvoříme ji z Excelu
if not os.path.exists(DB_NAME):
    conn = get_conn()
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.iloc[:, :10] # Bereme prvních 10 sloupců
        df.columns = ['Firma', 'Cislo', 'Nazev', 'Nabidka', 'Termin_N', 'Termin_U', 'Vedouci', 'Smlouva', 'Faktura', 'Poznamka']
        df['Stav'] = 'V přípravě'
        df = df.dropna(subset=['Nazev'])
        # Převod Nabídky na číslo, aby šlo sčítat
        df['Nabidka'] = pd.to_numeric(df['Nabidka'], errors='coerce').fillna(0)
        df.to_sql('zakazky', conn, if_exists='replace', index=False)
        conn.commit()
    except Exception as e:
        st.error(f"Chyba importu: {e}")
    conn.close()

conn = get_conn()
df_all = pd.read_sql('SELECT rowid as ID, * FROM zakazky', conn)

# --- 3. HLAVNÍ PLOCHA ---
st.markdown('<div class="main-title">🏗️ Evidence zakázek 2026</div>', unsafe_allow_html=True)

# Filtry
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    hledat = st.text_input("🔍 Hledat v tabulce...", placeholder="Název, firma, číslo...")
with col2:
    vedouci_opt = ["Všichni"] + sorted(df_all['Vedouci'].dropna().unique().tolist())
    sel_vedouci = st.selectbox("Vedoucí", vedouci_opt)
with col3:
    sel_stav = st.selectbox("Stav", ["Vše", "V přípravě", "Probíhá", "Hotovo", "Fakturace"])

# Filtrování dat
df_f = df_all.copy()
if hledat:
    df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
if sel_vedouci != "Všichni":
    df_f = df_f[df_f['Vedouci'] == sel_vedouci]
if sel_stav != "Vše":
    df_f = df_f[df_f['Stav'] == sel_stav]

# --- 4. SOUČTY (Statistiky) ---
total_nabidka = df_f['Nabidka'].sum()
count_stavby = len(df_f)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-box"><div class="metric-label">Počet zakázek</div><div class="metric-value">{count_stavby}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box"><div class="metric-label">Celková hodnota</div><div class="metric-value">{total_nabidka:,.0f} Kč'.replace(',', ' ') + '</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-box"><div class="metric-label">Průměrná zakázka</div><div class="metric-value">{(total_nabidka/count_stavby if count_stavby > 0 else 0):,.0f} Kč'.replace(',', ' ') + '</div></div>', unsafe_allow_html=True)

st.write("##")

# --- 5. TABULKA ---
st.dataframe(
    df_f.drop(columns=['ID']),
    use_container_width=True,
    height=450,
    column_config={
        "Nabidka": st.column_config.NumberColumn("Nabídka", format="%d Kč"),
        "Termin_U": st.column_config.DateColumn("Ukončení")
    }
)

# --- 6. EDITACE ---
st.markdown("---")
st.subheader("📝 Rychlá aktualizace stavu")
cs1, cs2, cs3 = st.columns([2, 1, 1])

with cs1:
    vyber = st.selectbox("Vyberte stavbu:", df_f['Nazev'].tolist())
with cs2:
    novy_stav = st.selectbox("Nový stav:", ["V přípravě", "Probíhá", "Hotovo", "Fakturace"])
with cs3:
    st.write("##")
    if st.button("💾 ULOŽIT ZMĚNU", use_container_width=True):
        id_up = int(df_f[df_f['Nazev'] == vyber]['ID'].iloc[0])
        conn.execute("UPDATE zakazky SET Stav = ? WHERE rowid = ?", (novy_stav, id_up))
        conn.commit()
        st.success("Aktualizováno!")
        st.rerun()

conn.close()
