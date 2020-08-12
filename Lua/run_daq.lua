run_number = 129
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
  config_tdc_slots = {10}
]]

function dump_run_configuration(fhandle, run_num)
  write(fhandle, "Begin DAQ config for run ", run_num, '\n')
  write(fhandle, format("%q\n", daq_configuration_chunk))
  write(fhandle, "End DAQ config for run ", run_num, '\n')
end

function read_adc_slot(F, slot)
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
    error(format("In read_adc_slot: failed to read slot %d", slot))
  end
  return {a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11}
end

function read_tdc_slot(F, slot)
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
      error(format("In read_tdc_slot: failed to read slot %d", slot))
    end
    return {a0, a1, a2, a3, a4, a5, a6, a7}
  else
    -- LeCroy 2228A Q and LAM suppression kicked in
    return tdc_nodata
  end
end

function unpack8(t)
  return t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8]
end

function unpack12(t)
  return t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9], t[10], t[11], t[12]
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
  enable_data_taking(true)

  -- Event loop
  for event_number=1,maxev do
    -- Wait for LAM
    CCLWT(config_lam_slot)
    enable_data_taking(false)

    -- Read out CAMAC modules.
    -- We need event time stamps... Counter?
    for _, slot in config_tdc_slots do
      slot_data[slot] = read_tdc_slot(camac_read_and_clear, slot)
    end

    for _, slot in config_adc_slots do
      slot_data[slot] = read_adc_slot(camac_read_and_clear, slot)
    end

    hwc = nim_getcev(1)
    deadtime = nim_getcdtc(1)
    enable_data_taking(true)

    -- Write out event contents
    write(fhandle, "Event ", event_number-1, "\n")
    for _, slot in config_tdc_slots do
      write(fhandle, "S ", slot, " D ", format(int_dump_format_8, unpack8(slot_data[slot])))
    end
    for _, slot in config_adc_slots do
      write(fhandle, "S ", slot, " D ", format(int_dump_format_12, unpack12(slot_data[slot])))
    end
    write(fhandle, "HWC ", hwc, '\n')
    write(fhandle, "DT ", deadtime, '\n')
  end

  enable_data_taking(false)
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
camac_read_and_clear = 2
slot_data = {}
tdc_nodata = {-1, -1, -1, -1, -1, -1, -1, -1}
int_dump_format_8 = "%d %d %d %d %d %d %d %d\n"
int_dump_format_12 = "%d %d %d %d %d %d %d %d %d %d %d %d\n"

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

-- Disable the trigger veto by the "busy" signal
nim_enablecombo(1, 1)
