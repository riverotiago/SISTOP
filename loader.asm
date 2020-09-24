;===============
; LOADER V3
;===============
; Entradas:
; 	00 0a 0xxx bb
; 	01 0a 0xxx bbbbbb
;   FF 0xxx
; Legenda:
;   t    : tipo (const 1byte, instru 3bytes, fim)
; 	0xxx : endr
; 	a    : 2*endr_rel + op_rel (relocabilidade)
;   bbbb : bytes a adicionar

;=================

;0 /0 /1 /2 /3 /4 /5 /6 /7 /8 /9 /a /b /c /d /e /f
; -------------------reserved--------------------
;1 /0 /1 /2 /3 /4 /5 /6 /7 /8 /9 /a /b /c /d /e /f
;  
;2 /0 /1 /2 /3 /4 /5 /6 /7 /8 /9 /a /b /c /d /e /f
;

        @$ 30
inicio  GD
        JN fim ; Detecta byte FF, fim do arquivo
        JZ const ; Trata constantes

; Trata instruçoes
        ; Armazena o endereço e o nibble de relocabilidade
const   GD    
        MM /0
        GD
        MM /1
        GD
        MM /2
        GD
        MM /3
        ; Escreve a instrução e reloca caso necessário
        SO /2 
        MM /0
        JP inicio

; Trata constante
        ; Armazena o endereço e o nibble de relocabilidade
const   GD    
        MM /0
        GD
        MM /1
        GD
        MM /2
        GD
        MM /3
        ; Escreve a constante e reloca caso necessário
        SO /1
        JP inicio

; Escreve o primeiro endereço válido
fim     LV /0
        MM /0
        GD
        MM /1
        GD
        MM /2
        HM

        
        
        


        
    
        

    