import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk
from helpers.path import relPath
from .drawer.drawer import Drawer
from .recorder.recorder import Recorder
from app.drawer.world import World

class App:
    def __init__(self, world: World, onDestroy = None):
        self.world = world
        self.externalOnDestroy = onDestroy

    def onDestroy(self, window: Gtk.Window):
        if self.onDestroy: self.externalOnDestroy()
        Gtk.main_quit()

    def run(self):
        # Builds static ui elements
        builder = Gtk.Builder.new_from_file(relPath("app.ui"))

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(relPath("app.css"))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Get and show app window
        window = builder.get_object("AppWindow")

        # Connect to destroy event
        window.connect("destroy", self.onDestroy)

        # Get drawing area
        drawingArea = builder.get_object("AppDrawingArea")

        # Creates recorder
        recorder = Recorder(builder, self.world)

        # Creates drawer
        drawer = Drawer(drawingArea, recorder.worldProvider)

        # Show content
        window.show_all()

        # Start application
        Gtk.main()