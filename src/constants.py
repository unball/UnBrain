#VSSS VISION SOCKET
HOST_VSSS_VISION = "224.5.23.2"
PORT_VSSS_VISION = 10015

#REFEREE SOCKET
HOST_REFEREE = "224.5.23.2"
PORT_REFEREE_COMMAND = 10028
PORT_REFEREE_REPLACEMENT = 10029
PORT_REFEREE_BLUE = 1003
PORT_REFEREE_YELLOW = 1004

#CAMISAS UTILIZADAS
CAMISA_1 = 0 #0 no alp 
CAMISA_2 = 2 #1 no alp
CAMISA_3 = 3 #2 no alp

#TRANSMISSION DEBUG VARIABLES
DEBUG_WIFI = False #Variable that verifies if the sendWifi is working correctly
SHOW_DEBUG_WIFI_ERROR = False
if DEBUG_WIFI:
    SHOW_DEBUG_WIFI_ERROR = True  #it disables the default serial default debug. ("Falha ao abrir serial: Causa")
DEBUG_ACTUATE = True  #Variable that verifies if the actuate is sending the methods (use it for when there's no transmiter),

HOST_FIRASIM_VISION = "224.0.0.1"
HOST_FIRASIM_COMMAND = "127.0.0.1"
PORT_FIRASIM_VISION = 10002
PORT_FIRASIM_COMMAND = 20011