import datetime
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.lang.builder import Builder

_modname = 'BTE'
_modversion = '0.0.1'

class BTE(TabbedPanelItem):
    def __init__(self, runner, **kwargs):
        # Base init (super and name)
        super(TabbedPanelItem, self).__init__(**kwargs)
        self.text = 'BTE'

        # Load kv file
        self.kv = Builder.load_file(f'{os.path.dirname(__file__)}/ui.kv')
        Builder.apply(self)

        # Register CAN callbacks
        print('registering BSI calls')
        runner.register(100, self.can_message)

        self.bits = 0

    def on_toggle(self, bit, value):
        if value == 'down':
            self.bits |= 1<<bit
        else:
            self.bits &= ~(1<<bit)

    def can_message(self):
        b1 = self.bits
        return 0x12B, [b1]
