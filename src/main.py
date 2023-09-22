from loop import Loop
import argparse
import logging
import client.gui

logging.basicConfig(level=logging.INFO)

# Argumentos
parser = argparse.ArgumentParser(description='ALP-Winners system')
parser.add_argument('--team-color', dest='team_color', type=str, choices=['yellow', 'blue'], help='Team color.')
parser.add_argument('--team-side', dest='team_side', type=str, choices=['left', 'right'], help='Team side.')
parser.add_argument('--immediate-start', dest='immediate_start', action='store_const', const=True, default=False, help='If robots should start moving without VSSReferee telling so.')
parser.add_argument('--static-entities', dest='static_entities', action='store_const', const=True, default=False, help='If strategy will keep robots with the same entities all the time.')
parser.add_argument('--disable-alp-gui', dest='disable_alp_gui', action='store_const', const=True, default=False, help='If set, no communciation with ALP-GUI overhead will be added.')
parser.add_argument('--port', dest='port', type=int, default=5001, help='Port number to bind the pickle socket.')
parser.add_argument('--n_robots', dest='n_robots', type=int, default=5, help='Number of robots for each time in the match.')
args = parser.parse_args()

if args.disable_alp_gui: client.gui.disabled = True

# Instancia o programa principal
loop = Loop(
    draw_uvf=False, 
    team_yellow=True,
    team_side=1,
    immediate_start=True,
    static_entities=False,
    port=args.port,
    n_robots=3
)

loop.run()