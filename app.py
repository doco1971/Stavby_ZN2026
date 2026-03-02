import streamlit as st
import pandas as pd

# --- KONFIGURACE STRÁNKY ---
st.set_page_config(page_title="Evidence 2026", layout="wide")

# --- EXTRÉMNÍ CSS PRO POSUVNÍK A TABULKU ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    .block-container { padding-top: 1rem !important; }
    
    /* Kontejner pro tabulku s pevnou výškou a obřím posuvníkem */
    .table-container {
        height: 600px; /* Výška pro cca 16 řádků */
        overflow-y: scroll;
        overflow-x: auto;
        border: 1px solid #ccc;
    }

    /* Vlastní design posuvníku - Extrémně tlustý */
    .table-container::-webkit-scrollbar {
        width: 30px !important;
        height: 30px !important;
    }
    .table-container::-webkit-scrollbar-track {
        background: #f1f1f1 !important;
    }
    .table-container::-webkit-scrollbar-thumb {
        background: #888 !important;
        border: 5px solid #f1f1f1 !important;
    }
    .table-container::-webkit-scrollbar-thumb:hover {
        background: #555 !important;
    }

    /* Styl samotné HTML tabulky */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-family: sans-serif;
        font-size: 14px;
    }
    .custom-table th {
        position: sticky;
        top: 0;
        background: #f8f9fa;
        padding: 10px;
        border: 1px solid #dee2e6;
        z-index: 10;
    }
    .custom-table td {
        padding: 8px;
        border: 1px solid #dee2e6;
        white-space: nowrap;
    }
    .neg-value { color: #d00000; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- NAČTENÍ DAT ---
@st.cache_data(ttl=1)
def load_data():
    try:
        df = pd.read_excel('Soupis zakázek tabulka 2026_ZN.xlsx', skiprows=4, engine='openpyxl')
        df = df.dropna(how='all') # Smaže jen úplně prázdné řádky
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # Metriky (horní lišta)
    money_cols = [c for c in df.columns if any(x in c.lower() for x in ['nabídka', 'rozdíl', 'bez dph', 'vyfaktur', 'ps', 'snk', 'bo', 'poruchy'])]
    col_n = next((c for c in money_cols if 'nabídka' in c.lower()), money_cols[0])
    
    total_val = pd.to_numeric(df[col_n], errors='coerce').sum()
    
    c1, c2 = st.columns([1, 4])
    with c1: st.metric("CELKEM", f"{total_val:,.2f}".replace(",", " ") + " Kč")
    with c2: st.metric("ZAKÁZEK", len(df))

    # --- GENEROVÁNÍ HTML TABULKY ---
    # Záhlaví
    html = '<div class="table-container"><table class="custom-table"><thead><tr>'
    for col in df.columns:
        html += f'<th>{col}</th>'
    html += '</tr></thead><tbody>'

    # Data
    for _, row in df.iterrows():
        html += '<tr>'
        for col in df.columns:
            val = row[col]
            
            # Formátování čísel
            if col in money_cols:
                try:
                    num = float(val)
                    formatted = f"{num:.2f}"
                    # Červená pro záporný rozdíl
                    style = ' class="neg-value"' if 'rozdíl' in col.lower() and num < 0 else ''
                    html += f'<td{style}>{formatted}</td>'
                except:
                    html += f'<td>{val if pd.notna(val) else ""}</td>'
            
            # Datumy
            elif any(x in col.lower() for x in ['dne', 'ukončení']):
                try:
                    d = pd.to_datetime(val).strftime('%d.%m.%Y')
                    html += f'<td>{d}</td>'
                except:
                    html += f'<td>{val if pd.notna(val) else ""}</td>'
            
            else:
                html += f'<td>{val if pd.notna(val) else ""}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    
    # Vykreslení
    st.markdown(html, unsafe_allow_html=True)

else:
    st.error("Data nenalezena.")
