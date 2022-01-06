import can
import datetime
import time
import threading
import sched

class CanRunner():
    def __init__(self):
        self.bus = can.Bus(channel='can0', interface='socketcan', bitrate=125000)
        self.sender = threading.Thread(target=self.sender)
        self.sender_exit = threading.Event()
        self.receiver = threading.Thread(target=self.receiver)
        self.receiver_exit = threading.Event()
        self.messages = []
        self.mess = []
        self.modules = {}

    def reg(self, func, id, schedule, tp_id=None, tp_callback=None, *args, **kwargs):
        new_module = {
            'id': id,
            'timer': datetime.datetime.now(),
            'schedule': schedule/1000,
            'call': func,
            'tp_id': tp_id,
            'tp_callback': tp_callback
        }
        self.mess.append(new_module)

    def register(self, schedule, call):
        new_module = {
            'timer': datetime.datetime.now(),
            'schedule': schedule/1000,
            'call': call
        }
        self.messages.append(new_module)

    def receiver(self):
        while True:
            if self.receiver_exit.is_set():
                return
            recvd = self.bus.recv(1.0)
            if not recvd:
                continue
            for message in self.mess:
                if message['tp_id'] == recvd['arbitration_id']:
                    message['tp_callback'](recvd['data'])


    def sender(self):
        while True:
            # If we need to exit
            if self.sender_exit.is_set():
                return

            for message in self.mess:
                now = datetime.datetime.now()
                if (now - message['timer']).total_seconds() >= message['schedule']:
                    data = message['call']() #self.modules[message['module']])
                    if data != None:
                        self.bus.send(can.Message(arbitration_id=message['id'], data=data, is_extended_id=False))
                    message['timer'] = now

            for message in self.messages:
                now = datetime.datetime.now()
                if (now - message['timer']).total_seconds() >= message['schedule']:
                    id, data = message['call']()
                    #print(f'sending {id}')
                    self.bus.send(can.Message(arbitration_id=id, data=data, is_extended_id=False))
                    message['timer'] = now

            # Wait until next round
            time.sleep(0.01)

    def run(self):
        self.sender.start()
        self.receiver.start()

    def stop(self):
        self.sender_exit.set()
        self.receiver_exit.set()
