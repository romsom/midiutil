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

def map_events(mapping, controller, device):
    '''Map control events of this controller to generators of device using mapping information in mapping.'''
    params = device.parameters()
    return [ev.filter >> params[mapping[name]].event(ev.min, ev.max) >> md.Print(mapping[name]) for name, ev in controller.ctrls().items() if name in mapping]

def create_scenes(pages, controller, device, create_scene):
    '''pages: dict of dicts of parameter identifiers organized by page name and controller element name
    controller: controller device
    device: midi device to be controlled
    create_scene: function which creates a a complete scene from a control event list returned from map_events.'''
    scs = {}
    for i, (name, page) in enumerate(sorted(pages.items(), key=lambda x: x[0])):
        print("index: {}; name: {}; page:".format(i, name))
        for p in sorted(page):
            print('{}: {}'.format(p, page[p]))
        print('map:')
        for m in map_events(page, controller, device):
            print(m)
        scs[i+1] = md.Scene(name, create_scene(map_events(page, controller, device)))# index < 1 will crash mididings
    return scs
