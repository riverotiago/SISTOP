;/////////////////////////////
;// Programa 2 
;// 

	@$ /200
	JP ini
ov1	PD
	OS /3 	; Chama monitor de overlay
	K /1 	; Ativar
	K /1 	; Overlay1
	RS

ov2	PD
	OS /3 	; Chama monitor de overlay
	K /1 	; Ativar
	K /2 	; Overlay2
	RS

ini     @$ /300
	; Printa 8
	LV 8	
	PD
	CP 8
	JPE safe 
	HM
safe    SC ov1
	SC ov2	
	# ini

	overlay 1
	@ /0
	<< 1
	PD
	OS /3	; Chama monitor de overlay
	K /0 	; Desativar
	K /1	; Overlay1
	endoverlay

	overlay 2
	@ /0
	>> 2
	PD
	OS /3	; Chama monitor de overlay
	K /0 	; Desativar
	K /2	; Overlay2
	endoverlay		
	