import streamlit as st
import pandas as pd

# --- 1. KONFIGURACE A DESIGN ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container { 
        padding-top: 0.5rem !important; 
        padding-bottom: 0rem !important;
        padding-left: 1rem !important; 
        padding-right: 1rem !important; 
    }
    
    .stApp { background-color: #f4f6f8; }
    
    /* POŘÁDNÝ ŠIROKÝ POSUVNÍK (SCROLLBAR) */
    ::-webkit-scrollbar {
        width: 14px !important;
        height: 14px !important;
        display: block !important;
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

    /* KOMPAKTNÍ METRIKY */
    div[data-testid="stMetric"] { 
        border: 1px solid #e2e8f0; 
        background-color: white; 
        padding: 4px 8px !important; 
        border-radius: 4px; 
        height: 48px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 0.95rem !important; font-weight: 700 !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.65rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. NAČTENÍ A FORMÁT DATA ---
@st.cache_data(ttl=2)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        df = df[df[df.columns[0]].notna()]
        
        # Peněžní sloupce - převod na text pro fixaci desetin
        money_cols = [c for c in df.columns if any(x in c.lower() for x in ['nabídka', 'rozdíl', 'bez dph', 'vyfaktur', 'ps', 'snk', 'bo', 'poruchy'])]
        
        for c in money_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).apply(lambda x: f"{x:.2f}")
            
        return df, money_cols
    except Exception as e:
        st.error(f"Chyba: {e}")
        return pd.DataFrame(), []

df_raw, money_cols = load_data()

if not df_raw.empty:
    col_stav = next((c for c in df_raw.columns if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_rozdil = next((c for c in df_raw.columns if 'rozdíl' in c.lower()), None)

    # --- 3. LIŠTA (NADPIS + HLEDÁNÍ) ---
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown("#### 🏗️ Evidence 2026")
    with c2:
        hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat...")

    df_f = df_raw.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    # --- 4. SOUČTY ---
    def fmt_num(val):
        return f"{val:,.2f}".replace(",", " ").replace(".", ",") + " Kč"

    def get_sum(kw):
        col_n = next((c for c in money_cols if 'nabídka' in c.lower()), None)
        if col_stav and col_n:
            return df_f[df_f[col_stav].astype(str).str.contains(kw, case=False, na=False)][col_n].astype(float).sum()
        return 0

    m1, m2, m3, m4, m5 = st.columns(5)
    col_n_ref = next((c for c in money_cols if 'nabídka' in c.lower()), money_cols[0] if money_cols else None)
    total_val = df_f[col_n_ref].astype(float).sum() if col_n_ref else 0
    
    m1.metric("CELKEM", fmt_num(total_val))
    m2.metric("HOTOVO", fmt_num(get_sum('hotov')))
    m3.metric("FAKTURACE", fmt_num(get_sum('faktur')))
    m4.metric("PROBÍHÁ", fmt_num(get_sum('probíh')))
    m5.metric("ZAKÁZEK", len(df_f))

    # --- 5. STYLING A TABULKA ---
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
            try:
                # Červená pro záporný rozdíl (mínus v textu)
                if "-" in str(row[col_rozdil]):
                    styles[idx] += '; color: #d00000; font-weight: bold;'
            except: pass
        return styles

    # Formátování dat
    for c in df_f.columns:
        if any(x in c.lower() for x in ['dne', 'ukončení']):
            df_f[c] = pd.to_datetime(df_f[c], errors='coerce').dt.strftime('%d.%m.%Y').replace('NaT', '')

    # VÝŠKA NASTAVENA PRO 13 ŘÁDKŮ (CCA 355 PX)
    st.dataframe(
        df_f.style.apply(style_row, axis=1),
        use_container_width=True, 
        height=355, 
        hide_index=True
    )
    
else:
    st.error("Data nenalezena.")
