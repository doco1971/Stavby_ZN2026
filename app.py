import streamlit as st
import pandas as pd

# --- 1. NASTAVENÍ A FIXACE HORNÍHO PANELU ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    /* Skrytí lišty Streamlit */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* FIXACE CELÉHO VRŠKU (Sticky Header) */
    [data-testid="stVerticalBlock"] > div:first-child {
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 1000;
        padding-top: 0.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f2f6;
    }

    /* Úprava mezer a vzhledu */
    .block-container { padding-top: 0rem; }
    h4 { margin: 0; padding-bottom: 10px; font-size: 1.3rem; color: #1e3a5f; font-weight: 800; }
    
    /* Vzhled boxů se součty (bílé karty) */
    .stMetric { 
        border: 1px solid #e6e9ef; 
        background-color: #ffffff;
        padding: 5px 10px !important;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    div[data-testid="stMetricValue"] { font-size: 1.1rem !important; font-weight: 700; color: #111; }
    div[data-testid="stMetricLabel"] { font-size: 0.75rem !important; color: #666; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=10)
def load_data():
    try:
        # Načítáme Excel (skiprows=4 podle vašeho formátu)
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        return pd.DataFrame()

df_all = load_data()

if not df_all.empty:
    # Identifikace sloupců (automaticky hledá 'nabídka', 'stav', 'stavbyvedoucí')
    cols = df_all.columns.tolist()
    col_nabidka = next((c for c in cols if 'nabídka' in c.lower() or 'cena' in c.lower()), None)
    col_stav = next((c for c in cols if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_vedouci = next((c for c in cols if 'vedoucí' in c.lower() or 'stavbyved' in c.lower()), None)

    # Převod nabídek na čísla pro součty
    if col_nabidka:
        df_all[col_nabidka] = pd.to_numeric(df_all[col_nabidka], errors='coerce').fillna(0)

    # --- 3. UKOTVENÝ KONTEJNER (Nadpis, Filtry, Součty) ---
    with st.container():
        st.markdown("#### 🏗️ Evidence zakázek 2026")
        
        # Řádek s filtry
        f1, f2, f3 = st.columns([2, 1, 1])
        with f1:
            hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Rychlé hledání v tabulce...")
        with f2:
            v_opt = ["Všichni vedoucí"] + sorted([str(x) for x in df_all[col_vedouci].dropna().unique()]) if col_vedouci else ["Všichni"]
            sel_v = st.selectbox("Vedoucí", v_opt, label_visibility="collapsed")
        with f3:
            # Oprava: Pokud sloupec stav v Excelu neexistuje, vytvoříme virtuální 'Všechny stavy'
            s_opt = ["Všechny stavy"]
            if col_stav:
                unique_s = sorted([str(x) for x in df_all[col_stav].dropna().unique()])
                s_opt.extend(unique_s)
            sel_s = st.selectbox("Stav", s_opt, label_visibility="collapsed")

        # --- FILTROVÁNÍ DAT (Pro výpočty i tabulku) ---
        df_f = df_all.copy()
        if hledat:
            df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
        if col_vedouci and sel_v != "Všichni vedoucí":
            df_f = df_f[df_f[col_vedouci].astype(str) == sel_v]
        if col_stav and sel_s != "Všechny stavy":
            df_f = df_f[df_f[col_stav].astype(str) == sel_s]

        # Řádek s bílými boxy (Součty) - reagují na filtry
        if col_nabidka:
            m1, m2, m3, m4, m5 = st.columns(5)
            
            def sum_kw(df, kw):
                if col_stav:
                    return df[df[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_nabidka].sum()
                return 0

            m1.metric("CELKEM", f"{df_f[col_nabidka].sum():,.0f} Kč".replace(',', ' '))
            m2.metric("HOTOVO", f"{sum_kw(df_f, 'hotov'):,.0f} Kč".replace(',', ' '))
            m3.metric("FAKTURACE", f"{sum_kw(df_f, 'faktur'):,.0f} Kč".replace(',', ' '))
            m4.metric("PROBÍHÁ", f"{sum_kw(df_f, 'probíh'):,.0f} Kč".replace(',', ' '))
            m5.metric("STAVEB", f"{len(df_f)}")

    # --- 4. TABULKA (Rolovací část) ---
    # Funkce pro barvy řádků
    def style_rows(row):
        color = ''
        if col_stav:
            status = str(row[col_stav]).lower()
            if 'hotov' in status: color = 'background-color: #dcfce7'
            elif 'probíh' in status: color = 'background-color: #fef9c3'
            elif 'faktur' in status: color = 'background-color: #dbeafe'
        return [color] * len(row)

    # Zobrazení tabulky se zachováním stylu
    st.dataframe(df_f.style.apply(style_rows, axis=1), use_container_width=True, height=1000)
    
else:
    st.error("Nepodařilo se načíst data z Excelu. Zkontrolujte, zda je soubor na GitHubu.")
