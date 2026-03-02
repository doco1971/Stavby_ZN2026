import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# --- KONFIGURACE ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

# --- EXTRÉMNÍ CSS PRO POSUVNÍK ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container { padding-top: 0.5rem !important; }
    
    /* Vynucení tlustého posuvníku */
    html, body, [data-testid="stAppViewContainer"], .stDataFrame, div[data-testid="stDataTableVisualizer"] {
        scrollbar-width: thick !important;
        scrollbar-color: #888888 #f1f1f1 !important;
    }

    ::-webkit-scrollbar {
        width: 35px !important; 
        height: 35px !important;
        display: block !important;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
        display: block !important;
    }
    ::-webkit-scrollbar-thumb {
        background: #888888 !important;
        border-radius: 0px !important;
        border: 5px solid #f1f1f1 !important;
        display: block !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAČTENÍ DAT ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all')
        df.columns = [str(c).strip() for c in df.columns]
        
        # Striktní formátování všech čísel na 2 desetinná místa jako text
        money_cols = [c for c in df.columns if any(x in c.lower() for x in ['nabídka', 'rozdíl', 'bez dph', 'vyfaktur', 'ps', 'snk', 'bo', 'poruchy'])]
        for c in money_cols:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).apply(lambda x: f"{x:.2f}")
            
        return df, money_cols
    except:
        return pd.DataFrame(), []

df_raw, money_cols = load_data()

if not df_raw.empty:
    col_stav = next((c for c in df_raw.columns if 'stav' in c.lower() and 'název' not in c.lower()), None)
    col_rozdil = next((c for c in df_raw.columns if 'rozdíl' in c.lower()), None)

    # --- FILTR A METRIKY ---
    hledat = st.text_input("Hledat", label_visibility="collapsed", placeholder="Hledat...")
    df_f = df_raw.copy()
    if hledat:
        df_f = df_f[df_f.apply(lambda r: hledat.lower() in r.astype(str).str.lower().values, axis=1)]

    m1, m2, m3, m4, m5 = st.columns(5)
    cn = next((c for c in money_cols if 'nabídka' in c.lower()), money_cols[0])
    
    m1.metric("CELKEM", f"{df_f[cn].astype(float).sum():,.2f}".replace(",", " ") + " Kč")
    m5.metric("ZAKÁZEK", len(df_f))

    # --- TABULKA NA 16 ŘÁDKŮ ---
    def style_row(row):
        styles = [''] * len(row)
        if col_stav:
            s = str(row[col_stav]).lower()
            if 'hotov' in s: styles = ['background-color: #f1fcf4'] * len(row)
            elif 'probíh' in s: styles = ['background-color: #fffdf2'] * len(row)
        if col_rozdil and "-" in str(row[col_rozdil]):
            styles[row.index.get_loc(col_rozdil)] += 'color: #d00000; font-weight: bold;'
        return styles

    for c in df_f.columns:
        if any(x in c.lower() for x in ['dne', 'ukončení']):
            df_f[c] = pd.to_datetime(df_f[c], errors='coerce').dt.strftime('%d.%m.%Y').replace('NaT', '')

    # Výška nastavena nízko, aby vynutila 16 řádků i při velkém rozlišení
    st.dataframe(
        df_f.style.apply(style_row, axis=1),
        use_container_width=True, 
        height=480, 
        hide_index=True
    )

    # --- INJEKCE JAVASCRIPTU PRO POSUVNÍK ---
    components.html("""
        <script>
        var style = window.parent.document.createElement('style');
        style.innerHTML = `
            div[data-testid="stDataTableVisualizer"] ::-webkit-scrollbar { 
                width: 35px !important; 
                height: 35px !important; 
                display: block !important;
            }
            div[data-testid="stDataTableVisualizer"] ::-webkit-scrollbar-thumb { 
                background: #888 !important; 
                border: 5px solid #f1f1f1 !important;
                display: block !important;
            }
            div[data-testid="stDataTableVisualizer"] ::-webkit-scrollbar-track { 
                background: #f1f1f1 !important; 
                display: block !important;
            }
        `;
        window.parent.document.head.appendChild(style);
        </script>
    """, height=0)

else:
    st.error("Data nenalezena.")
