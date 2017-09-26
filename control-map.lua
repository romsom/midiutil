require('bases')
-- generic class for control map (controller ->  device)
local ControlMap = {
   active_tab = {},
   tabs = {},
   controller_state = {},
   -- controller device class. We need this to create new patches
   Controller = bases.Device,
   -- device/instrument class. We neet it if we want to send/recieve patches
   controller = nil,
   Device = bases.Device,
   device = nil,
}

function ControlMap:new (Device, Controller)
   o = {}
   setmetatable(o, self)
   -- init device and controller
   o.Device = Device
   o.device = o.Device:new()
   o.Controller = Controller
   o.controller = o.Controller:new()
   return o
end

function ControlMap:update_controller()
   self.controller.send_active_patch(active_tab.patch)
end

-- controller parameter changes have types and trigger lua-functions
-- you can define any behaviour you want
-- but can also use these methods to implement standard behaviour
local assign_parameter = function(source, destination, new_value)
   -- scale and shift
   local scale = (destination.max - destination.min) / (source.max - source.min)
   local value = scale * (new_value - source.min) + destination.min
   -- return feedback
   local feedback = destination.assign(value)
   return (feedback - destination.min) / scale + source.min
end

local assign_parameters = function(definitions)
   -- resolve parameters at init to save a bit of time
   local tab = {}
   for k,v in pairs(definitions) do
      local controller_param = lookup_controller_param(k)
      local device_param = lookup_device_param(v)
      tab[k] = {
	 -- insert callable object which also contains references to source and dest
	 __call = function(new_value)
	    return controller_param, assign_parameter(controller_param, device_param, new_value)
	 end,
	 controller_param = controller_param,
	 device_param = device_param
      }
   end
   return tab
end

function ControlMap:trigger_change (sourceid, new_value)
   -- this function will be called everytime a value change is detected
   -- lookup handling function and return feedback
   return self.active_tab[sourceid](new_value)
end

function ControlMap:set_active_tab(id)
   self.active_tab = self.tabs[id]
   self.update_controller()
end
-- controller and device parameters are scaled and shifted to they have the same range
-- there will be warnings if there is a possible loss of range and/or resolution
-- if you want special behaviour (e.g. fine control, values up to half of the device params range etc.) you can
--  - implement in a special function
--  - define custom parameters in the map definition

--[[ TODO
   - class for table entry
     - function call
     - source parameter? - do we still need this if we have the containing patch?
   - class for table
     - Controller Patch
     - mapping table
]]--

control_map = {
   ControlMap = ControlMap
}
return control_map
