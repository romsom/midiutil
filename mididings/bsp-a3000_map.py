#!/usr/bin/env python3

import mididings as md
import mididings.extra.osc as mdosc
from arturia_bsp_map import Arturia_BSP
from yamaha_a3000_map import A3000_RemoteControl, A3000_SysExFilter
from common_map import SaveSysEx, map_events, create_scenes

arturia = Arturia_BSP()
yam_rc = A3000_RemoteControl()

synth_port_pattern = r'(a2j:USB MIDI Interface.*MIDI 1)|(a2j:Ploytec.*: \[0\].*)'
keys_port_pattern = r'(a2j:Axiom.*MIDI 1)|(a2j:RtMidi.*ebus_bridge)|(a2j:Arturia BeatStep Pro.*\(capture\).*MIDI 1)'  # BSP: Pads output
control_port_pattern = r'a2j:Arturia BeatStep Pro.*MIDI 2'  # Mackie MCU output

md.config(backend='jack',
          client_name='control-map',
          in_ports=[('keys_in', keys_port_pattern),
                    ('control_in', control_port_pattern),
                    ('synth_in', synth_port_pattern)],
          out_ports=[('keys_out', keys_port_pattern),
                     # ('control_out', control_port_pattern),
                     ('synth_out', synth_port_pattern)])

pages = {
    'remote': {
        'mackie_encoder_0': 'knob1_encoder',
        'mackie_encoder_1': 'knob2_encoder',
        'mackie_encoder_2': 'knob3_encoder',
        'mackie_encoder_3': 'knob4_encoder',
        'mackie_encoder_4': 'knob5_encoder',
    }
}

def create_scene(control_scene):
    return [md.PortFilter('control_in') >> control_scene >> md.Port('synth_out'),
            md.PortFilter('keys_in') >> md.Print('keys') >> md.Port('synth_out'),
            md.PortFilter('synth_in') >> md.Print('synth') >> A3000_SysExFilter() >> SaveSysEx('a3000_patch') >> md.Discard()]

scenes = create_scenes(pages, arturia, yam_rc, create_scene)

control = md.PortFilter('control_in')
pre = None #md.Print('input')
post = None #md.Print('output')
# enable OSC Interface for livedings
md.hook(mdosc.OSCInterface(56418, 56419))

md.run(scenes,
       control=control,
       pre=pre,
       post=post)
