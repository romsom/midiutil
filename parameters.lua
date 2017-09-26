-- parameter classes
local Parameter = {}

function Parameter:new (min, max, continuous, class, values, data)
   o = {
      'min' = min,
      'max' = max,
      'continuous' = continuous, -- or are there holes?
      'class' = class, -- 'int', 'real', 'enum', 'string', 'data'
      'values' = values, -- allowed values and aliases
      'data' = data, -- the actual value
   }
   setmetatable(o, self)
   return o
end

function Parameter:assign(value)
   
end

local midi = {
   NoteOnOff = function(notenumber, on_map, off_map)
      return {
	 '0x90' = Parameter:new(0, 127, false, 'enum', on_map, 0),
	 '0x80' = Parameter:new(0, 127, false, 'enum', off_map, 0),
      }
   end,

   Custom = function(cmd)
   end


}
