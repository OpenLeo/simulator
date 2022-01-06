import datetime
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.lang.builder import Builder

_modname = 'BSI_trip'
_modversion = '0.0.1'

class BSI_trip(TabbedPanelItem):
    def __init__(self, runner, **kwargs):
        # Base init (super and name)
        super(TabbedPanelItem, self).__init__(**kwargs)
        self.text = 'BSI/Trip'

        # Load kv file
        self.kv = Builder.load_file(f'{os.path.dirname(__file__)}/bsi.kv')
        Builder.apply(self)

        # Register CAN callbacks
        print('registering BSI calls')
        runner.register(100, self.can_inst)
        runner.register(100, self.can_trip1)
        runner.register(100, self.can_trip2)

        self.inst_params = {
            'hide_fuel': 0,
            'hide_dist': 0,
            'com_left': 0,
            'com_right': 0,
            'fuel': 0,
            'autonomy': 0,
            'dist': 0
        }

        self.history = [
            {'speed': 0, 'dist': 0, 'fuel': 0},
            {'speed': 0, 'dist': 0, 'fuel': 0}
        ]

    def on_inst_button(self, name, value):
        self.inst_params[name] = 1 if value == 'down' else 0

    def on_inst_param(self, param, value):
        labels = {
            'fuel': 'fuel consumption: {:2.1f} l/km',
            'autonomy': 'autonomy: {} km',
            'dist': 'dist to dest: {} km'
        }
        self.inst_params[param] = value
        self.ids[f'cur_inst_{param}'].text = labels[param].format(value)

    def on_hist_param(self, hist, param, value):
        labels = {
            'speed': 'average speed: {} km/h',
            'dist': 'distance: {} km',
            'fuel': 'average consumption: {:2.1f} l/km'
        }
        self.history[hist][param] = value
        self.ids[f'cur_hist{hist}_{param}'].text = labels[param].format(value)

    def can_inst(self):
        params = self.inst_params
        # Other bits seems unused
        b0 = params['hide_fuel']<<7 | params['hide_dist']<<6 | params['com_right']<<3 | params['com_left']
        fuel = int(params['fuel']*10)
        autonomy = int(params['autonomy'])
        distance = int(params['dist']*10)
        return 0x221, [b0, fuel>>8, fuel&0xFF, autonomy>>8, autonomy&0xFF, distance>>8, distance&0xFF]

    def can_trip1(self):
        hist = self.history[0]
        dist = int(hist['dist'])
        fuel = int(hist['fuel']*10)
        # No idea why there's two trailing bytes, but they're needed
        # Else everything shows "--"
        return 0x2A1, [int(hist['speed']), dist>>8, dist&0xFF, fuel>>8, fuel&0xFF, 0x00, 0x00]

    def can_trip2(self):
        hist = self.history[1]
        dist = int(hist['dist'])
        fuel = int(hist['fuel']*10)
        # No idea why there's two trailing bytes, but they're needed
        # Else everything shows "--"
        return 0x261, [int(hist['speed']), dist>>8, dist&0xFF, fuel>>8, fuel&0xFF, 0x00, 0x00]
