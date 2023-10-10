from app.app import App
from helpers.path import relPath
from app.drawer.world import World
from classes.server.server import WorldServer

world = World()
server = WorldServer(world, 'localhost', 20010)

app = App(world, onDestroy=server.stop)

server.start()
app.run()