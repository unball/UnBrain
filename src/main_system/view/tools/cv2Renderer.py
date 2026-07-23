from gi.repository import Gdk, GdkPixbuf, GLib, Gtk
from pkg_resources import resource_filename
from main_system.helpers import LoopThread
import cv2
import time

class cv2Renderer(Gtk.Frame, LoopThread):
  """Esta classe é um renderizador de um frame retornado pela opencv"""

  def __init__(self, worker=None, interpolation=cv2.INTER_LINEAR, widthHeightProportion=471/350, target_fps=150):
    """Se for passado uma função `worker`, ela será executada repetidamente para
    atualizar o GtkImage gerado dentro do GtkFrame, a até `target_fps` quadros
    por segundo.

    `target_fps` controla só a taxa de EXIBIÇÃO deste renderer específico — não
    a taxa de captura/tracking da visão (que roda à parte, no loop do
    Controller, e não é afetada por este valor). O padrão (150) é o usado pela
    aba de visão (`MainVisionView`), cujo `worker` É o próprio pipeline de
    visão sendo mostrado; subclasses que só desenham o estado do mundo (ex.:
    `HighLevelRenderer`, usado nas abas HLC/Controle/Teleporte/Teste de
    Episódios) devem passar um valor menor (ex.: 60), já que redesenhar um
    campo vetorial a 150 FPS não traz nenhum ganho perceptível e só consome
    CPU/GIL que a UI precisa para responder a cliques."""
    Gtk.Frame.__init__(self)

    self.__target_period = 1.0 / target_fps

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
    """Método que fica executando a thread que mantém a GUI renderizando.

    O trabalho pesado de imagem (resize/cvtColor/tobytes) é feito AQUI, na
    thread de fundo, e não mais em `do_update_frame` (que roda na thread
    principal do GTK via `idle_add`). Antes, `resize`+`cvtColor` de um frame
    inteiro rodavam na thread da UI a até 150x/s, roubando tempo do
    processamento de eventos (cliques, redesenho) — a causa da sensação de
    interface "travando". Agora a thread principal só recebe bytes prontos e
    monta o pixbuf."""
    t0 = time.time()
    image_data = self.__worker()
    if image_data is not None:
        image_sized = cv2.resize(image_data, self.__shape, interpolation=self.__interpolation)
        image_rgb = cv2.cvtColor(image_sized, cv2.COLOR_BGR2RGB)
        h, w, d = image_rgb.shape
        # tobytes() já roda fora da thread do GTK
        image_bytes = image_rgb.tobytes()
        GLib.idle_add(self.do_update_frame, image_bytes, w, h, d)
    dt = time.time() - t0
    remaining = self.__target_period - dt
    if remaining > 0:
        time.sleep(remaining)

  def do_update_frame(self, image_bytes, w, h, d):
    """Monta o pixbuf a partir de bytes RGB já prontos (produzidos em
    `get_worker_frame`, na thread de fundo) e atualiza o GtkImage. Roda na
    thread principal do GTK — deve ficar o mais leve possível."""
    self._current_image_bytes = image_bytes
    pixbuf = GdkPixbuf.Pixbuf.new_from_data(self._current_image_bytes, GdkPixbuf.Colorspace.RGB, False, 8, w, h, w * d)
    self.__gtk_image.set_from_pixbuf(pixbuf)
    self.__gtk_image.show()

  def clear_image(self):
    """Limpa o que estiver no GtkImage e coloca uma carinha triste"""
    self.__gtk_image.set_from_icon_name("face-crying-symbolic", 200)
