outputfile = "/nfs/hello2.log"
handle = openfile(outputfile, "w")
write(handle, "Hello2, World!\n")
closefile(handle)
