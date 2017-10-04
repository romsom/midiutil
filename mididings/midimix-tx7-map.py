#!/usr/bin/env python

import mididings as md
import mididings.extra.osc as mdosc
from akai_midimix_map import Akai_MidiMix
from yamaha_tx7_map import TX7_Patch, TX7_DumpRequest, TX7_SysExFilter
from common_map import SaveSysEx
# sd: source ding, dd: destination ding

akai = Akai_MidiMix()
# for now we use only one patch
yam = TX7_Patch()

md.config(backend='jack',
          client_name='control-map',
          in_ports=[('keys_in', 'a2j:Axiom.*MIDI 1'),
                    ('control_in', 'a2j:MIDI Mix.*MIDI 1'),
                    ('synth_in', 'a2j:USB MIDI Interface.*MIDI 1')],
          out_ports=[('keys_out', 'a2j:Axiom.*MIDI 1'),
                     ('control_out', 'a2j:MIDI Mix.*MIDI 1'),
                     ('synth_out', 'a2j:USB MIDI Interface.*MIDI 1')])

control_switches = [md.KeyFilter(notes=[27]) >> (TX7_DumpRequest(0) >> md.Port('synth_out')),
                    md.KeyFilter(notes=[25]) >> md.SceneSwitch(offset=-1),
                    md.KeyFilter(notes=[26]) >> md.SceneSwitch(offset=1)]

control = md.PortFilter('control_in') >> md.Filter(md.NOTEON) >> control_switches #control = md.PortFilter('control_in') >> md.Print('control')
pre = md.Print('input') # bank/page buttons, solo button
post = md.Print('output')

def fill_pages():
    """returns a dict of page descriptions.
    These are dicts as well, that map input_controller_names to parameter_names"""
    ps = {'op[1-3]_eg': {},
          'op[4-6]_eg': {},
          'frequency':  {}}
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
    # volume on all pages
    for p in ps.values():
        for op in range(0,6):
            p['slider_{}'.format(op)] = 'op{}_operator_output_level'.format(op+1)
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
