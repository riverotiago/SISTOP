class Evento:
    def __init__(self, motor_from, tipo, dados=None):
        self.motor_from = motor_from
        self.tipo = tipo
        self.dados = dados
    
    def setDados(self, dados):
        self.dados = dados

class MotorDeEventos:
    def __init__(self, name):
        #print(f"hey i'm {name}")
        self.name = name
        self.motores_ent = {}
        self.motores_ext = {}
        self.ent = []
        self.ext = []

    def addMotorEntrada(self,motor_from):
        """
        Adiciona um objeto MotorDeEventos, do qual receberemos objetos Eventos,
        como referência, no dicionário interno desta classe.
        """
        if not motor_from.name in self.motores_ent:
            self.motores_ent[motor_from.name] = motor_from

    def addMotorSaida(self,motor_to):
        """
        Adiciona um objeto MotorDeEventos, ao qual evniaremos objetos Eventos,
        como referência, no dicionário interno desta classe.
        """
        if not motor_to.name in self.motores_ext:
            self.motores_ext[motor_to.name] = motor_to

    def linkarMotor(self,motores_ent,motores_ext):
        """
        Rotina para linkar as entradas e saídas desta classe com a de outros
        objetos MotorDeEvento.
        """
        for motor in motores_ent:
            self.addMotorEntrada(motor)
            motor.addMotorSaida(self)

        for motor in motores_ext:
            self.addMotorSaida(motor)
            motor.addMotorEntrada(self)
        
        #print(self.name, self.motores_ent.keys(), self.motores_ext.keys())

    def addEntrada(self, evento):
        """ Adiciona um evento a lista de entrada. """
        self.ent.append(evento)
        
    def output(self, motor_to_name, evento):
        """ Faz o output de um Evento para a lista de entrada do MotorDeEventos identificado
        por motor_to_name. E força o motor ao qual enviamos o evento a executar ação.
        """
        self.motores_ext[motor_to_name].addEntrada(evento)
        #self.motores_ext[motor_to_name].run()

    def getNextEvento(self):
        """ Retira e retorna o próximo evento da queue. """
        if self.ent:
            return self.ent.pop()
        else:
            return None
        