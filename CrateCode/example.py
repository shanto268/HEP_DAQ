# Examples for copy-pasting into python3 session

# Create an instance of the controller communicator
from CAEN_C111C import CAEN_C111C
h = CAEN_C111C()

# Perform a crate initialize operation. This is a binary command.
h.CCCZ()

# Perform a crate clear operation. This is a binary command.
h.CCCC()

# Figure out which slots are filled with modules. This is a binary command.
slotmask = h.CSCAN()
for i in range(24):
    if slotmask & (1 << i):
        print("Slot %d is filled" % (i + 1))

# Talk to some module (in this case, LeCroy 2249W ADC) using a 24-bit
# CAMAC command. The order of the arguments is F, N, A, data. This is
# a binary command.
result = h.CFSA(0, 17, 3, 0)

# Examine the result. You can also just print it.
result.Q()
result.X()
result.datum()
print(result)

# Simple ASCII commands, for which a single line of response is expected,
# are given with the "stdCMDSR" function. The command "vn24", for example,
# returns the voltage provided by the +24V power supply. For the complete
# list of such commands, see Section 9 ("ASCII Commands reference") in the
# C111C User Manual. "stdCMDSR" stands for "standard command send-receive".
h.stdCMDSR("vn24")

# Note that, even if no meaningful result is expected, in most cases the
# controller still sends the status. You can still use "stdCMDSR" for
# such commands. It will process the status, raising exceptions as
# necessary, and will return an empty string.
h.stdCMDSR("jn_led 3 1")

# It is possible to just send the command and receive the response later.
# This is useful in case either no response at all is expected or the
# response is multiline. You will need to call "CMDR()" function as many
# times as the number of lines in the response. This can be tricky if you
# don't know how many lines to expect -- if you call "CMDR()" once to many,
# it may block, potentially waiting for response forever. If you know that
# at least one or more lines of response is coming but do not know the
# exact count, use the "mlCMDR()" method instead.
h.CMDS("help")
response = h.mlCMDR()
print(response)

# Waiting for "interrupt". The argument "True" to "waitForIRQ" method tells
# the code that the interrupt should be acknowledged immediately. You can
# also acknowledge it later with the "ackIRQ()" method. In this case, give
# the argument "False" or no argument at all. The following line will wait
# for interrupt forever. You can test it by pressing the button "Default"
# on the controller.
interrupt = h.waitForIRQ(True)
print(interrupt)

# Turn on NIM output 1 on the crate controller
h.NOSOS(1, True)

# Tuning the delay of the "COMBO" I/O
lam_slot = 17
h.CFSA(26, lam_slot, 0, 0)
h.stdCMDSR("nim_enablecombo 1 0")
while True:
    h.CCLWT(lam_slot)
    h.CFSA(2, lam_slot, 11, 0)
    h.stdCMDSR("nim_cack 1")
