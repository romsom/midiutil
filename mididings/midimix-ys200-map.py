#!/usr/bin/env python3

import mididings as md
import mididings.extra.osc as mdosc
from akai_midimix_map import Akai_MidiMix
from yamaha_ys200_map import YS200_Patch, YS200_DumpRequest, YS200_SysExFilter
from common_map import SaveSysEx, map_events, create_scenes
# sd: source ding, dd: destination ding

akai = Akai_MidiMix()
# for now we use only one patch
yam = YS200_Patch()

synth_port_pattern = r'(a2j:USB MIDI Interface.*MIDI 1)|(a2j:Ploytec GM5.*: \[1\].*)'
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

control_switches = [md.KeyFilter(notes=[27]) >> (YS200_DumpRequest(3) >> md.Port('synth_out')),
                    md.KeyFilter(notes=[25]) >> md.SceneSwitch(offset=-1),
                    md.KeyFilter(notes=[26]) >> md.SceneSwitch(offset=1)]

control = md.PortFilter('control_in') >> md.Filter(md.NOTEON) >> control_switches #control = md.PortFilter('control_in') >> md.Print('control')
pre = None #md.Print('input') # bank/page buttons, solo button
post = None #md.Print('output')

def fill_pages():
    """returns a dict of page descriptions.
    These are dicts as well, that map input_controller_names to parameter_names"""
    ps = {'eg': {},
          'frequency':  {},
          'pitch_eg/lfo': {},
          'op_mod_sensitivity': {},
          'keyboard_level_scaling_depth': {},
          'keyboard_level_scaling_curve': {},
          'name': {},
          'performance': {},
    }
    # EG
    eg_elems = ['attack', 'decay1', 'decay2', 'release']
    # YS200 only has dedicated level for decay1, so another layout containing all eg controls on one page is possible
    for op in range(0,4):
        ps['eg'][f'pot_{2*op}_0'] = f'op{op + 1}_attack_rate'
        ps['eg'][f'pot_{2*op + 1}_0'] = f'op{op + 1}_release_rate'
        ps['eg'][f'pot_{2*op}_1'] = f'op{op + 1}_decay1_rate'
        ps['eg'][f'pot_{2*op+1}_1'] = f'op{op + 1}_decay1_level'
        ps['eg'][f'pot_{2*op}_2'] = f'op{op + 1}_decay2_rate'
    # freq
    for op in range(0,4):
        ps['frequency']['pot_{}_0'.format(op)] = 'op{}_detune'.format(op+1)
        ps['frequency']['pot_{}_1'.format(op)] = 'op{}_frequency_range_fine'.format(op+1)
        ps['frequency']['pot_{}_2'.format(op)] = 'op{}_frequency'.format(op+1)
    ps['frequency']['pot_6_0'.format(op)] = 'algorithm'
    # ps['frequency']['pot_6_1'.format(op)] = 'oscillator_key_sync'
    ps['frequency']['pot_6_2'.format(op)] = 'transpose'
    #ps['frequency']['pot_6_1'.format(op)] = 'oscillator_key_sync' # use button!
    # pitch eg/lfo
    ps['pitch_eg/lfo']['pot_0_1'] = 'lfo_speed'
    ps['pitch_eg/lfo']['pot_1_1'] = 'lfo_delay'
    ps['pitch_eg/lfo']['pot_2_1'] = 'lfo_pitch_modulation_depth'
    ps['pitch_eg/lfo']['pot_3_1'] = 'lfo_pitch_modulation_sensitivity'
    ps['pitch_eg/lfo']['pot_4_1'] = 'lfo_amplitude_modulation_depth'
    ps['pitch_eg/lfo']['pot_5_1'] = 'lfo_key_sync'
    ps['pitch_eg/lfo']['pot_6_1'] = 'lfo_wave'
    #for op in range(0,6):
    #    ps['pitch_eg']['pot_{}_1'.format(op)] = 'op{}_oscillator_'.format(op+1)
    #ps['pitch_eg']['pot_2_0'] = 'algorithm_select'
    #ps['pitch_eg']['pot_2_1'] = 'algorithm_select'
    # op_mode_sensitivity
    for op in range(0,4):
        ps['op_mod_sensitivity']['pot_{}_0'.format(op)] = f'op{op+1}_amplitude_modulation_enable'
        ps['op_mod_sensitivity']['pot_{}_1'.format(op)] = f'op{op+1}_key_velocity_sensitivity'
        ps['op_mod_sensitivity']['pot_{}_2'.format(op)] = f'op{op+1}_eg_bias_sensitivity'
    # kls_depth
    # for op in range(0,4):
    #     fs = 'keyboard_level_scaling{}'
    #     ps[fs.format('_depth')]['pot_{}_0'.format(op)] = 'op{}_'.format(op+1) + fs.format('_break_point')
    #     ps[fs.format('_depth')]['pot_{}_1'.format(op)] = 'op{}_'.format(op+1) + fs.format('_left_depth')
    #     ps[fs.format('_depth')]['pot_{}_2'.format(op)] = 'op{}_'.format(op+1) + fs.format('_right_depth')

    # kls_curve
    # for op in range(0,4):
    #     fs = 'level_scaling{}'
    #     ps[fs.format('_curve')]['pot_{}_0'.format(op)] = 'op{}_'.format(op+1) + 'rate_scaling'
    #     ps[fs.format('_curve')]['pot_{}_1'.format(op)] = 'op{}_'.format(op+1) + fs.format('_left_curve')
    #     ps[fs.format('_curve')]['pot_{}_2'.format(op)] = 'op{}_'.format(op+1) + fs.format('_right_curve')

    for i in range(0,8):
        ps['name']['pot_{}_0'.format(i)] = 'voice_name_{}'.format(i+1)
    for i in range(0,2):
        ps['name']['pot_{}_1'.format(i)] = 'voice_name_{}'.format(i+1+8)

    # performance parameters
    ps['performance']['pot_0_0'] = 'poly/mono'
    ps['performance']['pot_1_0'] = 'pitch_bend_range'
    # ps['performance']['pot_2_0'] = 'pitch_bend_step'
    ps['performance']['pot_3_0'] = 'portamento_mode'
    # ps['performance']['pot_4_0'] = 'portamento/glissando'
    ps['performance']['pot_5_0'] = 'portamento_time'
    ps['performance']['pot_0_1'] = 'modulation_wheel_pitch'
    ps['performance']['pot_0_2'] = 'modulation_wheel_amplitude'
    ps['performance']['pot_1_1'] = 'foot_controller_pitch'
    ps['performance']['pot_1_2'] = 'foot_controller_amplitude'
    ps['performance']['pot_2_1'] = 'breath_controller_pitch'
    ps['performance']['pot_2_2'] = 'breath_controller_amplitude'
    # ps['performance']['pot_3_1'] = 'after_touch_pitch'
    # ps['performance']['pot_3_2'] = 'after_touch_amplitude'
    # global params (sliders)
    for p in ps.values():
        for op in range(0,4):
            p['slider_{}'.format(op)] = 'op{}_operator_output_level'.format(op+1)
        p['slider_6'] = 'feedback'
        p['slider_7'] = 'lfo_speed'
    return ps



# controller mappings
def create_scene(control_scene):
    '''Create a complete scene from a control event list returned from map_events'''
    sc = [md.PortFilter('control_in') >> ~md.KeyFilter(notes=[25,26,27]) >> control_scene >> md.Port('synth_out'),
          md.PortFilter('keys_in') >> md.Print('keys') >> md.Port('synth_out'),
          md.PortFilter('synth_in') >> md.Print('synth') >> YS200_SysExFilter() >> SaveSysEx('ys200_patch') >> md.Discard()]
    return sc
    #return md.Print('scene_input') >> control_scene
    #return control_scene


scenes = create_scenes(fill_pages(), akai, yam, create_scene)
#print(scenes)

# enable OSC Interface for livedings
md.hook(mdosc.OSCInterface(56418, 56419))

md.run(scenes,
       control=control,
       pre=pre,
       post=post)
