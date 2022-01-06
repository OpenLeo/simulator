#!/usr/bin/env python3

import kivy
import can
import datetime
import time
import threading
import sched
import yaml
import importlib
from functools import partial

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.clock import Clock

from can_runner import CanRunner

class PeugeotSim(App):
    def build(self):
        return Builder.load_file('main.kv')

    def on_start(self):
        # Get tabs id
        tabs = self.root.ids['modules']
        tabs.clear_widgets()

        with open('config.yml', 'r') as conf_file:
            self.conf = yaml.load(conf_file, Loader=yaml.FullLoader)

        # Init CAN runner
        self.can_runner = CanRunner()
        self.can_runner.run()

        # Init modules
        self.modules = {}
        for name in self.conf['modules']:
            module = importlib.import_module(f'modules.{name}')
            self.modules[name] = getattr(module, module._modname)(self.can_runner)
            if not tabs.tab_list:
                tabs.add_widget(self.modules[name])
                Clock.schedule_once(partial(tabs.switch_to, self.modules[name]))
            else:
                tabs.add_widget(self.modules[name])

    def on_stop(self):
        print('closing app')
        self.can_runner.stop()
        self.thread_exit = True

if __name__ == '__main__':
    PeugeotSim().run()
