# --- 4. HTML TABULKA ---
    html = '<div class="table-container"><table class="html-table">'
    
    # Definice šířek sloupců (první sloupec změněn na 35px)
    html += '<colgroup>'
    html += '<col style="width:35px">' # poř.č.
    html += '<col style="width:100px">' # firma
    html += '<col style="width:90px"><col style="width:90px"><col style="width:90px">' # Kat I
    html += '<col style="width:90px"><col style="width:90px"><col style="width:90px">' # Kat II
    html += '<col style="width:90px"><col style="width:250px"><col style="width:100px">' # stavba
    html += '<col style="width:100px"><col style="width:100px"><col style="width:80px">' # finance
    html += '<col style="width:80px"><col style="width:80px"><col style="width:80px">' # termíny
    html += '<col style="width:100px"><col style="width:100px"><col style="width:100px">' # lidé
    html += '<col style="width:100px"><col style="width:100px"><col style="width:100px">' # fakturace
    html += '</colgroup>'

    html += '<thead><tr><th rowspan="2">poř.č.</th><th rowspan="2">firma</th><th colspan="3">kategorie i</th><th colspan="3">kategorie ii</th><th rowspan="2">č.stavby</th><th rowspan="2">název stavby</th><th rowspan="2">nabídka</th><th rowspan="2">rozdíl</th><th rowspan="2">vyfaktur.</th><th rowspan="2">ukončení</th><th rowspan="2">zrealiz.</th><th rowspan="2">SOD</th><th rowspan="2">ze dne</th><th rowspan="2">objednatel</th><th rowspan="2">stavbyved.</th><th rowspan="2">nabídková c.</th><th rowspan="2">č.faktury</th><th rowspan="2">bez DPH</th><th rowspan="2">splatná</th></tr>'
    html += '<tr><th>PS</th><th>SNK</th><th>BO</th><th>PS</th><th>BO</th><th>poruch</th></tr></thead><tbody>'

    for _, row in df.iterrows():
        html += '<tr>'
        for i in range(23):
            val = row[i]
            td_cls = ""
            
            # PŘIDÁNO: Zarovnání doprava pro index 0 (poř.č.) a číselné sloupce
            if i == 0 or i in [2,3,4,5,6,7,10,11,12,19,21]:
                td_cls = ' class="num-align"'
                try:
                    # Pokud je to číslo (kromě prvního sloupce), formátujeme na tisíce
                    if i != 0:
                        n = float(val)
                        val = f"{n:,.2f}".replace(",", " ") if n != 0 else ""
                        if i == 11 and n < 0: td_cls = ' class="red-bold"'
                except:
                    if i != 0: val = ""
            
            elif i in [13, 14, 16, 22]:
                try: val = pd.to_datetime(val).strftime('%d.%m.%Y')
                except: val = ""
                
            html += f'<td{td_cls}>{val}</td>'
        html += '</tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)
