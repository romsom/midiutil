import mididings as md
from common_map import *

# Control events for default Mackie MCU mode
class Arturia_BSP:
    def __init__(self):
        self.encoders = {}
        for i in range(8):
            self.encoders['mackie_encoder_{}'.format(i)] = ControlEvent(16 + i)
        for i in range(8, 16):
            # TODO midi channels
            self.encoders['mackie_encoder_{}'.format(i)] = PitchbendEvent(0, 8192)
            
    def ctrls(self):
        return self.encoders

    def Print(self):
        return [ev.filter >> md.Print(name) for name, ev in self.ctrls().items()] #+ [md.Print('arturia')]
