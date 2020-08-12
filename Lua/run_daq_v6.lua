run_number = 127
max_events = 10000

-- Set emulation_mode to 0 in order to run this script on the crate
-- and to 1 in order to run on the host computer like hep-daq
emulation_mode = 0

-- All DAQ configuration should be performed below
-- inside the "daq_configuration_chunk" code snippet.
-- This snippet will be saved together with the run data.
daq_configuration_chunk = [[
  config_lam_slot = 17
  config_adc_slots = {17}
  config_adc_channels = 12
  config_tdc_slots = {10}
  config_tdc_channels = 8
]]

function dump_run_configuration(fhandle, run_num)
  write(fhandle, "Begin DAQ config for run ", run_num, '\n')
  write(fhandle, format("%q\n", daq_configuration_chunk))
  write(fhandle, "End DAQ config for run ", run_num, '\n')
end

function dump_hw_counter(fhandle)
  write(fhandle, "HWC ", nim_getcev(1), '\n')
end

function dump_deadtime(fhandle)
  write(fhandle, "DT ", nim_getcdtc(1), '\n')
end

function dump_adc_slot(fhandle, F, slot)
  local q0, a0 = CFSA(F, slot, 0, 0)
  local q1, a1 = CFSA(F, slot, 1, 0)
  local q2, a2 = CFSA(F, slot, 2, 0)
  local q3, a3 = CFSA(F, slot, 3, 0)
  local q4, a4 = CFSA(F, slot, 4, 0)
  local q5, a5 = CFSA(F, slot, 5, 0)
  local q6, a6 = CFSA(F, slot, 6, 0)
  local q7, a7 = CFSA(F, slot, 7, 0)
  local q8, a8 = CFSA(F, slot, 8, 0)
  local q9, a9 = CFSA(F, slot, 9, 0)
  local q10, a10 = CFSA(F, slot, 10, 0)
  local q11, a11 = CFSA(F, slot, 11, 0)
  if q0 ~= 1 or q1 ~= 1 or q2 ~= 1 or q3 ~= 1 or q4 ~= 1 or q5 ~= 1 or q6 ~= 1 or q7 ~= 1 or q8 ~= 1 or q9 ~= 1 or q10 ~= 1 or q11 ~= 1 then
    error(format("In dump_adc_slot: failed to read slot %d", slot))
  end
  local d = format(slot_dump_format[12], a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11)
  write(fhandle, "S ", slot, " D ", d)
end

function dump_tdc_slot(fhandle, F, slot)
  local q0, a0 = CFSA(F, slot, 0, 0)
  if q0 == 1 then
    local q1, a1 = CFSA(F, slot, 1, 0)
    local q2, a2 = CFSA(F, slot, 2, 0)
    local q3, a3 = CFSA(F, slot, 3, 0)
    local q4, a4 = CFSA(F, slot, 4, 0)
    local q5, a5 = CFSA(F, slot, 5, 0)
    local q6, a6 = CFSA(F, slot, 6, 0)
    local q7, a7 = CFSA(F, slot, 7, 0)
    if q1 ~= 1 or q2 ~= 1 or q3 ~= 1 or q4 ~= 1 or q5 ~= 1 or q6 ~= 1 or q7 ~= 1 then
      error(format("In dump_tdc_slot: failed to read slot %d", slot))
    end
    tdc_dump_d = format(slot_dump_format[8], a0, a1, a2, a3, a4, a5, a6, a7)
  else
    -- LeCroy 2228A Q and LAM suppression kicked in
    tdc_dump_d = "-1 -1 -1 -1 -1 -1 -1 -1"
  end
  write(fhandle, "S ", slot, " D ", tdc_dump_d)
end

function clear_camac_modules()
  nim_resetcev(1)
  for _, slot in config_adc_slots do
    CFSA(9, slot, 0, 0)
  end
  for _, slot in config_tdc_slots do
    CFSA(9, slot, 0, 0)
  end
end

function enable_data_taking(enable)
  if enable ~= 0 then
     nim_cack(1)
  end
end

function run_daq(fhandle, run_num, maxev)
  -- Enable LAM on the slot with the module used for the trigger
  CFSA(26, config_lam_slot, 0, 0)
  write(fhandle, "Begin run ", run_num, " date ", date(), "\n")
  for event_number=1,maxev do
    enable_data_taking(true)
    CCLWT(config_lam_slot)
    enable_data_taking(false)
    -- We need event time stamps... Counter?
    write(fhandle, "Event ", event_number-1, "\n")
    for _, slot in config_adc_slots do
      dump_adc_slot(fhandle, 2, slot)
    end
    for _, slot in config_tdc_slots do
      dump_tdc_slot(fhandle, 2, slot)
    end
    dump_hw_counter(fhandle)
    dump_deadtime(fhandle)
  end
  write(fhandle, "End run ", run_num, " date ", date(), " events ", maxev, "\n")
end

-- If necessary, emulate CAEN CAMAC interface functions
if emulation_mode ~= 0 then
  dofile("camac_emulation.lua")
end

-- Initialize some global variables.
-- Note that Lua v4.0 did not have boolean types.
true = 1
false = 0
slot_dump_format = {}
slot_dump_format[8]  = "%d %d %d %d %d %d %d %d\n"
slot_dump_format[12] = "%d %d %d %d %d %d %d %d %d %d %d %d\n"

-- Come up with the name for the output file
if emulation_mode ~= 0 then
  outputfile = format("run_%d.txt", run_number)
else
  outputfile = format("/nfs/Runs/run_%d.txt", run_number)
end

-- Initialize the crate and run the data acquisition sequence
CCCZ()
enable_data_taking(false)
CCCC()
assert(dostring(daq_configuration_chunk), "DAQ configuration failure")
clear_camac_modules()
handle = openfile(outputfile, "w")
dump_run_configuration(handle, run_number)
run_daq(handle, run_number, max_events)
closefile(handle)
