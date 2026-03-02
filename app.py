import streamlit as st
import pandas as pd

# --- 1. NASTAVENÍ A ŠETRNÝ DESIGN ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Pozadí aplikace - tlumená šedá, aby to nesvítilo */
    .stApp { background-color: #f1f3f6; }
    .block-container { padding-top: 0.5rem; }
    
    h4 { margin: 0; padding: 0 0 10px 0; font-size: 1.2rem; color: #1e3a5f; }
    
    /* Boxy se součty - mírně krémový/šedý podklad */
    div[data-testid="stMetric"] { 
        border: 1px solid #d1d5db; 
        background-color: #fcfcfc;
        padding: 5px 10px !important;
        border-radius: 6px;
    }
    div[data-testid="stMetricValue"] { font-size: 1.1rem !important; color: #111827; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=10)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all').dropna(axis=1, how='all')
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

df_all = load_data()

if not df_all.empty:
    cols = df_all.columns.tolist()
    col_nabidka = next((c for c in cols if 'nabídka' in c.lower() or 'cena' in c.lower()), None)
    col_stav = next((c for c in cols if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_vedouci = next((c for c in cols if 'vedoucí' in c.lower() or 'stavbyved' in c.lower()), None)

    # Převod na čísla
    if col_nabidka:
        df_all[col_nabidka] = pd.to_numeric(df_all[col_nabidka], errors='coerce').fillna(0)

    # --- 3. FILTRY ---
    st.markdown("#### 🏗️ Evidence zakázek 2026")
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat...")
    with f2:
        v_opt = ["Všichni vedoucí"] + sorted([str(x) for x in df_all[col_vedouci].dropna().unique()]) if col_vedouci else ["Všichni"]
        sel_v = st.selectbox("Vedoucí", v_opt, label_visibility="collapsed")
    with f3:
        s_opt = ["Všechny stavy"] + sorted([str(x) for x in df_all[col_stav].dropna().unique()]) if col_stav else ["Vše"]
        sel_s = st.selectbox("Stav", s_opt, label_visibility="collapsed")

    # Filtrování
    df_f = df_all.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
    if col_vedouci and sel_v != "Všichni vedoucí":
        df_f = df_f[df_f[col_vedouci].astype(str) == sel_v]
    if col_stav and sel_s != "Všechny stavy":
        df_f = df_f[df_f[col_stav].astype(str) == sel_s]

    # --- 4. SOUČTY (S formátováním) ---
    if col_nabidka:
        # Formátování: 1 234 567.89 Kč
        def fmt(val):
            return f"{val:,.2f}".replace(",", " ").replace(".", ",") + " Kč"

        m1, m2, m3, m4, m5 = st.columns(5)
        def get_sum(kw):
            return df_f[df_f[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_nabidka].sum() if col_stav else 0

        m1.metric("CELKEM", fmt(df_f[col_nabidka].sum()))
        m2.metric("HOTOVO", fmt(get_sum('hotov')))
        m3.metric("FAKTURACE", fmt(get_sum('faktur')))
        m4.metric("PROBÍHÁ", fmt(get_sum('probíh')))
        m5.metric("STAVEB", len(df_f))

    # --- 5. TABULKA (Skrytý index a formátování čísel) ---
    def style_rows(row):
        color = ''
        if col_stav:
            status = str(row[col_stav]).lower()
            if 'hotov' in status: color = 'background-color: #dcfce7'
            elif 'probíh' in status: color = 'background-color: #fef9c3'
            elif 'faktur' in status: color = 'background-color: #dbeafe'
        return [color] * len(row)

    # Příprava zobrazení čísel v tabulce (všechny číselné sloupce na 2 des. místa)
    df_display = df_f.style.apply(style_rows, axis=1).format(
        subset=[col_nabidka] if col_nabidka else [], 
        formatter="{:,.2f}"
    )

    st.dataframe(
        df_display, 
        use_container_width=True, 
        height=650,
        hide_index=True # <--- TADY SE VYPÍNÁ TEN PRVNÍ SLOUPEC S ČÍSLY
    )
    
else:
    st.error("Data nebyla nalezena.")
