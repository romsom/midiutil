#!/usr/bin/env python2

import mididings as md
import mididings.extra.osc as mdosc
from akai_midimix_map import Akai_MidiMix
from yamaha_tx7_map import TX7_Patch, TX7_DumpRequest, TX7_SysExFilter
from common_map import SaveSysEx
# sd: source ding, dd: destination ding

akai = Akai_MidiMix()
# for now we use only one patch
yam = TX7_Patch()

synth_port_pattern = r'(a2j:USB MIDI Interface.*MIDI 1)|(a2j:Ploytec.*: \[3\].*)'
keys_port_pattern = r'(a2j:Axiom.*MIDI 1)|(a2j:RtMidi.*ebus_bridge)'
control_port_pattern = r'a2j:MIDI Mix.*MIDI 1'

md.config(backend='jack',
          client_name='control-map',
          in_ports=[('keys_in', keys_port_pattern),
                    ('control_in', control_port_pattern),
                    ('synth_in', synth_port_pattern)],
          out_ports=[('keys_out', keys_port_pattern),
                     ('control_out', control_port_pattern),
                     ('synth_out', synth_port_pattern)])

control_switches = [md.KeyFilter(notes=[27]) >> (TX7_DumpRequest(0) >> md.Port('synth_out')),
                    md.KeyFilter(notes=[25]) >> md.SceneSwitch(offset=-1),
                    md.KeyFilter(notes=[26]) >> md.SceneSwitch(offset=1)]

control = md.PortFilter('control_in') >> md.Filter(md.NOTEON) >> control_switches #control = md.PortFilter('control_in') >> md.Print('control')
pre = None #md.Print('input') # bank/page buttons, solo button
post = None #md.Print('output')

