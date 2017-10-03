import mididings as md
from common_map import *
from functools import zip

class TX7_SXParamChange:
    def __init__(self, group, h, parameter, max=99, min=0):
        # group in range(0,5), h in [0,1], parameter in range(0,128)
        self.generator = md.SysEx([0xf0, 0x43, 0x10, md.EVENT_VALUE, group * 4 + h, parameter, 0xf7])
        self.filter = md.SysExFilter([0xf0, 0x43]) # at the moment we can only match up to the last byte, pattern matching would be nice though
        self.min = min
        self.max = max
class TX7_Patch:
    def __init__(self, idx):
        self.parameters = {}
        for op in range(0,6):
            op_ofs = 21 * (5-op)
            # 0
            for i in range(0,4):
                self.parameters['op{}_eg_rate_{}'.format(op+1, i+1)] = TX7_SXParamChange(0, 0, op_ofs + i)
                self.parameters['op{}_eg_level_{}'.format(op+1, i+1)] = TX7_SXParamChange(0, 0, op_ofs + 4 + i)
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
                self.parameters[itm[0].format(op+1)] = TX7_SXParamChange(0,0,op_ofs + 8 + i itm[1])
            # 21=next_op
            
class Yamaha_TX7:
    def __init__(self):
        self.patches = {'buffer': }
        
