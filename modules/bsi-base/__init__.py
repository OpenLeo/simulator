import datetime
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.lang.builder import Builder

_modname = 'BSI_base'
_modversion = '0.0.1'

class BSI_base(TabbedPanelItem):
    def __init__(self, runner, **kwargs):
        # Base init (super and name)
        super(TabbedPanelItem, self).__init__(**kwargs)
        self.text = 'BSI/Base'

        # Load kv file
        self.kv = Builder.load_file(f'{os.path.dirname(__file__)}/bsi.kv')
        Builder.apply(self)

        # Register CAN callbacks
        print('registering BSI calls')
        runner.register(50, self.can_commandes)
        runner.register(100, self.can_slow)
        runner.register(100, self.can_vin_vis)
        runner.register(100, self.can_vin_wmi)
        runner.register(100, self.can_vin_vds)
        runner.register(50, self.can_fast)
        runner.register(100, self.can_temp_level)

        # COMMANDES_BSI values
        self.commands = {
            'economy': 0,
            'dash_lights': 0,
            'dark_mode': 0,
            'lum': 10,
            'power_mode': 0x01
        }

        self.gauges = {
            'rpm': 0,
            'speed': 0,
            'fuel': 0,
            'oil': 0,
            'coolant': 0
        }
        self.temperature = 20

    def on_command(self, command, value):
        if not command in self.commands:
            print('command not found?!?')
        if command in ['economy', 'dash_lights', 'dark_mode']:
            value = 1 if value == 'down' else 0
        self.commands[command] = int(value)
        if command == 'lum':
            self.ids['cur_lum'].text = f'lum: {value}'

    def on_temp(self, step, value):
        # Avoid overflows, anything over 250 (85.0) is not displayed
        if self.temperature == -40 and value == -0.5:
            return
        elif self.temperature == 85 and value == +0.5:
            return

        if step:
            self.temperature += value
        else:
            self.temperature = value
        self.ids['cur_ext_temp'].text = f'temp: {self.temperature}'

    def on_val(self, name, value):
        texts = {
            'rpm': 'RPM: {}',
            'speed': 'Speed: {} km/h',
            'fuel': 'Fuel: {}%',
            'oil': 'Oil temp: {} deg',
            'coolant': 'Coolant temp: {} deg'
        }

        self.ids[f'cur_{name}'].text = texts[name].format(value)
        self.gauges[name] = int(value)

    def can_commandes(self):
        com = self.commands
        b2 = com['economy']<<7
        b3 = com['dash_lights']<<5 | com['dark_mode']<<4 | com['lum']&0xFF
        b4 = com['power_mode']
        return 0x036, [0x0E, 0x00, b2, b3, b4, 0x80, 0x00, 0xA0]

    def can_slow(self):
        temp = int((self.temperature+40)*2)
        coolant = int(self.gauges['coolant']+40)
        return 0x0F6, [0x08, coolant, 0x00, 0x1F, 0x00, temp, temp, 0x01]

    def can_fast(self):
        rpm = int(self.gauges['rpm']*10)
        speed = int(self.gauges['speed']*100)
        return 0x0B6, [rpm>>8, rpm&0xFF, speed>>8, speed&0xFF, 0x00, 0x00, 0x00, 0x00]

    def can_vin_vis(self):
        return 0x2B6, [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

    def can_vin_wmi(self):
        return 0x336, [0x56, 0x46, 0x33]

    def can_vin_vds(self):
        return 0x3B6, [0x00, 0x00, 0x00, 0x46, 0x00, 0x00]

    def can_temp_level(self):
        oil = self.gauges['oil']+40
        return 0x161, [0x00, 0x00, oil, self.gauges['fuel'], 0xff, 0xff, 0xff, 0xff]
