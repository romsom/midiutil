import mididings as md
from common_map import *
#from functools import zip

VCED = (4, 2) # Voice Edit
ACED = (4, 3)
PCED = (4, 3) # same as ACED
REMOTE_SWITCH = (0,0) # TX81, data=0 -> off, data=0x7f -> on
SYS = (4, 0)

def gen_param_sysex_scaled(ev, group, parameter, scale, limit, source_offset, target_offset):
    val = (ev.value - source_offset) // scale + target_offset
    if val > limit:
        val = limit
    return md.event.SysExEvent(ev.port, [0xf0, 0x43, 0x10, group, parameter, val & 0x7f, 0xf7])
def gen_param_sysex(ev, group, parameter):
    return md.event.SysExEvent(ev.port, [0xf0, 0x43, 0x10, group, parameter, ev.value & 0x7f, 0xf7])
def gen_dump_rq_sysex(ev, format, channel):
    ev.type = md.SYSEX
    return md.event.SysExEvent(ev.port, [0xf0, 0x43, channel, format & 0x7f, 0xf7])
def YS200_DumpRequest(format=0, channel=0):
    return md.Process(lambda ev: gen_dump_rq_sysex(ev, format, channel))
def YS200_SysExFilter():
    return md.SysExFilter([0xf0, 0x43]) # at the moment we can only match up to the last byte, pattern matching would be nice though

