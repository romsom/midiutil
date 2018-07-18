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
    def Generator(self, min=None, max=None):
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
        for op in range(0,6):
            op_ofs = 21 * (5-op) # operator offset
            # 0
            for i in range(0,4):
                self.params['op{}_eg_rate_{}'.format(op+1, i+1)] = YS200_SXParamChange(0, 0, op_ofs + i, 99)
                self.params['op{}_eg_level_{}'.format(op+1, i+1)] = YS200_SXParamChange(0, 0, op_ofs + 4 + i, 99)
            # 8
            itms = [('op{}_keyboard_level_scaling_break_point', 99),
                    ('op{}_keyboard_level_scaling_left_depth', 99),
                    ('op{}_keyboard_level_scaling_right_depth', 99),
                    ('op{}_keyboard_level_scaling_left_curve', 3),
                    ('op{}_keyboard_level_scaling_right_curve', 3),
                    ('op{}_keyboard_rate_scaling', 7),
                    ('op{}_amplitude_modulation_sensitivity', 3),
                    ('op{}_key_velocity_sensitivity', 7),
                    ('op{}_operator_output_level', 99),
                    ('op{}_oscillator_mode', 1),
                    ('op{}_oscillator_frequency_coarse', 31),
                    ('op{}_oscillator_frequency_fine', 99),
                    ('op{}_oscillator_detune', 14)]
            for i, itm in enumerate(itms):
                self.params[itm[0].format(op+1)] = YS200_SXParamChange(0,0,op_ofs + 8 + i, itm[1])
            # 21=next_op
        # global parameters
        
        self.params['pitch_eg_rate_1'] = YS200_SXParamChange(0, 0, 126, 99)
        self.params['pitch_eg_rate_2'] = YS200_SXParamChange(0, 0, 127, 99)
        self.params['pitch_eg_rate_3'] = YS200_SXParamChange(0, 1, 0, 99)
        self.params['pitch_eg_rate_4'] = YS200_SXParamChange(0, 1, 1, 99)
        self.params['pitch_eg_level_1'] = YS200_SXParamChange(0, 1, 2, 99) # normal at 50/0x32
        self.params['pitch_eg_level_2'] = YS200_SXParamChange(0, 1, 3, 99)
        self.params['pitch_eg_level_3'] = YS200_SXParamChange(0, 1, 4, 99)
        self.params['pitch_eg_level_4'] = YS200_SXParamChange(0, 1, 5, 99)
        self.params['algorithm_select'] = YS200_SXParamChange(0, 1, 6, 31)
        self.params['feedback'] = YS200_SXParamChange(0, 1, 7, 7)
        self.params['oscillator_key_sync'] = YS200_SXParamChange(0, 1, 8, 1)
        
        self.params['lfo_speed'] = YS200_SXParamChange(0, 1, 9, 99)
        self.params['lfo_delay'] = YS200_SXParamChange(0, 1, 10, 99)
        self.params['lfo_pitch_modulation_depth'] = YS200_SXParamChange(0, 1, 11, 99)
        self.params['lfo_amplitude_modulation_depth'] = YS200_SXParamChange(0, 1, 12, 99)
        self.params['lfo_key_sync'] = YS200_SXParamChange(0, 1, 13, 1)
        # tri, saw down, saw up, square, sine, s/h
        self.params['lfo_wave'] = YS200_SXParamChange(0, 1, 14, 5)
        self.params['lfo_pitch_modulation_sensitivity'] = YS200_SXParamChange(0, 1, 15, 7)
        self.params['transpose'] = YS200_SXParamChange(0, 1, 16, 48) # normal at 24/0x18

        self.params['voice_name_1'] = YS200_SXParamChange(0, 1, 17) # ascii
        self.params['voice_name_2'] = YS200_SXParamChange(0, 1, 18)
        self.params['voice_name_3'] = YS200_SXParamChange(0, 1, 19)
        self.params['voice_name_4'] = YS200_SXParamChange(0, 1, 20)
        self.params['voice_name_5'] = YS200_SXParamChange(0, 1, 21)
        self.params['voice_name_6'] = YS200_SXParamChange(0, 1, 22)
        self.params['voice_name_7'] = YS200_SXParamChange(0, 1, 23)
        self.params['voice_name_8'] = YS200_SXParamChange(0, 1, 24)
        self.params['voice_name_9'] = YS200_SXParamChange(0, 1, 25)
        self.params['voice_name_10'] = YS200_SXParamChange(0, 1, 26)
        self.params['operator_on/off'] = YS200_SXParamChange(0, 1, 27, 63) # bitmap for ops, lsb: op6
        self.params['operator_select'] = YS200_SXParamChange(0, 1, 27, 5)
        # DX Function Parameter Change
        # group 1
        self.params['dx_source_select'] = YS200_SXParamChange(1, 0, 1, 16, 1)
        self.params['dx_poly/mono'] = YS200_SXParamChange(1, 0, 2, 1)
        self.params['dx_pitch_bend_range'] = YS200_SXParamChange(1, 0, 3, 12)
        self.params['dx_pitch_bend_step'] = YS200_SXParamChange(1, 0, 4, 12)
        self.params['dx_portamento_time'] = YS200_SXParamChange(1, 0, 5, 99)
        self.params['dx_portamento/glissando'] = YS200_SXParamChange(1, 0, 6, 1)
        self.params['dx_portamento_mode'] = YS200_SXParamChange(1, 0, 7, 1)
        # 8 not defined
        self.params['dx_modulation_wheel_sensitivity'] = YS200_SXParamChange(1, 0, 9, 15)
        self.params['dx_modulation_wheel_assign'] = YS200_SXParamChange(1, 0, 10, 7)
        self.params['dx_foot_controller_sensitivity'] = YS200_SXParamChange(1, 0, 11, 15)
        self.params['dx_foot_controller_assign'] = YS200_SXParamChange(1, 0, 12, 7)
        self.params['dx_after_touch_sensitivity'] = YS200_SXParamChange(1, 0, 13, 15)
        self.params['dx_after_touch_assign'] = YS200_SXParamChange(1, 0, 14, 7)
        self.params['dx_breath_controller_sensitivity'] = YS200_SXParamChange(1, 0, 15, 15)
        self.params['dx_breath_controller_assign'] = YS200_SXParamChange(1, 0, 16, 7)
        # lots undefined
        self.params['dx_audio_output_level_attenuator'] = YS200_SXParamChange(1, 0, 26, 7)
        self.params['dx_master_tuning'] = YS200_SXParamChange(1, 0, 64)

        # Function Parameter Change
        self.params['poly/mono'] = YS200_SXParamChange(2, 0, 64, 1)
        self.params['pitch_bend_range'] = YS200_SXParamChange(2, 0, 65, 12)
        self.params['pitch_bend_step'] = YS200_SXParamChange(2, 0, 66, 12)
        self.params['portamento_mode'] = YS200_SXParamChange(2, 0, 67, 1)
        self.params['portamento/glissando'] = YS200_SXParamChange(2, 0, 68, 1)
        self.params['portamento_time'] = YS200_SXParamChange(2, 0, 69, 99)
        self.params['modulation_wheel_sensitivity'] = YS200_SXParamChange(2, 0, 70, 99)
        self.params['modulation_wheel_assign'] = YS200_SXParamChange(2, 0, 71, 7)
        self.params['foot_controller_sensitivity'] = YS200_SXParamChange(2, 0, 72, 99)
        self.params['foot_controller_assign'] = YS200_SXParamChange(2, 0, 73, 7)
        self.params['breath_controller_sensitivity'] = YS200_SXParamChange(2, 0, 74, 99)
        self.params['breath_controller_assign'] = YS200_SXParamChange(2, 0, 75, 7)
        self.params['after_touch_sensitivity'] = YS200_SXParamChange(2, 0, 76, 99)
        self.params['after_touch_assign'] = YS200_SXParamChange(2, 0, 77, 7)

        # tx function parameters
        self.params['data_entry_recieve_switch'] = YS200_SXParamChange(4, 0, 0, 1)
        self.params['control_change_recieve_switch'] = YS200_SXParamChange(4, 0, 1, 1)
        self.params['data_entry_volume_switch'] = YS200_SXParamChange(4, 0, 2, 1)
        self.params['compute_communication_switch'] = YS200_SXParamChange(4, 0, 3, 1)
        self.params['combined/individual'] = YS200_SXParamChange(4, 0, 4)
        self.params['note_limit_low'] = YS200_SXParamChange(4, 0, 5)
        self.params['note_limit_high'] = YS200_SXParamChange(4, 0, 6)
        self.params['memory_protection_off/on'] = YS200_SXParamChange(4, 0, 7) # 0 or 127
        self.params['load_function_select_int/ext'] = YS200_SXParamChange(4, 0, 11) # 0 or 127

    def parameters(self):
        return self.params
#class Yamaha_YS200:
#    def __init__(self):
#        self.patches = {'buffer': }
        
