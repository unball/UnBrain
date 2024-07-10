from classes.construction.blocks import Block
import pygame as pg
from pygame import Vector2, Rect
from classes.construction.blocks import *
from color_constants import *
import threading
import sys
import os
dir_atual = os.path.dirname(os.path.abspath(__file__))
dir_src = os.path.abspath(os.path.join(dir_atual, "../../.."))
sys.path.append(dir_src)
from loop import Loop
import loop

class GUI:
    """General class for the graphic interface"""
    def __init__(self) -> None:
        # Initialize the pygame application
        pg.init()

        self.unbrain_loop = None

        # Create a window 
        windowSize = Vector2(1366,768)
        window = pg.display.set_mode((int(windowSize.x), int(windowSize.y)), flags=pg.NOFRAME)
        window.fill(BACKGROUND_COLOR)

        # Create navigation screen
        self.navigationScreen = Screen()
        self.navigationScreen.setWindow(window)
        self.navigationScreen.setCaption("IGGLU")
        self.navigationScreen.setIcon("images/Logo_ice.png")

        # sets the active screen as the navigationScreen
        self.activeScreen = self.navigationScreen

       # Create blocks on the navigation screen  
        menuBar = MenuBar("menuBar", windowSize.x+8, 68, -4, -4, BACKGROUND_MENU_COLOR, window, self, border=True)
        self.navigationScreen.setMenuBar(menuBar)


        screenDivisionLeft = Block("screenDivisionLeft", windowSize.x/2, windowSize.y, 0, 60, BORDER_COLOR, window, self, preference=False)
        self.navigationScreen.addBlock(screenDivisionLeft)

        screenDivisionLeftMargin = Block("screenDivisionLeftMargin", windowSize.x/2-3, windowSize.y, 0, 63, BACKGROUND_COLOR, window, self, preference=False)
        self.navigationScreen.addBlock(screenDivisionLeftMargin)

        screenDivisionRight = Block("screenDivisionRight", windowSize.x/2, windowSize.y, windowSize.x/2, 60, BORDER_COLOR, window, self, preference=False)
        self.navigationScreen.addBlock(screenDivisionRight)

        screenDivisionRightMargin = Block("screenDivisionRightMargin", windowSize.x/2-3, windowSize.y, windowSize.x/2, 63, BACKGROUND_COLOR, window, self, preference=False)
        self.navigationScreen.addBlock(screenDivisionRightMargin)


        playButton = Button("playButton", 30, 30, 20, 13, BACKGROUND_COLOR, window, self, border=False)
        playButton.setImage("images/play_button.png")
        self.navigationScreen.menuBar.addButton(playButton)

        pauseButton = Button("pauseButton", 30, 30, playButton.pos.x + 50, playButton.pos.y, BACKGROUND_COLOR, window, self, border=False)
        pauseButton.setImage("images/pause_button.png")
        self.navigationScreen.menuBar.addButton(pauseButton)

        stopButton = Button("stopButton", 30, 30, pauseButton.pos.x + 50, playButton.pos.y, BACKGROUND_COLOR, window, self, border=False)
        stopButton.setImage("images/stop_button.png")
        self.navigationScreen.menuBar.addButton(stopButton)

        recordButton = Button("recordButton", 30, 30, stopButton.pos.x + 50, playButton.pos.y, BACKGROUND_COLOR, window, self, border=False)
        recordButton.setImage("images/record_button.png")
        self.navigationScreen.menuBar.addButton(recordButton)

        configButton = Button("configButton", 30, 30, recordButton.pos.x + 50, playButton.pos.y, BACKGROUND_COLOR, window, self, border=False)
        configButton.setImage("images/config_button.png")
        self.navigationScreen.menuBar.addButton(configButton)

        navegacaoButton = Button("navegacaoButton", 160, 40, configButton.pos.x + 130, playButton.pos.y -3, BORDER_COLOR, window, self)
        navegacaoButton.setText("Navegação", GRAY_LABEL, 27, center=True)
        self.navigationScreen.menuBar.addButton(navegacaoButton)

        movimentacaoButton = Button("movimentacaoButton", navegacaoButton.size.x, navegacaoButton.size.y, navegacaoButton.pos.x + navegacaoButton.size.x-2, navegacaoButton.pos.y, BACKGROUND_COLOR, window, self)
        movimentacaoButton.setText("Movimentação", GRAY_LABEL, 27, center=True)
        self.navigationScreen.menuBar.addButton(movimentacaoButton)

        comunicacaoButton = Button("comunicacaoButton", movimentacaoButton.size.x, movimentacaoButton.size.y, movimentacaoButton.pos.x + movimentacaoButton.size.x-2, movimentacaoButton.pos.y, BACKGROUND_COLOR, window, self)
        comunicacaoButton.setText("Comunicação", GRAY_LABEL, 27, center=True)
        self.navigationScreen.menuBar.addButton(comunicacaoButton)

        vsssButton = Button("vsssButton", navegacaoButton.size.x-70, 30, comunicacaoButton.pos.x + comunicacaoButton.size.x + 90, comunicacaoButton.pos.y + 5, BORDER_COLOR, window, self)
        vsssButton.setText("VSSS", GRAY_LABEL, center=True)
        self.navigationScreen.menuBar.addButton(vsssButton)

        sslButton = Button("sslButton", vsssButton.size.x, vsssButton.size.y, vsssButton.pos.x + vsssButton.size.x-2, vsssButton.pos.y, BACKGROUND_COLOR, window, self)
        sslButton.setText("SSL", GRAY_LABEL, center=True)
        self.navigationScreen.menuBar.addButton(sslButton)

        minimizeButton = Button("minimizeButton", configButton.size.x+7, configButton.size.y+7, sslButton.pos.x + sslButton.size.x + 90, configButton.pos.y, BACKGROUND_COLOR, window, self)
        minimizeButton.setImage("images/minimize_button.png")
        self.navigationScreen.menuBar.addButton(minimizeButton)

        maximizeButton = Button("maximizeButton", minimizeButton.size.x, minimizeButton.size.y, minimizeButton.pos.x + minimizeButton.size.x + 20, minimizeButton.pos.y, BACKGROUND_COLOR, window, self)
        maximizeButton.setImage("images/save_button.png")
        self.navigationScreen.menuBar.addButton(maximizeButton)

        closeButton = Button("closeButton", minimizeButton.size.x, minimizeButton.size.y, maximizeButton.pos.x + maximizeButton.size.x + 20, maximizeButton.pos.y, BACKGROUND_COLOR, window, self)
        closeButton.setImage("images/close_button.png")
        self.navigationScreen.menuBar.addButton(closeButton)


        gameMiniMap = Block("gameMiniMap", windowSize.x/2-30, windowSize.y/3+100, 15, 80, BLACK, window, self)
        self.navigationScreen.addBlock(gameMiniMap)

        arrow = Block("arrow", windowSize.x*0.25, 30, 168, windowSize.y/3+192, BACKGROUND_COLOR, window, self)
        arrow.setImage("images/arrow.png")
        self.navigationScreen.addBlock(arrow)

        lblLadoEsquerdo = Block("lblLadoEsquerdo", 110, 30, 35, windowSize.y/3+186, BACKGROUND_COLOR, window, self)
        lblLadoEsquerdo.setText("Lado aliado", LIGHT_GRAY_LABEL, center=False)
        self.navigationScreen.addBlock(lblLadoEsquerdo)

        lblLadoDireito = Block("lblLadoDireito", 110, 30, 165 + windowSize.x*0.25 + 20, lblLadoEsquerdo.pos.y, BACKGROUND_COLOR, window, self)
        lblLadoDireito.setText("Lado inimigo", LIGHT_GRAY_LABEL, center=False)
        self.navigationScreen.addBlock(lblLadoDireito)

        lblInfoBola = Block("lblInfoBola", 200, 30, gameMiniMap.pos.x+4, gameMiniMap.pos.y+gameMiniMap.size.y+60, BACKGROUND_COLOR, window, self)
        lblInfoBola.setText("Informações sobre a bola", BLACK_LABEL, 26, center=False)
        self.navigationScreen.addBlock(lblInfoBola)

        boxInfoBola = Block("boxInfoBola", gameMiniMap.size.x, gameMiniMap.size.y*0.6, gameMiniMap.pos.x, lblInfoBola.pos.y+40, BACKGROUND_COLOR, window, self, border=True)
        self.navigationScreen.addBlock(boxInfoBola)

        lblPosicao = Block("lblPosicao", 80, 30, boxInfoBola.pos.x + 20, boxInfoBola.pos.y + 20, BACKGROUND_COLOR, window, self)
        lblPosicao.setText("Posição", GRAY_LABEL, center=False)
        self.navigationScreen.addBlock(lblPosicao)

        boxPosicao = Block("boxPosicao", 180, lblPosicao.size.y + 10, lblPosicao.pos.x, lblPosicao.pos.y + lblPosicao.size.y, BACKGROUND_COLOR, window, self, border=True)
        boxPosicao.setText("x: 0.045m   y: 1.674m", LIGHT_GRAY_LABEL, center=True)
        self.navigationScreen.addBlock(boxPosicao)

        lblAceleracao = Block("lblAceleracao", lblPosicao.size.x, lblPosicao.size.y, lblPosicao.pos.x, boxPosicao.pos.y + boxPosicao.size.y + 25, BACKGROUND_COLOR, window, self)
        lblAceleracao.setText("Aceleração", GRAY_LABEL, center=False)
        self.navigationScreen.addBlock(lblAceleracao)

        boxAceleracao = Block("boxAceleracao", boxPosicao.size.x, boxPosicao.size.y, lblAceleracao.pos.x, lblAceleracao.pos.y + lblAceleracao.size.y, BACKGROUND_COLOR, window, self, border=True)
        boxAceleracao.setText("3 m/s\u00B2", LIGHT_GRAY_LABEL, center=True)
        self.navigationScreen.addBlock(boxAceleracao)

        lblVelocidade = Block("lblVelocidade", lblPosicao.size.x, lblPosicao.size.y, boxInfoBola.size.x/2 + 80, lblPosicao.pos.y, BACKGROUND_COLOR, window, self)
        lblVelocidade.setText("Velocidade", GRAY_LABEL, center=False)
        self.navigationScreen.addBlock(lblVelocidade)

        boxVelocidade = Block("boxVelocidade", boxAceleracao.size.x, boxAceleracao.size.y, lblVelocidade.pos.x, lblVelocidade.pos.y + lblVelocidade.size.y, BACKGROUND_COLOR, window, self, border=True)
        boxVelocidade.setText("3 m/s", LIGHT_GRAY_LABEL, center=True)
        self.navigationScreen.addBlock(boxVelocidade)

        navigationScrollPanel = ScrollingBackground("navigationScrollPanel", screenDivisionRightMargin.size.x, int(screenDivisionRightMargin.size.y*1.6), screenDivisionRightMargin.pos.x, screenDivisionRightMargin.pos.y, BACKGROUND_COLOR, window, self, screenDivisionRightMargin.size.y,  screenDivisionRightMargin.pos.y)

        self.navigationScreen.addScrollingBackground(navigationScrollPanel)

        # blocks of navigationScrollPanel
        lblCorTime = Block("lblCorTime", lblInfoBola.size.x-40, lblInfoBola.size.y, navigationScrollPanel.pos.x+30, navigationScrollPanel.pos.y+30, BACKGROUND_COLOR, window, self)
        lblCorTime.setText("Cor do time", BLACK_LABEL, 28, center=False)
        navigationScrollPanel.addBlock(lblCorTime)

        lblSelecionaCorTime = Block("lblSelecionaCorTime", lblCorTime.size.x, lblCorTime.size.y, lblCorTime.pos.x + 30, lblCorTime.pos.y+lblCorTime.size.y-5, BACKGROUND_COLOR, window, self)
        lblSelecionaCorTime.setText("Seleciona a cor do time", center=False)
        navigationScrollPanel.addBlock(lblSelecionaCorTime)

        lblInversaoCampo = Block("lblInversaoCampo", lblCorTime.size.x+75, lblCorTime.size.y, lblCorTime.pos.x, lblSelecionaCorTime.pos.y+lblCorTime.size.y*2, BACKGROUND_COLOR, window, self)
        navigationScrollPanel.addBlock(lblInversaoCampo)
        lblInversaoCampo.setText("Inversão de campo", BLACK_LABEL, 28, center=False)

        lblInverteCampoAliado = Block("lblInverteCampoAliado", lblSelecionaCorTime.size.x, lblSelecionaCorTime.size.y, lblSelecionaCorTime.pos.x, lblInversaoCampo.pos.y+lblInversaoCampo.size.y-5, BACKGROUND_COLOR, window, self)
        lblInverteCampoAliado.setText("Inverte o lado do campo aliado", center=False)
        navigationScrollPanel.addBlock(lblInverteCampoAliado)

        inversaoToggleButton = ToggleButton("inversaoToggleButton", 70, 50, lblCorTime.pos.x + 400, lblInversaoCampo.pos.y, BACKGROUND_COLOR, window, self, border=True)
        inversaoToggleButton.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        navigationScrollPanel.addButton(inversaoToggleButton)

        chooseColorComboBox = ComboBox("chooseColorComboBox", lblCorTime.size.x-30, lblCorTime.size.y, lblCorTime.pos.x + 400, lblCorTime.pos.y+lblCorTime.size.y/2, WHITE, window, self, "Azul", BACKGROUND_COLOR)
        navigationScrollPanel.addButton(chooseColorComboBox)
        chooseColorComboBox.addOptions(["Azul", "Amarelo"])

        lblDireitoOuEsquerdo = Block("lblDireitoOuEsquerdo", lblCorTime.size.x-50, lblCorTime.size.y, inversaoToggleButton.pos.x+inversaoToggleButton.size.x+15, inversaoToggleButton.pos.y+12, BACKGROUND_COLOR, window, self)
        lblDireitoOuEsquerdo.setText("Esquerdo", center=False)
        navigationScrollPanel.addBlock(lblDireitoOuEsquerdo)

        lblFormacaoEntidades = Block("lblFormacaoEntidades", lblInversaoCampo.size.x, lblInversaoCampo.size.y, lblInversaoCampo.pos.x, lblInverteCampoAliado.pos.y+lblInversaoCampo.size.y*2, BACKGROUND_COLOR, window, self)
        lblFormacaoEntidades.setText("Formação das entidades", BLACK_LABEL, 28, center=False)
        navigationScrollPanel.addBlock(lblFormacaoEntidades)

        lblSelecioneTipoFormacao = Block("lblSelecioneTipoFormacao", lblInverteCampoAliado.size.x+5, lblInverteCampoAliado.size.y, lblInverteCampoAliado.pos.x, lblFormacaoEntidades.pos.y+lblFormacaoEntidades.size.y/2+10, BACKGROUND_COLOR, window, self)
        lblSelecioneTipoFormacao.setText("Selecione o tipo de formação", center=False)
        navigationScrollPanel.addBlock(lblSelecioneTipoFormacao)

        lblNumRobots = Block("lblNumRobots", lblInversaoCampo.size.x, lblInversaoCampo.size.y, lblInversaoCampo.pos.x, lblSelecioneTipoFormacao.pos.y+lblInversaoCampo.size.y*2, BACKGROUND_COLOR, window, self)
        lblNumRobots.setText("Número de robôs", BLACK_LABEL, 28, center=False)
        navigationScrollPanel.addBlock(lblNumRobots)

        lblSelecioneNumRobos = Block("lblSelecioneNumRobos", lblInverteCampoAliado.size.x+5, lblInverteCampoAliado.size.y, lblInverteCampoAliado.pos.x, lblNumRobots.pos.y+lblNumRobots.size.y/2+10, BACKGROUND_COLOR, window, self)
        lblSelecioneNumRobos.setText("Selecione o número de robôs e seus IDs", center=False)
        navigationScrollPanel.addBlock(lblSelecioneNumRobos)

        lblConfigRobos = Block("lblConfigRobos", lblNumRobots.size.x, lblNumRobots.size.y, lblNumRobots.pos.x, lblSelecioneNumRobos.pos.y+lblNumRobots.size.y*2, BACKGROUND_COLOR, window, self)
        lblConfigRobos.setText("Configuração dos robôs", BLACK_LABEL, 28, center=False)
        navigationScrollPanel.addBlock(lblConfigRobos)

        boxConfigRobos = Block("boxConfigRobos", screenDivisionRightMargin.size.x-60, 250, lblConfigRobos.pos.x, lblConfigRobos.pos.y+lblConfigRobos.size.y+5, BACKGROUND_COLOR, window, self, border=True)
        navigationScrollPanel.addBlock(boxConfigRobos)

        robotIDComboBox = ComboBox("robotIDComboBox", lblFormacaoEntidades.size.x, chooseColorComboBox.size.y, boxConfigRobos.pos.x+boxConfigRobos.size.x/2-lblFormacaoEntidades.size.x/2, boxConfigRobos.pos.y+10, WHITE, window, self, "Robô ID")
        navigationScrollPanel.addButton(robotIDComboBox)
        robotIDComboBox.addOptions(["Robô 00", "Robô 01", "Robô 02"])

        chooseNumRobotsComboBox = ComboBox("chooseNumRobotsComboBox", chooseColorComboBox.size.x, chooseColorComboBox.size.y, chooseColorComboBox.pos.x, lblNumRobots.pos.y+lblFormacaoEntidades.size.y/2-5, WHITE, window, self, "0, 1, 2", BACKGROUND_COLOR)
        navigationScrollPanel.addButton(chooseNumRobotsComboBox)
        chooseNumRobotsComboBox.addOptions(["0", "1", "2", "0, 1", "0, 2", "1, 2", "0, 1, 2"])

        chooseEntityTypeComboBox = ComboBox("chooseEntityTypeComboBox", lblFormacaoEntidades.size.x, chooseColorComboBox.size.y, lblFormacaoEntidades.pos.x+lblFormacaoEntidades.size.x+90, lblFormacaoEntidades.pos.y+lblFormacaoEntidades.size.y/2-5, WHITE, window, self, "Entidades dinâmicas", BACKGROUND_COLOR)
        navigationScrollPanel.addButton(chooseEntityTypeComboBox)
        chooseEntityTypeComboBox.addOptions(["Entidades dinâmicas", "Entidades estáticas", "Control Tester"])
        
        lblBateria = Block("lblBateria", lblDireitoOuEsquerdo.size.x-50, lblDireitoOuEsquerdo.size.y, boxConfigRobos.pos.x+40, robotIDComboBox.pos.y+robotIDComboBox.size.y+25, BACKGROUND_COLOR, window, self)
        lblBateria.setText("Bateria:", BLACK_LABEL, center=False)
        navigationScrollPanel.addBlock(lblBateria)

        percentBattery = Block("percentBattery", lblBateria.size.x, lblBateria.size.y, lblBateria.pos.x+lblBateria.size.x+5, lblBateria.pos.y, BACKGROUND_COLOR, window, self)
        percentBattery.setText("100%", center=False)
        navigationScrollPanel.addBlock(percentBattery)

        cor1Robot = Block("cor1Robot", lblBateria.size.x*2, lblBateria.size.x, lblBateria.pos.x, lblBateria.pos.y+lblBateria.size.y+5, RED, window, self)
        navigationScrollPanel.addBlock(cor1Robot)

        cor2Robot = Block("cor2Robot", cor1Robot.size.x, cor1Robot.size.y, cor1Robot.pos.x, cor1Robot.pos.y+cor1Robot.size.y, LIGHT_BLUE, window, self)
        navigationScrollPanel.addBlock(cor2Robot)

        lblPosicaoConfig = Block("lblPosicaoConfig", lblBateria.size.x, lblBateria.size.y, cor1Robot.pos.x+cor1Robot.size.x+60, cor1Robot.pos.y-5, BACKGROUND_COLOR, window, self)
        lblPosicaoConfig.setText("Posição", BLACK_LABEL, center=False)
        navigationScrollPanel.addBlock(lblPosicaoConfig)

        boxPosicaoConfig = Block("boxPosicaoConfig", lblPosicaoConfig.size.x*3, lblPosicaoConfig.size.y, lblPosicaoConfig.pos.x+lblPosicaoConfig.size.x, lblPosicaoConfig.pos.y, BACKGROUND_COLOR, window, self)
        boxPosicaoConfig.setText("x: 0.0m   y: 0.0m", center=True)
        navigationScrollPanel.addBlock(boxPosicaoConfig)

        lblOrientacaoConfig = Block("lblOrientacaoConfig", lblPosicaoConfig.size.x+26, lblPosicaoConfig.size.y, lblPosicaoConfig.pos.x, lblPosicaoConfig.pos.y+lblPosicaoConfig.size.y+5, BACKGROUND_COLOR, window, self)
        lblOrientacaoConfig.setText("Orientação", BLACK_LABEL, center=False)
        navigationScrollPanel.addBlock(lblOrientacaoConfig)

        boxOrientacaoConfig = Block("boxOrientacaoConfig", boxPosicaoConfig.size.x-30, boxPosicaoConfig.size.y, lblOrientacaoConfig.pos.x+lblOrientacaoConfig.size.x, lblOrientacaoConfig.pos.y, BACKGROUND_COLOR, window, self)
        boxOrientacaoConfig.setText("th: 0.0 graus", center=True)
        navigationScrollPanel.addBlock(boxOrientacaoConfig)

        lblVelocidadeConfig = Block("lblVelocidadeConfig", lblOrientacaoConfig.size.x+5, lblOrientacaoConfig.size.y, lblOrientacaoConfig.pos.x, lblOrientacaoConfig.pos.y+lblOrientacaoConfig.size.y+5, BACKGROUND_COLOR, window, self)
        lblVelocidadeConfig.setText("Velocidade", BLACK_LABEL, center=False)
        navigationScrollPanel.addBlock(lblVelocidadeConfig)

        boxVelocidadeConfig = Block("boxVelocidadeConfig", boxPosicaoConfig.size.x+30, boxOrientacaoConfig.size.y, lblVelocidadeConfig.pos.x+lblVelocidadeConfig.size.x, lblVelocidadeConfig.pos.y, BACKGROUND_COLOR, window, self)
        boxVelocidadeConfig.setText("v: 0.0m/s   w: 0.0rad/s", center=True)
        navigationScrollPanel.addBlock(boxVelocidadeConfig)

        lblPosicionamento = Block("lblPosicionamento", lblInversaoCampo.size.x-15, lblInversaoCampo.size.y, lblInversaoCampo.pos.x, boxConfigRobos.pos.y+boxConfigRobos.size.y+15, BACKGROUND_COLOR, window, self)
        lblPosicionamento.setText("Posicionamento", BLACK_LABEL, 28, center=False)
        navigationScrollPanel.addBlock(lblPosicionamento)

        boxPosicionamento = Block("boxPosicionamento", boxConfigRobos.size.x, boxConfigRobos.size.y-50, boxConfigRobos.pos.x, lblPosicionamento.pos.y+lblPosicionamento.size.y+5, BACKGROUND_COLOR, window, self, border=True)
        navigationScrollPanel.addBlock(boxPosicionamento)

        lblPosJuizVirtual = Block("lblPosJuizVirtual", boxPosicionamento.size.x/2-30, lblPosicionamento.size.y, lblBateria.pos.x, boxPosicionamento.pos.y+25, BACKGROUND_COLOR, window, self)
        lblPosJuizVirtual.setText("Usar posicionamento do juiz virtual", center=False)
        navigationScrollPanel.addBlock(lblPosJuizVirtual)

        virtualJudgeToggleButton = ToggleButton("virtualJudgeToggleButton", inversaoToggleButton.size.x, inversaoToggleButton.size.y, lblPosJuizVirtual.pos.x+lblPosJuizVirtual.size.x+170, lblPosJuizVirtual.pos.y-12, BACKGROUND_COLOR, window, self)
        virtualJudgeToggleButton.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        navigationScrollPanel.addButton(virtualJudgeToggleButton)

        lblSelecionarPosicionamento = Block("lblSelecionarPosicionamento", lblPosJuizVirtual.size.x-60, lblPosJuizVirtual.size.y, lblPosJuizVirtual.pos.x, lblPosJuizVirtual.pos.y+lblPosJuizVirtual.size.y+30, BACKGROUND_COLOR, window, self)
        lblSelecionarPosicionamento.setText("Selecionar posicionamento", center=False)
        navigationScrollPanel.addBlock(lblSelecionarPosicionamento)

        positioningComboBox = ComboBox("positioningComboBox", lblSelecionarPosicionamento.size.x-30, lblSelecionarPosicionamento.size.y, lblSelecionarPosicionamento.pos.x+lblSelecionarPosicionamento.size.x+130, lblSelecionarPosicionamento.pos.y, WHITE, window, self, "FreeBall")
        navigationScrollPanel.addButton(positioningComboBox)
        positioningComboBox.addOptions(["FreeBall"])

        lblTempoPosicionar = Block("lblTempoPosicionamento", lblPosJuizVirtual.size.x-32, lblPosJuizVirtual.size.y, lblSelecionarPosicionamento.pos.x, lblSelecionarPosicionamento.pos.y+lblSelecionarPosicionamento.size.y+30, BACKGROUND_COLOR, window, self)
        lblTempoPosicionar.setText("Tempo tentando se posicionar:", center=False)
        navigationScrollPanel.addBlock(lblTempoPosicionar)

        tempoPosicionar = Block("tempoPosicionar", 35, lblTempoPosicionar.size.y, lblTempoPosicionar.pos.x+lblTempoPosicionar.size.x+20, lblTempoPosicionar.pos.y, BACKGROUND_COLOR, window, self)
        tempoPosicionar.setText("8s", center=False)
        navigationScrollPanel.addBlock(tempoPosicionar)



        UVFButton = ToggleButton("UVFButton", boxPosicionamento.size.x, menuBar.size.y-3, boxPosicionamento.pos.x, boxPosicionamento.pos.y+boxPosicionamento.size.y+30, BUTTON_HELD_SCREEN_COLOR, window, self)
        UVFButton.setImage("images/button_screen_held.png", "images/button_screen_expanded.png", center=True)
        UVFButton.setText("UVF", BLACK_LABEL, 32, center=True)
        navigationScrollPanel.addButton(UVFButton)

        UVFScreen = ScrollingBackground("UVFScreen", UVFButton.size.x, windowSize.y, UVFButton.pos.x, UVFButton.pos.y+UVFButton.size.y+5, BACKGROUND_COLOR, window, self, UVFButton.size.x, windowSize.y, border=True)
        navigationScrollPanel.addScrollingBackground(UVFScreen)

        robotIDUVFComboBox = ComboBox("robotIDUVFComboBox", robotIDComboBox.size.x, robotIDComboBox.size.y, UVFScreen.pos.x+30, UVFScreen.pos.y+20, WHITE, window, self, "Robô ID")
        UVFScreen.addButton(robotIDUVFComboBox)
        robotIDUVFComboBox.addOptions(["Robô 00", "Robô 01", "Robô 02"])

        lblVisualizarCampoUVF = Block("lblVisualizarCampoUVF", robotIDUVFComboBox.size.x-50, robotIDUVFComboBox.size.y, robotIDUVFComboBox.pos.x, robotIDUVFComboBox.pos.y+robotIDUVFComboBox.size.y+50, BACKGROUND_COLOR, window, self)
        lblVisualizarCampoUVF.setText("Visualizar campo UVF", center=False)
        UVFScreen.addBlock(lblVisualizarCampoUVF)

        decreaseQuantPontos = Button("decreaseQuantPontos", inversaoToggleButton.size.x-20, lblVisualizarCampoUVF.size.y, lblVisualizarCampoUVF.pos.x+lblVisualizarCampoUVF.size.x+210, lblVisualizarCampoUVF.pos.y, WHITE, window, self)
        decreaseQuantPontos.setText("-", center=True)
        UVFScreen.addButton(decreaseQuantPontos)

        increaseQuantPontos = Button("increaseQuantPontos", decreaseQuantPontos.size.x, decreaseQuantPontos.size.y, decreaseQuantPontos.pos.x+decreaseQuantPontos.size.x-3, decreaseQuantPontos.pos.y, WHITE, window, self)
        increaseQuantPontos.setText("+", center=True)
        UVFScreen.addButton(increaseQuantPontos)

        txtQuantPontos = TextField("txtQuantPontos", decreaseQuantPontos.size.x+increaseQuantPontos.size.x, decreaseQuantPontos.size.y, decreaseQuantPontos.pos.x-(decreaseQuantPontos.size.x+increaseQuantPontos.size.x)+3, decreaseQuantPontos.pos.y, WHITE, window, self)
        txtQuantPontos.setText("10", center=True)
        UVFScreen.addButton(txtQuantPontos)

        lblQuantPontos = Block("lblQuantPontos", txtQuantPontos.size.x+increaseQuantPontos.size.x+decreaseQuantPontos.size.x-6, lblVisualizarCampoUVF.size.y-7, txtQuantPontos.pos.x, txtQuantPontos.pos.y-lblVisualizarCampoUVF.size.y+10, BACKGROUND_COLOR, window, self)
        lblQuantPontos.setText("Quantidade de pontos", fontSize=21, center=True)
        UVFScreen.addBlock(lblQuantPontos)

        viewCampoUVF = Button("viewCampoUVF", inversaoToggleButton.size.x/2, inversaoToggleButton.size.y/2, increaseQuantPontos.pos.x+increaseQuantPontos.size.x+30, increaseQuantPontos.pos.y, BACKGROUND_COLOR, window, self)
        viewCampoUVF.setImage("images/visualize.png")
        UVFScreen.addButton(viewCampoUVF)

        lblSelecionarCampo = Block("lblSelecionarCampo", lblVisualizarCampoUVF.size.x-30, lblVisualizarCampoUVF.size.y, lblVisualizarCampoUVF.pos.x, lblVisualizarCampoUVF.pos.y+lblVisualizarCampoUVF.size.y*2.5, BACKGROUND_COLOR, window, self)
        lblSelecionarCampo.setText("Selecionar campo", center=False)
        UVFScreen.addBlock(lblSelecionarCampo)

        selectFieldComboBox = ComboBox("selectFieldComboBox", chooseColorComboBox.size.x+16, lblSelecionarCampo.size.y, txtQuantPontos.pos.x+txtQuantPontos.size.x/2, lblSelecionarCampo.pos.y, WHITE, window, self, "Nenhum")
        UVFScreen.addButton(selectFieldComboBox)
        selectFieldComboBox.addOptions(["Nenhum"])

        lblPontoFinalSelec = Block("lblPontoFinalSelec", lblVisualizarCampoUVF.size.x+20, lblVisualizarCampoUVF.size.y, lblSelecionarCampo.pos.x, lblSelecionarCampo.pos.y+lblSelecionarCampo.size.y*2.5, BACKGROUND_COLOR, window, self)
        lblPontoFinalSelec.setText("Ponto final selecionável", center=False)
        UVFScreen.addBlock(lblPontoFinalSelec)

        lblHabilitaPontoFinal = Block("lblHabilitaPontoFinal", lblVisualizarCampoUVF.size.x*2.5, lblPontoFinalSelec.size.y-5, lblPontoFinalSelec.pos.x+30, lblPontoFinalSelec.pos.y+lblPontoFinalSelec.size.y-6, BACKGROUND_COLOR, window, self)
        lblHabilitaPontoFinal.setText("Habilita a seleção manual de ponto final das trajetórias", fontSize=21, center=False)
        UVFScreen.addBlock(lblHabilitaPontoFinal)

        pontoFinalSelecToggleButton = ToggleButton("pontoFinalSelecComboBox", inversaoToggleButton.size.x, inversaoToggleButton.size.y, lblHabilitaPontoFinal.pos.x+lblHabilitaPontoFinal.size.x+50, lblPontoFinalSelec.pos.y, BACKGROUND_COLOR, window, self)
        pontoFinalSelecToggleButton.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        UVFScreen.addButton(pontoFinalSelecToggleButton)

        lblRaio = Block("lblRaio", lblSelecionarCampo.size.x/2-24, lblSelecionarCampo.size.y, lblPontoFinalSelec.pos.x, lblPontoFinalSelec.pos.y+lblPontoFinalSelec.size.y*2.5, BACKGROUND_COLOR, window, self)
        lblRaio.setText("Raio:", center=False)
        UVFScreen.addBlock(lblRaio)

        decreaseRaio = Button("decreaseRaio", decreaseQuantPontos.size.x, decreaseQuantPontos.size.y, lblRaio.pos.x+txtQuantPontos.size.x-5, lblRaio.pos.y+lblRaio.size.y-5, WHITE, window, self)
        decreaseRaio.setText("-", center=True)
        UVFScreen.addButton(decreaseRaio)

        increaseRaio = Button("increaseRaio", decreaseRaio.size.x, decreaseRaio.size.y, decreaseRaio.pos.x+decreaseRaio.size.x-3, decreaseRaio.pos.y, WHITE, window, self)
        increaseRaio.setText("+", center=True)
        UVFScreen.addButton(increaseRaio)

        txtRaio = TextField("txtRaio", increaseRaio.size.x*2, increaseRaio.size.y, decreaseRaio.pos.x-txtQuantPontos.size.x+6, increaseRaio.pos.y, WHITE, window, self)
        txtRaio.setText("10", center=True)
        UVFScreen.addButton(txtRaio)

        lblConstSuavizacao = Block("lblConstSuavizacao", lblPontoFinalSelec.size.x+14, lblRaio.size.y, lblRaio.pos.x, txtRaio.pos.y+txtRaio.size.y+10, BACKGROUND_COLOR, window, self)
        lblConstSuavizacao.setText("Constante de suavização:", center=False)
        UVFScreen.addBlock(lblConstSuavizacao)

        decreaseConstSuav = Button("decreaseConstSuav", decreaseRaio.size.x, decreaseRaio.size.y, decreaseRaio.pos.x, lblConstSuavizacao.pos.y+lblConstSuavizacao.size.y-5, WHITE, window, self)
        decreaseConstSuav.setText("-", center=True)
        UVFScreen.addButton(decreaseConstSuav)

        increaseConstSuav = Button("increaseConstSuav", increaseQuantPontos.size.x, increaseQuantPontos.size.y, decreaseConstSuav.pos.x+decreaseConstSuav.size.x-3, decreaseConstSuav.pos.y, WHITE, window, self)
        increaseConstSuav.setText("+", center=True)
        UVFScreen.addButton(increaseConstSuav)

        txtConstSuav = TextField("txtConstSuav", increaseConstSuav.size.x*2, increaseConstSuav.size.y, decreaseConstSuav.pos.x-increaseConstSuav.size.x*2+6, decreaseConstSuav.pos.y, WHITE, window, self)
        txtConstSuav.setText("10", center=True)
        UVFScreen.addButton(txtConstSuav)

        lblConstSuavUnidir = Block("lblConstSuavUnidir", lblSelecionarCampo.size.x*2+16, lblConstSuavizacao.size.y, lblConstSuavizacao.pos.x, txtConstSuav.pos.y+txtConstSuav.size.y+10, BACKGROUND_COLOR, window, self)
        lblConstSuavUnidir.setText("Constante de suavização unidirecional:", center=False)
        UVFScreen.addBlock(lblConstSuavUnidir)

        decreaseConstSuavUnidir = Button("decreaseConstSuavUnidir", decreaseConstSuav.size.x, decreaseConstSuav.size.y, decreaseConstSuav.pos.x, lblConstSuavUnidir.pos.y+lblConstSuavUnidir.size.y-5, WHITE, window, self)
        decreaseConstSuavUnidir.setText("-", center=True)
        UVFScreen.addButton(decreaseConstSuavUnidir)

        increaseConstSuavUnidir = Button("increaseConstSuavUnidir", decreaseConstSuavUnidir.size.x, decreaseConstSuavUnidir.size.y, increaseConstSuav.pos.x, decreaseConstSuavUnidir.pos.y, WHITE, window, self)
        increaseConstSuavUnidir.setText("+", center=True)
        UVFScreen.addButton(increaseConstSuavUnidir)

        txtConstSuavUnidir = TextField("txtConstSuavUnidir", txtConstSuav.size.x, txtConstSuav.size.y, txtConstSuav.pos.x, decreaseConstSuavUnidir.pos.y, WHITE, window, self)
        txtConstSuavUnidir.setText("10", center=True)
        UVFScreen.addButton(txtConstSuavUnidir)

        lblVisualizarTodosCamposUVF = Block("lblVisualizarTodosCamposUVF", lblConstSuavUnidir.size.x-50, lblConstSuavUnidir.size.y, lblConstSuavUnidir.pos.x, txtConstSuavUnidir.pos.y+txtConstSuavUnidir.size.y+70, BACKGROUND_COLOR, window, self)
        lblVisualizarTodosCamposUVF.setText("Visualizar todos os campos UVF", center=False)
        UVFScreen.addBlock(lblVisualizarTodosCamposUVF)

        lblHabilitaVisualizacaoCampos = Block("lblHabilitaVisualizacaoCampos", lblVisualizarTodosCamposUVF.size.x+105, lblHabilitaPontoFinal.size.y, lblVisualizarTodosCamposUVF.pos.x+30, lblVisualizarTodosCamposUVF.pos.y+lblVisualizarTodosCamposUVF.size.y-6, BACKGROUND_COLOR, window, self)
        lblHabilitaVisualizacaoCampos.setText("Habilita visualização dos campos de todos os robôs", fontSize=21, center=False)
        UVFScreen.addBlock(lblHabilitaVisualizacaoCampos)

        visualizarTodosCamposToggleButton = ToggleButton("visualizarTodosCamposToggleButton", inversaoToggleButton.size.x, inversaoToggleButton.size.y, pontoFinalSelecToggleButton.pos.x, lblVisualizarTodosCamposUVF.pos.y, BACKGROUND_COLOR, window, self)
        visualizarTodosCamposToggleButton.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        UVFScreen.addButton(visualizarTodosCamposToggleButton)

        UVFScreen.setVisible(False)


        projecoesButton = ToggleButton("projecoesButton", UVFButton.size.x, UVFButton.size.y, UVFButton.pos.x, UVFButton.pos.y+UVFButton.size.y+30, BUTTON_HELD_SCREEN_COLOR, window, self)
        projecoesButton.setImage("images/button_screen_held.png", "images/button_screen_expanded.png", center=True)
        projecoesButton.setText("Projeções", BLACK_LABEL, 32, center=True)
        navigationScrollPanel.addButton(projecoesButton)

        projecoesScreen = ScrollingBackground("projecoesScreen", UVFScreen.size.x, boxConfigRobos.size.y, UVFScreen.pos.x, projecoesButton.pos.y+projecoesButton.size.y+5, BACKGROUND_COLOR, window, self, boxConfigRobos.size.y, projecoesButton.pos.y+projecoesButton.size.y+5, border=True)
        navigationScrollPanel.addScrollingBackground(projecoesScreen)

        robotIDProjecoesComboBox = ComboBox("robotIDProjecoesComboBox", robotIDUVFComboBox.size.x, robotIDUVFComboBox.size.y, robotIDUVFComboBox.pos.x, projecoesScreen.pos.y+20, WHITE, window, self, "Robô ID")
        projecoesScreen.addButton(robotIDProjecoesComboBox)
        robotIDProjecoesComboBox.addOptions(["Robô 00", "Robô 01", "Robô 02"])        

        lblAtacanteGolBola = Block("lblAtacanteGolBola", lblVisualizarCampoUVF.size.x-44, lblVisualizarCampoUVF.size.y, lblVisualizarCampoUVF.pos.x, lblVisualizarCampoUVF.pos.y+lblVisualizarCampoUVF.size.y+50, BACKGROUND_COLOR, window, self)
        lblAtacanteGolBola.setText("Atacante gol bola", center=False)
        projecoesScreen.addBlock(lblAtacanteGolBola)

        decreaseAtacGolBola = Button("decreaseAtacGolBola", decreaseQuantPontos.size.x, decreaseQuantPontos.size.y, decreaseQuantPontos.pos.x, lblAtacanteGolBola.pos.y, WHITE, window, self)
        decreaseAtacGolBola.setText("-", center=True)
        projecoesScreen.addButton(decreaseAtacGolBola)

        increaseAtacGolBola = Button("increaseAtacGolBola", increaseQuantPontos.size.x, increaseQuantPontos.size.y, increaseQuantPontos.pos.x, decreaseAtacGolBola.pos.y, WHITE, window, self)
        increaseAtacGolBola.setText("+", center=True)
        projecoesScreen.addButton(increaseAtacGolBola)

        txtAtacGolBola = TextField("txtAtacGolBola", txtQuantPontos.size.x, txtQuantPontos.size.y, txtQuantPontos.pos.x, increaseAtacGolBola.pos.y, WHITE, window, self)
        txtAtacGolBola.setText("10", center=True)
        projecoesScreen.addButton(txtAtacGolBola)

        lblQuantPontosAtacGolBola = Block("lblQuantPontosAtacGolBola", txtAtacGolBola.size.x+increaseAtacGolBola.size.x+decreaseAtacGolBola.size.x-6, lblAtacanteGolBola.size.y-7, txtAtacGolBola.pos.x, txtAtacGolBola.pos.y-lblAtacanteGolBola.size.y+10, BACKGROUND_COLOR, window, self)
        lblQuantPontosAtacGolBola.setText("Quantidade de pontos", fontSize=21, center=True)
        projecoesScreen.addBlock(lblQuantPontosAtacGolBola)

        viewAtacGolBola = Button("viewAtacGolBola", viewCampoUVF.size.x, viewCampoUVF.size.y, increaseAtacGolBola.pos.x+increaseAtacGolBola.size.x+30, increaseAtacGolBola.pos.y, BACKGROUND_COLOR, window, self)
        viewAtacGolBola.setImage("images/visualize.png")
        projecoesScreen.addButton(viewAtacGolBola)

        lblZagueiroAreaAliada = Block("lblZagueiroAreaAliada", lblAtacanteGolBola.size.x+23, lblAtacanteGolBola.size.y, lblAtacanteGolBola.pos.x, lblAtacanteGolBola.pos.y+lblAtacanteGolBola.size.y*2.5, BACKGROUND_COLOR, window, self)
        lblZagueiroAreaAliada.setText("Zagueiro área aliada", center=False)
        projecoesScreen.addBlock(lblZagueiroAreaAliada)

        decreaseZagAreaAliada = Button("decreaseZagAreaAliada", decreaseAtacGolBola.size.x, decreaseAtacGolBola.size.y, decreaseAtacGolBola.pos.x, lblZagueiroAreaAliada.pos.y, WHITE, window, self)
        decreaseZagAreaAliada.setText("-", center=True)
        projecoesScreen.addButton(decreaseZagAreaAliada)

        increaseZagAreaAliada = Button("increaseZagAreaAliada", increaseAtacGolBola.size.x, increaseAtacGolBola.size.y, increaseAtacGolBola.pos.x, decreaseZagAreaAliada.pos.y, WHITE, window, self)
        increaseZagAreaAliada.setText("+", center=True)
        projecoesScreen.addButton(increaseZagAreaAliada)

        txtZagAreaAliada = TextField("txtZagAreaAliada", txtAtacGolBola.size.x, txtAtacGolBola.size.y, txtAtacGolBola.pos.x, increaseZagAreaAliada.pos.y, WHITE, window, self)
        txtZagAreaAliada.setText("10", center=True)
        projecoesScreen.addButton(txtZagAreaAliada)

        lblQuantPontosZagAreaAliada = Block("lblQuantPontosZagAreaAliada", txtZagAreaAliada.size.x+increaseZagAreaAliada.size.x+decreaseZagAreaAliada.size.x-6, lblZagueiroAreaAliada.size.y-7, txtZagAreaAliada.pos.x, txtZagAreaAliada.pos.y-lblZagueiroAreaAliada.size.y+10, BACKGROUND_COLOR, window, self)
        lblQuantPontosZagAreaAliada.setText("Quantidade de pontos", fontSize=21, center=True)
        projecoesScreen.addBlock(lblQuantPontosZagAreaAliada)

        viewZagAreaAliada = Button("viewZagAreaAliada", viewCampoUVF.size.x, viewCampoUVF.size.y, increaseZagAreaAliada.pos.x+increaseZagAreaAliada.size.x+30, increaseZagAreaAliada.pos.y, BACKGROUND_COLOR, window, self)
        viewZagAreaAliada.setImage("images/visualize.png")
        projecoesScreen.addButton(viewZagAreaAliada)

        projecoesScreen.setVisible(False)

        # Create movement screen
        self.movementScreen = Screen()
        self.movementScreen.setCaption("IGGLU")
        self.movementScreen.setIcon("images/Logo_ice.png")

        # Create or add blocks on the movement screen
        self.movementScreen.setMenuBar(self.navigationScreen.menuBar)
        self.movementScreen.addBlock(screenDivisionLeft)
        self.movementScreen.addBlock(screenDivisionLeftMargin)
        self.movementScreen.addBlock(screenDivisionRight)
        self.movementScreen.addBlock(screenDivisionRightMargin)
        self.movementScreen.addBlock(gameMiniMap)
        self.movementScreen.addBlock(arrow)
        self.movementScreen.addBlock(lblLadoEsquerdo)
        self.movementScreen.addBlock(lblLadoDireito)
        self.movementScreen.addBlock(lblInfoBola)
        self.movementScreen.addBlock(boxInfoBola)
        self.movementScreen.addBlock(lblPosicao)
        self.movementScreen.addBlock(boxPosicao)
        self.movementScreen.addBlock(lblAceleracao)
        self.movementScreen.addBlock(boxAceleracao)
        self.movementScreen.addBlock(lblVelocidade)
        self.movementScreen.addBlock(boxVelocidade)

        movementScrollPanel = ScrollingBackground("movementScrollPanel", screenDivisionRightMargin.size.x, int(screenDivisionRightMargin.size.y), screenDivisionRightMargin.pos.x, screenDivisionRightMargin.pos.y, BACKGROUND_COLOR, window, self, screenDivisionRightMargin.size.y,  screenDivisionRightMargin.pos.y)
        self.movementScreen.addScrollingBackground(movementScrollPanel)

        graficosControleButton = ToggleButton("graficosControleButton", UVFButton.size.x, UVFButton.size.y, movementScrollPanel.pos.x+20, movementScrollPanel.pos.y+30, BUTTON_HELD_SCREEN_COLOR, window, self)
        graficosControleButton.setImage("images/button_screen_held.png", "images/button_screen_expanded.png", center=True)
        graficosControleButton.setText("Gráficos de controle", BLACK_LABEL, 32, center=True)
        movementScrollPanel.addButton(graficosControleButton)

        graficosControleScreen = ScrollingBackground("graficosControleScreen", graficosControleButton.size.x, windowSize.y, graficosControleButton.pos.x, graficosControleButton.pos.y+graficosControleButton.size.y+5, BACKGROUND_COLOR, window, self, graficosControleButton.size.x, windowSize.y, border=True)
        movementScrollPanel.addScrollingBackground(graficosControleScreen)

        robotIDGraficosControleComboBox = ComboBox("robotIDGraficosControleComboBox", robotIDComboBox.size.x, robotIDComboBox.size.y, graficosControleScreen.pos.x+20, graficosControleScreen.pos.y+10, WHITE, window, self, "Robô ID", BACKGROUND_COLOR)
        graficosControleScreen.addButton(robotIDGraficosControleComboBox)
        robotIDGraficosControleComboBox.addOptions(["Robô 00", "Robô 01", "Robô 02"])

        lblPosicaoGraficosControle = Block("lblPosicaoGraficosControle", lblPosicao.size.x-14, lblPosicao.size.y, robotIDGraficosControleComboBox.pos.x, robotIDGraficosControleComboBox.pos.y+robotIDGraficosControleComboBox.size.y+20, BACKGROUND_COLOR, window, self)
        lblPosicaoGraficosControle.setText("Posição", BLACK_LABEL, center=False)
        graficosControleScreen.addBlock(lblPosicaoGraficosControle)

        boxPosicaoGraficosControle = Block("boxPosicaoGraficosControle", boxPosicao.size.x, boxPosicao.size.y, lblPosicaoGraficosControle.pos.x, lblPosicaoGraficosControle.pos.y+lblPosicaoGraficosControle.size.y, BACKGROUND_COLOR, window, self, border=True)
        boxPosicaoGraficosControle.setText("x: 0.0m   y: 0.0m", center=True)
        graficosControleScreen.addBlock(boxPosicaoGraficosControle)

        lblBateriaGraficosControle = Block("lblBateriaGraficosControle", lblBateria.size.x, lblBateria.size.y, boxPosicaoGraficosControle.pos.x+boxPosicaoGraficosControle.size.x+60, lblPosicaoGraficosControle.pos.y, BACKGROUND_COLOR, window, self)
        lblBateriaGraficosControle.setText("Bateria", BLACK_LABEL, center=False)
        graficosControleScreen.addBlock(lblBateriaGraficosControle)

        boxBateriaGraficosControle = Block("boxBateriaGraficosControle", boxPosicaoGraficosControle.size.x, boxPosicaoGraficosControle.size.y, lblBateriaGraficosControle.pos.x, boxPosicaoGraficosControle.pos.y, BACKGROUND_COLOR, window, self, border=True)
        boxBateriaGraficosControle.setText("100%", center=True)
        graficosControleScreen.addBlock(boxBateriaGraficosControle)

        lblVelocidadeLinearGraficosControle = Block("lblVelocidadeLinearGraficosControle", lblPosicaoGraficosControle.size.x*2+8, lblPosicaoGraficosControle.size.y, lblPosicaoGraficosControle.pos.x, boxPosicaoGraficosControle.pos.y+boxPosicaoGraficosControle.size.y+20, BACKGROUND_COLOR, window, self)
        lblVelocidadeLinearGraficosControle.setText("Velocidade linear", BLACK_LABEL, center=False)
        graficosControleScreen.addBlock(lblVelocidadeLinearGraficosControle)

        boxVelocidadeLinearGraficosControle = Block("boxVelocidadeLinearGraficosControle", graficosControleScreen.size.x-40, boxPosicaoGraficosControle.size.y*4, boxPosicaoGraficosControle.pos.x, lblVelocidadeLinearGraficosControle.pos.y+lblVelocidadeLinearGraficosControle.size.y, BACKGROUND_COLOR, window, self, border=True)
        graficosControleScreen.addBlock(boxVelocidadeLinearGraficosControle)

        lblVelocidadeAngularGraficosControle = Block("lblVelocidadeAngularGraficosControle", lblVelocidadeLinearGraficosControle.size.x+18, lblVelocidadeLinearGraficosControle.size.y, lblVelocidadeLinearGraficosControle.pos.x, boxVelocidadeLinearGraficosControle.pos.y+boxVelocidadeLinearGraficosControle.size.y+10, BACKGROUND_COLOR, window, self)
        lblVelocidadeAngularGraficosControle.setText("Velocidade angular", BLACK_LABEL, center=False)
        graficosControleScreen.addBlock(lblVelocidadeAngularGraficosControle)

        boxVelocidadeAngularGraficosControle = Block("boxVelocidadeAngularGraficosControle", boxVelocidadeLinearGraficosControle.size.x, boxVelocidadeLinearGraficosControle.size.y, boxVelocidadeLinearGraficosControle.pos.x, lblVelocidadeAngularGraficosControle.pos.y+lblVelocidadeAngularGraficosControle.size.y, BACKGROUND_COLOR, window, self, border=True)
        graficosControleScreen.addBlock(boxVelocidadeAngularGraficosControle)

        lblAceleracaoGraficosControle = Block("lblAceleracaoGraficosControle", lblVelocidadeAngularGraficosControle.size.x/2+14, lblVelocidadeAngularGraficosControle.size.y, lblVelocidadeAngularGraficosControle.pos.x, boxVelocidadeAngularGraficosControle.pos.y+boxVelocidadeAngularGraficosControle.size.y+10, BACKGROUND_COLOR, window, self)
        lblAceleracaoGraficosControle.setText("Aceleração", BLACK_LABEL, center=False)
        graficosControleScreen.addBlock(lblAceleracaoGraficosControle)

        boxAceleracaoGraficosControle = Block("boxAceleracaoGraficosControle", boxVelocidadeAngularGraficosControle.size.x, boxVelocidadeAngularGraficosControle.size.y, boxVelocidadeAngularGraficosControle.pos.x, lblAceleracaoGraficosControle.pos.y+lblAceleracaoGraficosControle.size.y, BACKGROUND_COLOR, window, self, border=True)
        graficosControleScreen.addBlock(boxAceleracaoGraficosControle)

        graficosControleScreen.setVisible(False)

        controleManualButton = ToggleButton("controleManualButton", graficosControleButton.size.x, graficosControleButton.size.y, graficosControleButton.pos.x, graficosControleButton.pos.y+graficosControleButton.size.y+30, BUTTON_HELD_SCREEN_COLOR, window, self)
        controleManualButton.setImage("images/button_screen_held.png", "images/button_screen_expanded.png", center=True)
        controleManualButton.setText("Controle manual", BLACK_LABEL, 32, center=True)
        movementScrollPanel.addButton(controleManualButton)

        controleManualScreen = ScrollingBackground("controleManualScreen", controleManualButton.size.x, windowSize.y*0.8, controleManualButton.pos.x, controleManualButton.pos.y+controleManualButton.size.y+5, BACKGROUND_COLOR, window, self, controleManualButton.size.x, windowSize.y, border=True)
        movementScrollPanel.addScrollingBackground(controleManualScreen)

        robotIDControleManualComboBox = ComboBox("robotIDControleManualComboBox", robotIDGraficosControleComboBox.size.x, robotIDGraficosControleComboBox.size.y, controleManualScreen.pos.x+20, controleManualScreen.pos.y+20, WHITE, window, self, "Robô ID")
        controleManualScreen.addButton(robotIDControleManualComboBox)
        robotIDControleManualComboBox.addOptions(["Robô 00", "Robô 01", "Robô 02"])

        lblHabilitarJoystick = Block("lblHabilitarJoystick", robotIDControleManualComboBox.size.x, lblVelocidadeLinearGraficosControle.size.y, robotIDControleManualComboBox.pos.x, robotIDControleManualComboBox.pos.y+robotIDControleManualComboBox.size.y+60, BACKGROUND_COLOR, window, self)
        lblHabilitarJoystick.setText("Habilitar joystick", center=False)
        controleManualScreen.addBlock(lblHabilitarJoystick)

        enableJoystickToggleButton = ToggleButton("enableJoystickToggleButton", virtualJudgeToggleButton.size.x, virtualJudgeToggleButton.size.y, virtualJudgeToggleButton.pos.x, lblHabilitarJoystick.pos.y-12, BACKGROUND_COLOR, window, self)
        enableJoystickToggleButton.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        controleManualScreen.addButton(enableJoystickToggleButton)

        directionComboBox = ComboBox("directionComboBox", robotIDControleManualComboBox.size.x, robotIDControleManualComboBox.size.y, robotIDControleManualComboBox.pos.x, lblHabilitarJoystick.pos.y+lblHabilitarJoystick.size.y+60, WHITE, window, self, "Para frente")
        controleManualScreen.addButton(directionComboBox)
        directionComboBox.addOptions(["Para frente", "Curva direita", "Curva esquerda", "Girar horário", "Girar anti-horário"])

        enableDirectionToggleButton = ToggleButton("enableDirectionToggleButton", enableJoystickToggleButton.size.x, enableJoystickToggleButton.size.y, enableJoystickToggleButton.pos.x, directionComboBox.pos.y-12, BACKGROUND_COLOR, window, self)
        enableDirectionToggleButton.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        controleManualScreen.addButton(enableDirectionToggleButton)

        lblHabilitarControleManual = Block("lblHabilitarControleManual", robotIDControleManualComboBox.size.x, lblHabilitarJoystick.size.y, lblHabilitarJoystick.pos.x, directionComboBox.pos.y+directionComboBox.size.y+60, BACKGROUND_COLOR, window, self)
        lblHabilitarControleManual.setText("Habilitar controle manual", center=False)
        controleManualScreen.addBlock(lblHabilitarControleManual)

        enableControleManualToggleButton = ToggleButton("enableControleManualToggleButton", enableDirectionToggleButton.size.x, enableDirectionToggleButton.size.y, enableDirectionToggleButton.pos.x, lblHabilitarControleManual.pos.y-12, BACKGROUND_COLOR, window, self)
        enableControleManualToggleButton.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        controleManualScreen.addButton(enableControleManualToggleButton)

        lblVelocidadeLinearControleManual = Block("lblVelocidadeLinearControleManual", controleManualScreen.size.x-20, lblVelocidadeLinearGraficosControle.size.y, controleManualScreen.pos.x+10, lblHabilitarControleManual.pos.y+lblHabilitarControleManual.size.y+60, BACKGROUND_COLOR, window, self)
        lblVelocidadeLinearControleManual.setText("Velocidade linear", center=True)
        controleManualScreen.addBlock(lblVelocidadeLinearControleManual)

        velocidadeLinearBar = Block("velocidadeLinearBar", controleManualScreen.size.x-60, 10, controleManualScreen.pos.x+30, lblVelocidadeLinearControleManual.pos.y+lblVelocidadeLinearControleManual.size.y+5, SLIDER_BAR_COLOR, window, self)
        controleManualScreen.addBlock(velocidadeLinearBar)

        velocidadeLinearSlider = Slider("velocidadeLinearSlider", 20, 10, velocidadeLinearBar.pos.x, velocidadeLinearBar.pos.y+velocidadeLinearBar.size.y/2, BACKGROUND_COLOR, window, self, velocidadeLinearBar)
        controleManualScreen.addButton(velocidadeLinearSlider)
        velocidadeLinearSlider.createLabel()

        lblVelocidadeAngularControleManual = Block("lblVelocidadeAngularControleManual", lblVelocidadeLinearControleManual.size.x, lblVelocidadeLinearControleManual.size.y, lblVelocidadeLinearControleManual.pos.x, velocidadeLinearBar.pos.y+velocidadeLinearBar.size.y+20, BACKGROUND_COLOR, window, self)
        lblVelocidadeAngularControleManual.setText("Velocidade angular", center=True)
        controleManualScreen.addBlock(lblVelocidadeAngularControleManual)

        velocidadeAngularBar = Block("velocidadeAngularBar", velocidadeLinearBar.size.x, velocidadeLinearBar.size.y, controleManualScreen.pos.x+30, lblVelocidadeAngularControleManual.pos.y+lblVelocidadeAngularControleManual.size.y+5, SLIDER_BAR_COLOR, window, self)
        controleManualScreen.addBlock(velocidadeAngularBar)

        velocidadeAngularSlider = Slider("velocidadeAngularSlider", velocidadeLinearSlider.size.x, velocidadeLinearSlider.size.y, velocidadeAngularBar.pos.x, velocidadeAngularBar.pos.y+velocidadeAngularBar.size.y/2, BACKGROUND_COLOR, window, self, velocidadeAngularBar)
        controleManualScreen.addButton(velocidadeAngularSlider)
        velocidadeAngularSlider.createLabel()

        lblAceleracaoControleManual = Block("lblAceleracaoControleManual", lblVelocidadeAngularControleManual.size.x, lblVelocidadeAngularControleManual.size.y, lblVelocidadeAngularControleManual.pos.x, velocidadeAngularBar.pos.y+velocidadeAngularBar.size.y+20, BACKGROUND_COLOR, window, self)
        lblAceleracaoControleManual.setText("Aceleração", center=True)
        controleManualScreen.addBlock(lblAceleracaoControleManual)

        aceleracaoBar = Block("aceleracaoBar", velocidadeLinearBar.size.x, velocidadeLinearBar.size.y, controleManualScreen.pos.x+30, lblAceleracaoControleManual.pos.y+lblAceleracaoControleManual.size.y+5, SLIDER_BAR_COLOR, window, self)
        controleManualScreen.addBlock(aceleracaoBar)

        aceleracaoSlider = Slider("aceleracaoSlider", velocidadeLinearSlider.size.x, velocidadeLinearSlider.size.y, aceleracaoBar.pos.x, aceleracaoBar.pos.y+aceleracaoBar.size.y/2, BACKGROUND_COLOR, window, self, aceleracaoBar)
        controleManualScreen.addButton(aceleracaoSlider)
        aceleracaoSlider.createLabel()

        controleManualScreen.setVisible(False)

        controleUVFButton = ToggleButton("controleUVFButton", controleManualButton.size.x, controleManualButton.size.y, controleManualButton.pos.x, controleManualButton.pos.y+controleManualButton.size.y+30, BUTTON_HELD_SCREEN_COLOR, window, self)
        controleUVFButton.setImage("images/button_screen_held.png", "images/button_screen_expanded.png", center=True)
        controleUVFButton.setText("Controle UVF", BLACK_LABEL, 32, center=True)
        movementScrollPanel.addButton(controleUVFButton)

        controleUVFScreen = ScrollingBackground("controleUVFScreen", controleUVFButton.size.x, windowSize.y*0.8, controleUVFButton.pos.x, controleUVFButton.pos.y+controleUVFButton.size.y+5, BACKGROUND_COLOR, window, self, controleUVFButton.size.x, windowSize.y, border=True)
        movementScrollPanel.addScrollingBackground(controleUVFScreen)

        robotIDControleUVFComboBox = ComboBox("robotIDControleUVFComboBox", robotIDControleManualComboBox.size.x, robotIDControleManualComboBox.size.y, robotIDControleManualComboBox.pos.x, controleUVFScreen.pos.y+30, WHITE, window, self, "Robô ID")
        controleUVFScreen.addButton(robotIDControleUVFComboBox)
        robotIDControleUVFComboBox.addOptions(["Robô 00", "Robô 01", "Robô 02"])

        lblVisualizarCampoControleUVF = Block("lblVisualizarCampoControleUVF", lblVisualizarCampoUVF.size.x-36, lblVisualizarCampoUVF.size.y, robotIDControleUVFComboBox.pos.x, robotIDControleUVFComboBox.pos.y+robotIDControleUVFComboBox.size.y+30, BACKGROUND_COLOR, window, self)
        lblVisualizarCampoControleUVF.setText("Visualizar campo", center=False)
        controleUVFScreen.addBlock(lblVisualizarCampoControleUVF)

        lblHabilitaVisualizacaoCamposControleUVF = Block("lblHabilitaVisualizacaoCamposControleUVF", lblHabilitaVisualizacaoCampos.size.x, lblHabilitaVisualizacaoCampos.size.y, lblVisualizarCampoControleUVF.pos.x+30, lblVisualizarCampoControleUVF.pos.y+lblVisualizarCampoControleUVF.size.y-6, BACKGROUND_COLOR, window, self)
        lblHabilitaVisualizacaoCamposControleUVF.setText("Habilita a visualização do campo UVF do robô", fontSize=21, center=False)
        controleUVFScreen.addBlock(lblHabilitaVisualizacaoCamposControleUVF)

        viewCampoControleUVF = Button("viewCampoControleUVF", viewCampoUVF.size.x, viewCampoUVF.size.y, lblHabilitaVisualizacaoCamposControleUVF.pos.x+lblHabilitaVisualizacaoCamposControleUVF.size.x+100, lblVisualizarCampoControleUVF.pos.y+10, BACKGROUND_COLOR, window, self)
        viewCampoControleUVF.setImage("images/visualize.png")
        controleUVFScreen.addButton(viewCampoControleUVF)

        lblKw = Block("lblKw", 28, lblVisualizarCampoControleUVF.size.y, lblHabilitaVisualizacaoCamposControleUVF.pos.x-5, lblHabilitaVisualizacaoCamposControleUVF.pos.y+lblHabilitaVisualizacaoCamposControleUVF.size.y+50, BACKGROUND_COLOR, window, self)
        lblKw.setText("kw", center=False)
        controleUVFScreen.addBlock(lblKw)

        decreaseKw = Button("decreaseKw", decreaseAtacGolBola.size.x, decreaseAtacGolBola.size.y, lblKw.pos.x+txtRaio.size.x-5, lblKw.pos.y+lblKw.size.y-5, WHITE, window, self)
        decreaseKw.setText("-", center=True)
        controleUVFScreen.addButton(decreaseKw)

        increaseKw = Button("increaseKw", decreaseKw.size.x, decreaseKw.size.y, decreaseKw.pos.x+decreaseKw.size.x-3, decreaseKw.pos.y, WHITE, window, self)
        increaseKw.setText("+", center=True)
        controleUVFScreen.addButton(increaseKw)

        txtKw = TextField("txtKw", txtRaio.size.x, txtRaio.size.y, lblKw.pos.x, decreaseKw.pos.y, WHITE, window, self)
        txtKw.setText("10", center=True)
        controleUVFScreen.addButton(txtKw)

        lblKp = Block("lblKp", lblKw.size.x, lblKw.size.y, increaseKw.pos.x+increaseKw.size.x*3, lblKw.pos.y, BACKGROUND_COLOR, window, self)
        lblKp.setText("kp", center=False)
        controleUVFScreen.addBlock(lblKp)

        decreaseKp = Button("decreaseKp", decreaseKw.size.x, decreaseKw.size.y, lblKp.pos.x+txtKw.size.x-3, lblKp.pos.y+lblKp.size.y-5, WHITE, window, self)
        decreaseKp.setText("-", center=True)
        controleUVFScreen.addButton(decreaseKp)

        increaseKp = Button("increaseKp", decreaseKp.size.x, decreaseKp.size.y, decreaseKp.pos.x+decreaseKp.size.x-3, decreaseKp.pos.y, WHITE, window, self)
        increaseKp.setText("+", center=True)
        controleUVFScreen.addButton(increaseKp)

        txtKp = TextField("txtKp", txtKw.size.x, txtKw.size.y, lblKp.pos.x, decreaseKp.pos.y, WHITE, window, self)
        txtKp.setText("10", center=True)
        controleUVFScreen.addButton(txtKp)

        lblL = Block("lblL", lblKw.size.x/2, lblKw.size.y, lblKw.pos.x, txtKw.pos.y+txtKw.size.y*1.5, BACKGROUND_COLOR, window, self)
        lblL.setText("L", center=False)
        controleUVFScreen.addBlock(lblL)

        decreaseL = Button("decreaseL", decreaseKw.size.x, decreaseKw.size.y, decreaseKw.pos.x, lblL.pos.y+lblL.size.y-5, WHITE, window, self)
        decreaseL.setText("-", center=True)
        controleUVFScreen.addButton(decreaseL)

        increaseL = Button("increaseL", increaseKw.size.x, increaseKw.size.y, increaseKw.pos.x, decreaseL.pos.y, WHITE, window, self)
        increaseL.setText("+", center=True)
        controleUVFScreen.addButton(increaseL)

        txtL = TextField("txtL", txtKw.size.x, txtKw.size.y, txtKw.pos.x, increaseL.pos.y, WHITE, window, self)
        txtL.setText("10", center=True)
        controleUVFScreen.addButton(txtL)

        lblVmax = Block("lblVmax", lblKp.size.x*2-6, lblKp.size.y, lblKp.pos.x, lblL.pos.y, BACKGROUND_COLOR, window, self)
        lblVmax.setText("vmax", center=False)
        controleUVFScreen.addBlock(lblVmax)

        decreaseVmax = Button("decreaseVmax", decreaseKp.size.x, decreaseKp.size.y, decreaseKp.pos.x, decreaseL.pos.y, WHITE, window, self)
        decreaseVmax.setText("-", center=True)
        controleUVFScreen.addButton(decreaseVmax)

        increaseVmax = Button("increaseVmax", increaseKp.size.x, increaseKp.size.y, increaseKp.pos.x, decreaseVmax.pos.y, WHITE, window, self)
        increaseVmax.setText("+", center=True)
        controleUVFScreen.addButton(increaseVmax)

        txtVmax = TextField("txtVmax", txtKp.size.x, txtKp.size.y, txtKp.pos.x, increaseVmax.pos.y, WHITE, window, self)
        txtVmax.setText("10", center=True)
        controleUVFScreen.addButton(txtVmax)

        lblMu = Block("lblMu", lblKw.size.x, lblL.size.y, lblL.pos.x, txtL.pos.y+txtL.size.y*1.5, BACKGROUND_COLOR, window, self)
        lblMu.setText("mu", center=False)
        controleUVFScreen.addBlock(lblMu)

        decreaseMu = Button("decreaseMu", decreaseL.size.x, decreaseL.size.y, decreaseL.pos.x, lblMu.pos.y+lblMu.size.y-5, WHITE, window, self)
        decreaseMu.setText("-", center=True)
        controleUVFScreen.addButton(decreaseMu)

        increaseMu = Button("increaseMu", increaseL.size.x, increaseL.size.y, increaseL.pos.x, decreaseMu.pos.y, WHITE, window, self)
        increaseMu.setText("+", center=True)
        controleUVFScreen.addButton(increaseMu)

        txtMu = TextField("txtMu", txtL.size.x, txtL.size.y, txtL.pos.x, increaseMu.pos.y, WHITE, window, self)
        txtMu.setText("10", center=True)
        controleUVFScreen.addButton(txtMu)
        
        lblVref = Block("lblVref", lblKp.size.x+12, lblVmax.size.y, lblVmax.pos.x, lblMu.pos.y, BACKGROUND_COLOR, window, self)
        lblVref.setText("vref", center=False)
        controleUVFScreen.addBlock(lblVref)

        decreaseVref = Button("decreaseVref", decreaseVmax.size.x, decreaseVmax.size.y, decreaseVmax.pos.x, decreaseMu.pos.y, WHITE, window, self)
        decreaseVref.setText("-", center=True)
        controleUVFScreen.addButton(decreaseVref)

        increaseVref = Button("increaseVref", increaseVmax.size.x, increaseVmax.size.y, increaseVmax.pos.x, decreaseVref.pos.y, WHITE, window, self)
        increaseVref.setText("+", center=True)
        controleUVFScreen.addButton(increaseVref)

        txtVref = TextField("txtVref", txtVmax.size.x, txtVmax.size.y, txtVmax.pos.x, increaseVref.pos.y, WHITE, window, self)
        txtVref.setText("10", center=True)
        controleUVFScreen.addButton(txtVref)

        lblR = Block("lblR", lblL.size.x, lblL.size.y, lblMu.pos.x, txtMu.pos.y+txtMu.size.y*1.5, BACKGROUND_COLOR, window, self)
        lblR.setText("r", center=False)
        controleUVFScreen.addBlock(lblR)

        decreaseR = Button("decreaseR", decreaseMu.size.x, decreaseMu.size.y, decreaseMu.pos.x, lblR.pos.y+lblR.size.y-5, WHITE, window, self)
        decreaseR.setText("-", center=True)
        controleUVFScreen.addButton(decreaseR)

        increaseR = Button("decrease", decreaseR.size.x, decreaseR.size.y, increaseMu.pos.x, decreaseR.pos.y, WHITE, window, self)
        increaseR.setText("+", center=True)
        controleUVFScreen.addButton(increaseR)

        txtR = TextField("txtR", txtMu.size.x, txtMu.size.y, txtMu.pos.x, increaseR.pos.y, WHITE, window, self)
        txtR.setText("10", center=True)
        controleUVFScreen.addButton(txtR)

        lblMaxAngError = Block("lblMaxAngError", lblVmax.size.x*2+8, lblVref.size.y, lblVref.pos.x, lblR.pos.y, BACKGROUND_COLOR, window, self)
        lblMaxAngError.setText("maxangerror", center=False)
        controleUVFScreen.addBlock(lblMaxAngError)

        decreaseMaxAngError = Button("decreaseMaxAngError", decreaseVref.size.x, decreaseVref.size.y, decreaseVref.pos.x, decreaseR.pos.y, WHITE, window, self)
        decreaseMaxAngError.setText("-", center=True)
        controleUVFScreen.addButton(decreaseMaxAngError)

        increaseMaxAngError = Button("increaseMaxAngError", decreaseMaxAngError.size.x, decreaseMaxAngError.size.y, increaseVref.pos.x, decreaseMaxAngError.pos.y, WHITE, window, self)
        increaseMaxAngError.setText("+", center=True)
        controleUVFScreen.addButton(increaseMaxAngError)

        txtMaxAngError = TextField("txtMaxAngError", txtVref.size.x, txtVref.size.y, txtVref.pos.x, decreaseMaxAngError.pos.y, WHITE, window, self)
        txtMaxAngError.setText("10", center=True)
        controleUVFScreen.addButton(txtMaxAngError)

        lblTau = Block("lblTau", lblKp.size.x, lblR.size.y, lblR.pos.x, txtR.pos.y+txtR.size.y*1.5, BACKGROUND_COLOR, window, self)
        lblTau.setText("tau", center=False)
        controleUVFScreen.addBlock(lblTau)

        decreaseTau = Button("decreaseTau", decreaseR.size.x, decreaseR.size.y, decreaseR.pos.x, lblTau.pos.y+lblTau.size.y-5, WHITE, window, self)
        decreaseTau.setText("-", center=True)
        controleUVFScreen.addButton(decreaseTau)

        increaseTau = Button("increaseTau", decreaseTau.size.x, decreaseTau.size.y, increaseR.pos.x, decreaseTau.pos.y, WHITE, window, self)
        increaseTau.setText("+", center=True)
        controleUVFScreen.addButton(increaseTau)

        txtTau = TextField("txtTau", txtR.size.x, txtR.size.y, txtR.pos.x, increaseTau.pos.y, WHITE, window, self)
        txtTau.setText("10", center=True)
        controleUVFScreen.addButton(txtTau)

        controleUVFScreen.setVisible(False)


        # Create comunication screen
        self.communicationScreen = Screen()
        self.communicationScreen.setCaption("IGGLU")
        self.communicationScreen.setIcon("images/Logo_ice.png")

        # Create or add blocks on the communication screen
        self.communicationScreen.setMenuBar(self.navigationScreen.menuBar)
        self.communicationScreen.addBlock(screenDivisionLeft)
        self.communicationScreen.addBlock(screenDivisionLeftMargin)
        self.communicationScreen.addBlock(screenDivisionRight)
        self.communicationScreen.addBlock(screenDivisionRightMargin)

        faixaBackgroundGameMenuBarGameMiniMap = Block("faixaBackgroundGameMenuBarGameMiniMap", screenDivisionLeftMargin.size.x, 20, 0, screenDivisionLeft.pos.y, BACKGROUND_COLOR, window, self)
        self.communicationScreen.addBlock(faixaBackgroundGameMenuBarGameMiniMap)
        
        boxErrosWarnings = Block("boxErrosWarnings", gameMiniMap.size.x, gameMiniMap.size.y/1.5, gameMiniMap.pos.x, gameMiniMap.pos.y+gameMiniMap.size.y+20+lblInfoBola.size.y, BACKGROUND_COLOR, window, self, border=True, preference=False)
        self.communicationScreen.addBlock(boxErrosWarnings)

        errosWarningsScrollPanel = ScrollingBackground("errosWarningsScrollPanel", gameMiniMap.size.x-4, gameMiniMap.size.y/1.5-4, gameMiniMap.pos.x+2, gameMiniMap.pos.y+gameMiniMap.size.y+20+lblInfoBola.size.y+2, BACKGROUND_COLOR, window, self, gameMiniMap.size.y/1.5-4, gameMiniMap.pos.y+gameMiniMap.size.y+20+lblInfoBola.size.y, preference=False)
        self.communicationScreen.addScrollingBackground(errosWarningsScrollPanel)
        
        self.communicationScreen.addBlock(gameMiniMap)

        faixaBackgroundGameMiniMapErrosWarnings = Block("faixaBackgroundGameMiniMapErrosWarnings", screenDivisionLeftMargin.size.x, boxErrosWarnings.pos.y-gameMiniMap.pos.y-gameMiniMap.size.y, 0, gameMiniMap.pos.y+gameMiniMap.size.y, BACKGROUND_COLOR, window, self)
        self.communicationScreen.addBlock(faixaBackgroundGameMiniMapErrosWarnings)

        linhaCimaBoxErrosWarnings = Block("linhaCimaBoxErrosWarnings", boxErrosWarnings.size.x, 2, boxErrosWarnings.pos.x, boxErrosWarnings.pos.y, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaCimaBoxErrosWarnings)

        lblErrosWarnings = Block("lblErrosWarnings", gameMiniMap.size.x/4-14, lblInfoBola.size.y, gameMiniMap.pos.x, gameMiniMap.pos.y+gameMiniMap.size.y+20, BACKGROUND_COLOR, window, self)
        lblErrosWarnings.setText("Erros e Warnings", BLACK_LABEL, 26, center=False)
        self.communicationScreen.addBlock(lblErrosWarnings)
        
        errosWarningsLabelArea = LabelArea("errosWarningsLabelArea", boxErrosWarnings.size.x-30, 0, boxErrosWarnings.pos.x+15, boxErrosWarnings.pos.y+20, BACKGROUND_COLOR, window, self)
        errosWarningsLabelArea.setText("", center=False)
        errosWarningsScrollPanel.addBlock(errosWarningsLabelArea)
        errosWarningsLabelArea.addLabel("Comunicação Wifi: Porta Serial não encontrada")

        linhaBaixoBoxErrosWarnings = Block("linhaBaixoBoxErrosWarnings", boxErrosWarnings.size.x, 2, boxErrosWarnings.pos.x, boxErrosWarnings.pos.y+boxErrosWarnings.size.y-2, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaBaixoBoxErrosWarnings)

        faixaBackgroundBoxErrosWarningsEnd = Block("faixaBackgroundBoxErrosWarningsEnd", faixaBackgroundGameMiniMapErrosWarnings.size.x, faixaBackgroundGameMiniMapErrosWarnings.size.y, 0, boxErrosWarnings.pos.y+boxErrosWarnings.size.y, BACKGROUND_COLOR, window, self)
        self.communicationScreen.addBlock(faixaBackgroundBoxErrosWarningsEnd)

        lblWireless = Block("lblWireless", 86, lblCorTime.size.y, screenDivisionRightMargin.pos.x+24, gameMiniMap.pos.y, BACKGROUND_COLOR, window, self)
        lblWireless.setText("Wireless", BLACK_LABEL, 28, center=False)
        self.communicationScreen.addBlock(lblWireless)

        boxWireless = Block("boxWireless", boxErrosWarnings.size.x-16, boxErrosWarnings.size.y-35, lblWireless.pos.x, lblWireless.pos.y+lblWireless.size.y, BACKGROUND_COLOR, window, self, border=True)
        self.communicationScreen.addBlock(boxWireless)

        robotIDCommunicationComboBox = ComboBox("robotIDCommunicationComboBox", robotIDComboBox.size.x, robotIDComboBox.size.y, boxWireless.pos.x+20, boxWireless.pos.y+20, WHITE, window, self, "Robô ID")
        self.communicationScreen.addButton(robotIDCommunicationComboBox)
        robotIDCommunicationComboBox.addOptions(["Robô 00", "Robô 01", "Robô 02"])

        lblBateriaCommunication = Block("lblBateriaCommunication", lblBateria.size.x+6, lblBateria.size.y, robotIDCommunicationComboBox.pos.x+4, robotIDCommunicationComboBox.pos.y+robotIDCommunicationComboBox.size.y+20, BACKGROUND_COLOR, window, self)
        lblBateriaCommunication.setText("Bateria:", BLACK_LABEL, center=False)
        self.communicationScreen.addBlock(lblBateriaCommunication)

        percentBatteryCommunication = Block("percentBatteryCommunication", lblBateriaCommunication.size.x, lblBateriaCommunication.size.y, lblBateriaCommunication.pos.x+lblBateriaCommunication.size.x+5, lblBateriaCommunication.pos.y, BACKGROUND_COLOR, window, self)
        percentBatteryCommunication.setText("100%", center=False)
        self.communicationScreen.addBlock(percentBatteryCommunication)

        lblStatusWireless = Block("lblStatusWireless", lblBateriaCommunication.size.x, lblBateriaCommunication.size.y, percentBatteryCommunication.pos.x+340, lblBateriaCommunication.pos.y, BACKGROUND_COLOR, window, self)
        lblStatusWireless.setText("Status:", BLACK_LABEL, center=False)
        self.communicationScreen.addBlock(lblStatusWireless)

        valueStatusWireless = Block("valueStatusWireless", lblStatusWireless.size.x+50, lblStatusWireless.size.y, lblStatusWireless.pos.x+lblStatusWireless.size.x+10, lblStatusWireless.pos.y, BACKGROUND_COLOR, window, self)
        valueStatusWireless.setText("Conectado", center=False)
        self.communicationScreen.addBlock(valueStatusWireless)

        lblVelocidadeEnviada = Block("lblVelocidadeEnviada", lblBateriaCommunication.size.x*2.5-4, lblBateriaCommunication.size.y, lblBateriaCommunication.pos.x, lblBateriaCommunication.pos.y+lblBateriaCommunication.size.y+10, BACKGROUND_COLOR, window, self)
        lblVelocidadeEnviada.setText("Velocidade enviada", BLACK_LABEL, center=False)
        self.communicationScreen.addBlock(lblVelocidadeEnviada)

        valueVelocidadeEnviada = Block("valueVelocidadeEnviada", lblBateriaCommunication.size.x*2.5, lblVelocidadeEnviada.size.y, lblVelocidadeEnviada.pos.x+lblVelocidadeEnviada.size.x+30, lblVelocidadeEnviada.pos.y, BACKGROUND_COLOR, window, self)
        valueVelocidadeEnviada.setText("v: 0.0   w: 0.0", center=False)
        self.communicationScreen.addBlock(valueVelocidadeEnviada)

        lblFrequenciaEnvio = Block("lblFrequenciaEnvio", lblVelocidadeEnviada.size.x+4, lblVelocidadeEnviada.size.y, lblVelocidadeEnviada.pos.x, lblVelocidadeEnviada.pos.y+lblVelocidadeEnviada.size.y+10, BACKGROUND_COLOR, window, self)
        lblFrequenciaEnvio.setText("Frequência de envio", BLACK_LABEL, center=False)
        self.communicationScreen.addBlock(lblFrequenciaEnvio)

        valueFrequenciaEnvio = Block("valueFrequenciaEnvio", percentBatteryCommunication.size.x+44, percentBatteryCommunication.size.y, valueVelocidadeEnviada.pos.x, lblFrequenciaEnvio.pos.y, BACKGROUND_COLOR, window, self)
        valueFrequenciaEnvio.setText("2 MHz", center=False)
        self.communicationScreen.addBlock(valueFrequenciaEnvio)

        linhaBaixoBoxWireless = Block("linhaBaixoBoxWireless", boxWireless.size.x, 2, boxWireless.pos.x, boxWireless.pos.y+boxWireless.size.y, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaBaixoBoxWireless)

        faixaBackgroundWirelessReferee = Block("faixaBackgroundWirelessReferee", screenDivisionRightMargin.size.x, 50, screenDivisionRightMargin.pos.x, boxWireless.pos.y+boxWireless.size.y, BACKGROUND_COLOR, window, self)
        self.communicationScreen.addBlock(faixaBackgroundWirelessReferee)

        lblReferee = Block("lblReferee", lblWireless.size.x-10, lblWireless.size.y, lblWireless.pos.x, boxWireless.pos.y+boxWireless.size.y+20, BACKGROUND_COLOR, window, self)
        lblReferee.setText("Referee", BLACK_LABEL, 28, center=False)
        self.communicationScreen.addBlock(lblReferee)

        boxReferee = Block("boxReferee", boxWireless.size.x, boxWireless.size.y*0.7, boxWireless.pos.x, lblReferee.pos.y+lblReferee.size.y, BACKGROUND_COLOR, window, self, border=True)
        self.communicationScreen.addBlock(boxReferee)

        linhaCimaBoxReferee = Block("linhaCimaBoxReferee", boxReferee.size.x, 2, boxReferee.pos.x, boxReferee.pos.y, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaCimaBoxReferee)

        lblComandoRecebido = Block("lblComandoRecebido", lblFrequenciaEnvio.size.x-6, lblFrequenciaEnvio.size.y, boxReferee.pos.x+20, boxReferee.pos.y+20, BACKGROUND_COLOR, window, self)
        lblComandoRecebido.setText("Comando recebido:", BLACK_LABEL, center=False)
        self.communicationScreen.addBlock(lblComandoRecebido)

        valueComandoRecebido = Block("valueComandoRecebido", valueVelocidadeEnviada.size.x-10, valueVelocidadeEnviada.size.y, lblComandoRecebido.pos.x+lblComandoRecebido.size.x+40, lblComandoRecebido.pos.y, BACKGROUND_COLOR, window, self)
        valueComandoRecebido.setText("HALT", center=False)
        self.communicationScreen.addBlock(valueComandoRecebido)

        lblStatusReferee = Block("lblStatusReferee", lblStatusWireless.size.x, lblStatusWireless.size.y, lblStatusWireless.pos.x, lblComandoRecebido.pos.y, BACKGROUND_COLOR, window, self)
        lblStatusReferee.setText("Status:", BLACK_LABEL, center=False)
        self.communicationScreen.addBlock(lblStatusReferee)

        valueStatusReferee = Block("valueStatusReferee", valueStatusWireless.size.x, valueStatusWireless.size.y, valueStatusWireless.pos.x, lblStatusReferee.pos.y, BACKGROUND_COLOR, window, self)
        valueStatusReferee.setText("Desconectado", center=False)
        self.communicationScreen.addBlock(valueStatusReferee)

        lblLadoCampoReferee = Block("lblLadoCampoReferee", lblComandoRecebido.size.x-26, lblComandoRecebido.size.y, lblComandoRecebido.pos.x, lblComandoRecebido.pos.y+lblComandoRecebido.size.y+10, BACKGROUND_COLOR, window, self)
        lblLadoCampoReferee.setText("Lado do campo:", BLACK_LABEL, center=False)
        self.communicationScreen.addBlock(lblLadoCampoReferee)

        valueLadoCampoReferee = Block("valueLadoCampoReferee", valueStatusReferee.size.x, valueStatusReferee.size.y, valueComandoRecebido.pos.x, lblLadoCampoReferee.pos.y, BACKGROUND_COLOR, window, self)
        valueLadoCampoReferee.setText("Esquerdo", center=False)
        self.communicationScreen.addBlock(valueLadoCampoReferee)

        lblCorTimeReferee = Block("lblCorTimeReferee", lblLadoCampoReferee.size.x-36, lblLadoCampoReferee.size.y, lblLadoCampoReferee.pos.x, lblLadoCampoReferee.pos.y+lblLadoCampoReferee.size.y+10, BACKGROUND_COLOR, window, self)
        lblCorTimeReferee.setText("Cor do time:", BLACK_LABEL, center=False)
        self.communicationScreen.addBlock(lblCorTimeReferee)

        valueCorTimeReferee = Block("valueCorTimeReferee", 0, lblCorTimeReferee.size.y, valueLadoCampoReferee.pos.x, lblCorTimeReferee.pos.y, BACKGROUND_COLOR, window, self)
        valueCorTimeReferee.setText("Amarelo", center=False)
        self.communicationScreen.addBlock(valueCorTimeReferee)

        linhaBaixoBoxReferee = Block("linhaBaixoBoxReferee", boxReferee.size.x, 2, boxReferee.pos.x, boxReferee.pos.y+boxReferee.size.y, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaBaixoBoxReferee)

        faixaBackgroundRefereeVSSVision = Block("faixaBackgroundRefereeVSSVision", screenDivisionRightMargin.size.x, 50, screenDivisionRightMargin.pos.x, boxReferee.pos.y+boxReferee.size.y, BACKGROUND_COLOR, window, self)
        self.communicationScreen.addBlock(faixaBackgroundRefereeVSSVision)

        lblVSSVision = Block("lblVSSVision", lblReferee.size.x, lblReferee.size.y, lblReferee.pos.x, boxReferee.pos.y+boxReferee.size.y+20, BACKGROUND_COLOR, window, self)
        lblVSSVision.setText("VSS-VISION", BLACK_LABEL, 28, center=False)
        self.communicationScreen.addBlock(lblVSSVision)

        boxVSSVision = Block("boxVSSVision", boxReferee.size.x, boxWireless.size.y, boxReferee.pos.x, lblVSSVision.pos.y+lblVSSVision.size.y, BACKGROUND_COLOR, window, self, border=True, preference=False)
        self.communicationScreen.addBlock(boxVSSVision)

        linhaCimaBoxVSSVision = Block("linhaCimaBoxVSSVision", boxVSSVision.size.x, 2, boxVSSVision.pos.x, boxVSSVision.pos.y, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaCimaBoxVSSVision)

        vssVisionScrollPanel = ScrollingBackground("vssVisionScrollPanel", boxVSSVision.size.x-4, boxVSSVision.size.y*1.9, boxVSSVision.pos.x+2, boxVSSVision.pos.y+2, BACKGROUND_COLOR, window, self, boxVSSVision.size.y, boxVSSVision.pos.y+2, preference=False)
        self.communicationScreen.addScrollingBackground(vssVisionScrollPanel)

        lblCorTimeVSSVision = Block("lblCorTimeVSSVision", lblCorTimeReferee.size.x, lblCorTimeReferee.size.y, lblCorTimeReferee.pos.x, boxVSSVision.pos.y+20, BACKGROUND_COLOR, window, self)
        lblCorTimeVSSVision.setText("Time Azul", BLACK_LABEL, center=False)
        vssVisionScrollPanel.addBlock(lblCorTimeVSSVision)

        lblID0VSSVision = Block("lblID0VSSVision", lblCorTimeVSSVision.size.x, lblCorTimeVSSVision.size.y, lblCorTimeVSSVision.pos.x, lblCorTimeVSSVision.pos.y+lblCorTimeVSSVision.size.y, BACKGROUND_COLOR, window, self)
        lblID0VSSVision.setText("ID 0", BLACK_LABEL, center=False)
        vssVisionScrollPanel.addBlock(lblID0VSSVision)

        lblStatusVSSVision = Block("lblStatusVSSVision", lblStatusReferee.size.x, lblStatusReferee.size.y, lblStatusReferee.pos.x, lblCorTimeVSSVision.pos.y, BACKGROUND_COLOR, window, self)
        lblStatusVSSVision.setText("Status:", BLACK_LABEL, center=False)
        vssVisionScrollPanel.addBlock(lblStatusVSSVision)
        
        valueStatusVSSVision = Block("valueStatusVSSVision", valueStatusReferee.size.x, valueStatusReferee.size.y, valueStatusReferee.pos.x, lblStatusVSSVision.pos.y, BACKGROUND_COLOR, window, self)
        valueStatusVSSVision.setText("Conectado", center=False)
        vssVisionScrollPanel.addBlock(valueStatusVSSVision)

        lblPosicaoID0VSSVision = Block("lblPosicaoID0VSSVision", lblID0VSSVision.size.x, lblID0VSSVision.size.y, lblID0VSSVision.pos.x+10, lblID0VSSVision.pos.y+lblID0VSSVision.size.y, BACKGROUND_COLOR, window, self)
        lblPosicaoID0VSSVision.setText("Posição", BLACK_LABEL, center=False)
        vssVisionScrollPanel.addBlock(lblPosicaoID0VSSVision)

        valuePosicaoID0VSSVision = Block("valuePosicaoID0VSSVision", lblPosicaoID0VSSVision.size.x*2, lblPosicaoID0VSSVision.size.y, valueComandoRecebido.pos.x-10, lblPosicaoID0VSSVision.pos.y, BACKGROUND_COLOR, window, self)
        valuePosicaoID0VSSVision.setText("x: 0.0  y: 0.0  z: 0.0 th: 0.0", center=False)
        vssVisionScrollPanel.addBlock(valuePosicaoID0VSSVision)

        lblVelocidadeID0VSSVision = Block("lblVelocidadeID0VSSVision", lblPosicaoID0VSSVision.size.x, lblPosicaoID0VSSVision.size.y, lblPosicaoID0VSSVision.pos.x, lblPosicaoID0VSSVision.pos.y+lblPosicaoID0VSSVision.size.y, BACKGROUND_COLOR, window, self)
        lblVelocidadeID0VSSVision.setText("Velocidade", BLACK_LABEL, center=False)
        vssVisionScrollPanel.addBlock(lblVelocidadeID0VSSVision)

        valueVelocidadeID0VSSVision = Block("valueVelocidadeID0VSSVision", valuePosicaoID0VSSVision.size.x, valuePosicaoID0VSSVision.size.y, valuePosicaoID0VSSVision.pos.x, lblVelocidadeID0VSSVision.pos.y, BACKGROUND_COLOR, window, self)
        valueVelocidadeID0VSSVision.setText("v: 0.0  w: 0.0", center=False)
        vssVisionScrollPanel.addBlock(valueVelocidadeID0VSSVision)

        lblID1VSSVision = Block("lblID1VSSVision", lblCorTimeVSSVision.size.x, lblCorTimeVSSVision.size.y, lblCorTimeVSSVision.pos.x, lblVelocidadeID0VSSVision.pos.y+lblVelocidadeID0VSSVision.size.y+20, BACKGROUND_COLOR, window, self)
        lblID1VSSVision.setText("ID 1", BLACK_LABEL, center=False)
        vssVisionScrollPanel.addBlock(lblID1VSSVision)

        lblPosicaoID1VSSVision = Block("lblPosicaoID1VSSVision", lblID1VSSVision.size.x, lblID1VSSVision.size.y, lblID1VSSVision.pos.x+10, lblID1VSSVision.pos.y+lblID1VSSVision.size.y, BACKGROUND_COLOR, window, self)
        lblPosicaoID1VSSVision.setText("Posição", BLACK_LABEL, center=False)
        vssVisionScrollPanel.addBlock(lblPosicaoID1VSSVision)

        valuePosicaoID1VSSVision = Block("valuePosicaoID1VSSVision", lblPosicaoID1VSSVision.size.x*2, lblPosicaoID1VSSVision.size.y, valueComandoRecebido.pos.x-10, lblPosicaoID1VSSVision.pos.y, BACKGROUND_COLOR, window, self)
        valuePosicaoID1VSSVision.setText("x: 0.0  y: 0.0  z: 0.0 th: 0.0", center=False)
        vssVisionScrollPanel.addBlock(valuePosicaoID1VSSVision)

        lblVelocidadeID1VSSVision = Block("lblVelocidadeID1VSSVision", lblPosicaoID1VSSVision.size.x, lblPosicaoID1VSSVision.size.y, lblPosicaoID1VSSVision.pos.x, lblPosicaoID1VSSVision.pos.y+lblPosicaoID1VSSVision.size.y, BACKGROUND_COLOR, window, self)
        lblVelocidadeID1VSSVision.setText("Velocidade", BLACK_LABEL, center=False)
        vssVisionScrollPanel.addBlock(lblVelocidadeID1VSSVision)

        valueVelocidadeID1VSSVision = Block("valueVelocidadeID1VSSVision", valuePosicaoID1VSSVision.size.x, valuePosicaoID1VSSVision.size.y, valuePosicaoID1VSSVision.pos.x, lblVelocidadeID1VSSVision.pos.y, BACKGROUND_COLOR, window, self)
        valueVelocidadeID1VSSVision.setText("v: 0.0  w: 0.0", center=False)
        vssVisionScrollPanel.addBlock(valueVelocidadeID1VSSVision)

        lblID2VSSVision = Block("lblID2VSSVision", lblCorTimeVSSVision.size.x, lblCorTimeVSSVision.size.y, lblCorTimeVSSVision.pos.x, lblVelocidadeID1VSSVision.pos.y+lblVelocidadeID1VSSVision.size.y+20, BACKGROUND_COLOR, window, self)
        lblID2VSSVision.setText("ID 2", BLACK_LABEL, center=False)
        vssVisionScrollPanel.addBlock(lblID2VSSVision)

        lblPosicaoID2VSSVision = Block("lblPosicaoID2VSSVision", lblID2VSSVision.size.x, lblID2VSSVision.size.y, lblID2VSSVision.pos.x+10, lblID2VSSVision.pos.y+lblID2VSSVision.size.y, BACKGROUND_COLOR, window, self)
        lblPosicaoID2VSSVision.setText("Posição", BLACK_LABEL, center=False)
        vssVisionScrollPanel.addBlock(lblPosicaoID2VSSVision)

        valuePosicaoID2VSSVision = Block("valuePosicaoID2VSSVision", lblPosicaoID2VSSVision.size.x*2, lblPosicaoID2VSSVision.size.y, valueComandoRecebido.pos.x-10, lblPosicaoID2VSSVision.pos.y, BACKGROUND_COLOR, window, self)
        valuePosicaoID2VSSVision.setText("x: 0.0  y: 0.0  z: 0.0 th: 0.0", center=False)
        vssVisionScrollPanel.addBlock(valuePosicaoID2VSSVision)

        lblVelocidadeID2VSSVision = Block("lblVelocidadeID2VSSVision", lblPosicaoID2VSSVision.size.x, lblPosicaoID2VSSVision.size.y, lblPosicaoID2VSSVision.pos.x, lblPosicaoID2VSSVision.pos.y+lblPosicaoID2VSSVision.size.y, BACKGROUND_COLOR, window, self)
        lblVelocidadeID2VSSVision.setText("Velocidade", BLACK_LABEL, center=False)
        vssVisionScrollPanel.addBlock(lblVelocidadeID2VSSVision)

        valueVelocidadeID2VSSVision = Block("valueVelocidadeID2VSSVision", valuePosicaoID2VSSVision.size.x, valuePosicaoID2VSSVision.size.y, valuePosicaoID2VSSVision.pos.x, lblVelocidadeID2VSSVision.pos.y, BACKGROUND_COLOR, window, self)
        valueVelocidadeID2VSSVision.setText("v: 0.0  w: 0.0", center=False)
        vssVisionScrollPanel.addBlock(valueVelocidadeID2VSSVision)

        faixaBackgroundBoxVSSVisionEnd = Block("faixaBackgroundBoxVSSVisionEnd", screenDivisionRightMargin.size.x, 50, screenDivisionRightMargin.pos.x, boxVSSVision.pos.y+boxVSSVision.size.y, BACKGROUND_COLOR, window, self)
        self.communicationScreen.addBlock(faixaBackgroundBoxVSSVisionEnd)

        linhaBaixoBoxVSSVision = Block("linhaBaixoBoxVSSVision", boxVSSVision.size.x, 2, boxVSSVision.pos.x, boxVSSVision.pos.y+boxVSSVision.size.y-2, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaBaixoBoxVSSVision)

        # Draw the navigationScreen
        self.activeScreen.draw()


       # Instance button methods 
        def changeToNavigationScreen(self):
            """Instance method of navegacaoButton to make the button change the screen to the navigation screen"""
            #window = pg.display.set_mode((int(windowSize.x), int(windowSize.y))) 
            # perhaps is better to fill the screen towards doing this
            self.window.fill(BACKGROUND_COLOR)
            window.fill(BACKGROUND_COLOR)
            if self.gui.activeScreen != self.gui.navigationScreen:
                self.gui.activeScreen = self.gui.navigationScreen
            self.gui.activeScreen.menuBar.buttons[navegacaoButton.name].color = BORDER_COLOR
            self.gui.activeScreen.menuBar.buttons[movimentacaoButton.name].color = BACKGROUND_COLOR
            self.gui.activeScreen.menuBar.buttons[comunicacaoButton.name].color = BACKGROUND_COLOR
            self.gui.activeScreen.draw()
        
        def changeToMovementScreen(self):
            """Instance method of movimentacaoButton to make the button change the screen to the movement screen"""
            #window = pg.display.set_mode((int(windowSize.x), int(windowSize.y))) 
            # perhaps is better to fill the screen towards doing this
            self.window.fill(BACKGROUND_COLOR)
            window.fill(BACKGROUND_COLOR)
            if self.gui.activeScreen != self.gui.movementScreen:
                self.gui.activeScreen = self.gui.movementScreen
            self.gui.activeScreen.menuBar.buttons[navegacaoButton.name].color = BACKGROUND_COLOR
            self.gui.activeScreen.menuBar.buttons[movimentacaoButton.name].color = BORDER_COLOR
            self.gui.activeScreen.menuBar.buttons[comunicacaoButton.name].color = BACKGROUND_COLOR
            self.gui.activeScreen.draw()
        
        def changeToCommunicationScreen(self):
            """Instance method of comunicacaoButton to make the button change the screen to the communication screen"""
            #window = pg.display.set_mode((int(windowSize.x), int(windowSize.y))) 
            # perhaps is better to fill the screen towards doing this
            self.window.fill(BACKGROUND_COLOR)
            window.fill(BACKGROUND_COLOR)
            if self.gui.activeScreen != self.gui.communicationScreen:
                self.gui.activeScreen = self.gui.communicationScreen
            self.gui.activeScreen.menuBar.buttons[navegacaoButton.name].color = BACKGROUND_COLOR
            self.gui.activeScreen.menuBar.buttons[movimentacaoButton.name].color = BACKGROUND_COLOR
            self.gui.activeScreen.menuBar.buttons[comunicacaoButton.name].color = BORDER_COLOR
            self.gui.activeScreen.draw()

        def closeWindow(self):
            """Instance method of closeButton to make the application stop running and close the window"""
            if self.gui.unbrain_loop is not None:
                self.gui.unbrain_loop.handle_SIGINT(None, None, shut_down=True)
                self.gui.unbrain_loop = None
                print("UnBrain stopped")
            self.gui.running = False

        def minimizeWindow(self):
            """Instance method of minimizeButton to minimize the window of the application"""
            pg.display.iconify()

        def maximizeWindow(self):
            """Instance method of maximizeButton to minimize the window of the application"""
            pg.display.toggle_fullscreen()

        def showOptionsColorComboBox(self):
            """Instance method to show the color options in the chooseColorComboBox"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)
        
        def chooseOptionColorComboBox(self):
            """Instance method to choose the option in chooseColorComboBox"""
            if self.getText() == "Azul" and self.screen.buttons[inversaoToggleButton.name].isOn():
                self.screen.buttons[inversaoToggleButton.name].action()
            elif self.getText() == "Amarelo" and not self.screen.buttons[inversaoToggleButton.name].isOn():
                self.screen.buttons[inversaoToggleButton.name].action()
            self.screen.buttons[chooseColorComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[chooseColorComboBox.name].setOptionsVisibility(False)

        def changeSide(self):
            """Instance method to change the state of inversaoToggleButton"""
            self.changeState()
            self.imgs[self.isOn()]
            if self.isOn():    
                self.screen.blocks[lblDireitoOuEsquerdo.name].setText("Direito", center=True)
                self.gui.navigationScreen.blocks[lblLadoEsquerdo.name].setText("Lado inimigo", center=True)
                self.gui.navigationScreen.blocks[lblLadoDireito.name].setText("Lado aliado", center=True)
                self.gui.navigationScreen.blocks[arrow.name].setImage("images/arrow_inverted.png")
            else:
                self.screen.blocks[lblDireitoOuEsquerdo.name].setText("Esquerdo", center=True)
                self.gui.navigationScreen.blocks[lblLadoEsquerdo.name].setText("Lado aliado", center=True)
                self.gui.navigationScreen.blocks[lblLadoDireito.name].setText("Lado inimigo", center=True)
                self.gui.navigationScreen.blocks[arrow.name].setImage("images/arrow.png")

        def showOptionsTypeEntityComboBox(self):
            """Instance method to show the type options in chooseEntityTypeComboBox"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)

        def chooseOptionTypeEntityComboBox(self):
            """Instance method to choose the option in the chooseEntityTypeComboBox"""
            self.screen.buttons[chooseEntityTypeComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[chooseEntityTypeComboBox.name].setOptionsVisibility(False)

        def showOptionsNumRobotsComboBox(self):
            """Instance method to show the num robots options in chooseNumRobotsComboBox"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)

        def chooseOptionNumRobotsComboBox(self):
            """Instance method to choose the option in the chooseNumRobotsComboBox"""
            self.screen.buttons[chooseNumRobotsComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[chooseNumRobotsComboBox.name].setOptionsVisibility(False)

        def showOptionsRobotIDComboBox(self):
            """Instance method to show the type options in robotIDComboBox"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)

        def chooseOptionRobotIDComboBox(self):
            """Instance method to choose the option in the robotIDComboBox"""
            self.screen.buttons[robotIDComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[robotIDComboBox.name].setOptionsVisibility(False)

        def changeManualVirtualPos(self):
            """Instance method to change the state of virtualJudgeToggleButton"""
            self.changeState()
            self.imgs[self.isOn()]

        def showOptionsPositioningComboBox(self):
            """Instance method to show the positioning options in positioningComboBox"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)

        def expandUVFScreen(self):
            """Instance method to expand the UVFScreen"""
            resizeRange = self.screen.scrollingBackgrounds[UVFScreen.name].size.y
            visible = True
            if self.isOn():
                resizeRange *= -1
                visible = False
            self.changeState()
            self.screen.size.y += resizeRange
            self.screen.scrollingBackgrounds[projecoesScreen.name].pos.y += resizeRange
            self.screen.buttons[projecoesButton.name].pos.y += resizeRange
            for block in self.screen.scrollingBackgrounds[projecoesScreen.name].blocks.values():
                block.pos.y += resizeRange
            for button in self.screen.scrollingBackgrounds[projecoesScreen.name].buttons.values():
                button.pos.y += resizeRange
            self.screen.scrollingBackgrounds[UVFScreen.name].setVisible(visible)

        def chooseOptionRobotIDUVFComboBox(self):
            """Instance method to choose the option in the robotIDUVFComboBox"""
            self.screen.buttons[robotIDUVFComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[robotIDUVFComboBox.name].setOptionsVisibility(False)

        def editScoreQuant(self):
            """Instance method to edit the number in txtQuantPontos TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtQuantPontos.name].calcLimit()

        def increaseScoreQuant(self):
            """Instance method to increase the number in quantPontos TextField"""
            self.screen.buttons[txtQuantPontos.name].setText(str(int(self.screen.buttons[txtQuantPontos.name].getText())+1), center=True)
            self.screen.buttons[txtQuantPontos.name].calcLimit()

        def decreaseScoreQuant(self):
            """Instance method to decrease the number in quantPontos TextField"""
            self.screen.buttons[txtQuantPontos.name].setText(str(int(self.screen.buttons[txtQuantPontos.name].getText())-1), center=True)
            self.screen.buttons[txtQuantPontos.name].calcLimit()

        def showFieldComboBox(self):
            """Instance method to show the field options in selectFieldComboBox"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)

        def chooseFieldComboBox(self):
            """Instance method to choose the option in the selectFieldComboBox"""
            self.screen.buttons[selectFieldComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[selectFieldComboBox.name].setOptionsVisibility(False)

        def changePontoFinal(self):
            """Instance method to change the state of pontoFinalSelecToggleButton"""
            self.changeState()
            self.imgs[self.isOn()]

        def editRaioQuant(self):
            """Instance method to edit the number in txtRaio TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtRaio.name].calcLimit()

        def increaseRaioQuant(self):
            """Instance method to increase the number in txtRaio TextField"""
            self.screen.buttons[txtRaio.name].setText(str(int(self.screen.buttons[txtRaio.name].getText())+1), center=True)
            self.screen.buttons[txtRaio.name].calcLimit()

        def decreaseRaioQuant(self):
            """Instance method to decrease the number in txtRaio TextField"""
            self.screen.buttons[txtRaio.name].setText(str(int(self.screen.buttons[txtRaio.name].getText())-1), center=True)
            self.screen.buttons[txtRaio.name].calcLimit()

        def editConstSuavQuant(self):
            """Instance method to edit the number in txtConstSuav TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtConstSuav.name].calcLimit()

        def increaseConstSuavQuant(self):
            """Instance method to increase the number in txtConstSuav TextField"""
            self.screen.buttons[txtConstSuav.name].setText(str(int(self.screen.buttons[txtConstSuav.name].getText())+1), center=True)
            self.screen.buttons[txtConstSuav.name].calcLimit()

        def decreaseConstSuavQuant(self):
            """Instance method to decrease the number in txtConstSuav TextField"""
            self.screen.buttons[txtConstSuav.name].setText(str(int(self.screen.buttons[txtConstSuav.name].getText())-1), center=True)
            self.screen.buttons[txtConstSuav.name].calcLimit()

        def editConstSuavUnidirQuant(self):
            """Instance method to edit the number in txtConstSuavUnidir TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtConstSuavUnidir.name].calcLimit()

        def increaseConstSuavUnidirQuant(self):
            """Instance method to increase the number in txtConstSuavUnidir TextField"""
            self.screen.buttons[txtConstSuavUnidir.name].setText(str(int(self.screen.buttons[txtConstSuavUnidir.name].getText())+1), center=True)
            self.screen.buttons[txtConstSuavUnidir.name].calcLimit()

        def decreaseConstSuavUnidirQuant(self):
            """Instance method to decrease the number in txtConstSuavUnidir TextField"""
            self.screen.buttons[txtConstSuavUnidir.name].setText(str(int(self.screen.buttons[txtConstSuavUnidir.name].getText())-1), center=True)
            self.screen.buttons[txtConstSuavUnidir.name].calcLimit()

        def changeViewAllFields(self):
            """Instance method to change the state of visualizarTodosCamposToggleButton"""
            self.changeState()
            self.imgs[self.isOn()]

        def expandprojecoesScreen(self):
            """Instance method to expand the projecoesScreen"""
            resizeRange = self.screen.scrollingBackgrounds[projecoesScreen.name].size.y
            visible = True
            if self.isOn():
                resizeRange *= -1
                visible = False
            self.changeState()
            self.screen.size.y += resizeRange
            self.screen.scrollingBackgrounds[projecoesScreen.name].setVisible(visible)

        def chooseOptionRobotIDProjecoesComboBox(self):
            """Instance method to choose the option in the robotIDProjecoesComboBox"""
            self.screen.buttons[robotIDProjecoesComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[robotIDProjecoesComboBox.name].setOptionsVisibility(False)

        def editAtacGolBolaQuant(self):
            """Instance method to edit the number in txtAtacGolBola TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtAtacGolBola.name].calcLimit()

        def increaseAtacGolBolaQuant(self):
            """Instance method to increase the number in txtAtacGolBola TextField"""
            self.screen.buttons[txtAtacGolBola.name].setText(str(int(self.screen.buttons[txtAtacGolBola.name].getText())+1), center=True)
            self.screen.buttons[txtAtacGolBola.name].calcLimit()

        def decreaseAtacGolBolaQuant(self):
            """Instance method to decrease the number in txtAtacGolBola TextField"""
            self.screen.buttons[txtAtacGolBola.name].setText(str(int(self.screen.buttons[txtAtacGolBola.name].getText())-1), center=True)
            self.screen.buttons[txtAtacGolBola.name].calcLimit()

        def editZagAreaAliadaQuant(self):
            """Instance method to edit the number in txtZagAreaAliada TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtZagAreaAliada.name].calcLimit()

        def increaseZagAreaAliadaQuant(self):
            """Instance method to increase the number in txtZagAreaAliada TextField"""
            self.screen.buttons[txtZagAreaAliada.name].setText(str(int(self.screen.buttons[txtZagAreaAliada.name].getText())+1), center=True)
            self.screen.buttons[txtZagAreaAliada.name].calcLimit()

        def decreaseZagAreaAliadaQuant(self):
            """Instance method to decrease the number in txtZagAreaAliada TextField"""
            self.screen.buttons[txtZagAreaAliada.name].setText(str(int(self.screen.buttons[txtZagAreaAliada.name].getText())-1), center=True)
            self.screen.buttons[txtZagAreaAliada.name].calcLimit()

        def expandGraficosControleScreen(self):
            """Instance method to expand the graficosControleScreen"""
            resizeRange = self.screen.scrollingBackgrounds[graficosControleScreen.name].size.y
            visible = True
            if self.isOn():
                resizeRange *= -1
                visible = False
            self.changeState()
            self.screen.size.y += resizeRange
            self.screen.scrollingBackgrounds[controleManualScreen.name].pos.y += resizeRange
            self.screen.buttons[controleManualButton.name].pos.y += resizeRange
            for block in self.screen.scrollingBackgrounds[controleManualScreen.name].blocks.values():
                block.pos.y += resizeRange
            for button in self.screen.scrollingBackgrounds[controleManualScreen.name].buttons.values():
                button.pos.y += resizeRange
            self.screen.scrollingBackgrounds[controleUVFScreen.name].pos.y += resizeRange
            self.screen.buttons[controleUVFButton.name].pos.y += resizeRange
            for block in self.screen.scrollingBackgrounds[controleUVFScreen.name].blocks.values():
                block.pos.y += resizeRange
            for button in self.screen.scrollingBackgrounds[controleUVFScreen.name].buttons.values():
                button.pos.y += resizeRange
            self.screen.scrollingBackgrounds[graficosControleScreen.name].setVisible(visible)

        def chooseOptionRobotIDGraficosControleComboBox(self):
            """Instance method to choose the option in the robotIDGraficosControleComboBox"""
            self.screen.buttons[robotIDGraficosControleComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[robotIDGraficosControleComboBox.name].setOptionsVisibility(False)

        def expandControleManualScreen(self):
            """Instance method to expand the controleManualScreen"""
            resizeRange = self.screen.scrollingBackgrounds[controleManualScreen.name].size.y
            visible = True
            if self.isOn():
                resizeRange *= -1
                visible = False
            self.changeState()
            self.screen.size.y += resizeRange
            self.screen.scrollingBackgrounds[controleUVFScreen.name].pos.y += resizeRange
            self.screen.buttons[controleUVFButton.name].pos.y += resizeRange
            for block in self.screen.scrollingBackgrounds[controleUVFScreen.name].blocks.values():
                block.pos.y += resizeRange
            for button in self.screen.scrollingBackgrounds[controleUVFScreen.name].buttons.values():
                button.pos.y += resizeRange
            self.screen.scrollingBackgrounds[controleManualScreen.name].setVisible(visible)

        def chooseOptionRobotIDControleManualComboBox(self):
            """Instance method to choose the option in the robotIDControleManualComboBox"""
            self.screen.buttons[robotIDControleManualComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[robotIDControleManualComboBox.name].setOptionsVisibility(False)

        def changeEnableJoystick(self):
            """Instance method to change the state of enableJoystickToggleButton"""
            self.changeState()
            self.imgs[self.isOn()]

        def changeEnableDirection(self):
            """Instance method to change the state of enableDirectionToggleButton"""
            self.changeState()
            self.imgs[self.isOn()]

        def changeEnableManualControl(self):
            """Instance method to change the state of enableControleManualToggleButton"""
            self.changeState()
            self.imgs[self.isOn()]

        def showOptionsDirectionComboBox(self):
            """Instance method to show the positioning options in directionComboBox"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)

        def chooseOptionDirectionComboBox(self):
            """Instance method to choose the option in the directionComboBox"""
            self.screen.buttons[directionComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[directionComboBox.name].setOptionsVisibility(False)

        def expandControleUVFScreen(self):
            """Instance method to expand the controleUVFScreen"""
            resizeRange = self.screen.scrollingBackgrounds[controleUVFScreen.name].size.y
            visible = True
            if self.isOn():
                resizeRange *= -1
                visible = False
            self.changeState()
            self.screen.size.y += resizeRange
            self.screen.scrollingBackgrounds[controleUVFScreen.name].setVisible(visible)

        def slide(self):
            """Instance method to slide a Slider object"""
            self.setActive(True)

        def chooseOptionRobotIDControleUVFComboBox(self):
            """Instance method to choose the option in the robotIDControleUVFComboBox"""
            self.screen.buttons[robotIDControleUVFComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[robotIDControleUVFComboBox.name].setOptionsVisibility(False)

        def editKwQuant(self):
            """Instance method to edit the number in txtKw TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtKw.name].calcLimit()

        def increaseKwQuant(self):
            """Instance method to increase the number in txtKw TextField"""
            self.screen.buttons[txtKw.name].setText(str(int(self.screen.buttons[txtKw.name].getText())+1), center=True)
            self.screen.buttons[txtKw.name].calcLimit()

        def decreaseKwQuant(self):
            """Instance method to decrease the number in txtKw TextField"""
            self.screen.buttons[txtKw.name].setText(str(int(self.screen.buttons[txtKw.name].getText())-1), center=True)
            self.screen.buttons[txtKw.name].calcLimit()

        def editKpQuant(self):
            """Instance method to edit the number in txtKp TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtKp.name].calcLimit()

        def increaseKpQuant(self):
            """Instance method to increase the number in txtKp TextField"""
            self.screen.buttons[txtKp.name].setText(str(int(self.screen.buttons[txtKp.name].getText())+1), center=True)
            self.screen.buttons[txtKp.name].calcLimit()

        def decreaseKpQuant(self):
            """Instance method to decrease the number in txtKp TextField"""
            self.screen.buttons[txtKp.name].setText(str(int(self.screen.buttons[txtKp.name].getText())-1), center=True)
            self.screen.buttons[txtKp.name].calcLimit()

        def editLQuant(self):
            """Instance method to edit the number in txtL TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtL.name].calcLimit()

        def increaseLQuant(self):
            """Instance method to increase the number in txtL TextField"""
            self.screen.buttons[txtL.name].setText(str(int(self.screen.buttons[txtL.name].getText())+1), center=True)
            self.screen.buttons[txtL.name].calcLimit()

        def decreaseLQuant(self):
            """Instance method to decrease the number in txtL TextField"""
            self.screen.buttons[txtL.name].setText(str(int(self.screen.buttons[txtL.name].getText())-1), center=True)
            self.screen.buttons[txtL.name].calcLimit()

        def editVmaxQuant(self):
            """Instance method to edit the number in txtVmax TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtVmax.name].calcLimit()

        def increaseVmaxQuant(self):
            """Instance method to increase the number in txtVmax TextField"""
            self.screen.buttons[txtVmax.name].setText(str(int(self.screen.buttons[txtVmax.name].getText())+1), center=True)
            self.screen.buttons[txtVmax.name].calcLimit()

        def decreaseVmaxQuant(self):
            """Instance method to decrease the number in txtVmax TextField"""
            self.screen.buttons[txtVmax.name].setText(str(int(self.screen.buttons[txtVmax.name].getText())-1), center=True)
            self.screen.buttons[txtVmax.name].calcLimit()

        def editMuQuant(self):
            """Instance method to edit the number in txtMu TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtMu.name].calcLimit()

        def increaseMuQuant(self):
            """Instance method to increase the number in txtMu TextField"""
            self.screen.buttons[txtMu.name].setText(str(int(self.screen.buttons[txtMu.name].getText())+1), center=True)
            self.screen.buttons[txtMu.name].calcLimit()

        def decreaseMuQuant(self):
            """Instance method to decrease the number in txtMu TextField"""
            self.screen.buttons[txtMu.name].setText(str(int(self.screen.buttons[txtMu.name].getText())-1), center=True)
            self.screen.buttons[txtMu.name].calcLimit()

        def editVrefQuant(self):
            """Instance method to edit the number in txtVref TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtVref.name].calcLimit()

        def increaseVrefQuant(self):
            """Instance method to increase the number in txtVref TextField"""
            self.screen.buttons[txtVref.name].setText(str(int(self.screen.buttons[txtVref.name].getText())+1), center=True)
            self.screen.buttons[txtVref.name].calcLimit()

        def decreaseVrefQuant(self):
            """Instance method to decrease the number in txtVref TextField"""
            self.screen.buttons[txtVref.name].setText(str(int(self.screen.buttons[txtVref.name].getText())-1), center=True)
            self.screen.buttons[txtVref.name].calcLimit()

        def editRQuant(self):
            """Instance method to edit the number in txtR TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtR.name].calcLimit()

        def increaseRQuant(self):
            """Instance method to increase the number in txtR TextField"""
            self.screen.buttons[txtR.name].setText(str(int(self.screen.buttons[txtR.name].getText())+1), center=True)
            self.screen.buttons[txtR.name].calcLimit()

        def decreaseRQuant(self):
            """Instance method to decrease the number in txtR TextField"""
            self.screen.buttons[txtR.name].setText(str(int(self.screen.buttons[txtR.name].getText())-1), center=True)
            self.screen.buttons[txtR.name].calcLimit()

        def editMaxAngErrorQuant(self):
            """Instance method to edit the number in txtMaxAngError TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtMaxAngError.name].calcLimit()

        def increaseMaxAngErrorQuant(self):
            """Instance method to increase the number in txtMaxAngError TextField"""
            self.screen.buttons[txtMaxAngError.name].setText(str(int(self.screen.buttons[txtMaxAngError.name].getText())+1), center=True)
            self.screen.buttons[txtMaxAngError.name].calcLimit()

        def decreaseMaxAngErrorQuant(self):
            """Instance method to decrease the number in txtMaxAngError TextField"""
            self.screen.buttons[txtMaxAngError.name].setText(str(int(self.screen.buttons[txtMaxAngError.name].getText())-1), center=True)
            self.screen.buttons[txtMaxAngError.name].calcLimit()

        def editTauQuant(self):
            """Instance method to edit the number in txtTau TextField"""
            self.setActive(not self.isActive())
            self.screen.buttons[txtTau.name].calcLimit()

        def increaseTauQuant(self):
            """Instance method to increase the number in txtTau TextField"""
            self.screen.buttons[txtTau.name].setText(str(int(self.screen.buttons[txtTau.name].getText())+1), center=True)
            self.screen.buttons[txtTau.name].calcLimit()

        def decreaseTauQuant(self):
            """Instance method to decrease the number in txtTau TextField"""
            self.screen.buttons[txtTau.name].setText(str(int(self.screen.buttons[txtTau.name].getText())-1), center=True)
            self.screen.buttons[txtTau.name].calcLimit()

        def chooseOptionRobotIDCommunicationComboBox(self):
            """Instance method to choose the option in the robotIDCommunicationComboBox"""
            self.screen.buttons[robotIDCommunicationComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[robotIDCommunicationComboBox.name].setOptionsVisibility(False)
        








        def play(self):
            if self.gui.unbrain_loop is None:
                teamColor = False if self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[chooseColorComboBox.name].getText() == "Azul" else True

                mirror = True if (teamColor == False and self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[inversaoToggleButton.name].isOn()) or (teamColor == True and self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[inversaoToggleButton.name].isOn()) else False

                numRobots = [int(e) for e in self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[chooseNumRobotsComboBox.name].getText().split(", ")]

                entitiesType = self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[chooseEntityTypeComboBox.name].getText()
                if entitiesType == "Entidades estáticas":
                    self.gui.unbrain_loop = Loop(team_yellow=teamColor, mirror=mirror, n_robots=numRobots, static_entities=True, vssvision=True)

                elif entitiesType == "Control Tester":
                    self.gui.unbrain_loop = Loop(team_yellow=teamColor, mirror=mirror, n_robots=numRobots, control=True, vssvision=True)
                    
                else:
                    self.gui.unbrain_loop = Loop(team_yellow=teamColor, mirror=mirror, n_robots=numRobots, vssvision=True)
                
                self.gui.unbrain_thread = threading.Thread(target=self.gui.unbrain_loop.run)
                self.gui.unbrain_thread.daemon = True
                self.gui.unbrain_thread.start()

            elif loop.unbrain_paused:
                loop.unbrain_paused = False
                print("UnBrain resumed")

            else:
                print("Nothing happened")

        self.navigationScreen.menuBar.buttons[playButton.name].actionAssign(play)


        def pause(self):
            if self.gui.unbrain_loop is not None and not loop.unbrain_paused:
                loop.unbrain_paused = True
                print("UnBrain paused")
            else:
                print("Nothing happened")

        self.navigationScreen.menuBar.buttons[pauseButton.name].actionAssign(pause)


        def stop(self):
            if self.gui.unbrain_loop is not None:
                self.gui.unbrain_loop.handle_SIGINT(None, None, shut_down=True)
                self.gui.unbrain_loop = None
                loop.unbrain_paused = False
                print("UnBrain stopped")
            else:
                print("Nothing happened")

        self.navigationScreen.menuBar.buttons[stopButton.name].actionAssign(stop)


        def play_firasim(self):
            if self.gui.unbrain_loop is None:
                teamColor = False if self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[chooseColorComboBox.name].getText() == "Azul" else True

                mirror = True if (teamColor == False and self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[inversaoToggleButton.name].isOn()) or (teamColor == True and self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[inversaoToggleButton.name].isOn()) else False

                numRobots = [int(e) for e in self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[chooseNumRobotsComboBox.name].getText().split(", ")]

                entitiesType = self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[chooseEntityTypeComboBox.name].getText()
                if entitiesType == "Entidades estáticas":
                    self.gui.unbrain_loop = Loop(team_yellow=teamColor, mirror=mirror, n_robots=numRobots, static_entities=True, firasim=True)

                elif entitiesType == "Control Tester":
                    self.gui.unbrain_loop = Loop(team_yellow=teamColor, mirror=mirror, n_robots=numRobots, control=True, firasim=True)
                    
                else:
                    self.gui.unbrain_loop = Loop(team_yellow=teamColor, mirror=mirror, n_robots=numRobots, firasim=True)
                
                self.gui.unbrain_thread = threading.Thread(target=self.gui.unbrain_loop.run)
                self.gui.unbrain_thread.daemon = True
                self.gui.unbrain_thread.start()

            elif loop.unbrain_paused:
                loop.unbrain_paused = False
                print("UnBrain resumed")

            else:
                print("Nothing happened")

        self.navigationScreen.menuBar.buttons[configButton.name].actionAssign(play_firasim)









        # Assigns the buttons with the changeScreen function
        self.navigationScreen.menuBar.buttons[navegacaoButton.name].actionAssign(changeToNavigationScreen)
        self.movementScreen.menuBar.buttons[movimentacaoButton.name].actionAssign(changeToMovementScreen)
        self.communicationScreen.menuBar.buttons[comunicacaoButton.name].actionAssign(changeToCommunicationScreen)
        self.navigationScreen.menuBar.buttons[closeButton.name].actionAssign(closeWindow)
        self.navigationScreen.menuBar.buttons[minimizeButton.name].actionAssign(minimizeWindow)
        self.navigationScreen.menuBar.buttons[maximizeButton.name].actionAssign(maximizeWindow)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[chooseColorComboBox.name].actionAssign(showOptionsColorComboBox)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[inversaoToggleButton.name].actionAssign(changeSide)

        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[chooseColorComboBox.name].options:
            button.actionAssign(chooseOptionColorComboBox)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[chooseEntityTypeComboBox.name].actionAssign(showOptionsTypeEntityComboBox)

        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[chooseEntityTypeComboBox.name].options:
            button.actionAssign(chooseOptionTypeEntityComboBox)
        
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[chooseNumRobotsComboBox.name].actionAssign(showOptionsNumRobotsComboBox)

        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[chooseNumRobotsComboBox.name].options:
            button.actionAssign(chooseOptionNumRobotsComboBox)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[robotIDComboBox.name].actionAssign(showOptionsRobotIDComboBox)

        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[robotIDComboBox.name].options:
            button.actionAssign(chooseOptionRobotIDComboBox)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[UVFButton.name].actionAssign(expandUVFScreen)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[virtualJudgeToggleButton.name].actionAssign(changeManualVirtualPos)
        
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[positioningComboBox.name].actionAssign(showOptionsPositioningComboBox)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[robotIDUVFComboBox.name].actionAssign(showOptionsRobotIDComboBox)
        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[robotIDUVFComboBox.name].options:
            button.actionAssign(chooseOptionRobotIDUVFComboBox)
        
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[txtQuantPontos.name].actionAssign(editScoreQuant)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[increaseQuantPontos.name].actionAssign(increaseScoreQuant)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[decreaseQuantPontos.name].actionAssign(decreaseScoreQuant)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[selectFieldComboBox.name].actionAssign(showFieldComboBox)
        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[selectFieldComboBox.name].options:
            button.actionAssign(chooseFieldComboBox)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[pontoFinalSelecToggleButton.name].actionAssign(changePontoFinal)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[txtRaio.name].actionAssign(editRaioQuant)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[increaseRaio.name].actionAssign(increaseRaioQuant)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[decreaseRaio.name].actionAssign(decreaseRaioQuant)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[txtConstSuav.name].actionAssign(editConstSuavQuant)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[increaseConstSuav.name].actionAssign(increaseConstSuavQuant)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[decreaseConstSuav.name].actionAssign(decreaseConstSuavQuant)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[txtConstSuavUnidir.name].actionAssign(editConstSuavUnidirQuant)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[increaseConstSuavUnidir.name].actionAssign(increaseConstSuavUnidirQuant)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[decreaseConstSuavUnidir.name].actionAssign(decreaseConstSuavUnidirQuant)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[visualizarTodosCamposToggleButton.name].actionAssign(changeViewAllFields)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[projecoesButton.name].actionAssign(expandprojecoesScreen)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[projecoesScreen.name].buttons[robotIDProjecoesComboBox.name].actionAssign(showOptionsRobotIDComboBox)

        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[projecoesScreen.name].buttons[robotIDProjecoesComboBox.name].options:
            button.actionAssign(chooseOptionRobotIDProjecoesComboBox)
        
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[projecoesScreen.name].buttons[txtAtacGolBola.name].actionAssign(editAtacGolBolaQuant)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[projecoesScreen.name].buttons[increaseAtacGolBola.name].actionAssign(increaseAtacGolBolaQuant)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[projecoesScreen.name].buttons[decreaseAtacGolBola.name].actionAssign(decreaseAtacGolBolaQuant)

        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[projecoesScreen.name].buttons[txtZagAreaAliada.name].actionAssign(editZagAreaAliadaQuant)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[projecoesScreen.name].buttons[increaseZagAreaAliada.name].actionAssign(increaseZagAreaAliadaQuant)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[projecoesScreen.name].buttons[decreaseZagAreaAliada.name].actionAssign(decreaseZagAreaAliadaQuant)



        # movementScreen's instance methods
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].buttons[graficosControleButton.name].actionAssign(expandGraficosControleScreen)
        
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].buttons[controleManualButton.name].actionAssign(expandControleManualScreen)
        
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].buttons[controleUVFButton.name].actionAssign(expandControleUVFScreen)
        
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[graficosControleScreen.name].buttons[robotIDGraficosControleComboBox.name].actionAssign(showFieldComboBox)
        
        for button in self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[graficosControleScreen.name].buttons[robotIDGraficosControleComboBox.name].options:
            button.actionAssign(chooseOptionRobotIDGraficosControleComboBox)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[robotIDControleManualComboBox.name].actionAssign(showFieldComboBox)
        
        for button in self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[robotIDControleManualComboBox.name].options:
            button.actionAssign(chooseOptionRobotIDControleManualComboBox)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[enableJoystickToggleButton.name].actionAssign(changeEnableJoystick)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[enableDirectionToggleButton.name].actionAssign(changeEnableDirection)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[enableControleManualToggleButton.name].actionAssign(changeEnableManualControl)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[directionComboBox.name].actionAssign(showOptionsDirectionComboBox)
        
        for button in self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[directionComboBox.name].options:
            button.actionAssign(chooseOptionDirectionComboBox)
        
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[velocidadeLinearSlider.name].actionAssign(slide)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[velocidadeAngularSlider.name].actionAssign(slide)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[aceleracaoSlider.name].actionAssign(slide)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[robotIDControleUVFComboBox.name].actionAssign(showOptionsRobotIDComboBox)
        
        for button in self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[robotIDControleUVFComboBox.name].options:
            button.actionAssign(chooseOptionRobotIDControleUVFComboBox)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[txtKw.name].actionAssign(editKwQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[increaseKw.name].actionAssign(increaseKwQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[decreaseKw.name].actionAssign(decreaseKwQuant)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[txtKp.name].actionAssign(editKpQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[increaseKp.name].actionAssign(increaseKpQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[decreaseKp.name].actionAssign(decreaseKpQuant)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[txtL.name].actionAssign(editLQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[increaseL.name].actionAssign(increaseLQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[decreaseL.name].actionAssign(decreaseLQuant)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[txtVmax.name].actionAssign(editVmaxQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[increaseVmax.name].actionAssign(increaseVmaxQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[decreaseVmax.name].actionAssign(decreaseVmaxQuant)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[txtMu.name].actionAssign(editMuQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[increaseMu.name].actionAssign(increaseMuQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[decreaseMu.name].actionAssign(decreaseMuQuant)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[txtVref.name].actionAssign(editVrefQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[increaseVref.name].actionAssign(increaseVrefQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[decreaseVref.name].actionAssign(decreaseVrefQuant)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[txtR.name].actionAssign(editRQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[increaseR.name].actionAssign(increaseRQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[decreaseR.name].actionAssign(decreaseRQuant)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[txtMaxAngError.name].actionAssign(editMaxAngErrorQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[increaseMaxAngError.name].actionAssign(increaseMaxAngErrorQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[decreaseMaxAngError.name].actionAssign(decreaseMaxAngErrorQuant)

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[txtTau.name].actionAssign(editTauQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[increaseTau.name].actionAssign(increaseTauQuant)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[decreaseTau.name].actionAssign(decreaseTauQuant)

        # communicationScreen's instance methods
        self.communicationScreen.buttons[robotIDCommunicationComboBox.name].actionAssign(showOptionsRobotIDComboBox)
        for button in self.communicationScreen.buttons[robotIDCommunicationComboBox.name].options:
            button.actionAssign(chooseOptionRobotIDCommunicationComboBox)


        # Initialize the running flag
        self.running = True


        self.wastedButtons = {}
        self.mousewheel = False

    def handleInput(self) -> None:
        """Method to handle input events from user"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            if event.type == pg.MOUSEWHEEL:
                self.mousewheel = True
                for scrollingBackground in self.activeScreen.scrollingBackgrounds.values():
                    scrollingBackground.scroll(event.y)

            elif event.type == pg.MOUSEBUTTONDOWN:
                # how to check all objects in the Screen in an optimized way ?
                if self.mousewheel:
                    self.mousewheel = False
                else:
                    mousePos = pg.mouse.get_pos()
                    for button in self.activeScreen.buttons.values():
                        button.actionPerformed()
                        if isinstance(button, TextField):
                            self.wastedButtons[button.name] = button
                        elif isinstance(button, ComboBox):
                            self.wastedButtons[button.name] = button
                    for scrollingBackground in self.activeScreen.scrollingBackgrounds.values():
                        for button in scrollingBackground.buttons.values():
                            if scrollingBackground.displayVerticalPos + scrollingBackground.displayVerticalSize >= mousePos[1] >= scrollingBackground.displayVerticalPos:
                                button.actionPerformed()
                                if isinstance(button, TextField):
                                    self.wastedButtons[button.name] = button
                                elif isinstance(button, ComboBox):
                                    self.wastedButtons[button.name] = button
                        for screen in scrollingBackground.scrollingBackgrounds.values():
                            for button in screen.buttons.values():
                                if scrollingBackground.displayVerticalPos + scrollingBackground.displayVerticalSize >= mousePos[1] >= scrollingBackground.displayVerticalPos:
                                    button.actionPerformed()
                                    if isinstance(button, TextField):
                                        self.wastedButtons[button.name] = button
                                    elif isinstance(button, ComboBox):
                                        self.wastedButtons[button.name] = button
                    for button in self.activeScreen.menuBar.buttons.values():
                        button.actionPerformed()
                        if isinstance(button, TextField):
                            self.wastedButtons[button.name] = button
                        elif isinstance(button, ComboBox):
                            self.wastedButtons[button.name] = button
                    popButtons = []
                    for button in self.wastedButtons.values():
                        if (button.pos.x < mousePos[0] < button.pos.x + button.size.x and button.pos.y < mousePos[1] < button.pos.y + button.size.y):
                            pass
                        else:
                            if isinstance(button, TextField):
                                button.setActive(False)
                                popButtons.append(button.name)
                            elif isinstance(button, ComboBox):
                                if button.getOptionsVisibility():
                                    button.setOptionsVisibility(False)
                                    popButtons.append(button.name)
                    for button in popButtons:
                        self.wastedButtons.pop(button)

            elif event.type == pg.KEYDOWN:
                mousePos = pg.mouse.get_pos()
                for button in self.activeScreen.buttons.values():
                    if isinstance(button, TextField) and button.isActive():
                        if event.key == pg.K_RETURN:
                            button.setActive(False)
                        elif event.key == pg.K_BACKSPACE:
                            button.setText(button.getText()[:-1], center=True)
                        else:
                            if event.unicode.isdigit():
                                button.setText(button.getText()+event.unicode, center=True)
                                button.calcLimit()
                for scrollingBackground in self.activeScreen.scrollingBackgrounds.values():
                    for button in scrollingBackground.buttons.values():
                        if scrollingBackground.displayVerticalPos + scrollingBackground.displayVerticalSize >= mousePos[1] >= scrollingBackground.displayVerticalPos:
                            if isinstance(button, TextField) and button.isActive():
                                if event.key == pg.K_RETURN:
                                    button.setActive(False)
                                elif event.key == pg.K_BACKSPACE:
                                    button.setText(button.getText()[:-1], center=True)
                                else:
                                    if event.unicode.isdigit():
                                        button.setText(button.getText()+event.unicode, center=True)
                                        button.calcLimit()
                    for screen in scrollingBackground.scrollingBackgrounds.values():
                        for button in screen.buttons.values():
                            if scrollingBackground.displayVerticalPos + scrollingBackground.displayVerticalSize >= mousePos[1] >= scrollingBackground.displayVerticalPos:
                                if isinstance(button, TextField) and button.isActive():
                                    if event.key == pg.K_RETURN:
                                        button.setActive(False)
                                    elif event.key == pg.K_BACKSPACE:
                                        button.setText(button.getText()[:-1], center=True)
                                    else:
                                        if event.unicode.isdigit():
                                            button.setText(button.getText()+event.unicode, center=True)
                                            button.calcLimit()
                for button in self.activeScreen.menuBar.buttons.values():
                    if isinstance(button, TextField) and button.isActive():
                        if event.key == pg.K_RETURN:
                            button.setActive(False)
                        elif event.key == pg.K_BACKSPACE:
                            button.setText(button.getText()[:-1], center=True)
                        else:
                            if event.unicode.isdigit():
                                button.setText(button.getText()+event.unicode, center=True)
                                button.calcLimit()

            elif event.type == pg.MOUSEBUTTONUP:
                self.mousewheel = False
                mousePos = pg.mouse.get_pos()
                for button in self.activeScreen.buttons.values():
                    if isinstance(button, Slider):
                        button.setActive(False)
                for scrollingBackground in self.activeScreen.scrollingBackgrounds.values():
                    for screen in scrollingBackground.scrollingBackgrounds.values():
                        for button in screen.buttons.values():
                            if isinstance(button, Slider):
                                button.setActive(False)
                    for button in scrollingBackground.buttons.values():
                        if isinstance(button, Slider):
                            button.setActive(False)
                for button in self.activeScreen.menuBar.buttons.values():
                    if isinstance(button, Slider):
                        button.setActive(False)

            elif event.type == pg.MOUSEMOTION:
                mousePos = pg.mouse.get_pos()
                for button in self.activeScreen.buttons.values():
                    if isinstance(button, Slider) and button.isActive():
                        button.pos.x = min(max(mousePos[0], button.bar.pos.x), button.bar.pos.x + button.bar.size.x)
                        button.label.pos.x = button.pos.x-button.size.x/2
                        button.label.setText(str(button.getValue()), center=True)
                for scrollingBackground in self.activeScreen.scrollingBackgrounds.values():
                    for screen in scrollingBackground.scrollingBackgrounds.values():
                        for button in screen.buttons.values():
                            if isinstance(button, Slider) and button.isActive():
                                button.pos.x = min(max(mousePos[0], button.bar.pos.x), button.bar.pos.x + button.bar.size.x)
                                button.label.pos.x = button.pos.x-button.size.x/2
                                button.label.setText(str(button.getValue()), center=True)
                    for button in scrollingBackground.buttons.values():
                        if isinstance(button, Slider) and button.isActive():
                            button.pos.x = min(max(mousePos[0], button.bar.pos.x), button.bar.pos.x + button.bar.size.x)
                            button.label.pos.x = button.pos.x-button.size.x/2
                            button.label.setText(str(button.getValue()), center=True)
                for button in self.activeScreen.menuBar.buttons.values():
                    if isinstance(button, Slider) and button.isActive():
                        button.pos.x = min(max(mousePos[0], button.bar.pos.x), button.bar.pos.x + button.bar.size.x)
                        button.label.pos.x = button.pos.x-button.size.x/2
                        button.label.setText(str(button.getValue()), center=True)
                    

    def updateGUI(self) -> None:
        raise NotImplementedError

    def renderGUI(self) -> None:
        self.activeScreen.draw()
        pg.display.flip()
    
    def run(self) -> None:
        while self.running:
            self.handleInput()
            self.renderGUI()
        pg.quit()
