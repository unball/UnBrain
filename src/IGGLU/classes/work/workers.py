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


        btnPlay = Button("btnPlay", 30, 30, 20, 13, BACKGROUND_COLOR, window, self, border=False)
        btnPlay.setImage("images/play_button.png")
        self.navigationScreen.menuBar.addButton(btnPlay)

        btnPause = Button("btnPause", 30, 30, btnPlay.pos.x + 50, btnPlay.pos.y, BACKGROUND_COLOR, window, self, border=False)
        btnPause.setImage("images/pause_button.png")
        self.navigationScreen.menuBar.addButton(btnPause)

        btnStop = Button("btnStop", 30, 30, btnPause.pos.x + 50, btnPlay.pos.y, BACKGROUND_COLOR, window, self, border=False)
        btnStop.setImage("images/stop_button.png")
        self.navigationScreen.menuBar.addButton(btnStop)

        btnRecord = Button("btnRecord", 30, 30, btnStop.pos.x + 50, btnPlay.pos.y, BACKGROUND_COLOR, window, self, border=False)
        btnRecord.setImage("images/record_button.png")
        self.navigationScreen.menuBar.addButton(btnRecord)

        btnConfig = Button("btnConfig", 30, 30, btnRecord.pos.x + 50, btnPlay.pos.y, BACKGROUND_COLOR, window, self, border=False)
        btnConfig.setImage("images/config_button.png")
        self.navigationScreen.menuBar.addButton(btnConfig)

        btnNavegacao = Button("btnNavegacao", 160, 40, btnConfig.pos.x + 130, btnPlay.pos.y -3, BORDER_COLOR, window, self)
        btnNavegacao.setText("Navegação", GRAY_LABEL, 27, center=True)
        self.navigationScreen.menuBar.addButton(btnNavegacao)

        btnMovimentacao = Button("btnMovimentacao", btnNavegacao.size.x, btnNavegacao.size.y, btnNavegacao.pos.x + btnNavegacao.size.x-2, btnNavegacao.pos.y, BACKGROUND_COLOR, window, self)
        btnMovimentacao.setText("Movimentação", GRAY_LABEL, 27, center=True)
        self.navigationScreen.menuBar.addButton(btnMovimentacao)

        btnComunicacao = Button("btnComunicacao", btnMovimentacao.size.x, btnMovimentacao.size.y, btnMovimentacao.pos.x + btnMovimentacao.size.x-2, btnMovimentacao.pos.y, BACKGROUND_COLOR, window, self)
        btnComunicacao.setText("Comunicação", GRAY_LABEL, 27, center=True)
        self.navigationScreen.menuBar.addButton(btnComunicacao)

        btnVsss = Button("btnVsss", btnNavegacao.size.x-70, 30, btnComunicacao.pos.x + btnComunicacao.size.x + 90, btnComunicacao.pos.y + 5, BORDER_COLOR, window, self)
        btnVsss.setText("VSSS", GRAY_LABEL, center=True)
        self.navigationScreen.menuBar.addButton(btnVsss)

        btnSsl = Button("btnSsl", btnVsss.size.x, btnVsss.size.y, btnVsss.pos.x + btnVsss.size.x-2, btnVsss.pos.y, BACKGROUND_COLOR, window, self)
        btnSsl.setText("SSL", GRAY_LABEL, center=True)
        self.navigationScreen.menuBar.addButton(btnSsl)

        btnMinimize = Button("btnMinimize", btnConfig.size.x+7, btnConfig.size.y+7, btnSsl.pos.x + btnSsl.size.x + 90, btnConfig.pos.y, BACKGROUND_COLOR, window, self)
        btnMinimize.setImage("images/minimize_button.png")
        self.navigationScreen.menuBar.addButton(btnMinimize)

        btnMaximize = Button("btnMaximize", btnMinimize.size.x, btnMinimize.size.y, btnMinimize.pos.x + btnMinimize.size.x + 20, btnMinimize.pos.y, BACKGROUND_COLOR, window, self)
        btnMaximize.setImage("images/save_button.png")
        self.navigationScreen.menuBar.addButton(btnMaximize)

        btnClose = Button("btnClose", btnMinimize.size.x, btnMinimize.size.y, btnMaximize.pos.x + btnMaximize.size.x + 20, btnMaximize.pos.y, BACKGROUND_COLOR, window, self)
        btnClose.setImage("images/close_button.png")
        self.navigationScreen.menuBar.addButton(btnClose)


        gameMiniMap = Block("gameMiniMap", windowSize.x/2-30, windowSize.y/3+100, 15, 80, BLACK, window, self)
        self.navigationScreen.addBlock(gameMiniMap)

        arrow = Block("arrow", windowSize.x*0.25, 30, 168, windowSize.y/3+192, BACKGROUND_COLOR, window, self)
        arrow.setImage("images/arrow.png")
        self.navigationScreen.addBlock(arrow)

        lblLadoEsquerdo = Label("lblLadoEsquerdo", 30, 35, windowSize.y/3+186, BACKGROUND_COLOR, window, self, "Lado aliado")
        self.navigationScreen.addBlock(lblLadoEsquerdo)

        lblLadoDireito = Label("lblLadoDireito", 30, 165 + windowSize.x*0.25 + 20, lblLadoEsquerdo.pos.y, BACKGROUND_COLOR, window, self, "Lado inimigo")
        self.navigationScreen.addBlock(lblLadoDireito)

        lblInfoBola = Label("lblInfoBola", 30, gameMiniMap.pos.x+4, gameMiniMap.pos.y+gameMiniMap.size.y+60, BACKGROUND_COLOR, window, self, "Informações sobre a bola", BLACK_LABEL, 26)
        self.navigationScreen.addBlock(lblInfoBola)

        boxInfoBola = Block("boxInfoBola", gameMiniMap.size.x, gameMiniMap.size.y*0.6, gameMiniMap.pos.x, lblInfoBola.pos.y+40, BACKGROUND_COLOR, window, self, border=True)
        self.navigationScreen.addBlock(boxInfoBola)

        lblPosicao = Label("lblPosicao", 30, boxInfoBola.pos.x + 20, boxInfoBola.pos.y + 20, BACKGROUND_COLOR, window, self, "Posição", GRAY_LABEL)
        self.navigationScreen.addBlock(lblPosicao)

        boxPosicao = Block("boxPosicao", 180, lblPosicao.size.y + 10, lblPosicao.pos.x, lblPosicao.pos.y + lblPosicao.size.y, BACKGROUND_COLOR, window, self, border=True)
        boxPosicao.setText("x: 0.045m   y: 1.674m", LIGHT_GRAY_LABEL, center=True)
        self.navigationScreen.addBlock(boxPosicao)

        lblAceleracao = Label("lblAceleracao", lblPosicao.size.y, lblPosicao.pos.x, boxPosicao.pos.y + boxPosicao.size.y + 25, BACKGROUND_COLOR, window, self, "Aceleração", GRAY_LABEL)
        self.navigationScreen.addBlock(lblAceleracao)

        boxAceleracao = Block("boxAceleracao", boxPosicao.size.x, boxPosicao.size.y, lblAceleracao.pos.x, lblAceleracao.pos.y + lblAceleracao.size.y, BACKGROUND_COLOR, window, self, border=True)
        boxAceleracao.setText("3 m/s\u00B2", LIGHT_GRAY_LABEL, center=True)
        self.navigationScreen.addBlock(boxAceleracao)

        lblVelocidade = Label("lblVelocidade", lblPosicao.size.y, boxInfoBola.size.x/2 + 80, lblPosicao.pos.y, BACKGROUND_COLOR, window, self, "Velocidade", GRAY_LABEL)
        self.navigationScreen.addBlock(lblVelocidade)

        boxVelocidade = Block("boxVelocidade", boxAceleracao.size.x, boxAceleracao.size.y, lblVelocidade.pos.x, lblVelocidade.pos.y + lblVelocidade.size.y, BACKGROUND_COLOR, window, self, border=True)
        boxVelocidade.setText("3 m/s", LIGHT_GRAY_LABEL, center=True)
        self.navigationScreen.addBlock(boxVelocidade)

        navigationScrollPanel = ScrollingBackground("navigationScrollPanel", screenDivisionRightMargin.size.x, int(screenDivisionRightMargin.size.y*1.6), screenDivisionRightMargin.pos.x, screenDivisionRightMargin.pos.y, BACKGROUND_COLOR, window, self, screenDivisionRightMargin.size.y,  screenDivisionRightMargin.pos.y)

        self.navigationScreen.addScrollingBackground(navigationScrollPanel)

        # blocks of navigationScrollPanel
        lblCorTime = Label("lblCorTime", lblInfoBola.size.y, navigationScrollPanel.pos.x+30, navigationScrollPanel.pos.y+30, BACKGROUND_COLOR, window, self, "Cor do time", BLACK_LABEL, 28)
        navigationScrollPanel.addBlock(lblCorTime)

        lblSelecionaCorTime = Label("lblSelecionaCorTime", lblCorTime.size.y, lblCorTime.pos.x + 30, lblCorTime.pos.y+lblCorTime.size.y-5, BACKGROUND_COLOR, window, self, "Seleciona a cor do time")
        navigationScrollPanel.addBlock(lblSelecionaCorTime)

        lblInversaoCampo = Label("lblInversaoCampo", lblCorTime.size.y, lblCorTime.pos.x, lblSelecionaCorTime.pos.y+lblCorTime.size.y*2, BACKGROUND_COLOR, window, self, "Inversão de campo", BLACK_LABEL, 28)
        navigationScrollPanel.addBlock(lblInversaoCampo)

        lblInverteCampoAliado = Label("lblInverteCampoAliado", lblSelecionaCorTime.size.y, lblSelecionaCorTime.pos.x, lblInversaoCampo.pos.y+lblInversaoCampo.size.y-5, BACKGROUND_COLOR, window, self, "Inverte o lado do campo aliado")
        navigationScrollPanel.addBlock(lblInverteCampoAliado)

        tglInversao = ToggleButton("tglInversao", 70, 50, lblCorTime.pos.x + 400, lblInversaoCampo.pos.y, BACKGROUND_COLOR, window, self, border=True)
        tglInversao.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        navigationScrollPanel.addButton(tglInversao)

        cmbChooseColor = ComboBox("cmbChooseColor", lblCorTime.size.x-30, lblCorTime.size.y, lblCorTime.pos.x + 400, lblCorTime.pos.y+lblCorTime.size.y/2, WHITE, window, self, "Azul", BACKGROUND_COLOR)
        navigationScrollPanel.addButton(cmbChooseColor)
        cmbChooseColor.addOptions(["Azul", "Amarelo"])

        lblDireitoOuEsquerdo = Label("lblDireitoOuEsquerdo", lblCorTime.size.y, tglInversao.pos.x+tglInversao.size.x+15, tglInversao.pos.y+12, BACKGROUND_COLOR, window, self, "Esquerdo")
        navigationScrollPanel.addBlock(lblDireitoOuEsquerdo)

        lblFormacaoEntidades = Label("lblFormacaoEntidades", lblInversaoCampo.size.y, lblInversaoCampo.pos.x, lblInverteCampoAliado.pos.y+lblInversaoCampo.size.y*2, BACKGROUND_COLOR, window, self, "Formação das entidades", BLACK_LABEL, 28)
        navigationScrollPanel.addBlock(lblFormacaoEntidades)

        lblSelecioneTipoFormacao = Label("lblSelecioneTipoFormacao", lblInverteCampoAliado.size.y, lblInverteCampoAliado.pos.x, lblFormacaoEntidades.pos.y+lblFormacaoEntidades.size.y/2+10, BACKGROUND_COLOR, window, self, "Selecione o tipo de formação")
        navigationScrollPanel.addBlock(lblSelecioneTipoFormacao)

        lblNumRobots = Label("lblNumRobots", lblInversaoCampo.size.y, lblInversaoCampo.pos.x, lblSelecioneTipoFormacao.pos.y+lblInversaoCampo.size.y*2, BACKGROUND_COLOR, window, self, "Número de robôs", BLACK_LABEL, 28)
        navigationScrollPanel.addBlock(lblNumRobots)

        lblSelecioneNumRobos = Label("lblSelecioneNumRobos", lblInverteCampoAliado.size.y, lblInverteCampoAliado.pos.x, lblNumRobots.pos.y+lblNumRobots.size.y/2+10, BACKGROUND_COLOR, window, self, "Selecione o número de robôs e seus IDs")
        navigationScrollPanel.addBlock(lblSelecioneNumRobos)

        lblConfigRobos = Label("lblConfigRobos", lblNumRobots.size.y, lblNumRobots.pos.x, lblSelecioneNumRobos.pos.y+lblNumRobots.size.y*2, BACKGROUND_COLOR, window, self, "Configuração dos robôs", BLACK_LABEL, 28)
        navigationScrollPanel.addBlock(lblConfigRobos)

        boxConfigRobos = Block("boxConfigRobos", screenDivisionRightMargin.size.x-60, 250, lblConfigRobos.pos.x, lblConfigRobos.pos.y+lblConfigRobos.size.y+5, BACKGROUND_COLOR, window, self, border=True)
        navigationScrollPanel.addBlock(boxConfigRobos)

        cmbRobotID = ComboBox("cmbRobotID", lblFormacaoEntidades.size.x, cmbChooseColor.size.y, boxConfigRobos.pos.x+boxConfigRobos.size.x/2-lblFormacaoEntidades.size.x/2, boxConfigRobos.pos.y+10, WHITE, window, self, "Robô ID")
        navigationScrollPanel.addButton(cmbRobotID)
        cmbRobotID.addOptions(["Robô 00", "Robô 01", "Robô 02"])

        cmbChooseNumRobots = ComboBox("cmbChooseNumRobots", cmbChooseColor.size.x, cmbChooseColor.size.y, cmbChooseColor.pos.x, lblNumRobots.pos.y+lblFormacaoEntidades.size.y/2-5, WHITE, window, self, "0, 1, 2", BACKGROUND_COLOR)
        navigationScrollPanel.addButton(cmbChooseNumRobots)
        cmbChooseNumRobots.addOptions(["0", "1", "2", "0, 1", "0, 2", "1, 2", "0, 1, 2"])

        cmbChooseEntityType = ComboBox("cmbChooseEntityType", lblFormacaoEntidades.size.x, cmbChooseColor.size.y, lblFormacaoEntidades.pos.x+lblFormacaoEntidades.size.x+90, lblFormacaoEntidades.pos.y+lblFormacaoEntidades.size.y/2-5, WHITE, window, self, "Entidades dinâmicas", BACKGROUND_COLOR)
        navigationScrollPanel.addButton(cmbChooseEntityType)
        cmbChooseEntityType.addOptions(["Entidades dinâmicas", "Entidades estáticas", "Control Tester"])
        
        lblBateria = Label("lblBateria", lblDireitoOuEsquerdo.size.y, boxConfigRobos.pos.x+40, cmbRobotID.pos.y+cmbRobotID.size.y+25, BACKGROUND_COLOR, window, self, "Bateria:", BLACK_LABEL)
        navigationScrollPanel.addBlock(lblBateria)

        lblpercentBattery = Label("lblpercentBattery", lblBateria.size.y, lblBateria.pos.x+lblBateria.size.x+5, lblBateria.pos.y, BACKGROUND_COLOR, window, self, "100%")
        navigationScrollPanel.addBlock(lblpercentBattery)

        cor1Robot = Block("cor1Robot", lblBateria.size.x*2, lblBateria.size.x, lblBateria.pos.x, lblBateria.pos.y+lblBateria.size.y+5, RED, window, self)
        navigationScrollPanel.addBlock(cor1Robot)

        cor2Robot = Block("cor2Robot", cor1Robot.size.x, cor1Robot.size.y, cor1Robot.pos.x, cor1Robot.pos.y+cor1Robot.size.y, LIGHT_BLUE, window, self)
        navigationScrollPanel.addBlock(cor2Robot)

        lblPosicaoConfig = Label("lblPosicaoConfig", lblBateria.size.y, cor1Robot.pos.x+cor1Robot.size.x+60, cor1Robot.pos.y-5, BACKGROUND_COLOR, window, self, "Posição", BLACK_LABEL)
        navigationScrollPanel.addBlock(lblPosicaoConfig)

        boxPosicaoConfig = Block("boxPosicaoConfig", lblPosicaoConfig.size.x*3, lblPosicaoConfig.size.y, lblPosicaoConfig.pos.x+lblPosicaoConfig.size.x, lblPosicaoConfig.pos.y, BACKGROUND_COLOR, window, self)
        boxPosicaoConfig.setText("x: 0.0m   y: 0.0m", center=True)
        navigationScrollPanel.addBlock(boxPosicaoConfig)

        lblOrientacaoConfig = Label("lblOrientacaoConfig", lblPosicaoConfig.size.y, lblPosicaoConfig.pos.x, lblPosicaoConfig.pos.y+lblPosicaoConfig.size.y+5, BACKGROUND_COLOR, window, self, "Orientação", BLACK_LABEL)
        navigationScrollPanel.addBlock(lblOrientacaoConfig)

        boxOrientacaoConfig = Block("boxOrientacaoConfig", boxPosicaoConfig.size.x-30, boxPosicaoConfig.size.y, lblOrientacaoConfig.pos.x+lblOrientacaoConfig.size.x, lblOrientacaoConfig.pos.y, BACKGROUND_COLOR, window, self)
        boxOrientacaoConfig.setText("th: 0.0 graus", center=True)
        navigationScrollPanel.addBlock(boxOrientacaoConfig)

        lblVelocidadeConfig = Label("lblVelocidadeConfig", lblOrientacaoConfig.size.y, lblOrientacaoConfig.pos.x, lblOrientacaoConfig.pos.y+lblOrientacaoConfig.size.y+5, BACKGROUND_COLOR, window, self, "Velocidade", BLACK_LABEL)
        navigationScrollPanel.addBlock(lblVelocidadeConfig)

        boxVelocidadeConfig = Block("boxVelocidadeConfig", boxPosicaoConfig.size.x+30, boxOrientacaoConfig.size.y, lblVelocidadeConfig.pos.x+lblVelocidadeConfig.size.x, lblVelocidadeConfig.pos.y, BACKGROUND_COLOR, window, self)
        boxVelocidadeConfig.setText("v: 0.0m/s   w: 0.0rad/s", center=True)
        navigationScrollPanel.addBlock(boxVelocidadeConfig)

        lblPosicionamento = Label("lblPosicionamento", lblInversaoCampo.size.y, lblInversaoCampo.pos.x, boxConfigRobos.pos.y+boxConfigRobos.size.y+15, BACKGROUND_COLOR, window, self, "Posicionamento", BLACK_LABEL, 28)
        navigationScrollPanel.addBlock(lblPosicionamento)

        boxPosicionamento = Block("boxPosicionamento", boxConfigRobos.size.x, boxConfigRobos.size.y-50, boxConfigRobos.pos.x, lblPosicionamento.pos.y+lblPosicionamento.size.y+5, BACKGROUND_COLOR, window, self, border=True)
        navigationScrollPanel.addBlock(boxPosicionamento)

        lblPosJuizVirtual = Label("lblPosJuizVirtual", lblPosicionamento.size.y, lblBateria.pos.x, boxPosicionamento.pos.y+25, BACKGROUND_COLOR, window, self, "Usar posicionamento do juiz virtual")
        navigationScrollPanel.addBlock(lblPosJuizVirtual)

        tglVirtualJudge = ToggleButton("tglVirtualJudge", tglInversao.size.x, tglInversao.size.y, lblPosJuizVirtual.pos.x+lblPosJuizVirtual.size.x+170, lblPosJuizVirtual.pos.y-12, BACKGROUND_COLOR, window, self)
        tglVirtualJudge.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        navigationScrollPanel.addButton(tglVirtualJudge)

        lblSelecionarPosicionamento = Label("lblSelecionarPosicionamento", lblPosJuizVirtual.size.y, lblPosJuizVirtual.pos.x, lblPosJuizVirtual.pos.y+lblPosJuizVirtual.size.y+30, BACKGROUND_COLOR, window, self, "Selecionar posicionamento")
        navigationScrollPanel.addBlock(lblSelecionarPosicionamento)

        cmbPositioning = ComboBox("cmbPositioning", lblSelecionarPosicionamento.size.x-30, lblSelecionarPosicionamento.size.y, lblSelecionarPosicionamento.pos.x+lblSelecionarPosicionamento.size.x+130, lblSelecionarPosicionamento.pos.y, WHITE, window, self, "FreeBall")
        navigationScrollPanel.addButton(cmbPositioning)
        cmbPositioning.addOptions(["FreeBall"])

        lblTempoPosicionar = Label("lblTempoPosicionamento", lblPosJuizVirtual.size.y, lblSelecionarPosicionamento.pos.x, lblSelecionarPosicionamento.pos.y+lblSelecionarPosicionamento.size.y+30, BACKGROUND_COLOR, window, self, "Tempo tentando se posicionar:")
        navigationScrollPanel.addBlock(lblTempoPosicionar)

        tempoPosicionar = Label("tempoPosicionar", lblTempoPosicionar.size.y, lblTempoPosicionar.pos.x+lblTempoPosicionar.size.x+20, lblTempoPosicionar.pos.y, BACKGROUND_COLOR, window, self, "8s")
        navigationScrollPanel.addBlock(tempoPosicionar)



        btnUVF = ToggleButton("btnUVF", boxPosicionamento.size.x, menuBar.size.y-3, boxPosicionamento.pos.x, boxPosicionamento.pos.y+boxPosicionamento.size.y+30, BUTTON_HELD_SCREEN_COLOR, window, self)
        btnUVF.setImage("images/button_screen_held.png", "images/button_screen_expanded.png", center=True)
        btnUVF.setText("UVF", BLACK_LABEL, 32, center=True)
        navigationScrollPanel.addButton(btnUVF)

        UVFScreen = ScrollingBackground("UVFScreen", btnUVF.size.x, windowSize.y, btnUVF.pos.x, btnUVF.pos.y+btnUVF.size.y+5, BACKGROUND_COLOR, window, self, btnUVF.size.x, windowSize.y, border=True)
        navigationScrollPanel.addScrollingBackground(UVFScreen)

        cmbRobotIDUVF = ComboBox("cmbRobotIDUVF", cmbRobotID.size.x, cmbRobotID.size.y, UVFScreen.pos.x+30, UVFScreen.pos.y+20, WHITE, window, self, "Robô ID")
        UVFScreen.addButton(cmbRobotIDUVF)
        cmbRobotIDUVF.addOptions(["Robô 00", "Robô 01", "Robô 02"])

        lblVisualizarCampoUVF = Label("lblVisualizarCampoUVF", cmbRobotIDUVF.size.y, cmbRobotIDUVF.pos.x, cmbRobotIDUVF.pos.y+cmbRobotIDUVF.size.y+50, BACKGROUND_COLOR, window, self, "Visualizar campo UVF")
        UVFScreen.addBlock(lblVisualizarCampoUVF)

        spnQuantPontos = Spinner("spnQuantPontos", 2*(tglInversao.size.x-20), 30, lblVisualizarCampoUVF.pos.x+lblVisualizarCampoUVF.size.x+210-2*(tglInversao.size.x-20)+3, lblVisualizarCampoUVF.pos.y, WHITE, window, self)
        spnQuantPontos.setText("10", center=True)
        UVFScreen.addButton(spnQuantPontos)

        lblQuantPontos = Label("lblQuantPontos", lblVisualizarCampoUVF.size.y-7, spnQuantPontos.pos.x, spnQuantPontos.pos.y-lblVisualizarCampoUVF.size.y+10, BACKGROUND_COLOR, window, self, "Quantidade de pontos", fontSize=21)
        UVFScreen.addBlock(lblQuantPontos)

        btnViewCampoUVF = Button("btnViewCampoUVF", tglInversao.size.x/2, tglInversao.size.y/2, spnQuantPontos.increaseButton.pos.x+spnQuantPontos.increaseButton.size.x+30, spnQuantPontos.increaseButton.pos.y, BACKGROUND_COLOR, window, self)
        btnViewCampoUVF.setImage("images/visualize.png")
        UVFScreen.addButton(btnViewCampoUVF)

        lblSelecionarCampo = Label("lblSelecionarCampo", lblVisualizarCampoUVF.size.y, lblVisualizarCampoUVF.pos.x, lblVisualizarCampoUVF.pos.y+lblVisualizarCampoUVF.size.y*2.5, BACKGROUND_COLOR, window, self, "Selecionar campo")
        UVFScreen.addBlock(lblSelecionarCampo)

        cmbSelectField = ComboBox("cmbSelectField", cmbChooseColor.size.x+16, lblSelecionarCampo.size.y, spnQuantPontos.pos.x+spnQuantPontos.size.x/2, lblSelecionarCampo.pos.y, WHITE, window, self, "Nenhum")
        UVFScreen.addButton(cmbSelectField)
        cmbSelectField.addOptions(["Nenhum"])

        lblPontoFinalSelec = Label("lblPontoFinalSelec", lblVisualizarCampoUVF.size.y, lblSelecionarCampo.pos.x, lblSelecionarCampo.pos.y+lblSelecionarCampo.size.y*2.5, BACKGROUND_COLOR, window, self, "Ponto final selecionável")
        UVFScreen.addBlock(lblPontoFinalSelec)

        lblHabilitaPontoFinal = Label("lblHabilitaPontoFinal", lblPontoFinalSelec.size.y-5, lblPontoFinalSelec.pos.x+30, lblPontoFinalSelec.pos.y+lblPontoFinalSelec.size.y-6, BACKGROUND_COLOR, window, self, "Habilita a seleção manual de ponto final das trajetórias", fontSize=21)
        UVFScreen.addBlock(lblHabilitaPontoFinal)

        tglPontoFinalSelec = ToggleButton("pontoFinalSelecComboBox", tglInversao.size.x, tglInversao.size.y, lblHabilitaPontoFinal.pos.x+lblHabilitaPontoFinal.size.x+50, lblPontoFinalSelec.pos.y, BACKGROUND_COLOR, window, self)
        tglPontoFinalSelec.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        UVFScreen.addButton(tglPontoFinalSelec)

        lblRaio = Label("lblRaio", lblSelecionarCampo.size.y, lblPontoFinalSelec.pos.x, lblPontoFinalSelec.pos.y+lblPontoFinalSelec.size.y*2.5, BACKGROUND_COLOR, window, self, "Raio:")
        UVFScreen.addBlock(lblRaio)

        spnRaio = Spinner("spnRaio", spnQuantPontos.size.x, spnQuantPontos.size.y, lblRaio.pos.x+1, lblRaio.pos.y+lblRaio.size.y-5, WHITE, window, self)
        spnRaio.setText("10", center=True)
        UVFScreen.addButton(spnRaio)

        lblConstSuavizacao = Label("lblConstSuavizacao", lblRaio.size.y, lblRaio.pos.x, spnRaio.pos.y+spnRaio.size.y+10, BACKGROUND_COLOR, window, self, "Constante de suavização:")
        UVFScreen.addBlock(lblConstSuavizacao)

        spnConstSuav = Spinner("spnConstSuav", spnRaio.size.x, spnRaio.size.y, spnRaio.pos.x, lblConstSuavizacao.pos.y+lblConstSuavizacao.size.y-5, WHITE, window, self)
        spnConstSuav.setText("10", center=True)
        UVFScreen.addButton(spnConstSuav)

        lblConstSuavUnidir = Label("lblConstSuavUnidir", lblConstSuavizacao.size.y, lblConstSuavizacao.pos.x, spnConstSuav.pos.y+spnConstSuav.size.y+10, BACKGROUND_COLOR, window, self, "Constante de suavização unidirecional:")
        UVFScreen.addBlock(lblConstSuavUnidir)

        spnConstSuavUnidir = Spinner("spnConstSuavUnidir", spnConstSuav.size.x, spnConstSuav.size.y, spnConstSuav.pos.x, lblConstSuavUnidir.pos.y+lblConstSuavUnidir.size.y-5, WHITE, window, self)
        spnConstSuavUnidir.setText("10", center=True)
        UVFScreen.addButton(spnConstSuavUnidir)

        lblVisualizarTodosCamposUVF = Label("lblVisualizarTodosCamposUVF", lblConstSuavUnidir.size.y, lblConstSuavUnidir.pos.x, spnConstSuavUnidir.pos.y+spnConstSuavUnidir.size.y+70, BACKGROUND_COLOR, window, self, "Visualizar todos os campos UVF")
        UVFScreen.addBlock(lblVisualizarTodosCamposUVF)

        lblHabilitaVisualizacaoCampos = Label("lblHabilitaVisualizacaoCampos", lblHabilitaPontoFinal.size.y, lblVisualizarTodosCamposUVF.pos.x+30, lblVisualizarTodosCamposUVF.pos.y+lblVisualizarTodosCamposUVF.size.y-6, BACKGROUND_COLOR, window, self, "Habilita visualização dos campos de todos os robôs", fontSize=21)
        UVFScreen.addBlock(lblHabilitaVisualizacaoCampos)

        tglVisualizarTodosCampos = ToggleButton("tglVisualizarTodosCampos", tglInversao.size.x, tglInversao.size.y, tglPontoFinalSelec.pos.x, lblVisualizarTodosCamposUVF.pos.y, BACKGROUND_COLOR, window, self)
        tglVisualizarTodosCampos.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        UVFScreen.addButton(tglVisualizarTodosCampos)

        UVFScreen.setVisible(False)


        tglProjecoes = ToggleButton("tglProjecoes", btnUVF.size.x, btnUVF.size.y, btnUVF.pos.x, btnUVF.pos.y+btnUVF.size.y+30, BUTTON_HELD_SCREEN_COLOR, window, self)
        tglProjecoes.setImage("images/button_screen_held.png", "images/button_screen_expanded.png", center=True)
        tglProjecoes.setText("Projeções", BLACK_LABEL, 32, center=True)
        navigationScrollPanel.addButton(tglProjecoes)

        projecoesScreen = ScrollingBackground("projecoesScreen", UVFScreen.size.x, boxConfigRobos.size.y, UVFScreen.pos.x, tglProjecoes.pos.y+tglProjecoes.size.y+5, BACKGROUND_COLOR, window, self, boxConfigRobos.size.y, tglProjecoes.pos.y+tglProjecoes.size.y+5, border=True)
        navigationScrollPanel.addScrollingBackground(projecoesScreen)

        cmbRobotIDProjecoes = ComboBox("cmbRobotIDProjecoes", cmbRobotIDUVF.size.x, cmbRobotIDUVF.size.y, cmbRobotIDUVF.pos.x, projecoesScreen.pos.y+20, WHITE, window, self, "Robô ID")
        projecoesScreen.addButton(cmbRobotIDProjecoes)
        cmbRobotIDProjecoes.addOptions(["Robô 00", "Robô 01", "Robô 02"])        

        lblAtacanteGolBola = Label("lblAtacanteGolBola", lblVisualizarCampoUVF.size.y, lblVisualizarCampoUVF.pos.x, lblVisualizarCampoUVF.pos.y+lblVisualizarCampoUVF.size.y+50, BACKGROUND_COLOR, window, self, "Atacante gol bola")
        projecoesScreen.addBlock(lblAtacanteGolBola)

        spnAtacGolBola = Spinner("spnAtacGolBola", spnQuantPontos.size.x, spnQuantPontos.size.y, spnQuantPontos.pos.x, lblAtacanteGolBola.pos.y, WHITE, window, self)
        spnAtacGolBola.setText("10", center=True)
        projecoesScreen.addButton(spnAtacGolBola)

        lblQuantPontosAtacGolBola = Block("lblQuantPontosAtacGolBola", spnAtacGolBola.size.x+spnAtacGolBola.increaseButton.size.x+spnAtacGolBola.decreaseButton.size.x-6, lblAtacanteGolBola.size.y-7, spnAtacGolBola.pos.x, spnAtacGolBola.pos.y-lblAtacanteGolBola.size.y+10, BACKGROUND_COLOR, window, self)
        lblQuantPontosAtacGolBola.setText("Quantidade de pontos", fontSize=21, center=True)
        projecoesScreen.addBlock(lblQuantPontosAtacGolBola)

        btnViewAtacGolBola = Button("btnViewAtacGolBola", btnViewCampoUVF.size.x, btnViewCampoUVF.size.y, spnAtacGolBola.increaseButton.pos.x+spnAtacGolBola.increaseButton.size.x+30, spnAtacGolBola.increaseButton.pos.y, BACKGROUND_COLOR, window, self)
        btnViewAtacGolBola.setImage("images/visualize.png")
        projecoesScreen.addButton(btnViewAtacGolBola)

        lblZagueiroAreaAliada = Label("lblZagueiroAreaAliada", lblAtacanteGolBola.size.y, lblAtacanteGolBola.pos.x, lblAtacanteGolBola.pos.y+lblAtacanteGolBola.size.y*2.5, BACKGROUND_COLOR, window, self, "Zagueiro área aliada")
        projecoesScreen.addBlock(lblZagueiroAreaAliada)

        spnZagAreaAliada = Spinner("spnZagAreaAliada", spnAtacGolBola.size.x, spnAtacGolBola.size.y, spnAtacGolBola.pos.x, lblZagueiroAreaAliada.pos.y, WHITE, window, self)
        spnZagAreaAliada.setText("10", center=True)
        projecoesScreen.addButton(spnZagAreaAliada)

        lblQuantPontosZagAreaAliada = Block("lblQuantPontosZagAreaAliada", spnZagAreaAliada.size.x+spnZagAreaAliada.increaseButton.size.x+spnZagAreaAliada.decreaseButton.size.x-6, lblZagueiroAreaAliada.size.y-7, spnZagAreaAliada.pos.x, spnZagAreaAliada.pos.y-lblZagueiroAreaAliada.size.y+10, BACKGROUND_COLOR, window, self)
        lblQuantPontosZagAreaAliada.setText("Quantidade de pontos", fontSize=21, center=True)
        projecoesScreen.addBlock(lblQuantPontosZagAreaAliada)

        btnViewZagAreaAliada = Button("btnViewZagAreaAliada", btnViewCampoUVF.size.x, btnViewCampoUVF.size.y, spnZagAreaAliada.increaseButton.pos.x+spnZagAreaAliada.increaseButton.size.x+30, spnZagAreaAliada.increaseButton.pos.y, BACKGROUND_COLOR, window, self)
        btnViewZagAreaAliada.setImage("images/visualize.png")
        projecoesScreen.addButton(btnViewZagAreaAliada)

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

        tglGraficos = ToggleButton("tglGraficos", btnUVF.size.x, btnUVF.size.y, movementScrollPanel.pos.x+20, movementScrollPanel.pos.y+30, BUTTON_HELD_SCREEN_COLOR, window, self)
        tglGraficos.setImage("images/button_screen_held.png", "images/button_screen_expanded.png", center=True)
        tglGraficos.setText("Gráficos de controle", BLACK_LABEL, 32, center=True)
        movementScrollPanel.addButton(tglGraficos)

        graficosControleScreen = ScrollingBackground("graficosControleScreen", tglGraficos.size.x, windowSize.y, tglGraficos.pos.x, tglGraficos.pos.y+tglGraficos.size.y+5, BACKGROUND_COLOR, window, self, tglGraficos.size.x, windowSize.y, border=True)
        movementScrollPanel.addScrollingBackground(graficosControleScreen)

        cmbRobotIDGraficosControle = ComboBox("cmbRobotIDGraficosControle", cmbRobotID.size.x, cmbRobotID.size.y, graficosControleScreen.pos.x+20, graficosControleScreen.pos.y+10, WHITE, window, self, "Robô ID", BACKGROUND_COLOR)
        graficosControleScreen.addButton(cmbRobotIDGraficosControle)
        cmbRobotIDGraficosControle.addOptions(["Robô 00", "Robô 01", "Robô 02"])

        lblPosicaoGraficosControle = Label("lblPosicaoGraficosControle", lblPosicao.size.y, cmbRobotIDGraficosControle.pos.x, cmbRobotIDGraficosControle.pos.y+cmbRobotIDGraficosControle.size.y+20, BACKGROUND_COLOR, window, self, "Posição", BLACK_LABEL)
        graficosControleScreen.addBlock(lblPosicaoGraficosControle)

        boxPosicaoGraficosControle = Block("boxPosicaoGraficosControle", boxPosicao.size.x, boxPosicao.size.y, lblPosicaoGraficosControle.pos.x, lblPosicaoGraficosControle.pos.y+lblPosicaoGraficosControle.size.y, BACKGROUND_COLOR, window, self, border=True)
        boxPosicaoGraficosControle.setText("x: 0.0m   y: 0.0m", center=True)
        graficosControleScreen.addBlock(boxPosicaoGraficosControle)

        lblBateriaGraficosControle = Label("lblBateriaGraficosControle", lblBateria.size.y, boxPosicaoGraficosControle.pos.x+boxPosicaoGraficosControle.size.x+60, lblPosicaoGraficosControle.pos.y, BACKGROUND_COLOR, window, self, "Bateria", BLACK_LABEL)
        graficosControleScreen.addBlock(lblBateriaGraficosControle)

        boxBateriaGraficosControle = Block("boxBateriaGraficosControle", boxPosicaoGraficosControle.size.x, boxPosicaoGraficosControle.size.y, lblBateriaGraficosControle.pos.x, boxPosicaoGraficosControle.pos.y, BACKGROUND_COLOR, window, self, border=True)
        boxBateriaGraficosControle.setText("100%", center=True)
        graficosControleScreen.addBlock(boxBateriaGraficosControle)

        lblVelocidadeLinearGraficosControle = Label("lblVelocidadeLinearGraficosControle", lblPosicaoGraficosControle.size.y, lblPosicaoGraficosControle.pos.x, boxPosicaoGraficosControle.pos.y+boxPosicaoGraficosControle.size.y+20, BACKGROUND_COLOR, window, self, "Velocidade linear", BLACK_LABEL)
        graficosControleScreen.addBlock(lblVelocidadeLinearGraficosControle)

        boxVelocidadeLinearGraficosControle = Block("boxVelocidadeLinearGraficosControle", graficosControleScreen.size.x-40, boxPosicaoGraficosControle.size.y*4, boxPosicaoGraficosControle.pos.x, lblVelocidadeLinearGraficosControle.pos.y+lblVelocidadeLinearGraficosControle.size.y, BACKGROUND_COLOR, window, self, border=True)
        graficosControleScreen.addBlock(boxVelocidadeLinearGraficosControle)

        lblVelocidadeAngularGraficosControle = Label("lblVelocidadeAngularGraficosControle", lblVelocidadeLinearGraficosControle.size.y, lblVelocidadeLinearGraficosControle.pos.x, boxVelocidadeLinearGraficosControle.pos.y+boxVelocidadeLinearGraficosControle.size.y+10, BACKGROUND_COLOR, window, self, "Velocidade angular", BLACK_LABEL)
        graficosControleScreen.addBlock(lblVelocidadeAngularGraficosControle)

        boxVelocidadeAngularGraficosControle = Block("boxVelocidadeAngularGraficosControle", boxVelocidadeLinearGraficosControle.size.x, boxVelocidadeLinearGraficosControle.size.y, boxVelocidadeLinearGraficosControle.pos.x, lblVelocidadeAngularGraficosControle.pos.y+lblVelocidadeAngularGraficosControle.size.y, BACKGROUND_COLOR, window, self, border=True)
        graficosControleScreen.addBlock(boxVelocidadeAngularGraficosControle)

        lblAceleracaoGraficosControle = Label("lblAceleracaoGraficosControle", lblVelocidadeAngularGraficosControle.size.y, lblVelocidadeAngularGraficosControle.pos.x, boxVelocidadeAngularGraficosControle.pos.y+boxVelocidadeAngularGraficosControle.size.y+10, BACKGROUND_COLOR, window, self, "Aceleração", BLACK_LABEL)
        graficosControleScreen.addBlock(lblAceleracaoGraficosControle)

        boxAceleracaoGraficosControle = Block("boxAceleracaoGraficosControle", boxVelocidadeAngularGraficosControle.size.x, boxVelocidadeAngularGraficosControle.size.y, boxVelocidadeAngularGraficosControle.pos.x, lblAceleracaoGraficosControle.pos.y+lblAceleracaoGraficosControle.size.y, BACKGROUND_COLOR, window, self, border=True)
        graficosControleScreen.addBlock(boxAceleracaoGraficosControle)

        graficosControleScreen.setVisible(False)

        tglControleManual = ToggleButton("tglControleManual", tglGraficos.size.x, tglGraficos.size.y, tglGraficos.pos.x, tglGraficos.pos.y+tglGraficos.size.y+30, BUTTON_HELD_SCREEN_COLOR, window, self)
        tglControleManual.setImage("images/button_screen_held.png", "images/button_screen_expanded.png", center=True)
        tglControleManual.setText("Controle manual", BLACK_LABEL, 32, center=True)
        movementScrollPanel.addButton(tglControleManual)

        controleManualScreen = ScrollingBackground("controleManualScreen", tglControleManual.size.x, windowSize.y*0.8, tglControleManual.pos.x, tglControleManual.pos.y+tglControleManual.size.y+5, BACKGROUND_COLOR, window, self, tglControleManual.size.x, windowSize.y, border=True)
        movementScrollPanel.addScrollingBackground(controleManualScreen)

        cmbRobotIDControleManual = ComboBox("cmbRobotIDControleManual", cmbRobotIDGraficosControle.size.x, cmbRobotIDGraficosControle.size.y, controleManualScreen.pos.x+20, controleManualScreen.pos.y+20, WHITE, window, self, "Robô ID")
        controleManualScreen.addButton(cmbRobotIDControleManual)
        cmbRobotIDControleManual.addOptions(["Robô 00", "Robô 01", "Robô 02"])

        lblHabilitarJoystick = Label("lblHabilitarJoystick", lblVelocidadeLinearGraficosControle.size.y, cmbRobotIDControleManual.pos.x, cmbRobotIDControleManual.pos.y+cmbRobotIDControleManual.size.y+60, BACKGROUND_COLOR, window, self, "Habilitar joystick")
        controleManualScreen.addBlock(lblHabilitarJoystick)

        tglEnableJoystick = ToggleButton("tglEnableJoystick", tglVirtualJudge.size.x, tglVirtualJudge.size.y, tglVirtualJudge.pos.x, lblHabilitarJoystick.pos.y-12, BACKGROUND_COLOR, window, self)
        tglEnableJoystick.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        controleManualScreen.addButton(tglEnableJoystick)

        cmbDirection = ComboBox("cmbDirection", cmbRobotIDControleManual.size.x, cmbRobotIDControleManual.size.y, cmbRobotIDControleManual.pos.x, lblHabilitarJoystick.pos.y+lblHabilitarJoystick.size.y+60, WHITE, window, self, "Para frente")
        controleManualScreen.addButton(cmbDirection)
        cmbDirection.addOptions(["Para frente", "Curva direita", "Curva esquerda", "Girar horário", "Girar anti-horário"])

        tglEnableDirection = ToggleButton("tglEnableDirection", tglEnableJoystick.size.x, tglEnableJoystick.size.y, tglEnableJoystick.pos.x, cmbDirection.pos.y-12, BACKGROUND_COLOR, window, self)
        tglEnableDirection.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        controleManualScreen.addButton(tglEnableDirection)

        lblHabilitarControleManual = Label("lblHabilitarControleManual", lblHabilitarJoystick.size.y, lblHabilitarJoystick.pos.x, cmbDirection.pos.y+cmbDirection.size.y+60, BACKGROUND_COLOR, window, self, "Habilitar controle manual")
        controleManualScreen.addBlock(lblHabilitarControleManual)

        tglEnableControleManual = ToggleButton("tglEnableControleManual", tglEnableDirection.size.x, tglEnableDirection.size.y, tglEnableDirection.pos.x, lblHabilitarControleManual.pos.y-12, BACKGROUND_COLOR, window, self)
        tglEnableControleManual.setImage("images/toggle_button_on.png", "images/toggle_button_off.png")
        controleManualScreen.addButton(tglEnableControleManual)

        lblVelocidadeLinearControleManual = Block("lblVelocidadeLinearControleManual", controleManualScreen.size.x-20, lblVelocidadeLinearGraficosControle.size.y, controleManualScreen.pos.x+10, lblHabilitarControleManual.pos.y+lblHabilitarControleManual.size.y+60, BACKGROUND_COLOR, window, self)
        lblVelocidadeLinearControleManual.setText("Velocidade linear", center=True)
        controleManualScreen.addBlock(lblVelocidadeLinearControleManual)

        velocidadeLinearBar = Block("velocidadeLinearBar", controleManualScreen.size.x-60, 10, controleManualScreen.pos.x+30, lblVelocidadeLinearControleManual.pos.y+lblVelocidadeLinearControleManual.size.y+5, SLIDER_BAR_COLOR, window, self)
        controleManualScreen.addBlock(velocidadeLinearBar)

        sldVelocidadeLinear = Slider("sldVelocidadeLinear", 20, 10, velocidadeLinearBar.pos.x, velocidadeLinearBar.pos.y+velocidadeLinearBar.size.y/2, BACKGROUND_COLOR, window, self, velocidadeLinearBar)
        controleManualScreen.addButton(sldVelocidadeLinear)
        sldVelocidadeLinear.createLabel()

        lblVelocidadeAngularControleManual = Block("lblVelocidadeAngularControleManual", lblVelocidadeLinearControleManual.size.x, lblVelocidadeLinearControleManual.size.y, lblVelocidadeLinearControleManual.pos.x, velocidadeLinearBar.pos.y+velocidadeLinearBar.size.y+20, BACKGROUND_COLOR, window, self)
        lblVelocidadeAngularControleManual.setText("Velocidade angular", center=True)
        controleManualScreen.addBlock(lblVelocidadeAngularControleManual)

        velocidadeAngularBar = Block("velocidadeAngularBar", velocidadeLinearBar.size.x, velocidadeLinearBar.size.y, controleManualScreen.pos.x+30, lblVelocidadeAngularControleManual.pos.y+lblVelocidadeAngularControleManual.size.y+5, SLIDER_BAR_COLOR, window, self)
        controleManualScreen.addBlock(velocidadeAngularBar)

        sldVelocidadeAngular = Slider("sldVelocidadeAngular", sldVelocidadeLinear.size.x, sldVelocidadeLinear.size.y, velocidadeAngularBar.pos.x, velocidadeAngularBar.pos.y+velocidadeAngularBar.size.y/2, BACKGROUND_COLOR, window, self, velocidadeAngularBar)
        controleManualScreen.addButton(sldVelocidadeAngular)
        sldVelocidadeAngular.createLabel()

        lblAceleracaoControleManual = Block("lblAceleracaoControleManual", lblVelocidadeAngularControleManual.size.x, lblVelocidadeAngularControleManual.size.y, lblVelocidadeAngularControleManual.pos.x, velocidadeAngularBar.pos.y+velocidadeAngularBar.size.y+20, BACKGROUND_COLOR, window, self)
        lblAceleracaoControleManual.setText("Aceleração", center=True)
        controleManualScreen.addBlock(lblAceleracaoControleManual)

        aceleracaoBar = Block("aceleracaoBar", velocidadeLinearBar.size.x, velocidadeLinearBar.size.y, controleManualScreen.pos.x+30, lblAceleracaoControleManual.pos.y+lblAceleracaoControleManual.size.y+5, SLIDER_BAR_COLOR, window, self)
        controleManualScreen.addBlock(aceleracaoBar)

        sldAceleracao = Slider("sldAceleracao", sldVelocidadeLinear.size.x, sldVelocidadeLinear.size.y, aceleracaoBar.pos.x, aceleracaoBar.pos.y+aceleracaoBar.size.y/2, BACKGROUND_COLOR, window, self, aceleracaoBar)
        controleManualScreen.addButton(sldAceleracao)
        sldAceleracao.createLabel()

        controleManualScreen.setVisible(False)

        tglControleUVF = ToggleButton("tglControleUVF", tglControleManual.size.x, tglControleManual.size.y, tglControleManual.pos.x, tglControleManual.pos.y+tglControleManual.size.y+30, BUTTON_HELD_SCREEN_COLOR, window, self)
        tglControleUVF.setImage("images/button_screen_held.png", "images/button_screen_expanded.png", center=True)
        tglControleUVF.setText("Controle UVF", BLACK_LABEL, 32, center=True)
        movementScrollPanel.addButton(tglControleUVF)

        controleUVFScreen = ScrollingBackground("controleUVFScreen", tglControleUVF.size.x, windowSize.y*0.8, tglControleUVF.pos.x, tglControleUVF.pos.y+tglControleUVF.size.y+5, BACKGROUND_COLOR, window, self, tglControleUVF.size.x, windowSize.y, border=True)
        movementScrollPanel.addScrollingBackground(controleUVFScreen)

        cmbRobotIDControleUVF = ComboBox("cmbRobotIDControleUVF", cmbRobotIDControleManual.size.x, cmbRobotIDControleManual.size.y, cmbRobotIDControleManual.pos.x, controleUVFScreen.pos.y+30, WHITE, window, self, "Robô ID")
        controleUVFScreen.addButton(cmbRobotIDControleUVF)
        cmbRobotIDControleUVF.addOptions(["Robô 00", "Robô 01", "Robô 02"])

        lblVisualizarCampoControleUVF = Label("lblVisualizarCampoControleUVF", lblVisualizarCampoUVF.size.y, cmbRobotIDControleUVF.pos.x, cmbRobotIDControleUVF.pos.y+cmbRobotIDControleUVF.size.y+30, BACKGROUND_COLOR, window, self, "Visualizar campo")
        controleUVFScreen.addBlock(lblVisualizarCampoControleUVF)

        lblHabilitaVisualizacaoCamposControleUVF = Label("lblHabilitaVisualizacaoCamposControleUVF", lblHabilitaVisualizacaoCampos.size.y, lblVisualizarCampoControleUVF.pos.x+30, lblVisualizarCampoControleUVF.pos.y+lblVisualizarCampoControleUVF.size.y-6, BACKGROUND_COLOR, window, self, "Habilita a visualização do campo UVF do robô", fontSize=21)
        controleUVFScreen.addBlock(lblHabilitaVisualizacaoCamposControleUVF)

        btnViewCampoControleUVF = Button("btnViewCampoControleUVF", btnViewCampoUVF.size.x, btnViewCampoUVF.size.y, lblHabilitaVisualizacaoCamposControleUVF.pos.x+lblHabilitaVisualizacaoCamposControleUVF.size.x+100, lblVisualizarCampoControleUVF.pos.y+10, BACKGROUND_COLOR, window, self)
        btnViewCampoControleUVF.setImage("images/visualize.png")
        controleUVFScreen.addButton(btnViewCampoControleUVF)

        lblKw = Label("lblKw", lblVisualizarCampoControleUVF.size.y, lblHabilitaVisualizacaoCamposControleUVF.pos.x-5, lblHabilitaVisualizacaoCamposControleUVF.pos.y+lblHabilitaVisualizacaoCamposControleUVF.size.y+50, BACKGROUND_COLOR, window, self, "kw")
        controleUVFScreen.addBlock(lblKw)

        spnKw = Spinner("spnKw", spnRaio.size.x, spnRaio.size.y, lblKw.pos.x, lblKw.pos.y+lblKw.size.y-5, WHITE, window, self)
        spnKw.setText("10", center=True)
        controleUVFScreen.addButton(spnKw)

        lblKp = Label("lblKp", lblKw.size.y, spnKw.increaseButton.pos.x+spnKw.increaseButton.size.x*3, lblKw.pos.y, BACKGROUND_COLOR, window, self, "kp")
        controleUVFScreen.addBlock(lblKp)

        spnKp = Spinner("spnKp", spnKw.size.x, spnKw.size.y, lblKp.pos.x, lblKp.pos.y+lblKp.size.y-5, WHITE, window, self)
        spnKp.setText("10", center=True)
        controleUVFScreen.addButton(spnKp)

        lblL = Label("lblL", lblKw.size.y, lblKw.pos.x, spnKw.pos.y+spnKw.size.y*1.5, BACKGROUND_COLOR, window, self, "L")
        controleUVFScreen.addBlock(lblL)

        spnL = Spinner("spnL", spnKw.size.x, spnKw.size.y, spnKw.pos.x, lblL.pos.y+lblL.size.y-5, WHITE, window, self)
        spnL.setText("10", center=True)
        controleUVFScreen.addButton(spnL)

        lblVmax = Label("lblVmax", lblKp.size.y, lblKp.pos.x, lblL.pos.y, BACKGROUND_COLOR, window, self, "vmax")
        controleUVFScreen.addBlock(lblVmax)

        spnVmax = Spinner("spnVmax", spnKp.size.x, spnKp.size.y, spnKp.pos.x, spnL.decreaseButton.pos.y, WHITE, window, self)
        spnVmax.setText("10", center=True)
        controleUVFScreen.addButton(spnVmax)

        lblMu = Label("lblMu", lblL.size.y, lblL.pos.x, spnL.pos.y+spnL.size.y*1.5, BACKGROUND_COLOR, window, self, "mu")
        controleUVFScreen.addBlock(lblMu)

        spnMu = Spinner("spnMu", spnL.size.x, spnL.size.y, spnL.pos.x, lblMu.pos.y+lblMu.size.y-5, WHITE, window, self)
        spnMu.setText("10", center=True)
        controleUVFScreen.addButton(spnMu)
        
        lblVref = Label("lblVref", lblVmax.size.y, lblVmax.pos.x, lblMu.pos.y, BACKGROUND_COLOR, window, self, "vref")
        controleUVFScreen.addBlock(lblVref)

        spnVref = Spinner("spnVref", spnVmax.size.x, spnVmax.size.y, spnVmax.pos.x, spnMu.decreaseButton.pos.y, WHITE, window, self)
        spnVref.setText("10", center=True)
        controleUVFScreen.addButton(spnVref)

        lblR = Label("lblR", lblL.size.y, lblMu.pos.x, spnMu.pos.y+spnMu.size.y*1.5, BACKGROUND_COLOR, window, self, "r")
        controleUVFScreen.addBlock(lblR)

        spnR = Spinner("spnR", spnMu.size.x, spnMu.size.y, spnMu.pos.x, lblR.pos.y+lblR.size.y-5, WHITE, window, self)
        spnR.setText("10", center=True)
        controleUVFScreen.addButton(spnR)

        lblMaxAngError = Label("lblMaxAngError", lblVref.size.y, lblVref.pos.x, lblR.pos.y, BACKGROUND_COLOR, window, self, "maxangerror")
        controleUVFScreen.addBlock(lblMaxAngError)

        spnMaxAngError = Spinner("spnMaxAngError", spnVref.size.x, spnVref.size.y, spnVref.pos.x, spnR.decreaseButton.pos.y, WHITE, window, self)
        spnMaxAngError.setText("10", center=True)
        controleUVFScreen.addButton(spnMaxAngError)

        lblTau = Label("lblTau", lblR.size.y, lblR.pos.x, spnR.pos.y+spnR.size.y*1.5, BACKGROUND_COLOR, window, self, "tau")
        controleUVFScreen.addBlock(lblTau)

        spnTau = Spinner("spnTau", spnR.size.x, spnR.size.y, spnR.pos.x, lblTau.pos.y+lblTau.size.y-5, WHITE, window, self)
        spnTau.setText("10", center=True)
        controleUVFScreen.addButton(spnTau)

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

        lblErrosWarnings = Label("lblErrosWarnings", lblInfoBola.size.y, gameMiniMap.pos.x, gameMiniMap.pos.y+gameMiniMap.size.y+20, BACKGROUND_COLOR, window, self, "Erros e Warnings", BLACK_LABEL, 26)
        self.communicationScreen.addBlock(lblErrosWarnings)
        
        errosWarningsLabelArea = LabelArea("errosWarningsLabelArea", boxErrosWarnings.size.x-30, 0, boxErrosWarnings.pos.x+15, boxErrosWarnings.pos.y+20, BACKGROUND_COLOR, window, self)
        errosWarningsLabelArea.setText("", center=False)
        errosWarningsScrollPanel.addBlock(errosWarningsLabelArea)
        errosWarningsLabelArea.addLabel("Comunicação Wifi: Porta Serial não encontrada")

        linhaBaixoBoxErrosWarnings = Block("linhaBaixoBoxErrosWarnings", boxErrosWarnings.size.x, 2, boxErrosWarnings.pos.x, boxErrosWarnings.pos.y+boxErrosWarnings.size.y-2, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaBaixoBoxErrosWarnings)

        faixaBackgroundBoxErrosWarningsEnd = Block("faixaBackgroundBoxErrosWarningsEnd", faixaBackgroundGameMiniMapErrosWarnings.size.x, faixaBackgroundGameMiniMapErrosWarnings.size.y, 0, boxErrosWarnings.pos.y+boxErrosWarnings.size.y, BACKGROUND_COLOR, window, self)
        self.communicationScreen.addBlock(faixaBackgroundBoxErrosWarningsEnd)

        lblWireless = Label("lblWireless", lblCorTime.size.y, screenDivisionRightMargin.pos.x+24, gameMiniMap.pos.y, BACKGROUND_COLOR, window, self, "Wireless", BLACK_LABEL, 28)
        self.communicationScreen.addBlock(lblWireless)

        boxWireless = Block("boxWireless", boxErrosWarnings.size.x-16, boxErrosWarnings.size.y-35, lblWireless.pos.x, lblWireless.pos.y+lblWireless.size.y, BACKGROUND_COLOR, window, self, border=True)
        self.communicationScreen.addBlock(boxWireless)

        robotIDCommunicationComboBox = ComboBox("robotIDCommunicationComboBox", cmbRobotID.size.x, cmbRobotID.size.y, boxWireless.pos.x+20, boxWireless.pos.y+20, WHITE, window, self, "Robô ID")
        self.communicationScreen.addButton(robotIDCommunicationComboBox)
        robotIDCommunicationComboBox.addOptions(["Robô 00", "Robô 01", "Robô 02"])

        lblBateriaCommunication = Label("lblBateriaCommunication", lblBateria.size.y, robotIDCommunicationComboBox.pos.x+4, robotIDCommunicationComboBox.pos.y+robotIDCommunicationComboBox.size.y+20, BACKGROUND_COLOR, window, self, "Bateria:", BLACK_LABEL)
        self.communicationScreen.addBlock(lblBateriaCommunication)

        lblpercentBatteryCommunication = Label("lblpercentBatteryCommunication", lblBateriaCommunication.size.y, lblBateriaCommunication.pos.x+lblBateriaCommunication.size.x+5, lblBateriaCommunication.pos.y, BACKGROUND_COLOR, window, self, "100%")
        self.communicationScreen.addBlock(lblpercentBatteryCommunication)

        lblStatusWireless = Label("lblStatusWireless", lblBateriaCommunication.size.y, lblpercentBatteryCommunication.pos.x+340, lblBateriaCommunication.pos.y, BACKGROUND_COLOR, window, self, "Status:", BLACK_LABEL)
        self.communicationScreen.addBlock(lblStatusWireless)

        lblValueStatusWireless = Label("lblValueStatusWireless", lblStatusWireless.size.y, lblStatusWireless.pos.x+lblStatusWireless.size.x+10, lblStatusWireless.pos.y, BACKGROUND_COLOR, window, self, "Conectado")
        self.communicationScreen.addBlock(lblValueStatusWireless)

        lblVelocidadeEnviada = Label("lblVelocidadeEnviada", lblBateriaCommunication.size.y, lblBateriaCommunication.pos.x, lblBateriaCommunication.pos.y+lblBateriaCommunication.size.y+10, BACKGROUND_COLOR, window, self, "Velocidade enviada", BLACK_LABEL)
        self.communicationScreen.addBlock(lblVelocidadeEnviada)

        lblValueVelocidadeEnviada = Label("lblValueVelocidadeEnviada", lblVelocidadeEnviada.size.y, lblVelocidadeEnviada.pos.x+lblVelocidadeEnviada.size.x+30, lblVelocidadeEnviada.pos.y, BACKGROUND_COLOR, window, self, "v: 0.0   w: 0.0")
        self.communicationScreen.addBlock(lblValueVelocidadeEnviada)

        lblFrequenciaEnvio = Label("lblFrequenciaEnvio", lblVelocidadeEnviada.size.y, lblVelocidadeEnviada.pos.x, lblVelocidadeEnviada.pos.y+lblVelocidadeEnviada.size.y+10, BACKGROUND_COLOR, window, self, "Frequência de envio", BLACK_LABEL)
        self.communicationScreen.addBlock(lblFrequenciaEnvio)

        lblValueFrequenciaEnvio = Label("lblValueFrequenciaEnvio", lblpercentBatteryCommunication.size.y, lblValueVelocidadeEnviada.pos.x, lblFrequenciaEnvio.pos.y, BACKGROUND_COLOR, window, self, "2 MHz")
        self.communicationScreen.addBlock(lblValueFrequenciaEnvio)

        linhaBaixoBoxWireless = Block("linhaBaixoBoxWireless", boxWireless.size.x, 2, boxWireless.pos.x, boxWireless.pos.y+boxWireless.size.y, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaBaixoBoxWireless)

        faixaBackgroundWirelessReferee = Block("faixaBackgroundWirelessReferee", screenDivisionRightMargin.size.x, 50, screenDivisionRightMargin.pos.x, boxWireless.pos.y+boxWireless.size.y, BACKGROUND_COLOR, window, self)
        self.communicationScreen.addBlock(faixaBackgroundWirelessReferee)

        lblReferee = Label("lblReferee", lblWireless.size.y, lblWireless.pos.x, boxWireless.pos.y+boxWireless.size.y+20, BACKGROUND_COLOR, window, self, "Referee", BLACK_LABEL, 28)
        self.communicationScreen.addBlock(lblReferee)

        boxReferee = Block("boxReferee", boxWireless.size.x, boxWireless.size.y*0.7, boxWireless.pos.x, lblReferee.pos.y+lblReferee.size.y, BACKGROUND_COLOR, window, self, border=True)
        self.communicationScreen.addBlock(boxReferee)

        linhaCimaBoxReferee = Block("linhaCimaBoxReferee", boxReferee.size.x, 2, boxReferee.pos.x, boxReferee.pos.y, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaCimaBoxReferee)

        lblComandoRecebido = Label("lblComandoRecebido", lblFrequenciaEnvio.size.y, boxReferee.pos.x+20, boxReferee.pos.y+20, BACKGROUND_COLOR, window, self, "Comando recebido:", BLACK_LABEL)
        self.communicationScreen.addBlock(lblComandoRecebido)

        lblValueComandoRecebido = Label("lblValueComandoRecebido", lblValueVelocidadeEnviada.size.y, lblComandoRecebido.pos.x+lblComandoRecebido.size.x+40, lblComandoRecebido.pos.y, BACKGROUND_COLOR, window, self, "HALT")
        self.communicationScreen.addBlock(lblValueComandoRecebido)

        lblStatusReferee = Label("lblStatusReferee", lblStatusWireless.size.y, lblStatusWireless.pos.x, lblComandoRecebido.pos.y, BACKGROUND_COLOR, window, self, "Status:", BLACK_LABEL)
        self.communicationScreen.addBlock(lblStatusReferee)

        lblValueStatusReferee = Label("lblValueStatusReferee", lblValueStatusWireless.size.y, lblValueStatusWireless.pos.x, lblStatusReferee.pos.y, BACKGROUND_COLOR, window, self, "Desconectado")
        self.communicationScreen.addBlock(lblValueStatusReferee)

        lblLadoCampoReferee = Label("lblLadoCampoReferee", lblComandoRecebido.size.y, lblComandoRecebido.pos.x, lblComandoRecebido.pos.y+lblComandoRecebido.size.y+10, BACKGROUND_COLOR, window, self, "Lado do campo:", BLACK_LABEL)
        self.communicationScreen.addBlock(lblLadoCampoReferee)

        lblValueLadoCampoReferee = Label("lblValueLadoCampoReferee", lblValueStatusReferee.size.y, lblValueComandoRecebido.pos.x, lblLadoCampoReferee.pos.y, BACKGROUND_COLOR, window, self, "Esquerdo")
        self.communicationScreen.addBlock(lblValueLadoCampoReferee)

        lblCorTimeReferee = Label("lblCorTimeReferee", lblLadoCampoReferee.size.y, lblLadoCampoReferee.pos.x, lblLadoCampoReferee.pos.y+lblLadoCampoReferee.size.y+10, BACKGROUND_COLOR, window, self, "Cor do time:", BLACK_LABEL)
        self.communicationScreen.addBlock(lblCorTimeReferee)

        lblValueCorTimeReferee = Label("lblValueCorTimeReferee", lblCorTimeReferee.size.y, lblValueLadoCampoReferee.pos.x, lblCorTimeReferee.pos.y, BACKGROUND_COLOR, window, self, "Amarelo")
        self.communicationScreen.addBlock(lblValueCorTimeReferee)

        linhaBaixoBoxReferee = Block("linhaBaixoBoxReferee", boxReferee.size.x, 2, boxReferee.pos.x, boxReferee.pos.y+boxReferee.size.y, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaBaixoBoxReferee)

        faixaBackgroundRefereeVSSVision = Block("faixaBackgroundRefereeVSSVision", screenDivisionRightMargin.size.x, 50, screenDivisionRightMargin.pos.x, boxReferee.pos.y+boxReferee.size.y, BACKGROUND_COLOR, window, self)
        self.communicationScreen.addBlock(faixaBackgroundRefereeVSSVision)

        lblVSSVision = Label("lblVSSVision", lblReferee.size.y, lblReferee.pos.x, boxReferee.pos.y+boxReferee.size.y+20, BACKGROUND_COLOR, window, self, "VSS-VISION", BLACK_LABEL, 28)
        self.communicationScreen.addBlock(lblVSSVision)

        boxVSSVision = Block("boxVSSVision", boxReferee.size.x, boxWireless.size.y, boxReferee.pos.x, lblVSSVision.pos.y+lblVSSVision.size.y, BACKGROUND_COLOR, window, self, border=True, preference=False)
        self.communicationScreen.addBlock(boxVSSVision)

        linhaCimaBoxVSSVision = Block("linhaCimaBoxVSSVision", boxVSSVision.size.x, 2, boxVSSVision.pos.x, boxVSSVision.pos.y, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaCimaBoxVSSVision)

        vssVisionScrollPanel = ScrollingBackground("vssVisionScrollPanel", boxVSSVision.size.x-4, boxVSSVision.size.y*1.9, boxVSSVision.pos.x+2, boxVSSVision.pos.y+2, BACKGROUND_COLOR, window, self, boxVSSVision.size.y, boxVSSVision.pos.y+2, preference=False)
        self.communicationScreen.addScrollingBackground(vssVisionScrollPanel)

        lblCorTimeVSSVision = Label("lblCorTimeVSSVision", lblCorTimeReferee.size.y, lblCorTimeReferee.pos.x, boxVSSVision.pos.y+20, BACKGROUND_COLOR, window, self, "Time Azul", BLACK_LABEL)
        vssVisionScrollPanel.addBlock(lblCorTimeVSSVision)

        lblID0VSSVision = Label("lblID0VSSVision", lblCorTimeVSSVision.size.y, lblCorTimeVSSVision.pos.x, lblCorTimeVSSVision.pos.y+lblCorTimeVSSVision.size.y, BACKGROUND_COLOR, window, self, "ID 0", BLACK_LABEL)
        vssVisionScrollPanel.addBlock(lblID0VSSVision)

        lblStatusVSSVision = Label("lblStatusVSSVision", lblStatusReferee.size.y, lblStatusReferee.pos.x, lblCorTimeVSSVision.pos.y, BACKGROUND_COLOR, window, self, "Status:", BLACK_LABEL)
        vssVisionScrollPanel.addBlock(lblStatusVSSVision)
        
        lblValueStatusVSSVision = Label("lblValueStatusVSSVision", lblValueStatusReferee.size.y, lblValueStatusReferee.pos.x, lblStatusVSSVision.pos.y, BACKGROUND_COLOR, window, self, "Conectado")
        vssVisionScrollPanel.addBlock(lblValueStatusVSSVision)

        lblPosicaoID0VSSVision = Label("lblPosicaoID0VSSVision", lblID0VSSVision.size.y, lblID0VSSVision.pos.x+10, lblID0VSSVision.pos.y+lblID0VSSVision.size.y, BACKGROUND_COLOR, window, self, "Posição", BLACK_LABEL)
        vssVisionScrollPanel.addBlock(lblPosicaoID0VSSVision)

        lblValuePosicaoID0VSSVision = Label("lblValuePosicaoID0VSSVision", lblPosicaoID0VSSVision.size.y, lblValueComandoRecebido.pos.x-10, lblPosicaoID0VSSVision.pos.y, BACKGROUND_COLOR, window, self, "x: 0.0  y: 0.0  z: 0.0 th: 0.0")
        vssVisionScrollPanel.addBlock(lblValuePosicaoID0VSSVision)

        lblVelocidadeID0VSSVision = Label("lblVelocidadeID0VSSVision", lblPosicaoID0VSSVision.size.y, lblPosicaoID0VSSVision.pos.x, lblPosicaoID0VSSVision.pos.y+lblPosicaoID0VSSVision.size.y, BACKGROUND_COLOR, window, self, "Velocidade", BLACK_LABEL)
        vssVisionScrollPanel.addBlock(lblVelocidadeID0VSSVision)

        lblValueVelocidadeID0VSSVision = Label("lblValueVelocidadeID0VSSVision", lblValuePosicaoID0VSSVision.size.y, lblValuePosicaoID0VSSVision.pos.x, lblVelocidadeID0VSSVision.pos.y, BACKGROUND_COLOR, window, self, "v: 0.0  w: 0.0")
        vssVisionScrollPanel.addBlock(lblValueVelocidadeID0VSSVision)

        lblID1VSSVision = Label("lblID1VSSVision", lblCorTimeVSSVision.size.y, lblCorTimeVSSVision.pos.x, lblVelocidadeID0VSSVision.pos.y+lblVelocidadeID0VSSVision.size.y+20, BACKGROUND_COLOR, window, self, "ID 1", BLACK_LABEL)
        vssVisionScrollPanel.addBlock(lblID1VSSVision)

        lblPosicaoID1VSSVision = Label("lblPosicaoID1VSSVision", lblID1VSSVision.size.y, lblID1VSSVision.pos.x+10, lblID1VSSVision.pos.y+lblID1VSSVision.size.y, BACKGROUND_COLOR, window, self, "Posição", BLACK_LABEL)
        vssVisionScrollPanel.addBlock(lblPosicaoID1VSSVision)

        lblValuePosicaoID1VSSVision = Label("lblValuePosicaoID1VSSVision", lblPosicaoID1VSSVision.size.y, lblValueComandoRecebido.pos.x-10, lblPosicaoID1VSSVision.pos.y, BACKGROUND_COLOR, window, self, "x: 0.0  y: 0.0  z: 0.0 th: 0.0")
        vssVisionScrollPanel.addBlock(lblValuePosicaoID1VSSVision)

        lblVelocidadeID1VSSVision = Label("lblVelocidadeID1VSSVision", lblPosicaoID1VSSVision.size.y, lblPosicaoID1VSSVision.pos.x, lblPosicaoID1VSSVision.pos.y+lblPosicaoID1VSSVision.size.y, BACKGROUND_COLOR, window, self, "Velocidade", BLACK_LABEL)
        vssVisionScrollPanel.addBlock(lblVelocidadeID1VSSVision)

        lblValueVelocidadeID1VSSVision = Label("lblValueVelocidadeID1VSSVision", lblValuePosicaoID1VSSVision.size.y, lblValuePosicaoID1VSSVision.pos.x, lblVelocidadeID1VSSVision.pos.y, BACKGROUND_COLOR, window, self, "v: 0.0  w: 0.0")
        vssVisionScrollPanel.addBlock(lblValueVelocidadeID1VSSVision)

        lblID2VSSVision = Label("lblID2VSSVision", lblCorTimeVSSVision.size.y, lblCorTimeVSSVision.pos.x, lblVelocidadeID1VSSVision.pos.y+lblVelocidadeID1VSSVision.size.y+20, BACKGROUND_COLOR, window, self, "ID 2", BLACK_LABEL)
        vssVisionScrollPanel.addBlock(lblID2VSSVision)

        lblPosicaoID2VSSVision = Label("lblPosicaoID2VSSVision", lblID2VSSVision.size.y, lblID2VSSVision.pos.x+10, lblID2VSSVision.pos.y+lblID2VSSVision.size.y, BACKGROUND_COLOR, window, self, "Posição", BLACK_LABEL)
        vssVisionScrollPanel.addBlock(lblPosicaoID2VSSVision)

        lblValuePosicaoID2VSSVision = Label("lblValuePosicaoID2VSSVision", lblPosicaoID2VSSVision.size.y, lblValueComandoRecebido.pos.x-10, lblPosicaoID2VSSVision.pos.y, BACKGROUND_COLOR, window, self, "x: 0.0  y: 0.0  z: 0.0 th: 0.0")
        vssVisionScrollPanel.addBlock(lblValuePosicaoID2VSSVision)

        lblVelocidadeID2VSSVision = Label("lblVelocidadeID2VSSVision", lblPosicaoID2VSSVision.size.y, lblPosicaoID2VSSVision.pos.x, lblPosicaoID2VSSVision.pos.y+lblPosicaoID2VSSVision.size.y, BACKGROUND_COLOR, window, self, "Velocidade", BLACK_LABEL)
        vssVisionScrollPanel.addBlock(lblVelocidadeID2VSSVision)

        lblValueVelocidadeID2VSSVision = Label("lblValueVelocidadeID2VSSVision", lblValuePosicaoID2VSSVision.size.y, lblValuePosicaoID2VSSVision.pos.x, lblVelocidadeID2VSSVision.pos.y, BACKGROUND_COLOR, window, self, "v: 0.0  w: 0.0")
        vssVisionScrollPanel.addBlock(lblValueVelocidadeID2VSSVision)

        faixaBackgroundBoxVSSVisionEnd = Block("faixaBackgroundBoxVSSVisionEnd", screenDivisionRightMargin.size.x, 50, screenDivisionRightMargin.pos.x, boxVSSVision.pos.y+boxVSSVision.size.y, BACKGROUND_COLOR, window, self)
        self.communicationScreen.addBlock(faixaBackgroundBoxVSSVisionEnd)

        linhaBaixoBoxVSSVision = Block("linhaBaixoBoxVSSVision", boxVSSVision.size.x, 2, boxVSSVision.pos.x, boxVSSVision.pos.y+boxVSSVision.size.y-2, BORDER_COLOR, window, self)
        self.communicationScreen.addBlock(linhaBaixoBoxVSSVision)

        # Draw the navigationScreen
        self.activeScreen.draw()


       # Instance button methods 
        def changeToNavigationScreen(self):
            """Instance method of btnNavegacao to make the button change the screen to the navigation screen"""
            #window = pg.display.set_mode((int(windowSize.x), int(windowSize.y))) 
            # perhaps is better to fill the screen towards doing this
            self.window.fill(BACKGROUND_COLOR)
            window.fill(BACKGROUND_COLOR)
            if self.gui.activeScreen != self.gui.navigationScreen:
                self.gui.activeScreen = self.gui.navigationScreen
            self.gui.activeScreen.menuBar.buttons[btnNavegacao.name].color = BORDER_COLOR
            self.gui.activeScreen.menuBar.buttons[btnMovimentacao.name].color = BACKGROUND_COLOR
            self.gui.activeScreen.menuBar.buttons[btnComunicacao.name].color = BACKGROUND_COLOR
            self.gui.activeScreen.draw()
        self.navigationScreen.menuBar.buttons[btnNavegacao.name].actionAssign(changeToNavigationScreen)
        

        def changeToMovementScreen(self):
            """Instance method of btnMovimentacao to make the button change the screen to the movement screen"""
            #window = pg.display.set_mode((int(windowSize.x), int(windowSize.y))) 
            # perhaps is better to fill the screen towards doing this
            self.window.fill(BACKGROUND_COLOR)
            window.fill(BACKGROUND_COLOR)
            if self.gui.activeScreen != self.gui.movementScreen:
                self.gui.activeScreen = self.gui.movementScreen
            self.gui.activeScreen.menuBar.buttons[btnNavegacao.name].color = BACKGROUND_COLOR
            self.gui.activeScreen.menuBar.buttons[btnMovimentacao.name].color = BORDER_COLOR
            self.gui.activeScreen.menuBar.buttons[btnComunicacao.name].color = BACKGROUND_COLOR
            self.gui.activeScreen.draw()
        self.movementScreen.menuBar.buttons[btnMovimentacao.name].actionAssign(changeToMovementScreen)
        

        def changeToCommunicationScreen(self):
            """Instance method of btnComunicacao to make the button change the screen to the communication screen"""
            #window = pg.display.set_mode((int(windowSize.x), int(windowSize.y))) 
            # perhaps is better to fill the screen towards doing this
            self.window.fill(BACKGROUND_COLOR)
            window.fill(BACKGROUND_COLOR)
            if self.gui.activeScreen != self.gui.communicationScreen:
                self.gui.activeScreen = self.gui.communicationScreen
            self.gui.activeScreen.menuBar.buttons[btnNavegacao.name].color = BACKGROUND_COLOR
            self.gui.activeScreen.menuBar.buttons[btnMovimentacao.name].color = BACKGROUND_COLOR
            self.gui.activeScreen.menuBar.buttons[btnComunicacao.name].color = BORDER_COLOR
            self.gui.activeScreen.draw()
        self.communicationScreen.menuBar.buttons[btnComunicacao.name].actionAssign(changeToCommunicationScreen)


        def closeWindow(self):
            """Instance method of btnClose to make the application stop running and close the window"""
            if self.gui.unbrain_loop is not None:
                self.gui.unbrain_loop.handle_SIGINT(None, None, shut_down=True)
                self.gui.unbrain_loop = None
                print("UnBrain stopped")
            self.gui.running = False
        self.navigationScreen.menuBar.buttons[btnClose.name].actionAssign(closeWindow)


        def minimizeWindow(self):
            """Instance method of btnMinimize to minimize the window of the application"""
            pg.display.iconify()
        self.navigationScreen.menuBar.buttons[btnMinimize.name].actionAssign(minimizeWindow)


        def maximizeWindow(self):
            """Instance method of btnMaximize to minimize the window of the application"""
            pg.display.toggle_fullscreen()
        self.navigationScreen.menuBar.buttons[btnMaximize.name].actionAssign(maximizeWindow)


        def showOptionsColorComboBox(self):
            """Instance method to show the color options in the cmbChooseColor"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbChooseColor.name].actionAssign(showOptionsColorComboBox)
        

        def chooseOptionColorComboBox(self):
            """Instance method to choose the option in cmbChooseColor"""
            if self.getText() == "Azul" and self.screen.buttons[tglInversao.name].isOn():
                self.screen.buttons[tglInversao.name].action()
            elif self.getText() == "Amarelo" and not self.screen.buttons[tglInversao.name].isOn():
                self.screen.buttons[tglInversao.name].action()
            self.screen.buttons[cmbChooseColor.name].setText(self.getText(), center=True)
            self.screen.buttons[cmbChooseColor.name].setOptionsVisibility(False)
        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbChooseColor.name].options:
            button.actionAssign(chooseOptionColorComboBox)


        def changeSide(self):
            """Instance method to change the state of tglInversao"""
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
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[tglInversao.name].actionAssign(changeSide)


        def showOptionsTypeEntityComboBox(self):
            """Instance method to show the type options in cmbChooseEntityType"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbChooseEntityType.name].actionAssign(showOptionsTypeEntityComboBox)


        def chooseOptionTypeEntityComboBox(self):
            """Instance method to choose the option in the cmbChooseEntityType"""
            self.screen.buttons[cmbChooseEntityType.name].setText(self.getText(), center=True)
            self.screen.buttons[cmbChooseEntityType.name].setOptionsVisibility(False)
        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbChooseEntityType.name].options:
            button.actionAssign(chooseOptionTypeEntityComboBox)


        def showOptionsNumRobotsComboBox(self):
            """Instance method to show the num robots options in cmbChooseNumRobots"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbChooseNumRobots.name].actionAssign(showOptionsNumRobotsComboBox)


        def chooseOptionNumRobotsComboBox(self):
            """Instance method to choose the option in the cmbChooseNumRobots"""
            self.screen.buttons[cmbChooseNumRobots.name].setText(self.getText(), center=True)
            self.screen.buttons[cmbChooseNumRobots.name].setOptionsVisibility(False)
        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbChooseNumRobots.name].options:
            button.actionAssign(chooseOptionNumRobotsComboBox)


        def showOptionscmbRobotID(self):
            """Instance method to show the type options in cmbRobotID"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbRobotID.name].actionAssign(showOptionscmbRobotID)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[cmbRobotIDUVF.name].actionAssign(showOptionscmbRobotID)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[projecoesScreen.name].buttons[cmbRobotIDProjecoes.name].actionAssign(showOptionscmbRobotID)


        def chooseOptioncmbRobotID(self):
            """Instance method to choose the option in the cmbRobotID"""
            self.screen.buttons[cmbRobotID.name].setText(self.getText(), center=True)
            self.screen.buttons[cmbRobotID.name].setOptionsVisibility(False)
        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbRobotID.name].options:
            button.actionAssign(chooseOptioncmbRobotID)


        def changeManualVirtualPos(self):
            """Instance method to change the state of tglVirtualJudge"""
            self.changeState()
            self.imgs[self.isOn()]
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[tglVirtualJudge.name].actionAssign(changeManualVirtualPos)

        def showOptionscmbPositioning(self):
            """Instance method to show the positioning options in cmbPositioning"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbPositioning.name].actionAssign(showOptionscmbPositioning)


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
            self.screen.buttons[tglProjecoes.name].pos.y += resizeRange
            for block in self.screen.scrollingBackgrounds[projecoesScreen.name].blocks.values():
                block.pos.y += resizeRange
            for button in self.screen.scrollingBackgrounds[projecoesScreen.name].buttons.values():
                button.pos.y += resizeRange
            self.screen.scrollingBackgrounds[UVFScreen.name].setVisible(visible)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[btnUVF.name].actionAssign(expandUVFScreen)


        def chooseOptioncmbRobotIDUVF(self):
            """Instance method to choose the option in the cmbRobotIDUVF"""
            self.screen.buttons[cmbRobotIDUVF.name].setText(self.getText(), center=True)
            self.screen.buttons[cmbRobotIDUVF.name].setOptionsVisibility(False)
        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[cmbRobotIDUVF.name].options:
            button.actionAssign(chooseOptioncmbRobotIDUVF)


        def showFieldComboBox(self):
            """Instance method to show the field options in cmbSelectField"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[cmbSelectField.name].actionAssign(showFieldComboBox)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[graficosControleScreen.name].buttons[cmbRobotIDGraficosControle.name].actionAssign(showFieldComboBox)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[cmbRobotIDControleManual.name].actionAssign(showFieldComboBox)


        def chooseFieldComboBox(self):
            """Instance method to choose the option in the cmbSelectField"""
            self.screen.buttons[cmbSelectField.name].setText(self.getText(), center=True)
            self.screen.buttons[cmbSelectField.name].setOptionsVisibility(False)
        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[cmbSelectField.name].options:
            button.actionAssign(chooseFieldComboBox)


        def changePontoFinal(self):
            """Instance method to change the state of tglPontoFinalSelec"""
            self.changeState()
            self.imgs[self.isOn()]
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[tglPontoFinalSelec.name].actionAssign(changePontoFinal)


        def changeViewAllFields(self):
            """Instance method to change the state of tglVisualizarTodosCampos"""
            self.changeState()
            self.imgs[self.isOn()]
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[UVFScreen.name].buttons[tglVisualizarTodosCampos.name].actionAssign(changeViewAllFields)


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
        self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[tglProjecoes.name].actionAssign(expandprojecoesScreen)


        def cmbRhooseOptionRobotIDProjecoes(self):
            """Instance method to choose the option in the cmbRobotIDProjecoes"""
            self.screen.buttons[cmbRobotIDProjecoes.name].setText(self.getText(), center=True)
            self.screen.buttons[cmbRobotIDProjecoes.name].setOptionsVisibility(False)
        for button in self.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].scrollingBackgrounds[projecoesScreen.name].buttons[cmbRobotIDProjecoes.name].options:
            button.actionAssign(cmbRhooseOptionRobotIDProjecoes)


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
            self.screen.buttons[tglControleManual.name].pos.y += resizeRange
            for block in self.screen.scrollingBackgrounds[controleManualScreen.name].blocks.values():
                block.pos.y += resizeRange
            for button in self.screen.scrollingBackgrounds[controleManualScreen.name].buttons.values():
                button.pos.y += resizeRange
            self.screen.scrollingBackgrounds[controleUVFScreen.name].pos.y += resizeRange
            self.screen.buttons[tglControleUVF.name].pos.y += resizeRange
            for block in self.screen.scrollingBackgrounds[controleUVFScreen.name].blocks.values():
                block.pos.y += resizeRange
            for button in self.screen.scrollingBackgrounds[controleUVFScreen.name].buttons.values():
                button.pos.y += resizeRange
            self.screen.scrollingBackgrounds[graficosControleScreen.name].setVisible(visible)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].buttons[tglGraficos.name].actionAssign(expandGraficosControleScreen)

        def cmbRhooseOptionRobotIDGraficosControle(self):
            """Instance method to choose the option in the cmbRobotIDGraficosControle"""
            self.screen.buttons[cmbRobotIDGraficosControle.name].setText(self.getText(), center=True)
            self.screen.buttons[cmbRobotIDGraficosControle.name].setOptionsVisibility(False)
        for button in self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[graficosControleScreen.name].buttons[cmbRobotIDGraficosControle.name].options:
            button.actionAssign(cmbRhooseOptionRobotIDGraficosControle)


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
            self.screen.buttons[tglControleUVF.name].pos.y += resizeRange
            for block in self.screen.scrollingBackgrounds[controleUVFScreen.name].blocks.values():
                block.pos.y += resizeRange
            for button in self.screen.scrollingBackgrounds[controleUVFScreen.name].buttons.values():
                button.pos.y += resizeRange
            self.screen.scrollingBackgrounds[controleManualScreen.name].setVisible(visible)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].buttons[tglControleManual.name].actionAssign(expandControleManualScreen)


        def cmbRhooseOptionRobotIDControleManual(self):
            """Instance method to choose the option in the cmbRobotIDControleManual"""
            self.screen.buttons[cmbRobotIDControleManual.name].setText(self.getText(), center=True)
            self.screen.buttons[cmbRobotIDControleManual.name].setOptionsVisibility(False)
        for button in self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[cmbRobotIDControleManual.name].options:
            button.actionAssign(cmbRhooseOptionRobotIDControleManual)


        def changeEnableJoystick(self):
            """Instance method to change the state of tglEnableJoystick"""
            self.changeState()
            self.imgs[self.isOn()]
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[tglEnableJoystick.name].actionAssign(changeEnableJoystick)

        def changeEnableDirection(self):
            """Instance method to change the state of tglEnableDirection"""
            self.changeState()
            self.imgs[self.isOn()]
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[tglEnableDirection.name].actionAssign(changeEnableDirection)

        def changeEnableManualControl(self):
            """Instance method to change the state of tglEnableControleManual"""
            self.changeState()
            self.imgs[self.isOn()]
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[tglEnableControleManual.name].actionAssign(changeEnableManualControl)


        def cmbDhowOptionsDirection(self):
            """Instance method to show the positioning options in cmbDirection"""
            if (self.getOptionsVisibility()):
                self.setOptionsVisibility(False)
            else:
                self.setOptionsVisibility(True)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[cmbDirection.name].actionAssign(cmbDhowOptionsDirection)


        def cmbDhooseOptionDirection(self):
            """Instance method to choose the option in the cmbDirection"""
            self.screen.buttons[cmbDirection.name].setText(self.getText(), center=True)
            self.screen.buttons[cmbDirection.name].setOptionsVisibility(False)
        for button in self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[cmbDirection.name].options:
            button.actionAssign(cmbDhooseOptionDirection)


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

        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].buttons[tglControleUVF.name].actionAssign(expandControleUVFScreen)


        def slide(self):
            """Instance method to slide a Slider object"""
            self.setActive(True)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[sldVelocidadeLinear.name].actionAssign(slide)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[sldVelocidadeAngular.name].actionAssign(slide)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleManualScreen.name].buttons[sldAceleracao.name].actionAssign(slide)


        def cmbRhooseOptionRobotIDControleUVF(self):
            """Instance method to choose the option in the cmbRobotIDControleUVF"""
            self.screen.buttons[cmbRobotIDControleUVF.name].setText(self.getText(), center=True)
            self.screen.buttons[cmbRobotIDControleUVF.name].setOptionsVisibility(False)
        self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[cmbRobotIDControleUVF.name].actionAssign(showOptionscmbRobotID)
        for button in self.movementScreen.scrollingBackgrounds[movementScrollPanel.name].scrollingBackgrounds[controleUVFScreen.name].buttons[cmbRobotIDControleUVF.name].options:
            button.actionAssign(cmbRhooseOptionRobotIDControleUVF)


        def chooseOptionRobotIDCommunicationComboBox(self):
            """Instance method to choose the option in the robotIDCommunicationComboBox"""
            self.screen.buttons[robotIDCommunicationComboBox.name].setText(self.getText(), center=True)
            self.screen.buttons[robotIDCommunicationComboBox.name].setOptionsVisibility(False)
        self.communicationScreen.buttons[robotIDCommunicationComboBox.name].actionAssign(showOptionscmbRobotID)
        for button in self.communicationScreen.buttons[robotIDCommunicationComboBox.name].options:
            button.actionAssign(chooseOptionRobotIDCommunicationComboBox)







        def play(self):
            if self.gui.unbrain_loop is None:
                teamColor = False if self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbChooseColor.name].getText() == "Azul" else True

                mirror = True if (teamColor == False and self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[tglInversao.name].isOn()) or (teamColor == True and self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[tglInversao.name].isOn()) else False

                numRobots = [int(e) for e in self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbChooseNumRobots.name].getText().split(", ")]

                entitiesType = self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbChooseEntityType.name].getText()
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

        self.navigationScreen.menuBar.buttons[btnPlay.name].actionAssign(play)


        def pause(self):
            if self.gui.unbrain_loop is not None and not loop.unbrain_paused:
                loop.unbrain_paused = True
                print("UnBrain paused")
            else:
                print("Nothing happened")

        self.navigationScreen.menuBar.buttons[btnPause.name].actionAssign(pause)


        def stop(self):
            if self.gui.unbrain_loop is not None:
                self.gui.unbrain_loop.handle_SIGINT(None, None, shut_down=True)
                self.gui.unbrain_loop = None
                loop.unbrain_paused = False
                print("UnBrain stopped")
            else:
                print("Nothing happened")

        self.navigationScreen.menuBar.buttons[btnStop.name].actionAssign(stop)


        def play_firasim(self):
            if self.gui.unbrain_loop is None:
                teamColor = False if self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbChooseColor.name].getText() == "Azul" else True

                mirror = True if (teamColor == False and self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[tglInversao.name].isOn()) or (teamColor == True and self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[tglInversao.name].isOn()) else False

                numRobots = [int(e) for e in self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbChooseNumRobots.name].getText().split(", ")]

                entitiesType = self.gui.navigationScreen.scrollingBackgrounds[navigationScrollPanel.name].buttons[cmbChooseEntityType.name].getText()
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

        self.navigationScreen.menuBar.buttons[btnConfig.name].actionAssign(play_firasim)




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