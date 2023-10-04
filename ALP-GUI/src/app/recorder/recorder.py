import numpy as np

from gi.repository import Gtk, GObject
from copy import deepcopy
from ..drawer.world import World
from threading import Thread
from time import sleep, time

class Recorder:
    def __init__(self, builder: Gtk.Builder, world: World):
        # Elements
        self.recordedLabel = builder.get_object("RecordingRecordedLabel")
        self.currentPositionLabel = builder.get_object("RecordingCurrentPositionLabel")
        self.recordingButton = builder.get_object("RecordingButton")
        self.backwardButton = builder.get_object("RecordingBackwardButton")
        self.playButton = builder.get_object("RecordingPlayButton")
        self.playButtonIcon = builder.get_object("RecordingPlayButtonIcon")
        self.forwardButton = builder.get_object("RecordingForwardButton")
        self.scaleAdjustment = builder.get_object("RecordingScaleAdjustment")
        self.playScaleAdjustment = builder.get_object("RecordingPlayScaleAdjustment")
        self.scale = builder.get_object("RecordingScale")

        # World
        self.world = world

        # Parameters
        self.recordingInterval = 0.03

        # States
        self.recordedWorlds = []
        self.__recording = False
        self.__playing = True
        self.__currentTime = 0
        self.playScale = 1
        self.scaleEnd = True
        self.lastSave = time()
        self.lastPlayUpdate = time()

        # Bindings
        self.scaleAdjustment.connect("value-changed", self.onScaleAdjustmentChanged)
        self.scale.connect("adjust-bounds", self.onScaleAdjustedBounds)
        self.recordingButton.connect("toggled", self.onRecordingToggled)
        self.playButton.connect("toggled", self.onPlayButtonToggled)
        self.playScaleAdjustment.connect("value-changed", self.onPlayScaleAdjustmentChanged)

        # Start recorder worker
        self.start()

    @property
    def recording(self):
        return self.__recording

    @recording.setter
    def recording(self, value):
        self.__recording = value
        self.updateRecordingButtonStyle()

    @property
    def playing(self):
        return self.__playing

    @playing.setter
    def playing(self, value):
        self.__playing = value
        self.lastPlayUpdate = time()

        if not self.__playing: self.scaleEnd = False
        self.playButtonIcon.set_from_icon_name("media-playback-pause-symbolic" if self.__playing else "media-playback-start-symbolic", self.playButtonIcon.get_icon_name()[1])

    @property
    def currentTime(self):
        return min(self.__currentTime, self.getRecordingLength())

    @currentTime.setter
    def currentTime(self, value):
        self.__currentTime = value
        self.updateScale()
        self.updateCurrentTimeLabel()

    def getCurrentWorld(self):
        try:
            index = self.getRecordingIndex(self.currentTime)
            if index+1 == len(self.recordedWorlds):
                return self.world
            else:
                return self.recordedWorlds[index]
        except:
            return self.world

    def worldProvider(self):
        return self.getCurrentWorld()

    def start(self):
        GObject.timeout_add(16, self.worker)

    def stop(self):
        self.recording = False

    def getRecordingLength(self):
        return len(self.recordedWorlds) * self.recordingInterval

    def getRecordingIndex(self, time: float):
        return int(np.floor(time / self.recordingInterval)) - 1

    def onScaleAdjustedBounds(self, slider: Gtk.Scale, value: float):
        length = self.getRecordingLength()
        if (length - value) / length > 0.05:
            self.scaleEnd = False
        else:
            self.scaleEnd = True

    def onScaleAdjustmentChanged(self, adjustment: Gtk.Adjustment):
        self.currentTime = adjustment.get_value()

    def onPlayScaleAdjustmentChanged(self, adjustment: Gtk.Adjustment):
        self.playScale = adjustment.get_value()

    def onRecordingToggled(self, recordingButton: Gtk.ToggleButton):
        self.recording = not self.recording

    def onPlayButtonToggled(self, playButton: Gtk.ToggleButton):
        self.playing = not self.playing

    def save(self):
        self.recordedWorlds.append(deepcopy(self.world))
        self.lastSave = time()
        self.updateUI()

    def updateUI(self):
        length = self.getRecordingLength()

        # Update recorded label
        self.recordedLabel.set_text("{:.2f}".format(length))

        # Update adjustment upper limit
        self.scaleAdjustment.set_upper(length)

        # Update adjustment position
        if self.scaleEnd and self.playing:
            self.scaleAdjustment.set_value(length)

        # Update current position label
        self.updateCurrentTimeLabel()

    def updateRecordingButtonStyle(self):
        context = Gtk.Widget.get_style_context(self.recordingButton)
        if self.recording:
            context.remove_class("recordButtonNotRecording")
            context.add_class("recordButtonRecording")
        else:
            context.remove_class("recordButtonRecording")
            context.add_class("recordButtonNotRecording")

    def updateCurrentTimeLabel(self):
        self.currentPositionLabel.set_text("{:.2f}".format(self.currentTime))

    def updateScale(self):
        self.scaleAdjustment.set_value(self.currentTime)

    def worker(self):
        if self.recording and time()-self.lastSave > self.recordingInterval:
            self.save()

        if self.playing:
            self.currentTime = self.currentTime + (time()-self.lastPlayUpdate) * self.playScale
            self.lastPlayUpdate = time()

        GObject.timeout_add(16, self.worker)
            
