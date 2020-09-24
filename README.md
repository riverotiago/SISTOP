# PCS3446 - Sistemas Operacionais
Criando um sistema operacional.

## MONTADOR
O montador faz montagens absoluta e relocável e é compatível com a técnica de overlays.

Instruções:

Jump, Jump if zero, Jump if negative, Load value (direct), Add, Substract, Multiply, Divide, Load data (indirect)
Memory Modify, Subroutine Call, Return Subroutine, Halt Machine, Get Data, Print Data, Operational System call,
Shift Right, Shift Left, Bitwise AND, Compare, Jump if equal, Jump if not equal.

Montagem em dois passos.

## MVN
O simulador de MVN tem memória RAM de 4kb.

## SISTEMA OPERACIONAL

## Loader relocável
Um dos bytes de metadado de cada instrução lida pelo loader indica se o endereço e operando são
relocáveis, isso é controlado pelo sistema operacional.

## Monitor de Overlay
Durante a execução do código, o carregamento de overlays podem ser chamados, e o monitor de overlay
controla a posição de escrita dos overlays, se utilizando do loader relocável.

