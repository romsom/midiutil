#!/usr/bin/env python3

import mididings as md
import mididings.extra.osc as mdosc

from roland_alphajuno_map import AlphaJuno_Patch
from akai_midimix_map import Akai_MidiMix

from common_map import SaveSysEx, map_events, create_scenes

akai = Akai_MidiMix()
rol = AlphaJuno_Patch()

synth_port_pattern = r'(a2j:USB Device.*MIDI 1)'
keys_port_pattern = r'(a2j:Axiom.*MIDI 1)|(a2j:RtMidi.*ebus_bridge)|(a2j:MIDIboxKB.*MIDI 1)'
control_port_pattern = r'a2j:MIDI Mix.*MIDI 1'

md.config(backend='jack',
          client_name='control-map',
          in_ports=[('keys_in', keys_port_pattern),
                    ('control_in', control_port_pattern),
                    ('synth_in', synth_port_pattern)],
          out_ports=[('keys_out', keys_port_pattern),
                     ('control_out', control_port_pattern),
                     ('synth_out', synth_port_pattern)])

control_switches = [# md.KeyFilter(notes=[27]) >> (AlphaJuno_DumpRequest(0) >> md.Port('synth_out')),
    md.KeyFilter(notes=[25]) >> md.SceneSwitch(offset=-1),
    md.KeyFilter(notes=[26]) >> md.SceneSwitch(offset=1)]

control = md.PortFilter('control_in') >> md.Filter(md.NOTEON) >> control_switches #control = md.PortFilter('control_in') >> md.Print('control')

control = md.PortFilter('control_in') >> md.Filter(md.NOTEON) >> control_switches #control = md.PortFilter('control_in') >> md.Print('control')
pre = None #md.Print('input') # bank/page buttons, solo button
post = None #md.Print('output')

ps = {
    '1: voice': {
        'pot_0_0' : 'dco_range',
        'pot_1_0' : 'dco_waveform_pulse',
        'pot_2_0' : 'dco_waveform_sawtooth',
        'pot_3_0' : 'dco_waveform_sub',
        'pot_4_0' : 'dco_env_mode',
        'pot_5_0' : 'dco_after_depth',
        'pot_6_0' : 'dco_lfo_mod_depth',
        'pot_7_0' : 'dco_env_mod_depth',

        'pot_0_1' : 'vcf_cutoff_freq',
        'pot_1_1' : 'vcf_resonance',
        'pot_2_1' : 'hpf_cutoff_freq',
        'pot_3_1' : 'vcf_key_follow',
        'pot_4_1' : 'vcf_env_mode',
        'pot_5_1' : 'vcf_after_depth',
        'pot_6_1' : 'vcf_lfo_mod_depth',
        'pot_7_1' : 'vcf_env_mod_depth',

        'pot_0_2' : 'env_t1',
        'pot_1_2' : 'env_t2',
        'pot_2_2' : 'env_l3',
        'pot_3_2' : 'env_t4',

        'pot_4_2' : 'vca_env_mode',
        'pot_5_2' : 'vca_after_depth',
        'pot_6_2' : 'portamento',
        'pot_7_2' : 'portamento_time',


        'slider_0' : 'dco_sub_level',
        'slider_1' : 'dco_noise_level',
        'slider_2' : 'dco_pw_pwm_depth',
        'slider_3' : 'dco_pwm_rate',
        'slider_4' : 'lfo_rate',
        'slider_5' : 'lfo_delay_time',
        'slider_6' : 'chorus',
        'slider_7' : 'chorus_rate',
        'master'   : 'main_volume',
    },
    '2: env': {
        'pot_0_0' : 'env_t1',
        'pot_1_0' : 'env_t2',
        'pot_2_0' : 'env_t3',
        'pot_3_0' : 'env_t4',
        'pot_4_0' : 'env_l1',
        'pot_5_0' : 'env_l2',
        'pot_6_0' : 'env_l3',
        'pot_7_0' : 'env_key_follow',


        'slider_0' : 'dco_sub_level',
        'slider_1' : 'dco_noise_level',
        'slider_2' : 'dco_pw_pwm_depth',
        'slider_3' : 'dco_pwm_rate',
        'slider_4' : 'lfo_rate',
        'slider_5' : 'lfo_delay_time',
        'slider_6' : 'chorus',
        'slider_7' : 'chorus_rate',
        'master'   : 'main_volume',
    }
}

# controller mappings
def create_scene(control_scene):
    '''Create a complete scene from a control event list returned from map_events'''
    sc = [md.PortFilter('control_in') >> ~md.KeyFilter(notes=[25,26,27]) >> control_scene >> md.Port('synth_out'),
          md.PortFilter('keys_in') >> md.Print('keys') >> md.Port('synth_out'),
          # md.PortFilter('synth_in') >> md.Print('synth') >> TX7_SysExFilter() >> SaveSysEx('dx7_patch') >> md.Discard()]
          ]
    return sc
#return md.Print('scene_input') >> control_scene
#return control_scene


scenes = create_scenes(ps, akai, rol, create_scene)
#print(scenes)

# enable OSC Interface for livedings
md.hook(mdosc.OSCInterface(56418, 56419))

md.run(scenes,
       control=control,
       pre=pre,
       post=post)