class YS200_SXParamChange:
    def __init__(self, group, subgroup, parameter, max=127, min=0, channel=0):
        # group in range(0,5), subgroup in [0,1], parameter in range(0,128)
        # channel is the configured basic receive channel of the device
        #print("creating sysex parameter object: {}".format(parameter))
        #self.generator = md.SysEx([0xf0, 0x43, 0x10, 0, group * 4 + subgroup, parameter, 0xf7])
        self.parameter = parameter
        self.group = group
        self.subgroup = subgroup
        self.filter = YS200_SysExFilter() # TODO distinguish voice dumps and parameter changes (needs pattern matching though)
        self.min = min
        self.max = max
    def event(self, min=None, max=None):
        if (min is None and max is None) or (min == self.min and max == self.max) :
            return md.Process(lambda ev: gen_param_sysex(ev, self.group*4 + self.subgroup, self.parameter))
        if min is None:
            min = self.min
        if max is None:
            max = self.max
        n_source = max + 1 - min
        n_target = self.max + 1 - self.min
        return md.Process(lambda ev: gen_param_sysex_scaled(ev, self.group*4 + self.subgroup, self.parameter,
                                                            n_source // n_target, self.max, min, self.min))
class YS200_Patch:
    # TODO:
    # - base on generic Patch (send, request, dump, load, serialize, deserialize)
    # - separate value, ParamChange, ParamRequest
    # - manage active and inactive patches
    def __init__(self, idx=None):
        self.params = {}
        # Voice Control parameters (VCED, g=4, h=2)
        
        # operator parameters
        for op in range(0,4):
            op_ofs = 13 * (3-op) # operator offset
            # 0
            self.params['op{}_attack_rate'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs, 31)
            self.params['op{}_decay1_rate'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs + 1, 31)
            self.params['op{}_decay2_rate'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs + 2, 31)
            self.params['op{}_release_rate'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs + 3, 15)
            self.params['op{}_decay1_level'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs + 4, 15)
            self.params['op{}_level_scaling'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs + 5, 99)
            self.params['op{}_rate_scaling'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs + 6, 3)
            self.params['op{}_eg_bias_sensitivity'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs + 7, 7)
            self.params['op{}_amplitude_modulation_enable'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs + 8, 1)
            self.params['op{}_key_velocity_sensitivity'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs + 9, 7)
            self.params['op{}_operator_output_level'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs + 10, 99)
            self.params['op{}_frequency'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs + 11, 63)
            self.params['op{}_detune'.format(op+1)] = YS200_SXParamChange(4, 2, op_ofs + 12, 6)
        
        self.params['algorithm'] = YS200_SXParamChange(4, 2, 52, 7)
        self.params['feedback'] = YS200_SXParamChange(4, 2, 53, 7)
        
        self.params['lfo_speed'] = YS200_SXParamChange(4, 2, 54, 99)
        self.params['lfo_delay'] = YS200_SXParamChange(4, 2, 55, 99)
        self.params['lfo_pitch_modulation_depth'] = YS200_SXParamChange(4, 2, 56, 99)
        self.params['lfo_amplitude_modulation_depth'] = YS200_SXParamChange(4, 2, 57, 99)
        self.params['lfo_key_sync'] = YS200_SXParamChange(4, 2, 58, 1)
        # tri, saw down, saw up, square, sine, s/h
        self.params['lfo_wave'] = YS200_SXParamChange(4, 2, 59, 3)
        self.params['lfo_pitch_modulation_sensitivity'] = YS200_SXParamChange(4, 2, 60, 7)
        self.params['lfo_amplitude_modulation_sensitivity'] = YS200_SXParamChange(4, 2, 61, 3)
        self.params['transpose'] = YS200_SXParamChange(4, 2, 62, 48) # normal at 24/0x18

        self.params['poly/mono'] = YS200_SXParamChange(4, 2, 63, 1)
        self.params['pitch_bend_range'] = YS200_SXParamChange(4, 2, 64, 12)
        self.params['portamento_mode'] = YS200_SXParamChange(4, 2, 65, 1)
        self.params['portamento_time'] = YS200_SXParamChange(4, 2, 66, 99)
        self.params['foot_controller_volume'] = YS200_SXParamChange(4, 2, 67, 99)
        self.params['sustain'] = YS200_SXParamChange(4, 2, 68, 1) # TODO check if foot controller
        #self.params['foot_controller_assign'] = YS200_SXParamChange(4, 2, 73, 7)
        self.params['portamento'] = YS200_SXParamChange(4, 2, 69, 1)
        self.params['chorus'] = YS200_SXParamChange(4, 2, 70, 1)
        self.params['modulation_wheel_pitch'] = YS200_SXParamChange(4, 2, 71, 99)
        self.params['modulation_wheel_amplitude'] = YS200_SXParamChange(4, 2, 72, 99)
        self.params['breath_controller_pitch'] = YS200_SXParamChange(4, 2, 73, 99)
        self.params['breath_controller_amplitude'] = YS200_SXParamChange(4, 2, 74, 99)
        self.params['breath_controller_eg_bias'] = YS200_SXParamChange(4, 2, 75, 99)
        self.params['breath_controller_pitch_bias'] = YS200_SXParamChange(4, 2, 76, 99)

        
        self.params['voice_name_1'] = YS200_SXParamChange(4, 2, 77) # ascii
        self.params['voice_name_2'] = YS200_SXParamChange(4, 2, 78)
        self.params['voice_name_3'] = YS200_SXParamChange(4, 2, 79)
        self.params['voice_name_4'] = YS200_SXParamChange(4, 2, 80)
        self.params['voice_name_5'] = YS200_SXParamChange(4, 2, 81)
        self.params['voice_name_6'] = YS200_SXParamChange(4, 2, 82)
        self.params['voice_name_7'] = YS200_SXParamChange(4, 2, 83)
        self.params['voice_name_8'] = YS200_SXParamChange(4, 2, 84)
        self.params['voice_name_9'] = YS200_SXParamChange(4, 2, 85)
        self.params['voice_name_10'] = YS200_SXParamChange(4, 2, 86)
        # 87 - 92 unused in TX81z
        self.params['operator_on/off'] = YS200_SXParamChange(4, 2, 93, 15) # bitmap for ops, lsb: op4
        # tx81 / ys200 done until here
        
        # ACED (g=4, h=3)
        for op in range(0,4):
            op_ofs = 5 * (3-op) # operator offset
            # 0
            self.params['op{}_fixed_frequency'.format(op+1)] = YS200_SXParamChange(4, 3, op_ofs, 1)
            self.params['op{}_fixed_frequency_range'.format(op+1)] = YS200_SXParamChange(4, 3, op_ofs + 1, 7)
            self.params['op{}_frequency_range_fine'.format(op+1)] = YS200_SXParamChange(4, 3, op_ofs + 2, 15)
            self.params['op{}_waveform'.format(op+1)] = YS200_SXParamChange(4, 3, op_ofs + 3, 7)
            self.params['op{}_eg_shift'.format(op+1)] = YS200_SXParamChange(4, 3, op_ofs + 4, 3)
        self.params['reverb_rate'] = YS200_SXParamChange(4, 3, 20, 7)
        self.params['foot_controller_pitch'] = YS200_SXParamChange(4, 3, 21, 99)
        self.params['foot_controller_amplitude'] = YS200_SXParamChange(4, 3, 22, 99)


        # performance parameters (g=4, h=3)

        for inst in range(0,8):
            inst_ofs = 12 * inst
            self.params['inst{}_maximum_notes'.format(inst+1)] = YS200_SXParamChange(4, 3, inst_ofs, 8)
            self.params['inst{}_voice_number_msb'.format(inst+1)] = YS200_SXParamChange(4, 3, inst_ofs + 1, 1)
            self.params['inst{}_voice_number'.format(inst+1)] = YS200_SXParamChange(4, 3, inst_ofs + 2)
            self.params['inst{}_reveive_channel'.format(inst+1)] = YS200_SXParamChange(4, 3, inst_ofs + 3, 16) # 16: omni
            self.params['inst{}_low_note_limit'.format(inst+1)] = YS200_SXParamChange(4, 3, inst_ofs + 4)
            self.params['inst{}_high_note_limit'.format(inst+1)] = YS200_SXParamChange(4, 3, inst_ofs + 5)
            self.params['inst{}_detune'.format(inst+1)] = YS200_SXParamChange(4, 3, inst_ofs + 6, 14)
            self.params['inst{}_note_shift'.format(inst+1)] = YS200_SXParamChange(4, 3, inst_ofs + 7, 48)
            self.params['inst{}_volume'.format(inst+1)] = YS200_SXParamChange(4, 3, inst_ofs + 8, 99)
            self.params['inst{}_output_assign'.format(inst+1)] = YS200_SXParamChange(4, 3, inst_ofs + 9, 3)
            self.params['inst{}_lfo_select'.format(inst+1)] = YS200_SXParamChange(4, 3, inst_ofs + 10, 99) # 0: off, 1: inst1, 2: inst2, 3: vib
            self.params['inst{}_micro_tune_enable'.format(inst+1)] = YS200_SXParamChange(4, 3, inst_ofs + 11, 1)

        self.params['micro_tune_table'] = YS200_SXParamChange(4, 3, inst_ofs + 96, 12)
        self.params['assign_mode'] = YS200_SXParamChange(4, 3, inst_ofs + 97, 1)
        self.params['effect'] = YS200_SXParamChange(4, 3, inst_ofs + 98, 3)
        self.params['micro_tune_key'] = YS200_SXParamChange(4, 3, inst_ofs + 99, 11)
        self.params['performance_name_1'] = YS200_SXParamChange(4, 3, inst_ofs + 100) # ascii
        self.params['performance_name_2'] = YS200_SXParamChange(4, 3, inst_ofs + 101)
        self.params['performance_name_3'] = YS200_SXParamChange(4, 3, inst_ofs + 102)
        self.params['performance_name_4'] = YS200_SXParamChange(4, 3, inst_ofs + 103)
        self.params['performance_name_5'] = YS200_SXParamChange(4, 3, inst_ofs + 104)
        self.params['performance_name_6'] = YS200_SXParamChange(4, 3, inst_ofs + 105)
        self.params['performance_name_7'] = YS200_SXParamChange(4, 3, inst_ofs + 106)
        self.params['performance_name_8'] = YS200_SXParamChange(4, 3, inst_ofs + 107)
        self.params['performance_name_9'] = YS200_SXParamChange(4, 3, inst_ofs + 108)
        self.params['performance_name_10'] = YS200_SXParamChange(4, 3, inst_ofs + 109)
            
        # TODO: remote switch parameters for TX81z, YS200 (if avail)

    def parameters(self):
        return self.params
#class Yamaha_YS200:
#    def __init__(self):
#        self.patches = {'buffer': }
        
