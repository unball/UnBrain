import subprocess
import sys
import os
import signal
import time

class UnBrainLauncher:
    """
    Gerencia a execução do subprocesso do UnBrain (src/main.py).
    Permite iniciar o core com diferentes flags e encerra-lo de forma segura.
    """
    def __init__(self):
        self.process = None
        self.simulator_mode = None

    def start(self, simulator_mode="firasim", port=5001, team_color="yellow", flags=None):
        """
        Inicia o subprocesso python3 src/main.py com as flags adequadas.
        simulator_mode: 'firasim', 'travesim', 'vssvision', 'simulado', 'mainsystem'
        """
        self.stop() # Garante que não há outro rodando

        print(f"[Launcher] Iniciando UnBrain: modo {simulator_mode}, time {team_color}")
        
        cmd = [
            sys.executable, "src/main.py", 
            "--team-color", team_color,
            "--port", str(port),
            "--mainsystem"
        ]
        
        if simulator_mode != "mainsystem" and simulator_mode != "none":
            cmd.append(f"--{simulator_mode}")

        if flags:
            if flags.get("referee"):
                cmd.append("--referee")
            if flags.get("debug"):
                cmd.append("--debug")
            if flags.get("ppo_ai"):
                cmd.append("--AI")
            if flags.get("enemy_ai"):
                cmd.append("--enemy_AI")
            if flags.get("record"):
                cmd.append("--record")
            if flags.get("use_kalman"):
                cmd.append("--use-kalman")
            if flags.get("use_neural_estimator"):
                cmd.append("--use-neural-estimator")
            if flags.get("static_entities"):
                # Se temos force_entities definidos, serializa as entidades em ordem de robô
                force_ents = flags.get("force_entities", {})
                if force_ents:
                    # Converte {"0": "Zagueiro", "1": "Atacante", "2": "AI"} -> "Zagueiro,Atacante,AI"
                    n_robots_str = flags.get("n_robots", "0,1,2")
                    if isinstance(n_robots_str, list):
                        robot_ids = n_robots_str
                    else:
                        robot_ids = [int(x) for x in str(n_robots_str).split(",") if x.strip()]
                    roles = [force_ents.get(str(r), "") for r in robot_ids]
                    roles_str = ",".join(r for r in roles if r)  # filtra slots vazios
                    if roles_str:
                        cmd.extend(["--static-entities", roles_str])
                    else:
                        cmd.append("--static-entities")
                else:
                    val = flags.get("static_entities")
                    if isinstance(val, str) and val:
                        cmd.extend(["--static-entities", val])
                    else:
                        cmd.append("--static-entities")

            # Passa os IDs dos robôs selecionados (ex: "0,2" para robô 0 e robô 2)
            n_robots_val = flags.get("n_robots", "0,1,2")
            if isinstance(n_robots_val, list):
                n_robots_val = ",".join(str(x) for x in n_robots_val)
            cmd.extend(["--n_robots", str(n_robots_val)])

        self.simulator_mode = simulator_mode

        self.process = subprocess.Popen(
            cmd, 
            stdout=sys.stdout, 
            stderr=sys.stderr,
            preexec_fn=os.setsid # Permite matar toda a árvore de processos se necessário
        )

    def stop(self):
        """
        Encerra o processo do UnBrain enviando SIGINT, permitindo que 
        o loop.py receba e mande velocidades zero para o robô.
        """
        if self.process is not None and self.process.poll() is None:
            print("[Launcher] Parando UnBrain (SIGINT)...")
            try:
                os.killpg(os.getpgid(self.process.pid), signal.SIGINT)
                for _ in range(20):
                    if self.process.poll() is not None:
                        break
                    time.sleep(0.1)

                if self.process.poll() is None:
                    print("[Launcher] Forçando parada (SIGKILL)...")
                    os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            except Exception as e:
                print(f"[Launcher] Erro ao parar processo: {e}")
            
            self.process = None
            self.simulator_mode = None
            print("[Launcher] UnBrain parado.")

    def is_running(self):
        return self.process is not None and self.process.poll() is None
