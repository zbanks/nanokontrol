#!/usr/bin/env python

import pygame
import pygame.midi

pygame.init()
pygame.midi.init()

class NanoKontrol2(object):
    def __init__(self):
        self.input_dev_id = None
        self.output_dev_id = None
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
        self.free_device()
        if self.input_dev_id is None or self.output_dev_id is None:
            self.find_device()
        if self.input_dev_id is None or self.output_dev_id is None:
            raise Exception("Unable to find nanoKontrol2 device")

        self.input_dev = pygame.midi.Input(self.input_dev_id)
        self.output_dev = pygame.midi.Output(self.output_dev_id)

    def free_device(self):
        if self.input_dev_id:
            self.input_dev.close()
        if self.output_dev_id:
            self.output_dev.close()

    def set_led(self, note, state):
        self.output_dev.write_short(176, note, 127 if state else 0)

    def process_input(self, 




if __name__ == "__main__":
    main()
