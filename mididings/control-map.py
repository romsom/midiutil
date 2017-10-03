#!/usr/bin/env python3

import mididings as md
# sd: source ding, dd: destination ding

md.config(backend='jack-rt', client_name='control-map')

control = md.KeyFilter(notes=[shift_key])
pre = ~control
