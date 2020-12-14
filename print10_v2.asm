
;/////////////////////////////
;// Programa 1
;// Printar os números de 10 a 0

        segmento 1
        @$ /100
ini     LV 10 ; Carrega val = 10 no acumulador 
loop    PD      ; Print
        CP /0   ; Checa se AC (val) == 0
        JPE fim ; Pula para o fim se for
        - one     ; subtrai 1 de val
        JP loop
fim     HM      ; Encerra
        # ini
        segmentoend

        segmento 2
        @$ /200
one     K /1
        # /200
        segmentoend

