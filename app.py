# --- 5. OPRAVENÉ VÝPOČTY (Sčítání sloupců dle Kategorie I a II) ---
df_active = st.session_state.data[(st.session_state.data[0] > 0) | (st.session_state.data[9] != "")]

if hledat:
    df_active = df_active[df_active.apply(lambda r: hledat.lower() in str(list(r.values)).lower(), axis=1)]

c1_dur = c1_zmes = c2_dur = c2_zmes = 0.0

for _, r in df_active.iterrows():
    # Kategorie I = PS (sl.2) + SNK (sl.3) + BO (sl.4)
    sum1 = float(r[2] or 0) + float(r[3] or 0) + float(r[4] or 0)
    # Kategorie II = PS (sl.5) + BO (sl.6) + Poruch (sl.7)
    sum2 = float(r[5] or 0) + float(r[6] or 0) + float(r[7] or 0)
    
    firma = str(r[1]).strip().upper()
    
    # Přičtení k DUR nebo ZMES na základě sloupce 'firma'
    if "DUR" in firma:
        c1_dur += sum1
        c2_dur += sum2
    elif "ZMES" in firma:
        c1_zmes += sum1
        c2_zmes += sum2

# --- 6. ZOBRAZENÍ METRIK (S opravenými součty) ---
m = st.columns([1, 1.5, 1.5, 1, 0.8])

# Celková nabídka
m[0].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Celkem Nabídka</div><div class='metric-value'>{df_active[10].sum():,.2f} Kč</div></div>".replace(",", " "), unsafe_allow_html=True)

# Kategorie I: Box se součtem pro DUR a ZMES
m[1].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Kategorie I (DUR / ZMES)</div><div class='metric-value'>{c1_dur:,.2f} / {c1_zmes:,.2f}</div></div>".replace(",", " "), unsafe_allow_html=True)

# Kategorie II: Box se součtem pro DUR a ZMES
m[2].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Kategorie II (DUR / ZMES)</div><div class='metric-value'>{c2_dur:,.2f} / {c2_zmes:,.2f}</div></div>".replace(",", " "), unsafe_allow_html=True)

m[3].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Probíhá</div><div class='metric-value'>0.00 Kč</div></div>", unsafe_allow_html=True)
m[4].markdown(f"<div class='metric-box-styled'><div class='cat-header-main'>Zakázek</div><div class='metric-value'>{len(df_active[df_active[0]>0])}</div></div>", unsafe_allow_html=True)
