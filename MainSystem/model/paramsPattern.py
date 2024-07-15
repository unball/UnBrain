from model import ModelContext

class ParamsPatternModel(ModelContext):
  """Mantém apenas parâmetros na forma de dicionário"""

  def __init__(self, source, default):
    ModelContext.__init__(self, {
      "params": (source + "_params", default)
    })
    """Variáveis armazenadas no modelo"""

    # Coloca variáveis novas nos parâmetros
    for key in list(default.keys()):
      if key not in list(self.params.keys()):
        self.params[key] = default[key]

class ParamsPattern:
  """Esta classe implementa um padrão de parâmetros que serão armazenados em memória permanente"""
  def __init__(self, source: str, default: dict, name: str = None, properties: dict = {}):
    """Recebe a fonte dos parâmetros `source` e o valor padrão deles `default` na forma de dicionário"""
    self._params = ParamsPatternModel(source, default).params
    """Dicionário que mantém os parâmetros da classe"""

    self.name = name
    """Nome da instância"""

    self.__properties = properties
    """Propriedades de parâmetros"""

    self.__paramsChanged = False

  @property
  def params(self):
    """Retorna os parâmetros do controle"""
    return self._params

  @property
  def paramsChanged(self):
    """Retorna se algum parâmetro mudou"""
    ret = self.__paramsChanged
    self.__paramsChanged = False
    return ret

  def getParam(self, key):
    """Retorna o parâmetro de chave `key` do controle"""
    return self._params[key]

  def setParam(self, key, value):
    """Altera um parâmetro de chave `key` para o valor `value`"""
    self._params[key] = value
    self.__paramsChanged = True

  def getProperties(self, key):
    """Retorna as propriedades de um parâmetro"""
    if self.__properties.get(key) is None: return {}
    else: return self.__properties[key]
