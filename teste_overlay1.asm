;/////////////////////////////
;// Programa 2 
;// 
;//

        @$ /100
ini     LV 100 ; Carrega val = 100 no acumulador 
loop    PD      ; Print
        CP /0   ; Checa se AC (val) == 0
        JPE fim ; Pula para o fim se for
        - 1     ; subtrai 1 de val
        JP loop
fim     HM      ; Encerra
        # ini 
