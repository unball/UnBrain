"""Aqui implementa-se o gerenciamento das variáveis permanentes do sistema no arquivo de configuração."""

import json
from helpers import Singleton

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
  
  def __init__(self, dictionary):
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
      
    if name == "variables":
      object.__setattr__(self, name, value)
      return
    
    self.variables[name][1] = value
    Model().setValue(self.variables[name][0], value)
  
  def __getattr__(self, name):
    """Todo acesso a variável passa por esse método, ele vai retornar o valor da variável no dicionário de variáveis"""
    return self.variables[name][1]

class Model(metaclass=Singleton):
  """Classe que gerencia as chaves em memória permanente. É uma classe singleton, isto é, só pode ser instanciada uma vez. Esta classe mantém em memória primária o conteúdo do arquivo de configuração e só salva em memória permanente quando um `flush` for feito"""
  
  def __init__(self):
    self.__config = Model.getConfig()
    """Mantém os dados do arquivo de configuração em uma variável"""
    
  def flush(self):
    """Salva o conteúdo no arquivo de configuração"""
    Model.saveConfig(self.__config)
    
  def getConfig():
    """Retorna o dicionário de configuração do arquivo"""
    try:
      with open("config.json", "r") as f:
        return json.load(f)
    except:
      Model.saveConfig({})
      return {}

  def saveConfig(config):
    """Salva um dicionário de configuração no arquivo"""
    with open("config.json", "w") as f:
      json.dump(config, f)
      
  def getValue(self, key, default_key=None):
    """Obtém um valor a partir de uma chave"""
    
    if self.__config.get(key) is None:
      self.__config[key] = default_key
      #Model.saveConfig(config)
    
    return self.__config[key]

  def setValue(self, key, value):
    """Define o valor de uma chave"""
    self.__config[key] = value
    #Model.saveConfig(config)
    
