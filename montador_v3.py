
class Montador:
    def __init__(self):
        pass

    def tokenziar(self):
        """ Extrai label, instrução e operando de uma linha de código. """
        pass

    def primeiro_passo(self):
        """ Extrai as tabelas de símbolos, tabela de entry points,
            tabela de externals.
        """
        pass

    def segundo_passo(self):
        """ Cria uma fila de montagem. """
        pass

    def montagem_absoluta(self):
        """ Cria um arquivo .hex carregável pelo loader. """
        pass

    def montagem_relocavel(self):
        """ Cria um arquivo .robj carregável pelo linker. """
        pass

    def montagem_loader(self):
        """ Cria um arquivo .hex carregável pela MVN. """
        pass
