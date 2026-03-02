# --- 4. HTML TABULKA (OPTIMALIZOVANÉ ŠÍŘKY PRO VELKÁ ČÍSLA) ---
    html = '<div class="table-container"><table class="html-table">'
    
    # Definice šířek sloupců pro zajištění místa pro formát -00 000 000.00
    html += '<colgroup>'
    html += '<col style="width:35px">'  # poř.č.
    html += '<col style="width:90px">'  # firma
    # Kategorie I (index 2,3,4) - zvětšeno na 110px
    html += '<col style="width:110px"><col style="width:110px"><col style="width:110px">' 
    # Kategorie II (index 5,6,7) - zvětšeno na 110px
    html += '<col style="width:110px"><col style="width:110px"><col style="width:110px">' 
    html += '<col style="width:90px">'  # č.stavby
    html += '<col style="width:250px">' # název stavby (ponecháno široké)
    # Finance (index 10,11,12) - nabídka, rozdíl, vyfaktur. - zvětšeno na 110px
    html += '<col style="width:110px"><col style="width:110px"><col style="width:110px">' 
    html += '<col style="width:80px"><col style="width:80px"><col style="width:80px"><col style="width:80px">' # termíny
    html += '<col style="width:100px"><col style="width:100px">' # objednatel, stavbyved.
    # Nabídková c., č.faktury, bez DPH, splatná (index 19,20,21,22)
    html += '<col style="width:110px"><col style="width:100px"><col style="width:110px"><col style="width:100px">' 
    html += '</colgroup>'
