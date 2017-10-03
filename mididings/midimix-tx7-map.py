#!/usr/bin/env python

import mididings as md
# sd: source ding, dd: destination ding


md.config(backend='jack-rt',
          client_name='control-map',
          in_ports=[('keys_in', 'a2j:Axiom.*MIDI 1'),
                    ('control_in', 'a2j:MIDI Mix.*MIDI 1'),
                    ('synth_in', 'a2j:USB MIDI Interface.*MIDI 1')],
          out_ports=[('keys_out', 'a2j:Axiom.*MIDI 1'),
                     ('control_out', 'a2j:MIDI Mix.*MIDI 1'),
                     ('synth_out', 'a2j:USB MIDI Interface.*MIDI 1')])


control = md.PortFilter('control_in') >> md.Print('control')
pre = ~md.PortFilter('control_in')
post = ~md.PortFilter('synth_in') >> md.Print('output')

sc = [md.PortFilter('keys_in') >> Print('keys') >> md.Port('synth_out'),
      md.PortFilter('synth_in') >> Print('synth')]

scenes = {1: sc}

# enable OSC Interface for livedings
#md.hook(md.OSCInterface(56418, 56419))

md.run(scenes,
       control=control,
       pre=pre,
       post=post)
