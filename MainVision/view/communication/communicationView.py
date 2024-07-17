from gi.repository import Gtk
from pkg_resources import resource_filename
from view.tools.viewMux import ViewMux

class CommunicationHandlerView():
  """Classe que gerencia a view do gerenciador do sistema de comunicação"""

  def __init__(self, controller, communicationSystems, menuButton):
    self.__menuButton = menuButton
    """Botão que chama o menu"""

    self.__communicationSystems = communicationSystems
    """Sistema de comunicação a ser gerenciado"""

    self.__controller = controller
    """Mantém referência ao controller principal"""

    # Carrega os elementos de interface gráfica
    builder = Gtk.Builder.new_from_file(resource_filename(__name__, "communication.ui"))

    communicationPopover = builder.get_object("communicationPopover")
    """Referência ao objeto de interface gráfica `communicationPopover`"""

    communicationMuxContainer = builder.get_object("communicationMuxContainer")
    communicationMuxView = ViewMux(controller)
    communicationMuxView.setMux(communicationSystems)
    communicationMuxContainer.add(communicationMuxView)

    # Faz com que quando o botão é clicado apareça o communicationPopover
    menuButton.set_popover(communicationPopover)
