;/////////////////////////////
;// Programa 2 
;// 

	@$ /200
	JP ini
ov1	PD
	OS /3 	; Chama monitor de overlay
	K /1 	; Ativar
	K /1 	; Overlay1
	RS ov1

ov2	PD
	OS /3 	; Chama monitor de overlay
	K /1 	; Ativar
	K /2 	; Overlay2
	RS ov2

    @$ /300
	; Printa 8
ini	LV 8	
	PD
	CP 8
	JPE firsttime
	HM ; Halt machine na terceira vez
firsttime SC ov1 ; Roda ov1 na primeira vez
	JP skip
secondtime SC ov2 ; Roda ov2 na segunda vez
skip PD
	# ini

	overlay 1
	@ /0
	LV /1
	PD
	OS /3	; Chama monitor de overlay
	K /0 	; Desativar
	K /1	; Overlay1
	JP /315 ; JP secondtime
	# /0
	endoverlay

	overlay 2
	@ /0
	LV /2
	PD
	OS /3	; Chama monitor de overlay
	K /0 	; Desativar
	K /2	; Overlay2
	JP /306 ; JP CP 8
	# /0
	endoverlay		
	