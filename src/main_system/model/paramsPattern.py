from main_system.model import ModelContext

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

  _deferred_instances = []
  """Registro global das instâncias deferred, para o botão de salvar dar commit em todas."""

  @staticmethod
  def commit_all_deferred():
    """Aplica as edições pendentes de TODAS as instâncias deferred (chamado pelo botão salvar)."""
    for inst in ParamsPattern._deferred_instances:
      inst.commit()

  @staticmethod
  def discard_all_deferred():
    for inst in ParamsPattern._deferred_instances:
      inst.discard()

  def __init__(self, source: str, default: dict, name: str = None, properties: dict = {}, deferred: bool = False):
    """Recebe a fonte dos parâmetros `source` e o valor padrão deles `default` na forma de dicionário.
    Se `deferred=True`, as alterações via setParam ficam num buffer local e SÓ vão para o
    Model/disco quando `commit()` for chamado (usado pelo botão de salvar da interface).
    Assim, um flush imediato de outra parte (ex.: calibração) não grava edições não-salvas."""
    self._params = ParamsPatternModel(source, default).params
    """Dicionário que mantém os parâmetros da classe (aliás do Model em memória)"""

    self.name = name
    """Nome da instância"""

    self.__properties = properties
    """Propriedades de parâmetros"""

    self.__paramsChanged = False

    self._deferred = deferred
    self._pending = {}
    """Buffer de edições não-salvas (só usado quando deferred=True)"""
    if deferred:
      ParamsPattern._deferred_instances.append(self)

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
    """Retorna o parâmetro de chave `key` (prioriza edição pendente, se houver)"""
    if self._deferred and key in self._pending:
      return self._pending[key]
    return self._params[key]

  def setParam(self, key, value):
    """Altera um parâmetro de chave `key` para o valor `value`.
    Em modo deferred, escreve só no buffer (não persiste até commit())."""
    if self._deferred:
      self._pending[key] = value
    else:
      self._params[key] = value
    self.__paramsChanged = True

  def commit(self):
    """Aplica as edições pendentes ao Model (em memória). O flush ao disco é do chamador."""
    if not self._deferred:
      return
    for k, v in self._pending.items():
      self._params[k] = v
    self._pending = {}

  def discard(self):
    """Descarta edições pendentes não-salvas."""
    self._pending = {}

  def getProperties(self, key):
    """Retorna as propriedades de um parâmetro"""
    if self.__properties.get(key) is None: return {}
    else: return self.__properties[key]
