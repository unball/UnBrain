import builtins
import logging
import os
import sys

# Garante que o diretório de logs exista
os.makedirs('logs', exist_ok=True)

# Configura o formato do log
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

try:
    file_handler = logging.FileHandler('logs/unbrain.log', mode='a', encoding='utf-8')
except PermissionError:
    file_handler = logging.FileHandler('/tmp/unbrain.log', mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Cria o logger raiz silenciado no console
unbrain_logger = logging.getLogger("UnBrain")
unbrain_logger.setLevel(logging.DEBUG)
unbrain_logger.addHandler(file_handler)

# Armazena a função print original
_original_print = builtins.print

def init_global_logger():
    """Injeta a interceptação global da função print()"""
    def _unbrain_print(*args, **kwargs):
        text = " ".join(str(a) for a in args)
        
        # O print tem flush explicitado, ou termina na mesma linha, ou possui carriage return?
        # É a barra de UI do loop.py! Mandamos para a tela e IGNORAMOS o log em arquivo.
        if "\r" in text or kwargs.get("end") in ["", "\r"]:
            _original_print(*args, **kwargs)
        else:
            # Qualquer outro print "comum" vira log silencioso no arquivo
            unbrain_logger.info(text)

    # Sobrescreve a função nativa do Python
    builtins.print = _unbrain_print

