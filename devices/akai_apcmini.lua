require('bases')

local AKAI_APCmini = {


}
setmetatable(AKAI_APCmini, bases.Device)

function AKAI_APCmini:new()
   o = {}
   setmetatable(o, self)
   return o
end

return AKAI_APCmini
