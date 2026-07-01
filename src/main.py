from utils.logger import init_global_logger
init_global_logger()

import argparse
import logging
import subprocess
import sys
import os

import threading
import signal

def signal_handler(sig, frame):
    print("\n[MAIN] Sinal recebido. Parando os robôs...")
    try:
        if 'loop' in globals() and hasattr(loop, 'command'):
            for i in range(3):
                loop.command.write(i, 0, 0)
    except Exception as e:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    import multiprocessing as mp
    mp.set_start_method('spawn', force=True)
    from system_preflight import system_preflight_check
    system_preflight_check()
    from loop import Loop
    import client.gui
    # Argumentos
    parser = argparse.ArgumentParser(description='ALP-Winners system')
    parser.add_argument('--team-color', dest='team_color',
                        type=str, choices=['yellow', 'blue'], default='yellow', help='Team color.')

    parser.add_argument('--immediate-start', dest='immediate_start',
                        action='store_const', const=True, default=True, help='If robots should start moving without VSSReferee telling so.')

    parser.add_argument('--static-entities', dest='static_entities',
                        type=str, nargs='?', const=True, default=False, help='If strategy will keep robots with the same entities all the time. Optionally pass comma-separated roles (e.g. AI_Attacker,GoalKeeper,Defender).')

    parser.add_argument('--disable-alp-gui', dest='disable_alp_gui',
                        action='store_const', const=True, default=False, help='If set, no communciation with ALP-GUI overhead will be added.')

    parser.add_argument('--referee', dest='referee', action='store_const', const=True,
                        default=False, help='If you are using referee for start.')

    parser.add_argument('--firasim', dest='firasim', action='store_const', const=True,
                        default=False, help='If you are using FIRASim for start.')

    parser.add_argument('--travesim', dest='travesim', action='store_const', const=True,
                        default=False, help='If you are using Travesim for start.')

    parser.add_argument('--simulado', dest='simulado', action='store_const', const=True, default=False, help='If you are using simulado for start.')
    parser.add_argument('--rsim', dest='rsim', action='store_const', const=True,
                        default=False, help='If you are using rsim for start.')

    parser.add_argument('--mainsystem', dest='mainsystem', action='store_const', const=True,
                        default=False, help='If you are using main-vision for start.')

    parser.add_argument('--control', dest='control', action='store_const', const=True,
                        default=False, help='If you want to make all entities work as ControlTester.')

    parser.add_argument('--debug', dest='debug', action='store_const',
                        const=True, default=False, help='Set debug mode for vision.')

    parser.add_argument('--port', dest='port', type=int, default=5001, help='Port number to bind the pickle socket.')

    parser.add_argument('--mirror', dest='mirror', action='store_const',
                        const=True, default=False, help='If vision is mirrored or not. Affects angles.')
                        
    parser.add_argument('--n_robots', dest='n_robots', type=str, default="0,1,2" , help='Number of robots for each time in the match.')

    parser.add_argument('--n_sims', dest='n_sims', type=int, default=1,
                        help='Quantas simulacoes rodar em paralelo (multiprocessing) na coleta de heatmap/dados. >1 escala com os nucleos da CPU.')
    parser.add_argument('--sim_duration', dest='sim_duration', type=int, default=300,
                        help='Duracao (segundos de relogio) de cada simulacao de coleta.')
    parser.add_argument('--num_episodes', dest='num_episodes', type=int, default=0,
                        help='>0 ativa a validacao justa episode-based (N cenarios seeded 0..N-1, '
                             'iguais entre modelos). 0 mantem a coleta time-based por --sim_duration.')
    parser.add_argument('--max_episode_steps', dest='max_episode_steps', type=int, default=int(600/0.016),
                        help='Maximo de passos por episodio na validacao justa (timeout). 600s / 0.016s = 37500 passos ~= 10 min simulados.')
    parser.add_argument('--timestep', dest='timestep', type=int, default=16,
                        help='Passo fisico do simulador em milissegundos (default 16ms). Define o dt das '
                             'velocidades e a cadencia de inferencia da IA (1 inferencia por passo).')

    parser.add_argument('--AI', dest='AI_attacker', action='store_const',
                        const=True, default=False, help='If you want to use AI_attacker strategy.')

    parser.add_argument('--enemy_AI', dest='enemy_AI', action='store_const',
                        const=True, default=False, help='If you want to use AI_attacker strategy as an enemy.')

    parser.add_argument('--systemtest', dest='systemtest',type=str, choices=[
                                                                            "draw_uvf", # plot do jogo com/sem uvf
                                                                            "firasim_ab", #test preditor                                                                        
                                                                            "heatmap_team", "heatmap_attacker_ia", "heatmap_attacker", "heatmap_defender", "heatmap_goalkeeper", "heatmap_ball" # heatmaps
                                                                         ],
                        default=False, help='Run parallel system instances in test mode.')

    parser.add_argument('--use-predictor', dest='use_predictor', action='store_true', default=False,
                        help='Force the system to use the predictor IA.')
    parser.add_argument('--disable-ai', dest='disable_ai', action='store_true', default=False,
                        help='Forces the predictor to run purely mathematically, disabling the residual neural network inference.')
    parser.add_argument('--record', dest='record', action='store_true', default=False,
                        help='Records vision frames and commands to dataset files for training the predictor IA.')
    parser.add_argument('--inject-delay', dest='inject_delay', type=float, default=0.0,
                        help='Inject artificial delay (in seconds) to simulate real-world camera lag in FIRASim.')
    parser.add_argument('--teleport', dest='teleport', type=str, default=None,
                        help='Teleport or reposition robots to predefined formations (e.g. "inicial"). Disables normal AI until ENTER is pressed.')

    parser.add_argument('--use-kalman', dest='use_kalman', action='store_true', default=False,
                        help='Enable Kalman Filter for object tracking.')
    parser.add_argument('--use-neural-estimator', dest='use_neural_estimator', action='store_true', default=False,
                        help='Enable Neural State Estimator for object tracking and Sim-to-Real delay compensation.')

    parser.add_argument('--render', action='store_true', default=False,
                        help='Ativa o renderizador matplotlib (extremamente lento) durante testes de sistema único.')

    args = parser.parse_args()

    # Se o usuário escolheu o teste A/B, garantimos que haja delay (se ele não passou explicitamente)
    if args.systemtest == "firasim_ab" and args.inject_delay == 0.0:
        args.inject_delay = 0.05

    if args.disable_alp_gui:
        client.gui.disabled = True

    team_yellow = True if args.team_color == 'yellow' else False

    if team_yellow:
        mirror = False if args.mirror else True
    else:
        mirror = args.mirror

    args.n_robots = [int(e) for e in args.n_robots.split(",")]

    if args.systemtest and not args.systemtest == "firasim_ab":
        original_argv = sys.argv.copy()
        if '--systemtest' in original_argv:
            original_argv.remove('--systemtest')

        draw_uvf = True if args.systemtest ==  "draw_uvf" else False
        test_type = args.systemtest if args.systemtest[:7] == "heatmap" else "heatmap_team"

        loop = Loop(
            draw_uvf=draw_uvf, 
            team_yellow=team_yellow,
            immediate_start=args.immediate_start,
            static_entities=args.static_entities,
            referee=args.referee,
            firasim=args.firasim,
            travesim=args.travesim,
            rsim=args.rsim,
            simulado=args.simulado,
            mainsystem=args.mainsystem,
            control=args.control,
            debug=args.debug,
            port=args.port,
            n_robots=args.n_robots,
            mirror=mirror, 
            test_type=test_type,
            AI_attacker=args.AI_attacker,
            enemy_AI=args.enemy_AI,
            teleport=args.teleport,
            use_kalman=args.use_kalman,
            use_neural_estimator=args.use_neural_estimator,
            timestep_ms=args.timestep
        )

        loop.test(n_threads=args.n_sims, duracao=args.sim_duration, render=args.render,
                  num_episodes=args.num_episodes, max_episode_steps=args.max_episode_steps)

        # loop_list = []
        # for i in range(10):
        #     loop = Loop(
        #     draw_uvf=False, 
        #     team_yellow=team_yellow,
        #     immediate_start=args.immediate_start,
        #     static_entities=args.static_entities,
        #     referee=args.referee,
        #     firasim=args.firasim,
        #     vssvision=args.vssvision,
        #     mainsystem=args.mainsystem,
        #     simulado=True,
        #     control=args.control,
        #     debug=args.debug,
        #     port=args.port,
        #     n_robots=args.n_robots,
        #     mirror=mirror)

        #     print(f"tesbols{i}")
        #     loop_thread = threading.Thread(target=loop.run)
        #     loop_list.append(loop_thread)
        #     loop_thread.start() # inicia essa thread do loop
        
        # print(threading.active_count())
        # print(len(loop_list))
        # loop_thread.join()

    else:
        test_type = args.systemtest
        
        # [Integração MainSystem] Iniciar o GTK da interface de visão em paralelo caso solicitado

        # Instancia o programa principal
        loop = Loop(
            draw_uvf=args.systemtest == "draw_uvf", 
            team_yellow=args.team_color == 'yellow',
            immediate_start=args.immediate_start,
            static_entities=args.static_entities,
            referee=args.referee,
            firasim=args.firasim,
            travesim=args.travesim,
            rsim=args.rsim,
            simulado=args.simulado,
            mainsystem=args.mainsystem,
            control=args.control,
            debug=args.debug,
            port=args.port,
            mirror=args.mirror,
            n_robots=args.n_robots,
            AI_attacker=args.AI_attacker,
            enemy_AI=args.enemy_AI,
            test_type=test_type,
            use_predictor=args.use_predictor,
            disable_ai=args.disable_ai,
            inject_delay=args.inject_delay,
            record=args.record,
            teleport=args.teleport,
            use_kalman=args.use_kalman,
            use_neural_estimator=args.use_neural_estimator,
            timestep_ms=args.timestep
        )

        if args.teleport is not None:
            def wait_for_enter():
                input("\n[TELEPORT] Pressione ENTER para destravar os robôs e iniciar o jogo...\n")
                loop.world.teleport_mode = None
                print("[MAIN] Jogo iniciado! Estratégia normal assumindo o controle.")
            
            threading.Thread(target=wait_for_enter, daemon=True).start()

        loop.run()