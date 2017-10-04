import mididings as md
import time

class ControlEvent:
    def __init__(self, num, min, max):
        self.filter = md.CtrlFilter(num)
        self.generator = md.Ctrl(num, md.EVENT_VALUE)
        self.min = min
        self.max = max
def save_sysex(ev, prefix):
    if ev.type != md.SYSEX:
        print("Trying to dump non-sysex data. Check your filters!")
        return
    print('dump to file')
    f = open('{}__{}.syx'.format(prefix, time.strftime('%Y-%m-%d_%H-%M-%S', time.localtime())), mode='wb')
    f.write(ev.sysex)
    f.close()
    
def SaveSysEx(prefix):
    return md.Call(thread=lambda ev: save_sysex(ev, prefix))
