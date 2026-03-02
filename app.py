if st.session_state.role == "supervisor":
    with st.expander("➕ ZADAT NOVOU STAVBU / ZAKÁZKU"):
        with st.form("nova_stavba_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.subheader("Základní údaje")
                f_firma = st.selectbox("Firma", ["DUR plus", "ZMES", "Ostatní"])
                f_cislo = st.text_input("Číslo stavby")
                f_nazev = st.text_area("Název stavby")
            
            with c2:
                st.subheader("Kategorie I & II")
                f_k1_ps = st.number_input("Kat I - PS", value=0.0)
                f_k1_snk = st.number_input("Kat I - SNK", value=0.0)
                f_k1_bo = st.number_input("Kat I - BO", value=0.0)
                st.divider()
                f_k2_ps = st.number_input("Kat II - PS", value=0.0)
                f_k2_bo = st.number_input("Kat II - BO", value=0.0)
                f_k2_por = st.number_input("Kat II - Poruchy", value=0.0)

            with c3:
                st.subheader("Ostatní & Termíny")
                f_nabidka = st.number_input("Nabídka celkem", value=0.0)
                f_objednatel = st.text_input("Objednatel")
                f_stavbyved = st.text_input("Stavbyvedoucí")
                f_ukončení = st.date_input("Termín ukončení", value=None)
            
            submit = st.form_submit_button("✅ ULOŽIT NOVOU ZAKÁZKU")
            
            if submit:
                # Tady se vytvoří nový řádek
                new_row = {
                    "Poř.č.": len(df_active) + 1,
                    "Firma": f_firma,
                    "K1_PS": f_k1_ps, "K1_SNK": f_k1_snk, "K1_BO": f_k1_bo,
                    "K2_PS": f_k2_ps, "K2_BO": f_k2_bo, "K2_Poruch": f_k2_por,
                    "Č.stavby": f_cislo, "Název": f_nazev, "Nabídka": f_nabidka,
                    "Rozdíl": -f_nabidka, # Automatický výpočet rozdílu
                    "Vyfaktur.": 0.0,
                    "Objednatel": f_objednatel,
                    "Stavbyved.": f_stavbyved
                }
                # Přidání do tabulky (zatím v paměti)
                st.success(f"Stavba '{f_nazev}' byla přidána do seznamu!")
