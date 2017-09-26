require('bases')
require('parameters')
require('string')

-- patch gets initialized here. If you want to see what it looks like: print it
function initPatch ()
   local Patch
   -- buttons
   local noteoff_send_map = {}
   local noteoff_recv_map = {0x7f = 'depressed'}
   local noteon_send_map = {0 = 'off', 1 = 'on', 2 = 'blink'}
   local noteon_recv_map = {0x7f = 'pressed'}

   -- record buttons
   for i = 0,7 do
      Patch['params']['send'][string.format('rec_%d', i)] =
	 Parameters.midi.NoteOnOff(64 + i, noteon_send_map, noteoff_send_map)
      Patch['params']['recieve'][string.format('rec_%d', i)] =
	 Parameters.midi.NoteOnOff(64 + i, noteon_recv_map, noteoff_recv_map)
   end

   -- scene control buttons
   for i = 0,7 do
      Patch['params']['send'][string.format('scene_%d', i)] =
	 Parameters.midi.NoteOnOff(82 + i, noteon_send_map, noteoff_send_map)
      Patch['params']['recieve'][string.format('scene_%d', i)] =
	 Parameters.midi.NoteOnOff(82 + i, noteon_recv_map, noteoff_recv_map)
   end

   --shift button
   Patch['params']['send']['shift'] =
      Parameters.midi.NoteOnOff(98, {}, {})
   Patch['params']['recieve']['shift'] =
      Parameters.midi.NoteOnOff(98, noteon_recv_map, noteoff_recv_map)
   
   -- 3 color buttons
   local tc_noteon_send_map = {0 = 'off', 1 = 'green', 3 = 'red', 5 = 'yellow'}
   
   for r = 0,7 do
      for c = 0,7 do
	 Patch['params']['send'][string.format('button_%d%d', 7-r, c)] =
	    Parameters.midi.NoteOnOff(8*r +c, tc_noteon_send_map, noteoff_send_map)
	 Patch['params']['recieve'][string.format('button_%d%d', 7-r, c)] =
	    Parameters.midi.NoteOnOff(8*r +c, noteon_recv_map, noteoff_recv_map)
      end
   end
   return Patch
end

local Patch = initPatch()
setmetatable(Patch, bases.Patch)
Patch.buildLUT()

local AKAI_APCmini = {
   -- this device only has one patch
   patches = { Patch:new() }

}
setmetatable(AKAI_APCmini, bases.Device)

function AKAI_APCmini:new()
   o = {}
   setmetatable(o, self)
   return o
end

function AKAI_APCmini:send_active_patch (patch)
   
end


return AKAI_APCmini
