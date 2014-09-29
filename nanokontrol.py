#!/usr/bin/env python

import pygame
import pygame.midi
import time

pygame.init()
pygame.midi.init()

__all__ = ["Map", "NanoKontrol2"]

class Map(object):
    SLIDERS = range(0, 8)
    KNOBS = range(16, 16+8)

    SS = range(32, 32+8)
    MS = range(48, 48+8)
    RS = range(64, 64+8)
    
    RWND = 43
    FFWD = 44
    STOP = 42
    PLAY = 41
    RECORD = 45

    CYCLE = 46
    SET = 60
    SLEFT = 61
    SRIGHT = 62

    LEFT = 58
    RIGHT = 59

    DIGITAL = set(range(32, 72))
    ANALOG = set(range(0, 32))

    ALL = DIGITAL | ANALOG


class NanoKontrol2(object):
    MAX_EVENTS = 100
    def __init__(self):
        self.input_dev_id = None
        self.output_dev_id = None

        self.led_state = {d: False for d in Map.DIGITAL}
        self.state = {d: False for d in Map.DIGITAL}
        self.state.update({a: 0.0 for a in Map.ANALOG})
        self.toggle_state = self.state.copy()
        self.events = {}

        self.setup_device()

    def find_device(self):
        self.input_dev_id = None
        self.output_dev_id = None
        for dev in range(pygame.midi.get_count()):
            _interface, name, inp, outp, opened = pygame.midi.get_device_info(dev)
            if "nanoKONTROL2" not in name:
                continue
            if inp: 
                self.input_dev_id = dev
            if outp: 
                self.output_dev_id = dev

    def setup_device(self):
        #self.free_device()
        if self.input_dev_id is None or self.output_dev_id is None:
            self.find_device()
        if self.input_dev_id is None or self.output_dev_id is None:
            raise Exception("Unable to find nanoKontrol2 device")

        self.input_dev = pygame.midi.Input(self.input_dev_id)
        self.output_dev = pygame.midi.Output(self.output_dev_id)

        self.clear_leds()

    def free_device(self):
        if self.input_dev_id:
            self.input_dev.close()
        if self.output_dev_id:
            self.output_dev.close()

    def clear_leds(self):
        for ch in Map.DIGITAL:
            self.set_led(ch, False, force=True)

    def set_led(self, note, state, force=False):
        if force or self.led_state[note] != state:
            self.output_dev.write_short(176, note, 127 if state else 0)
        self.led_state[note] = state

    def process_input(self):
        self.events = {}
        while True:
            raw_events = self.input_dev.read(self.MAX_EVENTS)
            if not raw_events:
                break
            for event in raw_events:
                (status, channel, data, _data2), timestamp = event

                if channel not in self.events:
                    self.events[channel] = []
                real_time = time.time() + (timestamp - pygame.midi.time()) / 1000.
                self.events[channel].append((real_time, data))

                if channel in Map.DIGITAL:
                    self.state[channel] = bool(data)
                    if data:
                        self.toggle_state[channel] = not self.toggle_state[channel]
                        self.set_led(channel, self.toggle_state[channel])
                elif channel in Map.ANALOG:
                    self.state[channel] = data / 127.0
                    self.toggle_state[channel] = data / 127.0
                else:
                    print "Unknown channel:", channel, event

    def update(self):
        return self.process_input()
            
def main():
    import time
    nk = NanoKontrol2()
    nk.clear_leds()
    while True:
        nk.process_input()
        for i in range(8):
            nk.set_led(Map.SS[i], nk.state[Map.SLIDERS[i]] > 0.5)
            nk.set_led(Map.MS[i], nk.state[Map.KNOBS[i]] > 0.5)
        time.sleep(0.01)

if __name__ == "__main__":
    main()
