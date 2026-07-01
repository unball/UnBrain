import socket
import sys
import os
import multiprocessing as mp
import logging

def check_udp_port(port, host='0.0.0.0'):
    """Tenta dar bind numa porta UDP e libera imediatamente. Retorna False se falhar."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, 'SO_REUSEPORT'):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    try:
        sock.bind((host, port))
        sock.close()
        return True
    except OSError:
        sock.close()
        return False

def check_file_exists(filepath):
    """Retorna True se o arquivo existir e for legível."""
    return os.path.isfile(filepath) and os.access(filepath, os.R_OK)

def system_preflight_check():
    print("\n\033[1;36m[PRE-FLIGHT] Iniciando verificações do sistema...\033[0m")
    
    # 1. Validar portas UDP de Receção (Bind)
    bind_ports = {
        10020: "FIRASim Visão",
        10003: "VSSReferee Commands"
    }
    
    for port, desc in bind_ports.items():
        if not check_udp_port(port):
            print(f"\033[1;31m[CRITICAL] Porta UDP {port} ({desc}) está bloqueada ou em uso por um processo zumbi!\033[0m")
            print("\033[1;31m[CRITICAL] O sistema não consegue operar cego. Abortando.\033[0m")
            sys.exit(1)
        else:
            print(f"\033[1;32m[OK] Porta UDP {port} ({desc}) livre.\033[0m")
            
    # Portas de Envio (Apenas tentamos conectar para não estoirar caso o simulador já esteja rodando nela)
    send_ports = {
        20011: "FIRASim Comando"
    }
    for port, desc in send_ports.items():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('127.0.0.1', port))
            s.close()
            print(f"\033[1;32m[OK] Porta UDP {port} ({desc}) testada para envio.\033[0m")
        except Exception as e:
            print(f"\033[1;33m[WARNING] Não foi possível conectar à porta UDP {port} ({desc}): {e}\033[0m")
            
    # 2. Validar Arquivos Críticos (Soft-Fail)
    critical_files = [
        "best_model_firasim.pth",
        "best_params.json",
        "neuro_controller_firasim.pth"
    ]
    
    for filename in critical_files:
        if not check_file_exists(filename):
            print(f"\033[1;33m[WARNING] Ficheiro crítico '{filename}' em falta ou ilegível. O sistema poderá usar fallback.\033[0m")
        else:
            print(f"\033[1;32m[OK] Ficheiro '{filename}' encontrado.\033[0m")

    # 3. Validar Multiprocessing Start Method
    try:
        mp.set_start_method('spawn', force=True)
        print("\033[1;32m[OK] Multiprocessing start method definido para 'spawn'.\033[0m")
    except RuntimeError as e:
        print(f"\033[1;33m[WARNING] Falha ao definir multiprocessing spawn: {e}\033[0m")

    print("\033[1;36m[PRE-FLIGHT] Verificações concluídas com sucesso.\033[0m\n")

if __name__ == '__main__':
    system_preflight_check()
