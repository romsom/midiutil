import mididings as md

class ControlEvent:
    def __init__(self, num, min, max):
        self.filter = md.CtrlFilter(num)
        self.generator = md.Ctrl(num, md.EVENT_VALUE)
        self.min = min
        self.max = max
