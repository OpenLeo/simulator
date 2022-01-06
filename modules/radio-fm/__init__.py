import datetime
import os

from kivy.clock import Clock
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.lang.builder import Builder

_modname = 'Radio_fm'
_version = '0.0.1'

class Radio_fm(TabbedPanelItem):
    def __init__(self, runner, **kwargs):
        # Base init (super and name)
        super(TabbedPanelItem, self).__init__(**kwargs)
        self.text = 'Radio/Fm'

        # Load kv file
        self.kv = Builder.load_file(f'{os.path.dirname(__file__)}/radio.kv')
        Builder.apply(self, 'Radio_fm')

        # Register CAN callbacks
        print('registering radio calls')
        runner.register(100, self.can_freq)
        runner.register(100, self.can_rds)
        runner.register(100, self.can_name)
        runner.register(100, self.can_radio)

        # FM Radio stuff
        self.freq = 0
        self.band = 0
        self.mem = 0
        self.pty = 0
        self.tun = 0
        self.rds = 0
        self.scan = 0
        self.tundir = 0
        self.list = 0

    def on_freq(self, freq):
        self.freq = int(freq)#int((freq-50)/0.05)
        disp_freq = freq*0.05+50
        self.ids['cur_freq'].text = self.band == 0x50 and f'{int(freq)} kHz' or f'{disp_freq:10.2f} MHz'

    def on_band(self, state, value):
        self.on_toggle('band', state, value)
        self.on_freq(self.freq)

    def on_toggle(self, var, state, value=None):
        if value and state == 'down' and hasattr(self, var):
            setattr(self, var, value)
        elif value == None and hasattr(self, var):
            setattr(self, var, int(state == 'down'))

    def can_freq(self):
        b0 = self.list<<7 | self.tundir<<5 | self.scan<<3 | self.rds<<2 | self.tun<<1 | self.pty
        return 0x225, [b0, self.mem, self.band, self.freq>>8, self.freq&0xFF]

    def can_rds(self):
        b0 = 0<<7 | 1<<5 | 1<<4
        b1 = 1<<7 | 1<<6 | 2<<4
        return 0x265, [b0, b1, 0x01, 0x00]

    def can_name(self):
        b = bytearray()
        b.extend(map(ord, 'test'))
        return 0x2A5, b

    def can_radio(self):
        return 0x1E0, [int('00100100',2), 0x00, 0x00, 0x00, 0x20]
