import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A DESIGN ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Odstranění okrajů stránky (Full Width) */
    .block-container { 
        padding-top: 0.5rem; 
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
        max-width: 100% !important; 
    }
    
    /* Tlumené pozadí celé aplikace */
    .stApp { background-color: #f4f6f8; }
    
    h4 { margin: 0; padding: 0 0 10px 0; font-size: 1.1rem; color: #334155; }
    
    /* Boxy se součty - decentní vzhled */
    div[data-testid="stMetric"] { 
        border: 1px solid #e2e8f0; 
        background-color: #ffffff;
        padding: 5px 10px !important;
        border-radius: 4px;
    }
    div[data-testid="stMetricValue"] { font-size: 1rem !important; color: #0f172a; }
    div[data-testid="stMetricLabel"] { font-size: 0.65rem !important; text-transform: uppercase; letter-spacing: 0.5px; }
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
    # Identifikace sloupců
    cols = df_all.columns.tolist()
    col_nabidka = next((c for c in cols if 'nabídka' in c.lower() or 'cena' in c.lower()), None)
    col_rozdil = next((c for c in cols if 'rozdíl' in c.lower()), None)
    col_stav = next((c for c in cols if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_vedouci = next((c for c in cols if 'vedoucí' in c.lower() or 'stavbyved' in c.lower()), None)

    # Převod všech finančních sloupců na čísla
    for c in [col_nabidka, col_rozdil]:
        if c: df_all[c] = pd.to_numeric(df_all[c], errors='coerce').fillna(0)

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

    # --- 4. SOUČTY ---
    def fmt_num(val):
        return f"{val:,.2f}".replace(",", " ").replace(".", ",") + " Kč"

    if col_nabidka:
        m1, m2, m3, m4, m5 = st.columns(5)
        def get_sum(kw):
            return df_f[df_f[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_nabidka].sum() if col_stav else 0

        m1.metric("CELKEM", fmt_num(df_f[col_nabidka].sum()))
        m2.metric("HOTOVO", fmt_num(get_sum('hotov')))
        m3.metric("FAKTURACE", fmt_num(get_sum('faktur')))
        m4.metric("PROBÍHÁ", fmt_num(get_sum('probíh')))
        m5.metric("STAVEB", len(df_f))

    # --- 5. STYLING TABULKY ---
    def apply_style(row):
        styles = [''] * len(row)
        # Barva řádku podle stavu
        if col_stav:
            status = str(row[col_stav]).lower()
            color = ''
            if 'hotov' in status: color = 'background-color: #f1fcf4' # ultra jemná zelená
            elif 'probíh' in status: color = 'background-color: #fffdf2' # ultra jemná žlutá
            elif 'faktur' in status: color = 'background-color: #f0f7ff' # ultra jemná modrá
            styles = [color] * len(row)
        
        # Červená barva pro záporný rozdíl
        if col_rozdil:
            idx_rozdil = row.index.get_loc(col_rozdil)
            if row[col_rozdil] < 0:
                styles[idx_rozdil] += '; color: #d00000; font-weight: bold;'
        
        return styles

    # Formátování čísel v tabulce (2 desetinná místa)
    format_dict = {}
    if col_nabidka: format_dict[col_nabidka] = "{:,.2f}"
    if col_rozdil: format_dict[col_rozdil] = "{:,.2f}"

    st.dataframe(
        df_f.style.apply(apply_style, axis=1).format(format_dict),
        use_container_width=True, 
        height=650,
        hide_index=True
    )
    
else:
    st.error("Data nebyla nalezena.")
