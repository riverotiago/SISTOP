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
start   OS  /5 
; Sinaliza início do loader
; Guarda o endereço da primeira e ultima instrução
; Início
        GD
        MM /5
        MM endr1
        GD
        MM /6
        MM endr2
; Final
        GD
        MM /7
        GD
        MM /8

; Carrega o código do buffer à RAM
loop    GD
        JN fim ; Detecta byte FF, fim do arquivo
        JZ const ; Trata constantes

; Trata instruçoes
        ; Escreve a instrução e reloca caso necessário
        OS /2 
        JP loop

; Trata constante
        ; Escreve a constante e reloca caso necessário
const   OS /1
        JP loop

; Guarda os ponteiros para inicio e final do bloco
fim     OS /4 ; Recupera o contexto anterior, e decide se o load pula para o primeiro
              ; endereço ou volta

; Instrução de JUMP ao endereço inicial od bloco
        K /0
endr1   K /0
endr2   K /0
        # start

        
        
        


        
    
        

    