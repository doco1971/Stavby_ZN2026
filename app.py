import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

# --- 2. EXTRÉMNÍ DESIGN (STYLING) ---
st.markdown("""
    <style>
    /* Skrytí standardních prvků */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 1rem !important; padding-bottom: 0rem !important; }

    /* KONTEJNER PRO TABULKU - Nastaveno na 16 řádků */
    .table-wrapper {
        height: 650px; 
        overflow-y: scroll;
        overflow-x: auto;
        border: 2px solid #262730;
        background-color: white;
    }

    /* POSUVNÍK - EXTRÉMNĚ TLUSTÝ (40px) */
    .table-wrapper::-webkit-scrollbar {
        width: 40px !important;
        height: 40px !important;
    }
    .table-wrapper::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
    }
    .table-wrapper::-webkit-scrollbar-thumb {
        background: #444 !important;
        border: 6px solid #f1f1f1;
        border-radius: 4px;
    }
    .table-wrapper::-webkit-scrollbar-thumb:hover {
        background: #222 !important;
    }

    /* STYL HTML TABULKY */
    .main-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 13px;
    }
    .main-table th {
        position: sticky;
        top: 0;
        background-color: #262730;
        color: white;
        padding: 12px 8px;
        text-align: left;
        border: 1px solid #444;
        z-index: 20;
    }
    .main-table td {
        padding: 8px;
        border: 1px solid #ddd;
        white-space: nowrap;
    }
    .main-table tr:hover { background-color: #f9f9f9; }
    
    /* Barvy stavů a záporných hodnot */
    .st-hotovo { background-color: #f1fcf4 !important; }
    .st-probiha { background-color: #fffdf2 !important; }
    .st-fakturace { background-color: #f0f7ff !important; }
    .negativni { color: #d00000; font-weight: bold; }

    /* DESIGN METRIK */
    .metric-card {
        background: white;
        border: 1px solid #e6e9ef;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA NAČÍTÁNÍ DAT ---
@st.cache_data(ttl=1)
def load_and_fix_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

df_raw = load_and_fix_data()

if not df_raw.empty:
    # Horní lišta: Název a Vyhledávání
    c1, c2 = st.columns([1, 2])
    with c1: st.markdown("## 🏗️ Evidence 2026")
    with c2: hledat = st.text_input("", placeholder="Zadejte text pro vyhledávání (firma, stav, číslo stavby...)", label_visibility="collapsed")

    # Filtrování
    df_filtered = df_raw.copy()
    if hledat:
        mask = df_filtered.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)
        df_filtered = df_filtered[mask]

    # Identifikace sloupců
    money_cols = [c for c in df_filtered.columns if any(x in c.lower() for x in ['nabídka', 'rozdíl', 'bez dph', 'vyfaktur', 'ps', 'snk', 'bo', 'poruchy'])]
    col_stav = next((c for c in df_filtered.columns if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_nabidka = next((c for c in money_cols if 'nabídka' in c.lower()), money_cols[0] if money_cols else None)

    # --- 4. VÝPOČET SOUČTŮ (METRIKY) ---
    def calc_sum(keyword=None):
        if not col_nabidka: return 0
        temp_df = df_filtered.copy()
        temp_df[col_nabidka] = pd.to_numeric(temp_df[col_nabidka], errors='coerce').fillna(0)
        if keyword and col_stav:
            return temp_df[temp_df[col_stav].astype(str).str.contains(keyword, case=False, na=False)][col_nabidka].sum()
        return temp_df[col_nabidka].sum()

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1: st.metric("CELKEM", f"{calc_sum():,.2f}".replace(",", " ").replace(".", ",") + " Kč")
    with m2: st.metric("HOTOVO", f"{calc_sum('hotov'):,.2f}".replace(",", " ").replace(".", ",") + " Kč")
    with m3: st.metric("FAKTURACE", f"{calc_sum('faktur'):,.2f}".replace(",", " ").replace(".", ",") + " Kč")
    with m4: st.metric("PROBÍHÁ", f"{calc_sum('probíh'):,.2f}".replace(",", " ").replace(".", ",") + " Kč")
    with m5: st.metric("ZAKÁZEK", len(df_filtered))

    # --- 5. GENERÁTOR HTML TABULKY ---
    html_code = '<div class="table-wrapper"><table class="main-table"><thead><tr>'
    for col in df_filtered.columns:
        html_code += f'<th>{col}</th>'
    html_code += '</tr></thead><tbody>'

    for _, row in df_filtered.iterrows():
        # Určení barvy řádku
        tr_class = ""
        if col_stav:
            s = str(row[col_stav]).lower()
            if 'hotov' in s: tr_class = ' class="st-hotovo"'
            elif 'probíh' in s: tr_class = ' class="st-probiha"'
            elif 'faktur' in s: tr_class = ' class="st-fakturace"'

        html_code += f'<tr{tr_class}>'
        for col in df_filtered.columns:
            val = row[col]
            td_style = ""
            display_val = str(val) if pd.notna(val) else ""

            # Formát čísel na 2 desetiny
            if col in money_cols:
                try:
                    num = float(val)
                    display_val = f"{num:.2f}"
                    if 'rozdíl' in col.lower() and num < 0: td_style = ' class="negativni"'
                except: pass
            
            # Formát data
            elif any(x in col.lower() for x in ['dne', 'ukončení']):
                try: display_val = pd.to_datetime(val).strftime('%d.%m.%Y')
                except: pass

            html_code += f'<td{td_style}>{display_val}</td>'
        html_code += '</tr>'
    
    html_code += '</tbody></table></div>'
    
    # Zobrazení tabulky
    st.markdown(html_code, unsafe_allow_html=True)

else:
    st.error("Soubor nebyl nalezen nebo je prázdný.")
