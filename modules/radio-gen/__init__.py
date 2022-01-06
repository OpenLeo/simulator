import datetime
import os

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.tabbedpanel import TabbedPanelItem
from kivy.lang.builder import Builder


_modname = 'Radio_gen'
_modversion = '0.0.1'

class Radio_gen(TabbedPanelItem):
    def __init__(self, runner, **kwargs):
        # Base init (super and name)
        super(TabbedPanelItem, self).__init__(**kwargs)
        self.text = 'Radio/Gen'

        # Load kv file
        self.kv = Builder.load_file(f'{os.path.dirname(__file__)}/radio.kv')
        Builder.apply(self, 'Radio')

        # Register CAN callbacks
        print('registering radio calls')
        runner.register(50, self.can_status)
        runner.register(100, self.can_volume)
        #runner.reg(self.can_volume, 0x1A5, 100)
        runner.register(50, self.can_panel)
        runner.register(100, self.can_audio)

        runner.reg(self.can_test, 0x0A4, 100, tp_id=0x09F, tp_callback=self.can_test_tp)

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

        self.audio = {
            'bass': 0x3F,
            'treble': 0x3F,
            'rf-bal': 0x3F,
            'lr-bal': 0x3F,
            'loudness': 0,
            'volume': 0,
            'ambiance': 'none',
            'menu': 'none'
        }

        self.ambiances = ['none', 'classical', 'jazz-blues', 'pop-rock', 'vocal', 'techno']
        self.ambiances_codes = {
            'none': 0x03,
            'classical': 0x07,
            'jazz-blues': 0x0B,
            'pop-rock': 0x0F,
            'vocal': 0x13,
            'techno': 0x17
        }
        # Order: ambiance, volume auto, L/R balance, R/F balance, loudness correction, treble, bass
        self.menus = ['none', 'ambiance', 'volume', 'lr-bal', 'rf-bal', 'loudness', 'treble', 'bass']

        self.input = 'TUN'
        self.inputs = {
            'TUN': 0x01,
            'CD': 0x02,
            'CDC': 0x03,
            'AUX1': 0x04,
            'AUX2': 0x05,
            'USB': 0x06,
            'BT': 0x07
        }

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

    def on_input(self, input):
       self.input = input

    def on_button(self, key):
        if key == 'audio':
            i = self.menus.index(self.audio['menu'])
            if i == len(self.menus)-1:
                i = 0
            else:
                i += 1
            #i += 1 if i == len(self.menus)-1 else 0
            self.audio['menu'] = self.menus[i]
            self.ids['cur_menu'].text = f'menu: {self.menus[i]}'

        if key == 'left':
            param = self.audio['menu']
            if param in ['lr-bal', 'rf-bal', 'bass', 'treble']:
                if not self.audio[param]-0x3F == -9:
                    self.audio[param] -= 1
                    self.ids[f'cur_param_{param}'].text = f'{param}: {self.audio[param]-0x3F}'
            elif param == 'loudness':
                self.audio[param] = 0x01
                self.ids[f'cur_param_{param}'].text = f'{param}: enabled'
            elif param == 'volume':
                self.audio[param] = 0x07
                self.ids[f'cur_param_{param}'].text = f'{param}: enabled'
            elif param == 'ambiance':
                i = self.ambiances.index(self.audio['ambiance'])
                if i != 0:
                    i -= 1
                else:
                    i = len(self.ambiances)-1
                self.audio['ambiance'] = self.ambiances[i]
                self.ids[f'cur_param_{param}'].text = f'{param}: {self.audio[param]}'

        if key == 'right':
            param = self.audio['menu']
            if param in ['lr-bal', 'rf-bal', 'bass', 'treble']:
                if not self.audio[param]-0x3F == 9:
                    self.audio[param] += 1
                    self.ids[f'cur_param_{param}'].text = f'{param}: {self.audio[param]-0x3F}'
            elif param == 'loudness' or param == 'volume':
                self.audio[param] = 0x00
                self.ids[f'cur_param_{param}'].text = f'{param}: disabled'
            elif param == 'ambiance':
                i = self.ambiances.index(self.audio['ambiance'])
                if i != len(self.ambiances)-1:
                    i += 1
                else:
                    i = 0
                self.audio['ambiance'] = self.ambiances[i]
                self.ids[f'cur_param_{param}'].text = f'{param}: {self.audio[param]}'

        if key == 'esc' and self.audio['menu'] != 'none':
            self.audio['menu'] = 'none'
            self.ids['cur_menu'].text = 'menu: none'

    def can_status(self):
        b2 = self.inputs[self.input]<<4
        return 0x165, [int('11001100', 2), int('1010100', 2), b2, 0x02]

    def can_volume(self, *args, **kwargs):
        return 0x1A5, [self.volflag | self.volume]

    def can_panel(self):
        keys = self.panel
        b0 = keys['menu']<<6 | keys['tel']<<4 | keys['clim']
        b1 = keys['trip']<<6 | keys['mode']<<4 | keys['audio']
        b2 = keys['ok']<<6 | keys['esc']<<4
        b5 = keys['up']<<6 | keys['down']<<4 | keys['right']<<2 | keys['left']
        return 0x3E5, [b0, b1, b2, 0x00, 0x00, b5]

    def can_audio(self):
        b0 = (self.audio['menu'] == 'lr-bal')<<7 | self.audio['lr-bal']
        b1 = (self.audio['menu'] == 'rf-bal')<<7 | self.audio['rf-bal']
        b2 = (self.audio['menu'] == 'bass')<<7 | self.audio['bass']
        b4 = (self.audio['menu'] == 'treble')<<7 | self.audio['treble']
        b5 = (self.audio['menu'] == 'loudness')<<7 | self.audio['loudness']<<6 | (self.audio['menu'] == 'volume')<<4 | self.audio['volume']
        b6 = (self.audio['menu'] == 'ambiance')<<6 | self.ambiances_codes[self.audio['ambiance']]
        return 0x1E5, [b0, b1, b2, 0x00, b4, b5, b6]

    def can_test(self):
        return [0x01, 0x01, 0x00, 0x10, 0x00, 116, 101, 115]

    def can_test_tp(self):
        print('received')
        return None
