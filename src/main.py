from loop import Loop
import argparse
import logging
import client.gui

logging.basicConfig(level=logging.INFO)

# Argumentos
parser = argparse.ArgumentParser(description='ALP-Winners system')
parser.add_argument('--team-color', dest='team_color',
                    type=str, choices=['yellow', 'blue'], required=True, help='Team color.')

parser.add_argument('--immediate-start', dest='immediate_start',
                    action='store_const', const=True, default=True, help='If robots should start moving without VSSReferee telling so.')

parser.add_argument('--static-entities', dest='static_entities',
                    action='store_const', const=True, default=False, help='If strategy will keep robots with the same entities all the time.')

parser.add_argument('--disable-alp-gui', dest='disable_alp_gui',
                    action='store_const', const=True, default=False, help='If set, no communciation with ALP-GUI overhead will be added.')

parser.add_argument('--referee', dest='referee', action='store_const', const=True,
                    default=False, help='If you are using referee for start.')

parser.add_argument('--firasim', dest='firasim', action='store_const', const=True,
                    default=False, help='If you are using FIRASim for start.')

parser.add_argument('--vssvision', dest='vssvision', action='store_const', const=True,
                    default=False, help='If you are using vssvision for start.')

parser.add_argument('--mainvision', dest='mainvision', action='store_const', const=True,
                    default=False, help='If you are using main-vision for start.')

parser.add_argument('--simulado', dest='simulado', action='store_const', const=True,
                    default=False, help='If you are using simulado for start.')

parser.add_argument('--control', dest='control', action='store_const', const=True,
                    default=False, help='If you want to make all entities work as ControlTester.')

parser.add_argument('--debug', dest='debug', action='store_const',
                    const=True, default=False, help='Set debug mode for vision.')

parser.add_argument('--port', dest='port', type=int, default=5001, help='Port number to bind the pickle socket.')

parser.add_argument('--mirror', dest='mirror', action='store_const',
                    const=True, default=False, help='If vision is mirrored or not. Affects angles.')
                    
parser.add_argument('--n_robots', dest='n_robots', type=str, default="0,1,2" , help='Number of robots for each time in the match.')


args = parser.parse_args()

if args.disable_alp_gui:
    client.gui.disabled = True

team_yellow = True if args.team_color == 'yellow' else False

if team_yellow:
    mirror = False if args.mirror else True
else:
    mirror = args.mirror

args.n_robots = [int(e) for e in args.n_robots.split(",")]

print(args.n_robots)

# Instancia o programa principal
loop = Loop(
    draw_uvf=False, 
    team_yellow=team_yellow,
    immediate_start=args.immediate_start,
    static_entities=args.static_entities,
    referee=args.referee,
    firasim=args.firasim,
    vssvision=args.vssvision,
    mainvision=args.mainvision,
    simulado=args.simulado,
    control=args.control,
    debug=args.debug,
    port=args.port,
    n_robots=args.n_robots,
    mirror=mirror
)

loop.run()