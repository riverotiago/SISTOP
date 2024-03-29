;////////////////
;// P3

;------ P3
    segmento 0
    @$ /100
ini SC B3
    HM
    segmentoend

;------ B1
    segmento 1
B1  PD
    LV /1 
    PD    ; Indica que entrou no B1
    OS /0 ; 2 operações de entrada/saída
    OS /0
    + /F ; 5 unidades de tempo de processamento
    + /F
    + /F
    + /F
    + /F
    OS /0 ; 1 op. de entrada/saída
    RS B1
    segmentoend

;------ B2
    segmento 2
B2  PD
    LV /2 
    PD    ; Indica que entrou no B2
    SC B1 ; Ativa B1
    + /F ; 4 unidades de tempo de processamento
    + /F
    + /F
    + /F
    OS /0 ; 2 operações de entrada/saída
    OS /0
    SC B1 ; Ativa B1
    + /F ; 4 unidades de tempo de processamento
    + /F
    + /F
    + /F
    OS /0 ; 2 operações de entrada/saída
    OS /0
    SC B1 ; Ativa B1
    + /F ; 4 unidades de tempo de processamento
    + /F
    + /F
    + /F
    OS /0 ; 2 operações de entrada/saída
    OS /0
    RS B2
    segmentoend

;------ B3
    segmento 3
B3  PD
    LV /3 
    PD    ; Indica que entrou no B3
    + /F ; 3 unidades de tempo de processamento
    + /F
    + /F
    + /F ; 2 unidades de tempo de processamento
    + /F
    SC B1
    + /F ; 3 unidades de tempo de processamento
    + /F
    + /F
    SC B2
    + /F ; 3 unidades de tempo de processamento
    + /F
    + /F
    SC B2
    RS B3
    segmentoend
    # ini