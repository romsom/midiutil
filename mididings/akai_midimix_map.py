import mididings as md
from common_map import *

#class NoteEvent:
#    def __init__
        
class Akai_MidiMix:
    def __init__(self):
        self.pots = {}
        for ch in range(0,4):
            for p in range(0,3):
                self.pots['pot_{}_{}'.format(ch, p)] = ControlEvent(16 + 4*ch + p, 0, 127)
        for ch in range(4,8):
            for p in range(0,3):
                self.pots['pot_{}_{}'.format(ch, p)] = ControlEvent(46 + 4*(ch-4) + p, 0, 127)
        self.sliders = {}
        for ch in range(0,4):
            self.sliders['slider_{}'.format(ch)] = ControlEvent(16 + 3 + 4*ch, 0, 127)
        for ch in range(4,8):
            self.sliders['slider_{}'.format(ch)] = ControlEvent(46 + 3 + 4*(ch-4), 0, 127)
        self.sliders['master'] = ControlEvent(62, 0, 127)

    def ctrls(self):
        return [self.pots, self.sliders]

    def Print(self):
        return [ev.filter >> md.Print(name) for ctrl in self.ctrls() for name, ev in ctrl.items()] #+ [md.Print('akai')]

    def Map(self, mapping, device):
        '''Map control events of this controller to generators of device using mapping information in mapping.'''
        params = device.parameters()
        return [ev.filter >> params[mapping[name]].event(ev.min, ev.max) >> md.Print(mapping[name]) for ctrl in self.ctrls() for name, ev in ctrl.items() if name in mapping]
