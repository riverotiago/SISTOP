import re
class TabelaTransicaoTratamento():
    def __init__(self, regras):
        self.pattern = "\A\s*>?(\d+)>?{(.*)}"
        self.tokens = {
            "e":"especial",
            "n":"numero",
            "p":"palavrachave",
            "i":"identificador"
        }
        self.rules = {}
        self.ini = 1
        self.parseRules(regras)
    
    def add(self, expression):
        #print(expression)
        """ Adiciona as regras descritas em expression na tabela. """
        if not expression.strip():
            return
        # Permite o uso de ; como string
        expression = expression.replace(":;",":'")
        
        # Extrai o estado de saída, e o conjunto de regras de transição
        exp_search = re.search(self.pattern, expression)
        stateFrom = int(exp_search.group(1))
        forwarding = exp_search.group(2).split(";")

        if expression.strip()[0] == ">":
            self.ini = stateFrom

        if not stateFrom in self.rules: # Adiciona se não houver
            self.rules[stateFrom] = {}

        for item in forwarding:
            # Extrai cada regra do conjunto
            temp = item.split(" ")

            condition, nextState, tratamento = None, None, None

            if len(temp) == 3:
                condition, nextState, tratamento = temp
            else:
                condition, nextState = temp

            abr_token, string = condition.split(":",1)
            string = string.replace("'",";")
            token = self.tokens[abr_token]
            nextState = int(nextState)

            if not nextState in self.rules: # Adiciona se não houver
                self.rules[nextState] = {}
            
            # Adiciona regra à tabela
            key = f"{token}:{string}"
            self.rules[stateFrom][key] = nextState, tratamento

    def parseRules(self,regras):
        """Extrai de uma string, uma expressão de regra por linha."""
        for exp in regras.split("\n"):
            self.add(exp)

    def transicao(self, entrada, token, string):
        """Computa a transição dado um estado de entrada, o tipo do token, e a string do token."""
        key = f"{token}:{string}"
        key1 = f"{token}:%"
        nextState = None
        tratamento = None
        
        if key in self.rules[entrada]:
            nextState, tratamento = self.rules[entrada][key]
        elif key1 in self.rules[entrada]:
            nextState, tratamento = self.rules[entrada][key1]
        elif token == "especial" and string == ";":
            nextState = self.ini 
            tratamento = "func_next"

        if not self.rules[entrada]:
            return None, None

        return nextState, tratamento



