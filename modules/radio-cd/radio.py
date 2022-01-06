import datetime
import os

from kivy.clock import Clock
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.lang.builder import Builder

class Radio(TabbedPanelItem):
    def __init__(self, runner, **kwargs):
        # Base init (super and name)
        super(TabbedPanelItem, self).__init__(**kwargs)
        self.text = 'Radio'

        # Load kv file
        self.kv = Builder.load_file(f'{os.path.dirname(__file__)}/radio.kv')
        Builder.apply(self, 'Radio')

        # Register CAN callbacks
        print('registering radio calls')
        runner.register(50, self.can_status)
        runner.register(100, self.can_volume)
        runner.register(50, self.can_panel)
        runner.register(100, self.can_freq)
        runner.register(100, self.can_rds)
        runner.register(100, self.can_name)
        runner.register(100, self.can_radio)

        # Volume specific stuff
        self.volume = 15
        self.volflag = 0xE0
        self.voltrig = None

        # Panel specific stuff
        self.panel = {
            'mode': 0,
            'menu': 0,
            'ok': 0,
            'esc': 0,
            'up': 0,
            'down': 0,
            'right': 0,
            'left': 0,
            'audio': 0,
            'trip': 0,
            'clim': 0,
            'tel': 0
        }

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

    def reset_volume(self, dt):
        self.volflag = 0xE0
        self.voltrig = None

    def on_volume(self, volume):
        if volume < 0:
            volume = 0
        if volume > 30:
            volume = 30
        self.volflag = 0x00
        self.volume = int(volume)
        self.ids['cur_vol'].text = f'{self.volume}'
        if self.ids['slider_vol'].value != volume:
            self.ids['slider_vol'].value = volume
        if self.voltrig:
            self.voltrig.cancel()
        self.voltrig = Clock.schedule_once(self.reset_volume, 2)

    def on_panel(self, key, status):
        if key in self.panel:
            self.panel[key] = int(status == 'down')

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

    def can_status(self):
        return 0x165, [int('11001100', 2), int('1010000', 2), 0x10, 0x00]

    def can_volume(self):
        return 0x1A5, [self.volflag | self.volume]

    def can_panel(self):
        keys = self.panel
        b0 = keys['menu']<<6 | keys['tel']<<4 | keys['clim']
        b1 = keys['trip']<<6 | keys['mode']<<4 | keys['audio']
        b2 = keys['ok']<<6 | keys['esc']<<4
        b5 = keys['up']<<6 | keys['down']<<4 | keys['right']<<2 | keys['left']
        return 0x3E5, [b0, b1, b2, 0x00, 0x00, b5]

    def can_freq(self):
        b0 = self.list<<7 | self.tundir<<5 | self.scan<<3 | self.rds<<2 | self.tun<<1 | self.pty
        return 0x225, [b0, self.mem, self.band, self.freq>>8, self.freq&0xFF]

    def can_rds(self):
        b0 = 1<<7 | 1<<5 | 1<<4 | 1<<2 | 0<<1 | 0
        b1 = 1<<7 | 1<<6 | 2<<4
        return 0x265, [b0, b1, 0x01, 0x01]

    def can_name(self):
        b = bytearray()
        b.extend(map(ord, 'test'))
        return 0x2A5, b

    def can_radio(self):
        return 0x1E0, [int('00100100',2), 0x00, 0x00, 0x00, 0x20]