def fill_pages():
    """returns a dict of page descriptions.
    These are dicts as well, that map input_controller_names to parameter_names"""
    ps = {'op[1-3]_eg': {},
          'op[4-6]_eg': {},
          'frequency':  {},
          'pitch_eg/lfo': {},
          'op_mod_sensitivity': {},
          'keyboard_level_scaling_depth': {},
          'keyboard_level_scaling_curve': {},
          'name': {},
          'performance': {},
    }
    # EG
    for op in range(0,3):
        for egi in range(0,4):
            ps['op[1-3]_eg']['pot_{}_{}'.format(egi, op)] = 'op{}_eg_rate_{}'.format(op+1, egi+1)
            ps['op[1-3]_eg']['pot_{}_{}'.format(egi+4, op)] = 'op{}_eg_level_{}'.format(op+1, egi+1)
    for op in range(3,6):
        for egi in range(0,4):
            ps['op[4-6]_eg']['pot_{}_{}'.format(egi, op-3)] = 'op{}_eg_rate_{}'.format(op+1, egi+1)
            ps['op[4-6]_eg']['pot_{}_{}'.format(egi+4, op-3)] = 'op{}_eg_level_{}'.format(op+1, egi+1)
    # freq
    for op in range(0,6):
        ps['frequency']['pot_{}_0'.format(op)] = 'op{}_oscillator_detune'.format(op+1)
        ps['frequency']['pot_{}_1'.format(op)] = 'op{}_oscillator_frequency_fine'.format(op+1)
        ps['frequency']['pot_{}_2'.format(op)] = 'op{}_oscillator_frequency_coarse'.format(op+1)
    ps['frequency']['pot_6_0'] = 'algorithm_select'
    ps['frequency']['pot_6_1'] = 'oscillator_key_sync'
    ps['frequency']['pot_6_2'] = 'transpose'
    #ps['frequency']['pot_6_1'.format(op)] = 'oscillator_key_sync' # use button!
    # pitch eg/lfo
    for egi in range(0,4):
        ps['pitch_eg/lfo']['pot_{}_0'.format(egi)] = 'pitch_eg_rate_{}'.format(egi+1)
        ps['pitch_eg/lfo']['pot_{}_0'.format(egi+4)] = 'pitch_eg_level_{}'.format(egi+1)
    
    ps['pitch_eg/lfo']['pot_0_1'] = 'lfo_speed'
    ps['pitch_eg/lfo']['pot_1_1'] = 'lfo_delay'
    ps['pitch_eg/lfo']['pot_2_1'] = 'lfo_pitch_modulation_depth'
    ps['pitch_eg/lfo']['pot_3_1'] = 'lfo_pitch_modulation_sensitivity'
    ps['pitch_eg/lfo']['pot_4_1'] = 'lfo_amplitude_modulation_depth'
    ps['pitch_eg/lfo']['pot_5_1'] = 'lfo_key_sync'
    ps['pitch_eg/lfo']['pot_6_1'] = 'lfo_wave'
    for op in range(0,6):
        ps['pitch_eg/lfo']['pot_{}_2'.format(op)] = 'op{}_oscillator_mode'.format(op+1)
    #for op in range(0,6):
    #    ps['pitch_eg']['pot_{}_1'.format(op)] = 'op{}_oscillator_'.format(op+1)
    #ps['pitch_eg']['pot_2_0'] = 'algorithm_select'
    #ps['pitch_eg']['pot_2_1'] = 'algorithm_select'
    # op_mode_sensitivity
    for op in range(0,6):
        fs = 'op{}_{}_sensitivity'.format(op+1, '{}')
        ps['op_mod_sensitivity']['pot_{}_0'.format(op)] = fs.format('amplitude_modulation')
        ps['op_mod_sensitivity']['pot_{}_1'.format(op)] = fs.format('key_velocity')
        #ps['op_mod_sensitivity']['pot_{}_2'.format(op)] = fs.format('')
    # kls_depth
    for op in range(0,6):
        fs = 'keyboard_level_scaling{}'
        ps[fs.format('_depth')]['pot_{}_0'.format(op)] = 'op{}_'.format(op+1) + fs.format('_break_point')
        ps[fs.format('_depth')]['pot_{}_1'.format(op)] = 'op{}_'.format(op+1) + fs.format('_left_depth')
        ps[fs.format('_depth')]['pot_{}_2'.format(op)] = 'op{}_'.format(op+1) + fs.format('_right_depth')

    # kls_curve
    for op in range(0,6):
        fs = 'keyboard_level_scaling{}'
        ps[fs.format('_curve')]['pot_{}_0'.format(op)] = 'op{}_'.format(op+1) + 'keyboard_rate_scaling'
        ps[fs.format('_curve')]['pot_{}_1'.format(op)] = 'op{}_'.format(op+1) + fs.format('_left_curve')
        ps[fs.format('_curve')]['pot_{}_2'.format(op)] = 'op{}_'.format(op+1) + fs.format('_right_curve')

    for i in range(0,8):
        ps['name']['pot_{}_0'.format(i)] = 'voice_name_{}'.format(i+1)
    for i in range(0,2):
        ps['name']['pot_{}_1'.format(i)] = 'voice_name_{}'.format(i+1+8)

    # performance parameters
    ps['performance']['pot_0_0'] = 'poly/mono'
    ps['performance']['pot_1_0'] = 'pitch_bend_range'
    ps['performance']['pot_2_0'] = 'pitch_bend_step'
    ps['performance']['pot_3_0'] = 'portamento_mode'
    ps['performance']['pot_4_0'] = 'portamento/glissando'
    ps['performance']['pot_5_0'] = 'portamento_time'
    ps['performance']['pot_0_1'] = 'modulation_wheel_sensitivity'
    ps['performance']['pot_0_2'] = 'modulation_wheel_assign'
    ps['performance']['pot_1_1'] = 'foot_controller_sensitivity'
    ps['performance']['pot_1_2'] = 'foot_controller_assign'
    ps['performance']['pot_2_1'] = 'breath_controller_sensitivity'
    ps['performance']['pot_2_2'] = 'breath_controller_assign'
    ps['performance']['pot_3_1'] = 'after_touch_sensitivity'
    ps['performance']['pot_3_2'] = 'after_touch_assign'
    # global params (sliders)
    for p in ps.values():
        for op in range(0,6):
            p['slider_{}'.format(op)] = 'op{}_operator_output_level'.format(op+1)
        p['slider_6'] = 'feedback'
        p['slider_7'] = 'lfo_speed'
    return ps



# controller mappings
def create_scene_wrapper(control_scene):
    sc = [md.PortFilter('control_in') >> ~md.KeyFilter(notes=[25,26,27]) >> control_scene >> md.Port('synth_out'),
          md.PortFilter('keys_in') >> md.Print('keys') >> md.Port('synth_out'),
          md.PortFilter('synth_in') >> md.Print('synth') >> TX7_SysExFilter() >> SaveSysEx('dx7_patch') >> md.Discard()]
    return sc
    #return md.Print('scene_input') >> control_scene
    #return control_scene

def create_scenes():
    scs = {}
    for i, (name, page) in enumerate(sorted(fill_pages().items(), key=lambda x: x[0])):
        print("index: {}; name: {}; page:".format(i, name))
        for p in sorted(page):
            print('{}: {}'.format(p, page[p]))
        print('map:')
        for m in akai.Map(page, yam):
            print(m)
        scs[i+1] = md.Scene(name, create_scene_wrapper(akai.Map(page, yam)))# index < 1 will crash mididings
    return scs

scenes = create_scenes()
#print(scenes)

# enable OSC Interface for livedings
md.hook(mdosc.OSCInterface(56418, 56419))

md.run(scenes,
       control=control,
       pre=pre,
       post=post)
