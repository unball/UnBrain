"""Aqui implementa-se o gerenciamento das variáveis permanentes do sistema no arquivo de configuração."""

import json
from main_system.helpers import Singleton

#class ModelList(list):
#  """
#  .. warning:: Essa classe só propaga alterações de elementos no primeiro nível da lista, se a lista tiver dimensão maior, mudanças em listas internas não afetarão o arquivo de configuração.
#  .. important:: A propagação feita é: mudança de elemento em primeiro nível da lista propaga para arquivo.
#  Essa classe implementa um tipo de lista conveniente para servir de variável de instância da classe `ModelContext`. Ela permite que alterações em elementos individuais da lista provoquem alteração no arquivo de configuração.
#  """
#  def __init__(self, l, keyOnFile):
#    list.__init__(self, l)
#    self.l = l
#    self.keyOnFile = keyOnFile
#    
#  def __setitem__(self, key, value):
#    self.l[key] = value
#    Model().setValue(self.keyOnFile, self.l)
#    
#  def __getitem__(self, key):
#    return self.l[key]

class ModelContext(object):
  """Essa classe é uma camada de acesso às variáveis no arquivo. Recebe um dicionário cujas chaves são o nome da variável de instância da classe e cujos valores são os nomes das variáveis no arquivo de configuração. A classe vai mapear cada variável no arquivo de configuração a uma variável de instância, isso permitirá que qualquer tentativa de acesso ou alteração da variável passe pelo crivo dessa classe, que fará a alteração no arquivo de configuração de modo transparente."""
  
  def __init__(self, dictionary, immediate=False):
    object.__setattr__(self, "_immediate", immediate)
    self.variables = {}

    for key in dictionary:
      if isinstance(dictionary[key], tuple):
        keyNameOnFile, defaultValue = dictionary[key]
      else:
        keyNameOnFile, defaultValue = (dictionary[key], None)

      self.variables[key] = [keyNameOnFile, self.getValue(keyNameOnFile, defaultValue)]
      
  def getValue(self, keyNameOnFile, defaultValue):
    """Obtém o valor de uma chave cujo nome é `keyNameOnFile` no arquivo de configuração. Se a chave não for encontrada, cria uma nova chave com esse nome e um valor padrão `defaultValue"""
    
    storedValue = Model().getValue(keyNameOnFile, defaultValue)
    #if(isinstance(storedValue, list)):
    #  storedValue = ModelList(storedValue, keyNameOnFile)
    return storedValue
  
  def __setattr__(self, name, value):
    """Toda atribuição de variável dessa classe passa por esse método, ele vai alterar no `Model` o valor correspondente a essa chave"""
    #if(isinstance(value, list)):
    #  value = ModelList(value, self.variables[name][0])
      
    if name in ("variables", "_immediate"):
      object.__setattr__(self, name, value)
      return

    self.variables[name][1] = value
    Model().setValue(self.variables[name][0], value)
    # Modelos de calibração usam immediate=True: gravam no disco na hora, para não
    # perder a calibração se o sistema for fechado pelo terminal ou faltar energia.
    if getattr(self, "_immediate", False):
      Model().flush()
  
  def __getattr__(self, name):
    """Todo acesso a variável passa por esse método, ele vai retornar o valor da variável no dicionário de variáveis"""
    return self.variables[name][1]

class Model(metaclass=Singleton):
  """Classe que gerencia as chaves em memória permanente. É uma classe singleton, isto é, só pode ser instanciada uma vez. Esta classe mantém em memória primária o conteúdo do arquivo de configuração e só salva em memória permanente quando um `flush` for feito"""
  
  def __init__(self):
    self.__config = Model.getConfig()
    """Mantém os dados do arquivo de configuração em uma variável"""
    self.__pending = {}
    """Chaves de topo com edição não-salva (persistem só no commit do botão de salvar)"""

  def flush(self):
    """Salva o conteúdo no arquivo de configuração. NÃO grava as edições pendentes
    (buffer): assim um flush imediato (ex.: calibração da câmera) persiste no disco
    sem levar junto configurações da interface ainda não confirmadas no botão."""
    Model.saveConfig(self.__config)

  def setDeferred(self, key, value):
    """Registra uma edição de chave de topo em buffer (não persiste até commitPending)."""
    self.__pending[key] = value

  def commitPending(self):
    """Move as edições pendentes para a config em memória (o flush é do chamador)."""
    self.__config.update(self.__pending)
    self.__pending = {}

  def discardPending(self):
    self.__pending = {}
    
  @staticmethod
  def _get_config_path():
    import os
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")

  def getConfig():
    """Retorna o dicionário de configuração do arquivo"""
    try:
      with open(Model._get_config_path(), "r") as f:
        return json.load(f)
    except:
      Model.saveConfig({})
      return {}

  def saveConfig(config):
    """Salva um dicionário de configuração no arquivo"""
    with open(Model._get_config_path(), "w") as f:
      json.dump(config, f)
      
  def getValue(self, key, default_key=None):
    """Obtém um valor a partir de uma chave (prioriza edição pendente não-salva)."""
    if key in self.__pending:
      return self.__pending[key]

    if self.__config.get(key) is None:
      self.__config[key] = default_key
      #Model.saveConfig(config)

    return self.__config[key]

  def setValue(self, key, value):
    """Define o valor de uma chave"""
    self.__config[key] = value
    #Model.saveConfig(config)
    
