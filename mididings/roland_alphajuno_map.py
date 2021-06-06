import mididings as md

def gen_param_sysex_scaled(ev, parameter, scale, limit, source_offset, target_offset):
    val = (ev.value - source_offset) // scale + target_offset
    if val > limit:
        val = limit
    unit = 0x00
    group = 0x1
    return md.event.SysExEvent(ev.port, [0xf0, 0x41, 0x36, unit, 0x23, 0x20, group, parameter, val & 0x7f, 0xf7])
def gen_param_sysex(ev, parameter):
    unit = 0x00
    group = 0x1
    return md.event.SysExEvent(ev.port, [0xf0, 0x41, 0x36, unit, 0x23, 0x20, group, parameter, ev.value & 0x7f, 0xf7])
# def gen_dump_rq_sysex(ev, format):
#     ev.type = md.SYSEX
#     # TODO: state machine, see manual
#     return md.event.SysExEvent(ev.port, [0xf0, 0x41, 0x20, format & 0x7f, 0xf7])
def AlphaJuno_SysExFilter():
    return md.SysExFilter([0xf0, 0x41]) # at the moment we can only match up to the last byte, pattern matching would be nice though

class AlphaJuno_SXParamChange:
    def __init__(self, parameter, max=127, min=0):
        # group in range(0,5), h in [0,1], parameter in range(0,128)
        #print("creating sysex parameter object: {}".format(parameter))
        #self.generator = md.SysEx([0xf0, 0x43, 0x10, 0, group * 4 + h, parameter, 0xf7])
        self.parameter = parameter
        self.group = 1
        self.filter = AlphaJuno_SysExFilter() # TODO distinguish voice dumps and parameter changes (needs pattern matching though)
        self.min = min
        self.max = max
    def event(self, min=None, max=None):
        if (min is None and max is None) or (min == self.min and max == self.max) :
            return md.Process(lambda ev: gen_param_sysex(ev, self.parameter))
        if min is None:
            min = self.min
        if max is None:
            max = self.max
        n_source = max + 1 - min
        n_target = self.max + 1 - self.min
        return md.Process(lambda ev: gen_param_sysex_scaled(ev, self.parameter,
                                                            n_source // n_target, self.max, min, self.min))

class AlphaJuno_CC_Parameter:
    def __init__(self, cc, max=127, min=0):
        self.cc = cc

    def event(self, min=None, max=None):
        # TODO: min/max
        return md.Ctrl(self.cc, md.EVENT_VALUE)

class AlphaJuno_Patch:
    def __init__(self):
        self._parameters = {
            'main_volume'           : AlphaJuno_CC_Parameter(0x7),

            'dco_sub_level'         : AlphaJuno_SXParamChange(7, 3),
            'dco_noise_level'       : AlphaJuno_SXParamChange(8, 3),

            'dco_range'             : AlphaJuno_SXParamChange(6, 3),
            'dco_waveform_sub'      : AlphaJuno_SXParamChange(5, 5),
            'dco_waveform_pulse'    : AlphaJuno_SXParamChange(3, 5),
            'dco_waveform_sawtooth' : AlphaJuno_SXParamChange(4, 5),
            'dco_env_mode'          : AlphaJuno_SXParamChange(0, 3),
            'dco_after_depth'       : AlphaJuno_SXParamChange(13),
            'dco_lfo_mod_depth'     : AlphaJuno_SXParamChange(11),
            'dco_env_mod_depth'     : AlphaJuno_SXParamChange(12),

            'dco_pw_pwm_depth'      : AlphaJuno_SXParamChange(14),
            'dco_pwm_rate'          : AlphaJuno_SXParamChange(15),
            
            'vcf_cutoff_freq'       : AlphaJuno_SXParamChange(16),
            'vcf_resonance'         : AlphaJuno_SXParamChange(17),
            'hpf_cutoff_freq'       : AlphaJuno_SXParamChange(9, 3),
            'vcf_env_mode'          : AlphaJuno_SXParamChange(1, 3),
            'vcf_key_follow'        : AlphaJuno_SXParamChange(20),
            'vcf_after_depth'       : AlphaJuno_SXParamChange(21),
            'vcf_lfo_mod_depth'     : AlphaJuno_SXParamChange(18),
            'vcf_env_mod_depth'     : AlphaJuno_SXParamChange(19),

            'vca_level'             : AlphaJuno_SXParamChange(22),
            'vca_env_mode'          : AlphaJuno_SXParamChange(2, 3),
            'vca_after_depth'       : AlphaJuno_SXParamChange(23),

            'lfo_rate'              : AlphaJuno_SXParamChange(24),
            'lfo_delay_time'        : AlphaJuno_SXParamChange(25),

            'env_t1'                : AlphaJuno_SXParamChange(26),
            'env_l1'                : AlphaJuno_SXParamChange(27),
            'env_t2'                : AlphaJuno_SXParamChange(28),
            'env_l2'                : AlphaJuno_SXParamChange(29),
            'env_t3'                : AlphaJuno_SXParamChange(30),
            'env_l3'                : AlphaJuno_SXParamChange(31),
            'env_t4'                : AlphaJuno_SXParamChange(32),
            'env_key_follow'        : AlphaJuno_SXParamChange(33),

            'chorus'                : AlphaJuno_SXParamChange(10, 1),
            'chorus_rate'           : AlphaJuno_SXParamChange(34),
            'bender_range'          : AlphaJuno_SXParamChange(35, 12),
            'hold'                  : AlphaJuno_CC_Parameter(0x40),
            'portamento'            : AlphaJuno_CC_Parameter(0x41),
            'portamento_time'       : AlphaJuno_CC_Parameter(0x5),

            'tone_name_1'           : AlphaJuno_SXParamChange(36, 63),
            'tone_name_2'           : AlphaJuno_SXParamChange(37, 63),
            'tone_name_3'           : AlphaJuno_SXParamChange(38, 63),
            'tone_name_4'           : AlphaJuno_SXParamChange(39, 63),
            'tone_name_5'           : AlphaJuno_SXParamChange(40, 63),
            'tone_name_6'           : AlphaJuno_SXParamChange(41, 63),
            'tone_name_7'           : AlphaJuno_SXParamChange(42, 63),
            'tone_name_8'           : AlphaJuno_SXParamChange(43, 63),
            'tone_name_9'           : AlphaJuno_SXParamChange(44, 63),
            'tone_name_10'          : AlphaJuno_SXParamChange(45, 63),
            # 46, 47 reserved
            # 48: ToneModify (increment/decrement mask, ignored if received)
        }
            
    def parameters(self):
        return self._parameters
            
            
