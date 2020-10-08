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

        @$ /10
inicio  GD
        JN fim ; Detecta byte FF, fim do arquivo
        JZ const ; Trata constantes

; Trata instruçoes
        ; Escreve a instrução e reloca caso necessário
        OS /2 
        JP inicio

; Trata constante
        ; Escreve a constante e reloca caso necessário
const   OS /1
        JP inicio

; Guarda os ponteiros para inicio e final do bloco
fim     OS /3
        K /2
        K /0
        # inicio

        
        
        


        
    
        

    