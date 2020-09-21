;===============
; LOADER V3
;===============
; Entradas:
; 	0xxx sa rr bb
; 	0xxx sa rr bbbb
; Legenda:
; 	0xxx : endr
;	s    : size
; 	a    : 2*ab (endr absoluto) + opab (operando absoluto)
;   rr   : 00 positivo, 11 negativo
;   bbbb : bytes a adicionar
;=================

;0 /0 /1 /2 /3 /4 /5 /6 /7 /8 /9 /a /b /c /d /e /f
; -------------------reserved--------------------
;1 /0 /1 /2 /3 /4 /5 /6 /7 /8 /9 /a /b /c /d /e /f
;  3x 
;2 /0 /1 /2 /3 /4 /5 /6 /7 /8 /9 /a /b /c /d /e /f
;

inicio  GD
    