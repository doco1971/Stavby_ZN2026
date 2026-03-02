import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A DESIGN POSUVNÍKU ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Odstranění horního volného místa */
    .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 0rem !important;
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
    }
    
    .stApp { background-color: #f4f6f8; }
    
    /* ŠIROKÝ A TRVALE VIDITELNÝ POSUVNÍK (SCROLLBAR) */
    ::-webkit-scrollbar {
        width: 16px !important;
        height: 16px !important;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #888888 !important;
        border-radius: 4px !important;
        border: 2px solid #f1f1f1 !important;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555555 !important;
    }

    /* KOMPAKTNÍ METRIKY (SOUČTY) */
    div[data-testid="stMetric"] { 
        border: 1px solid #e2e8f0; 
        background-color: white; 
        padding: 4px 8px !important; 
        border-radius: 4px; 
        height: 50px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 1rem !important; font-weight: 700 !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ A PŘÍSNÁ ÚPRAVA DAT ---
@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        # Ponechat jen řádky, kde je v prvním sloupci hodnota (poř.č.)
        df = df[df[df.columns[0]].notna()]
        
        # Identifikace finančních sloupců pro převod na text (fix desetin)
        money_cols = [c for c in df.columns if any(x in c.lower() for x in ['nabídka', 'rozdíl', 'bez dph', 'vyfaktur', 'ps', 'snk', 'bo', 'poruchy'])]
        
        for c in money_cols:
            # Převod na číslo a pak hned na text se 2 desetinami (brání Streamlitu v doplňování nul)
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).apply(lambda x: f"{x:.2f}")
            
        return df, money_cols
    except Exception as e:
        st.error(f"Chyba při načítání Excelu: {e}")
        return pd.DataFrame(), []

df_raw, money_cols = load_data()

if not df_raw.empty:
    col_stav = next((c for c in df_raw.columns if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_rozdil = next((c for c in df_raw.columns if 'rozdíl' in c.lower()), None)

    # --- 3. LIŠTA: NADPIS + HLEDÁNÍ ---
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown("#### 🏗️ Evidence 2026")
    with c2:
        hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat (jméno, stav, zakázku)...")

    # Univerzální vyhledávání
    df_f = df_raw.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    # --- 4. SOUČTY (METRIKY) ---
    def fmt_num(val):
        return f"{val:,.2f}".replace(",", " ").replace(".", ",") + " Kč"

    def get_sum_by_status(keyword):
        col_n = next((c for c in money_cols if 'nabídka' in c.lower()), None)
        if col_stav and col_n:
            # Musíme převést text zpět na číslo pro součet
            return df_f[df_f[col_stav].astype(str).str.contains(keyword, case=False, na=False)][col_n].astype(float).sum()
        return 0

    m1, m2, m3, m4, m5 = st.columns(5)
    col_main_n = next((c for c in money_cols if 'nabídka' in c.lower()), money_cols[0] if money_cols else None)
    total_val = df_f[col_main_n].astype(float).sum() if col_main_n else 0
    
    m1.metric("CELKEM", fmt_num(total_val))
    m2.metric("HOTOVO", fmt_num(get_sum_by_status('hotov')))
    m3.metric("FAKTURACE", fmt_num(get_sum_by_status('faktur')))
    m4.metric("PROBÍHÁ", fmt_num(get_sum_by_status('probíh')))
    m5.metric("ZAKÁZEK", len(df_f))

    # --- 5. STYLING A ZOBRAZENÍ TABULKY ---
    def style_row(row):
        styles = [''] * len(row)
        # Barva pozadí podle stavu
        if col_stav:
            s = str(row[col_stav]).lower()
            color = ''
            if 'hotov' in s: color = 'background-color: #f1fcf4'
            elif 'probíh' in s: color = 'background-color: #fffdf2'
            elif 'faktur' in s: color = 'background-color: #f0f7ff'
            styles = [color] * len(row)
        
        # Červené zvýraznění záporného rozdílu
        if col_rozdil:
            idx = row.index.get_loc(col_rozdil)
            try:
                if float(row[col_rozdil]) < 0:
                    styles[idx] += '; color: #d00000; font-weight: bold;'
            except: pass
        return styles

    # Formátování datových sloupců na DD.MM.RRRR
    for c in df_f.columns:
        if any(x in c.lower() for x in ['dne', 'ukončení']):
            df_f[c] = pd.to_datetime(df_f[c], errors='coerce').dt.strftime('%d.%m.%Y').replace('NaT', '')

    # TABULKA S PEVNOU VÝŠKOU PRO CCA 16 ŘÁDKŮ
    st.dataframe(
        df_f.style.apply(style_row, axis=1),
        use_container_width=True, 
        height=415, 
        hide_index=True
    )
    
else:
    st.error("Data nebyla nalezena nebo soubor neobsahuje správné sloupce.")
