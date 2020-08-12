slot_dump_format = {}
slot_dump_format[10] = "%d %d %d %d %d %d %d %d %d %d\n"
slot_dump_format[12] = "%d %d %d %d %d %d %d %d %d %d %d %d\n"

function read_camac_slot(F, slot, nchannels, i)
  i = i or 0
  if i < nchannels then
    local Q, data = CFSA(F, slot, i, 0)
    if Q ~= 1 then
      error(format("In read_slot: failed to read slot %d ch %d", slot, i))
    end
    return data, read_camac_slot(F, slot, nchannels, i+1)
  end
end

function dump_camac_slot(fhandle, F, slot, nchannels)
  local d = format(slot_dump_format[nchannels], read_camac_slot(F, slot, nchannels))
  write(fhandle, "S ", slot, " D ", d)
end

slot = 17
outputfile = "/nfs/junk.log"
handle = openfile(outputfile, "w")
dump_camac_slot(handle, 2, slot, 12)
closefile(handle)
