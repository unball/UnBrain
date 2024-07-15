from gi.repository import Gtk, GLib
from pkg_resources import resource_filename

class ViewMux(Gtk.ListBox):
  def __init__(self, controller):
    super().__init__()

    self.__mux = None

    self.__controller = controller

    self.connect("row-selected", self.select)

  def setMux(self, mux):
      self.__mux = mux
      self.createChild()
      self.show_all()

  def select(self, widget, widget_selected):
    if widget_selected is not None and self.__mux is not None:
      self.__controller.addEvent(self.__mux.select, widget_selected.get_index())

  def createChild(self):

    # Limpa os filhos
    self.foreach(lambda element: self.remove(element))

    # Cria cada linha
    for i,element in enumerate(self.__mux):
      rowWithSettingBuilder = Gtk.Builder.new_from_file(resource_filename(__name__, "rowWithSetting.ui"))
      rowWithSettingBuilder.get_object("RowLabel").set_text(element.name)

      # Cria o menu sobreposto
      popOver = rowWithSettingBuilder.get_object("RowPopover")
      grid = Gtk.Grid()
      grid.set_row_spacing(5)
      grid.set_column_spacing(5)
      grid.set_margin_left(5)
      grid.set_margin_top(5)
      grid.set_margin_right(5)
      grid.set_margin_bottom(5)

      # Preenche o menu com base nos parâmetros do elemento
      for idx,key in enumerate(element.params):
        properties = element.getProperties(key)

        # Nome do parâmetro
        label = Gtk.Label(key) if properties.get("name") is None else Gtk.Label(properties["name"])
        grid.attach(label, 0, idx, 1, 1)

        # O parâmetro é um booleano
        if type(element.params[key]) == bool:
          switch = Gtk.Switch()
          grid.attach(switch, 1, idx, 1, 1)
          switch.connect("state-set", self.updateParam_state_set, element, key)

        # O parâmetro é float
        else:
          spin = Gtk.SpinButton()
          spin.set_digits(3)
          grid.attach(spin, 1, idx, 1, 1)
          adj = Gtk.Adjustment(element.params[key], 0, 1000, 0.001, 1, 1)
          adj.connect("value-changed", self.updateParam, element, key)
          adj.set_value(element.params[key])
          spin.set_adjustment(adj)

      # Adiciona os filhos
      grid.show_all()
      popOver.add(grid)

      self.insert(rowWithSettingBuilder.get_object("RowBox"), -1)
      rowChild = self.get_row_at_index(i)

      # Seleciona o filho a depender do mux
      if i == self.__mux.selectedIndex():
        self.select_row(rowChild)

  def updateParam(self, widget, element, key):
    self.__controller.addEvent(element.setParam, key, widget.get_value())

  def updateParam_state_set(self, widget, state, element, key):
    self.__controller.addEvent(element.setParam, key, state)
