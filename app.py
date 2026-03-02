import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A EXTRÉMNĚ KOMPAKTNÍ DESIGN ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Odstranění horního okraje na minimum */
    .block-container { 
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important;
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
    }
    
    .stApp { background-color: #f4f6f8; }
    
    /* Nadpis - zmenšení mezery */
    h4 { margin-top: 0; margin-bottom: 5px; padding: 0; font-size: 1.1rem; color: #334155; }
    
    /* Kompaktní okenka se součty - poloviční výška */
    div[data-testid="stMetric"] { 
        border: 1px solid #e2e8f0; 
        background-color: #ffffff;
        padding: 2px 8px !important;
        border-radius: 4px;
        min-height: 45px !important;
    }
    div[data-testid="stMetricValue"] { 
        font-size: 0.95rem !important; 
        line-height: 1.2 !important;
    }
    div[data-testid="stMetricLabel"] { 
        font-size: 0.65rem !important; 
        margin-bottom: -5px !important;
    }
    
    /* Odstranění mezer mezi prvky */
    [data-testid="stVerticalBlock"] { gap: 0.3rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ DAT ---
@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        # Filtr: pouze řádky s vyplněným prvním sloupcem (poř.č.)
        df = df[df[df.columns[0]].notna()]
        return df
    except:
        return pd.DataFrame()

df_raw = load_data()

if not df_raw.empty:
    cols = df_raw.columns.tolist()
    col_nabidka = next((c for c in cols if 'nabídka' in c.lower()), None)
    col_rozdil = next((c for c in cols if 'rozdíl' in c.lower()), None)
    col_stav = next((c for c in cols if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_vedouci = next((c for c in cols if 'vedoucí' in c.lower()), None)

    # Převod na čísla
    fin_cols = [c for c in [col_nabidka, col_rozdil] if c]
    for c in fin_cols:
        df_raw[c] = pd.to_numeric(df_raw[c], errors='coerce').fillna(0)

    # Formátování dat (odstranění času)
    for c in cols:
        if 'dne' in c.lower() or 'ukončení' in c.lower():
            df_raw[c] = pd.to_datetime(df_raw[c], errors='coerce').dt.strftime('%d.%m.%Y').replace('NaT', '')

    # --- 3. FILTRY (V jednom řádku pro úsporu místa) ---
    st.markdown("#### 🏗️ Evidence zakázek 2026")
    f1, f2, f3 = st.columns([2, 1, 1])
    with f1: hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat...")
    with f2:
        v_opt = ["Všichni vedoucí"] + sorted([str(x) for x in df_raw[col_vedouci].dropna().unique() if str(x).strip() != ''])
        sel_v = st.selectbox("Vedoucí", v_opt, label_visibility="collapsed")
    with f3:
        s_opt = ["Všechny stavy"] + sorted([str(x) for x in df_raw[col_stav].dropna().unique() if str(x).strip() != ''])
        sel_s = st.selectbox("Stav", s_opt, label_visibility="collapsed")

    df_f = df_raw.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]
    if col_vedouci and sel_v != "Všichni vedoucí":
        df_f = df_f[df_f[col_vedouci].astype(str) == sel_v]
    if col_stav and sel_s != "Všechny stavy":
        df_f = df_f[df_f[col_stav].astype(str) == sel_s]

    # --- 4. SOUČTY (Kompaktní) ---
    def fmt_num(val):
        return f"{val:,.2f}".replace(",", " ").replace(".", ",") + " Kč"

    m1, m2, m3, m4, m5 = st.columns(5)
    def get_sum(kw):
        return df_f[df_f[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_nabidka].sum() if col_stav and col_nabidka else 0

    m1.metric("CELKEM", fmt_num(df_f[col_nabidka].sum()) if col_nabidka else "0 Kč")
    m2.metric("HOTOVO", fmt_num(get_sum('hotov')))
    m3.metric("FAKTURACE", fmt_num(get_sum('faktur')))
    m4.metric("PROBÍHÁ", fmt_num(get_sum('probíh')))
    m5.metric("ZAKÁZEK", len(df_f))

    # --- 5. TABULKA (Fix desetiných míst) ---
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
            if float(row[col_rozdil]) < 0:
                styles[idx] += '; color: #d00000; font-weight: bold;'
        return styles

    # Konfigurace sloupců pro vynucení formátu 000 000.00
    column_configuration = {
        c: st.column_config.NumberColumn(format="%.2f") for c in fin_cols
    }

    st.dataframe(
        df_f.style.apply(style_row, axis=1).format({c: "{:,.2f}".format for c in fin_cols}, thousands=" ", decimal="."),
        use_container_width=True, 
        height=650,
        hide_index=True,
        column_config=column_configuration
    )
    
else:
    st.error("Data nebyla nalezena.")
