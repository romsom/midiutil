import mididings as md

def A3000_SysExFilter():
    return md.SysExFilter([0xf0, 0x43]) # at the moment we can only match up to the last byte, pattern matching would be nice though

def gen_remote_switch_sysex(ev, format):
    # not sure about 0x10: first nibble should be device ID, 0x03: (Manual: binary: 1, hex: 3 ...), length of data also not clear
    if ev.value > 0x40:
        val = 0x80 - ev.value
    else:
        val = 0x40 + ev.value
    return md.event.SysExEvent(ev.port, [0xf0, 0x43, 0x10, 0x58, 0x03, format & 0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, val, 0xf7])

class A3000_RemoteSwitch:
    def __init__(self, number):
        self.number = number
    def event(self, min=None, max=None):
        return md.Process(lambda ev: gen_remote_switch_sysex(ev, self.number))

class A3000_RemoteControl:
    def __init__(self):
        self.params                  = {}
        self.params['fkey1']         = A3000_RemoteSwitch(0)
        self.params['fkey2']         = A3000_RemoteSwitch(1)
        self.params['fkey3']         = A3000_RemoteSwitch(2)
        self.params['fkey4']         = A3000_RemoteSwitch(3)
        self.params['fkey5']         = A3000_RemoteSwitch(4)
        self.params['fkey6']         = A3000_RemoteSwitch(5)
        self.params['command']       = A3000_RemoteSwitch(6)
        self.params['assignable']    = A3000_RemoteSwitch(7)
        self.params['audition']      = A3000_RemoteSwitch(8)
        self.params['play']          = A3000_RemoteSwitch(9)
        self.params['edit']          = A3000_RemoteSwitch(10)
        self.params['rec']           = A3000_RemoteSwitch(11)
        self.params['disk']          = A3000_RemoteSwitch(12)
        self.params['utility']       = A3000_RemoteSwitch(13)
        self.params['kno']           = A3000_RemoteSwitch(14)
        self.params['knob1_sw']      = A3000_RemoteSwitch(14)
        self.params['knob2_sw']      = A3000_RemoteSwitch(15)
        self.params['knob3_sw']      = A3000_RemoteSwitch(16)
        self.params['knob4_sw']      = A3000_RemoteSwitch(17)
        self.params['knob5_sw']      = A3000_RemoteSwitch(19)
        self.params['knob1_encoder'] = A3000_RemoteSwitch(123)
        self.params['knob2_encoder'] = A3000_RemoteSwitch(124)
        self.params['knob3_encoder'] = A3000_RemoteSwitch(125)
        self.params['knob4_encoder'] = A3000_RemoteSwitch(126)
        self.params['knob5_encoder'] = A3000_RemoteSwitch(127)

    def parameters(self):
        return self.params
