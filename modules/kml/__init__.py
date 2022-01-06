import datetime
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.lang.builder import Builder

_modname = 'KML'
_modversion = '0.0.1'

class KML(TabbedPanelItem):
    def __init__(self, runner, **kwargs):
        # Base init (super and name)
        super(TabbedPanelItem, self).__init__(**kwargs)
        self.text = 'KML'

        # Load kv file
        self.kv = Builder.load_file(f'{os.path.dirname(__file__)}/kml.kv')
        Builder.apply(self)

        # Register CAN callbacks
        print('registering BSI calls')
        runner.register(100, self.can_status)
        runner.register(100, self.can_message)
        runner.register(100, self.can_message2)

        self.opt = 0
        self.bits = 0

    def on_opt(self, value):
        self.opt = 1 if value == 'down' else 0

    def on_toggle(self, bit, value):
        if value == 'down':
            self.bits |= 1<<bit
        else:
            self.bits &= ~(1<<bit)

    def can_status(self):
        # status, unknown, "aucun mobile connecte", "echec connection", headset icon, "secret", unknown, "triangle" (sur message status)
        b1 = 0x80
        #  blinking message icon, message icon, responder icon, "reload" icon, charging battery icon, "phone" (status + icon), 2 unknown
        b2 = self.opt<<2
        b3 = 0 # signal
        b4 = 0 # battery
        # 5 unknown, voice commands
        b5 = 0
        # list title, 4 unknown
        b6 = 0
        b7 = 0 # 8 unknown
        return 0x1A3, [b1, b2, b3, b4, b5, b6, b7]

    def can_message(self):
        b1 = self.bits
        b2 = 0
        b3 = 0
        b4 = 0
        b5 = 0
        b6 = 0
        return 0x223, [b1, b2, b3, b4, b5, b6]

    def can_message2(self):
        b1 = 0<<7 | 1<<6 | 0x2<<4 | 0x2<<2 | 0x02
        b2 = 1<<3
        b3 = 1<<6 | 0x2<<4
        b4 = 0
        b5 = 0x02
        b6 = 0x02
        b7 = 0
        return 0x323, [b1, b2, b3, b4, b5, b6, b7]
