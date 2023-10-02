
from client.referee import RefereeCommands
from strategy.entity.automaticPlacement import AutomaticPlacement
import numpy as np 
from communication.serialWifi import SerialRadio

class AutomaticReplacer():
    def __init__(self, world):
        super().__init__()

        self.world = world
        self.radio = SerialRadio()

    def send(self, position):
        
        # Para parar todos os robos quando receber foul
        for robot in self.world.raw_team: robot.turnOff()

        # Pega pose e id do robo dada por position de manageReferee para enviar comandos depois
        robot_pose = []
        robot_id = []
        for i in range(0,len(position)):
            robot_id.append(position[i][0])
            robot_pose.append(position[i][1])

        #----------------------------------------------------------------------------------------
        # Aqui começamos a atualizar a entidade de todos os robos para posicionamento automatico
        # A ideia é a mesma feita em updateEntity do módulo strategy

        # OBS.: Todos serão com a mesma entidade mas o objetivo do campo será diferente para cada um,
        # como delimitado em manageReferee
        # Do jeito que está, não temos controle de qual robo especifico vai para o objetivo dele, mas
        # podemos melhorar de acordo com quem está mais próximo da posição ir para a posição desejada
        #TODO: Enviar posição desejada para robô que estiver mais próxima dela
        i = 0
        for robot in self.world.team:
            robot.entity = AutomaticPlacement(self.world, robot, robot_pose[i])
            i += 1

        # Para terminar de atualizar entidade precisamos delimitar seu campo e sua direção 
        for robot in self.world.team:
            robot.updateSpin()
            if robot.entity is not None:
                robot.entity.fieldDecider()
                robot.entity.directionDecider()
        
        #----------------------------------------------------------------------------------------
        # Aqui começamos a enviar os comandos para os robôs irem para a posição desejada

        # Pega pose de cada robô no time aliado
        # Estou usando rr para o código ficar menos verboso
        rr = []
        for robot in self.world.team:
            rr.append(np.array(robot.pose))
        
        # Cria variaveis boleanas para codigo ficar menos verboso no while True
        # Essas variaveis sao usadas para verificar se cada um dos 3 robos estão fora da posição desejada ou não
        # Na verdade não sabemos quem é o robo 0,1 ou 2. Foram nomes que dei para facilitar no desenvolvimento do 
        # código. Os ids dos robôs podem variar dependendo da camisa utilizada (considerando a vss-vision)
        isOutside_rr0 = np.abs(rr[0][0]) > np.abs(robot_pose[0][0]) or np.abs(rr[0][1]) > np.abs(robot_pose[0][1]) or np.abs(rr[0][2]) > np.abs(robot_pose[0][2])
        isOutside_rr1 = np.abs(rr[1][0]) > np.abs(robot_pose[1][0]) or np.abs(rr[1][1]) > np.abs(robot_pose[1][1]) or np.abs(rr[1][2]) > np.abs(robot_pose[1][2])
        isOutside_rr2 = np.abs(rr[2][0]) > np.abs(robot_pose[2][0]) or np.abs(rr[2][1]) > np.abs(robot_pose[2][1]) or np.abs(rr[2][2]) > np.abs(robot_pose[2][2])

        # Cria variaveis para robos para codigo ficar menos verboso no while True
        robot1 = self.world.team[robot_id[0]]
        robot2 = self.world.team[robot_id[1]]
        robot3 = self.world.team[robot_id[2]]
        
        for robot in self.world.raw_team: robot.turnOn()
        while True:
            # Inicializa vetor com v e w a serem enviados para robô
            control_output = []

            # Se todos os robôs chegaram na posição desejada
            if(not isOutside_rr0 and not isOutside_rr1 and not isOutside_rr2):
                for robot in self.world.raw_team: robot.turnOff()
                break
            
            # A partir daqui criamos o vetor com v e w de cada robo a ser enviado
            # para o modulo de comunicação do robo
            if(isOutside_rr0):
                control_output.append(robot1.entity.control.actuate(robot1))
            if( not isOutside_rr0):
                control_output.append((0,0))
            if(isOutside_rr1):
                control_output.append(robot2.entity.control.actuate(robot2))
            if(not isOutside_rr1):
                control_output.append((0,0))
            if(isOutside_rr2):
                control_output.append(robot3.entity.control.actuate(robot3))
            if(not isOutside_rr2):
                control_output.append((0,0))
            
            # Envia comando para robo
            self.radio.send(control_output)