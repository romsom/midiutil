-- generic class for device
local Device = {
   name = "Generic MIDI Device",
   patches = {},
   midiports = {
      input = -1,
      output = -1,
   },
   library = {} -- allow save and load
}

function Device:new ()
   o = {}
   setmetatable(o, self)
   return o
end

function Device:dump_request (patchrange)
   -- not implemented
end

function Device:send_patches (patchdict)
   -- not implemented
end

-- generic class for patch
local Patch = {
   params = {}
}

function Patch:new ()
   o = {}
   setmetatable(s, self)
   return o
end

function Patch:encode (location)
   --[[
      returns midi message to send the patch
   ]]--
   -- not implemented
   return {sysex = -1,
	   cc = -1}
end

function Patch:decode (midimessage)
   --[[
      sets params of a newly created patch according to the bytes in midimessage
   ]]--
   -- not implemented
   return Patch:new()
end

function Patch:request (location)
   --[[
      returns midi message to request the patch
   ]]--
   -- not implemented
   return {sysex = -1,
	   cc = -1}
end

function Patch:change (params)
   for k,v in pairs(params) do
      if self.params[k] then
	 self.params[k] = v
      else
	 print('unexpected param: ' .. k .. ':=' .. v)
      end
   end
end

function Patch:random (params)
   -- just an idea
   -- needs types and ranges in params
end

function Patch:__eq (other)
   if #(self.params) ~= #(other.params) then
      return false
   end
   for k,v in pairs(self.params) do
      if other[k] ~= v then
	 return false
      end
   end
   return true
end

bases = {
   ["Device"] = Device,
   ["Patch"] = Patch
}
return bases
