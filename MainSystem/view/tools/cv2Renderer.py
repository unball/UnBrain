from gi.repository import Gdk, GdkPixbuf, GLib, Gtk
from pkg_resources import resource_filename
from helpers import LoopThread
import cv2
import time

class cv2Renderer(Gtk.Frame, LoopThread):
  """Esta classe é um renderizador de um frame retornado pela opencv"""

  def __init__(self, worker=None, interpolation=cv2.INTER_LINEAR, widthHeightProportion=471/350):
    """Se for passado uma função `worker`, ela será executada a cada 30ms para atualizar o GtkImage gerado dentro do GtkFrame"""
    Gtk.Frame.__init__(self)

    self.set_shadow_type(Gtk.ShadowType.NONE)

    # Compõe a parte estática do cv2Renderer
    builder = Gtk.Builder.new_from_file(resource_filename(__name__, "cv2Renderer.ui"))
    self.add(builder.get_object("frame"))

    self.__gtk_image = builder.get_object("image")
    """Referência ao GtkImage onde serão renderizados os frames"""

    self.__event_box = builder.get_object("eventBox")
    """Referência ao GtkEventBox que gerenciará eventos de mouse"""

    # Habilita alguns eventos de movimento do mouse
    self.__event_box.add_events(Gdk.EventMask.POINTER_MOTION_MASK)

    # Adiciona o sinal de redimensionamento do frame de evento
    builder.get_object("frame").connect("check_resize", self.event_resize)

    self.__worker = worker
    """Função a ser executada continuamente para renderizar o conteúdo"""

    self.__shape = (471, 350)
    """Tamanho do frame a ser renderizado"""

    self.__widthHeightProportion = widthHeightProportion
    """Proporção entre largura e altura que será mantida ao longo do tempo"""

    self.__interpolation = interpolation
    """Método de interpolação a ser utilizado"""

    # Instancia uma thread que vai ficar executando o worker
    LoopThread.__init__(self, self.get_worker_frame)

    #self.set_halign(Gtk.Align.FILL)

    self.show_all()

  def getEventBox(self):
    """Retorna a caixa de evento gerada por esse cv2Renderer"""
    return self.__event_box

  def getShape(self):
    """Retorna o formato da janela de renderização"""
    return self.__shape

  def event_resize(self, widget):
    """Este método realiza o redimensionamento do frame na interface gráfica"""
    basewidth = widget.get_allocated_width()
    baseheight = widget.get_allocated_height()
    if basewidth <= 0 or baseheight <= 0: return

    candidateheight = int(basewidth/self.__widthHeightProportion)
    candidatewidth = int(baseheight*self.__widthHeightProportion)

    height = max(min(baseheight, candidateheight),1)
    width = max(min(basewidth, candidatewidth),1)
    self.__shape = (width, height)

  def get_worker_frame(self):
    """Método que fica executando a thread que mantém a GUI renderizando"""
    GLib.idle_add(self.do_update_frame, self.__worker())
    time.sleep(0.03)

  def do_update_frame(self, image_data):
    """Atualiza a o GtkImage para o conteúdo do frame passado `image_data` no formato de numpy array com dimensão (height,width,depth) no formato BGR."""
    if image_data is None: return
    image_converted = cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR)
    image_sized = cv2.resize(image_converted, self.__shape, interpolation=self.__interpolation)
    height, width, depth = image_sized.shape
    pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes(image_sized.tobytes()), GdkPixbuf.Colorspace.RGB, False, 8, width, height, depth*width)
    self.__gtk_image.set_from_pixbuf(None)
    self.__gtk_image.set_from_pixbuf(pixbuf.copy())
    self.__gtk_image.show()

  def clear_image(self):
    """Limpa o que estiver no GtkImage e coloca uma carinha triste"""
    self.__gtk_image.set_from_icon_name("face-crying-symbolic", 200)
