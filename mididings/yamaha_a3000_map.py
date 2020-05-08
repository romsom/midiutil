import mididings as md

def gen_remote_switch_sysex(ev, format):
    # not sure about 0x10: first nibble should be device ID, 0x03: (Manual: binary: 1, hex: 3 ...), length of data also not clear
    return md.event.SysExEvent(ev.port, [0xf0, 0x43, 0x10, 0x58, 0x03, format & 0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, ev.value, 0xf7])

class A3000_RemoteSwitch:
    FKEY1, FKEY2, FKEY3, FKEY4, FKEY5, FKEY6, COMMAND, ASSIGNABLE, AUDITION, PLAY, EDIT, REC, DISK, UTILITY, KNO, KNOB1_SW, KNOB2_SW, KNOB3_SW, KNOB4_SW, KNOB5_SW = range(19)
    KNOB1_ENCODER, KNOB2_ENCODER, KNOB3_ENCODER, KNOB4_ENCODER, KNOB5_ENCODER, KNOB6_ENCODER = range(123, 128)
    def __init__(self, number):
        self.number = number
    def event(self):
        return md.Process(lambda ev: gen_remote_switch_sysex(ev, self.number))

class A3000_RemoteControl:
    def __init__(self):
        self.params                  = {}
        self.params['fkey1']         = A3000_RemoteSwitch(A3000_RemoteSwitch.FKEY1)
        self.params['fkey2']         = A3000_RemoteSwitch(A3000_RemoteSwitch.FKEY2)
        self.params['fkey3']         = A3000_RemoteSwitch(A3000_RemoteSwitch.FKEY3)
        self.params['fkey4']         = A3000_RemoteSwitch(A3000_RemoteSwitch.FKEY4)
        self.params['fkey5']         = A3000_RemoteSwitch(A3000_RemoteSwitch.FKEY5)
        self.params['fkey6']         = A3000_RemoteSwitch(A3000_RemoteSwitch.FKEY6)
        self.params['command']       = A3000_RemoteSwitch(A3000_RemoteSwitch.COMMAND)
        self.params['assignable']    = A3000_RemoteSwitch(A3000_RemoteSwitch.ASSIGNABLE)
        self.params['audition']      = A3000_RemoteSwitch(A3000_RemoteSwitch.AUDITION)
        self.params['play']          = A3000_RemoteSwitch(A3000_RemoteSwitch.PLAY)
        self.params['rec']           = A3000_RemoteSwitch(A3000_RemoteSwitch.REC)
        self.params['disk']          = A3000_RemoteSwitch(A3000_RemoteSwitch.DISK)
        self.params['utility']       = A3000_RemoteSwitch(A3000_RemoteSwitch.UTILITY)
        self.params['kno']           = A3000_RemoteSwitch(A3000_RemoteSwitch.KNO)
        self.params['knob1_sw']      = A3000_RemoteSwitch(A3000_RemoteSwitch.KNOB1_SW)
        self.params['knob2_sw']      = A3000_RemoteSwitch(A3000_RemoteSwitch.KNOB2_SW)
        self.params['knob3_sw']      = A3000_RemoteSwitch(A3000_RemoteSwitch.KNOB3_SW)
        self.params['knob4_sw']      = A3000_RemoteSwitch(A3000_RemoteSwitch.KNOB4_SW)
        self.params['knob5_sw']      = A3000_RemoteSwitch(A3000_RemoteSwitch.KNOB5_SW)
        self.params['knob1_encoder'] = A3000_RemoteSwitch(A3000_RemoteSwitch.KNOB1_ENCODER)
        self.params['knob2_encoder'] = A3000_RemoteSwitch(A3000_RemoteSwitch.KNOB2_ENCODER)
        self.params['knob3_encoder'] = A3000_RemoteSwitch(A3000_RemoteSwitch.KNOB3_ENCODER)
        self.params['knob4_encoder'] = A3000_RemoteSwitch(A3000_RemoteSwitch.KNOB4_ENCODER)
        self.params['knob5_encoder'] = A3000_RemoteSwitch(A3000_RemoteSwitch.KNOB5_ENCODER)

    def parameters(self):
        return self.params
