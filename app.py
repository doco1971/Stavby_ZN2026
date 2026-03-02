import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A POSUVNÍK ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 0.5rem !important; padding-left: 1rem !important; padding-right: 1rem !important; }
    .stApp { background-color: #f4f6f8; }
    
    /* Široký a trvale viditelný scrollbar */
    section[data-testid="stTable"]::-webkit-scrollbar, 
    div[data-testid="stDataTableVisualizer"] > div::-webkit-scrollbar {
        width: 16px !important;
        height: 16px !important;
        display: block !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #888888 !important;
        border-radius: 4px !important;
        border: 2px solid #f1f1f1 !important;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
        display: block !important;
    }

    div[data-testid="stMetric"] { 
        border: 1px solid #e2e8f0; background-color: white; padding: 4px 8px !important; border-radius: 4px; height: 48px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 0.95rem !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        df = df[df[df.columns[0]].notna()]
        return df
    except:
        return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    cols = df_raw.columns.tolist()
    # Sloupce, které chceme formátovat jako peníze
    money_cols = [c for c in cols if any(x in c.lower() for x in ['nabídka', 'rozdíl', 'bez dph', 'vyfaktur'])]
    col_stav = next((c for c in cols if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_rozdil = next((c for c in cols if 'rozdíl' in c.lower()), None)

    # Pomocná funkce pro převod na hezký text (mezery, dvě desetiny)
    def to_pretty_text(val):
        try:
            num = float(val)
            return f"{num:,.2f}".replace(",", " ").replace(".", ",")
        except:
            return val

    # --- 3. VÝPOČET SOUČTŮ (dokud jsou to čísla) ---
    def get_sum(kw):
        col_n = next((c for c in money_cols if 'nabídka' in c.lower()), money_cols[0] if money_cols else None)
        if col_stav and col_n:
            return pd.to_numeric(df_raw[df_raw[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_n], errors='coerce').sum()
        return 0

    # --- 4. LIŠTA A METRIKY ---
    c1, c2 = st.columns([1, 3])
    with c1: st.markdown("#### 🏗️ Evidence 2026")
    with c2: hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat...")

    df_f = df_raw.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    m1, m2, m3, m4, m5 = st.columns(5)
    col_n_ref = next((c for c in money_cols if 'nabídka' in c.lower()), None)
    total_val = pd.to_numeric(df_f[col_n_ref], errors='coerce').sum() if col_n_ref else 0
    
    m1.metric("CELKEM", f"{total_val:,.2f}".replace(",", " ").replace(".", ",") + " Kč")
    m2.metric("HOTOVO", f"{get_sum('hotov'):,.2f}".replace(",", " ").replace(".", ",") + " Kč")
    m3.metric("FAKTURACE", f"{get_sum('faktur'):,.2f}".replace(",", " ").replace(".", ",") + " Kč")
    m4.metric("PROBÍHÁ", f"{get_sum('probíh'):,.2f}".replace(",", " ").replace(".", ",") + " Kč")
    m5.metric("ZAKÁZEK", len(df_f))

    # --- 5. FINÁLNÍ ÚPRAVA TABULKY (PŘEVOD ČÍSEL NA TEXT) ---
    # Záloha pro barvení (potřebujeme čísla)
    rozdil_numeric = pd.to_numeric(df_f[col_rozdil], errors='coerce').fillna(0).values if col_rozdil else []

    # Převod všech finančních sloupců na TEXT, aby Streamlit nemohl přidat nuly
    for c in money_cols:
        df_f[c] = df_f[c].apply(to_pretty_text)

    # Formátování dat
    for c in cols:
        if any(x in c.lower() for x in ['dne', 'ukončení']):
            df_f[c] = pd.to_datetime(df_f[c], errors='coerce').dt.strftime('%d.%m.%Y').replace('NaT', '')

    def style_row(row):
        styles = [''] * len(row)
        if col_stav:
            s = str(row[col_stav]).lower()
            color = ''
            if 'hotov' in s: color = 'background-color: #f1fcf4'
            elif 'probíh' in s: color = 'background-color: #fffdf2'
            elif 'faktur' in s: color = 'background-color: #f0f7ff'
            styles = [color] * len(row)
        
        if col_rozdil:
            idx = row.index.get_loc(col_rozdil)
            # Použijeme textovou hodnotu a zkusíme, zda obsahuje mínus
            if "-" in str(row[col_rozdil]):
                styles[idx] += '; color: #d00000; font-weight: bold;'
        return styles

    st.dataframe(
        df_f.style.apply(style_row, axis=1),
        use_container_width=True, 
        height=480, # Výška pro cca 16 řádků
        hide_index=True
    )
else:
    st.error("Data nebyla nalezena.")
