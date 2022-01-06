import datetime
import os

from kivy.clock import Clock
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.lang.builder import Builder

_modname = 'Clim'
_version = '0.0.1'

class Clim(TabbedPanelItem):
    def __init__(self, runner, **kwargs):
        # Base init (super and name)
        super(TabbedPanelItem, self).__init__(**kwargs)
        self.text = 'Clim'

        # Load kv file
        self.kv = Builder.load_file(f'{os.path.dirname(__file__)}/clim.kv')
        Builder.apply(self)

        # Register CAN callbacks
        print('registering radio calls')
        runner.register(100, self.can_clim_panel)
        runner.register(100, self.can_clim_cmd)
        runner.register(100, self.can_clim_emf)

        self.fan = 0
        self.dir = [0,0]
        self.options = {
            'unfrost_front': 0,
            'unfrost_read': 0,
            'recycle': 0,
            'auto': 0,
            'dual': 0
        }
        self.temps = [0, 0]
        self.temp_disp = [
            'LO',
            '15',
            '16',
            '17',
            '18', '18.5',
            '19', '19.5',
            '20', '20.5',
            '21', '21.5',
            '22', '22.5',
            '23', '23.5',
            '24',
            '25',
            '26',
            '27',
            'HI'
        ]

        self.bits = 0

    def on_dir(self, seat, dir):
        self.dir[seat] = dir

    def on_temp(self, zone, dir):
        if not (self.temps[zone] == 0 and dir == -1) and not (self.temps[zone] == 20 and dir == +1):
            self.temps[zone] += dir
            self.ids[f'cur_temp{zone}'].text = f'{self.temp_disp[self.temps[zone]]}c'

    def on_option(self, option, value):
        self.options[option] = 1 if value == 'down' else 0

    def on_toggle(self, bit, value):
        if value == 'down':
            self.bits |= 1<<bit
        else:
            self.bits &= ~(1<<bit)

    def can_clim_panel(self):
        b4 = self.options['recycle']<<5 | self.options['unfrost_front']<<4
        return 0x1D0, [0x00, 0x00, self.fan, self.dir[0], b4, self.temps[0], self.temps[1]]

    def can_clim_cmd(self):
        return 0x12D, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

    def can_clim_emf(self):
        # recycle, ac off, off, auto air, auto (text), hide fan, ext air, dual
        b1 = self.options['auto']<<3 | self.options['dual']
        # unfrost front, [3 bits] temperature offset, 4 bits unknown
        b2 = self.options['unfrost_front']<<7
        b3 = self.bits | self.temps[0] # unknown, 2 bits: if both 1: '--.-', 5 bits temperature // left seat + dual
        b4 = self.temps[1] # same as b4, right seat only
        b5 = self.dir[0]<<4 # 4 bits: direction, 4 bits unknown // left seat + dual
        b6 = self.dir[1]<<4 # 4 bits: direction, 4 bits unknown // right seat only
        b7 = self.fan # 4 unknown, 4 bits: fan
        return 0x1E3, [b1, b2, b3, b4, b5, b6, b7]
