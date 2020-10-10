"""
Python interface to the CAEN C111C CAMAC Crate Controller. The following
communication methods are provided (in alphabetical order):

  ackIRQ       -- Acknowledge interrupt message (needed if the message
                  was not already acknowledged by "waitForIRQ"). Declared
                  in CrateHandle.hh.

  BLKBUFFS     -- Set the buffer size for block transfers between the
                  CAMAC crate and the computer. Declared in CrateHandle.hh.

  CBINR        -- Enable/disable command acknowledgements for the binary
                  communication socket. Declared in CrateHandle.hh. Don't
                  mess with this unless you really know what you are doing.

  CCCC         -- Issue CAMAC clear command. Declared in CrateHandle.hh.

  CCCI         -- Set/clear CAMAC Inhibit. Declared in CrateHandle.hh.

  CCCZ         -- Initialize the CAMAC crate. Declared in CrateHandle.hh.

  CCLWT        -- Wait for LAM. Declared in CrateHandle.hh.

  CFSA         -- Execute a 24-bit CAMAC command. Declared in CrateHandle.hh.

  CLMR         -- Return the current status of all LAM lines. Declared in
                  CrateHandle.hh.

  CMDR         -- Receive one line of a controller response to a command.
                  Declared in CrateHandle.hh.

  CMDS         -- Send an ASCII command. Declared in CrateHandle.hh.
                  Note that you will normally have to receive the
                  controller response after this.

  CMDSR        -- Send an ASCII command and receive a one-line response.
                  Declared in CrateHandle.hh. You should normally use
                  "stdCMDSR" method instead.

  CRTOUT       -- Set timeout for all communication sockets. Declared in
                  CrateHandle.hh.

  CSCAN        -- Scan the crate and determine which slots are filled.
                  Declared in CrateHandle.hh.

  CSSA         -- Execute a 16-bit CAMAC command. Declared in CrateHandle.hh.

  CTCI         -- Test the status of the CAMAC crate Inhibit line. Declared
                  in CrateHandle.hh.

  CTLM         -- Test for LAM. Declared in CrateHandle.hh.

  CTSTAT       -- Returns Q and X values from the last access on the CAMAC
                  bus. Declared in CrateHandle.hh.

  getBLKBUFFS  -- Get the current block transfer buffer size. Declared in
                  CrateHandle.hh.

  getCrateId   -- Get the internal crate identifier (for use with the C
                  interface). Declared in CrateHandle.hh. Note that you
                  will probably never want to use this method for normal
                  operation.

  getCRTOUT    -- Get current timeout (for all communication sockets).
                  Declared in CrateHandle.hh.

  LACK         -- Acknowledge LAM. Declared in CrateHandle.hh.

  mlCMDR       -- Receive a multiline ASCII response. Intended for use with
                  "CMDS". Defined in this file. Note that you will probably
                  never want to use this method for normal operation.

  NOSOS        -- Set the NIM output on the controller front panel. Declared
                  in CrateHandle.hh.

  receiveBlock -- Transfer an array of integers from the CAMAC crate. Defined
                  in CrateHandle.i. Returns a numpy array.

  sendBlock    -- Transfer a numpy array of integers to some module in the
                  CAMAC crate. Declared in CrateHandle.hh, wrapped by SWIG
                  with the usual mapping of pointer and size into a numpy
                  array.

  read24Scan   -- Read a number of consequtive channels from a particular
                  slot. Defined in CrateHandle.i. Returns a numpy array.

  read24ScanScaler  -- Same as read24Scan, but checks for Q = 0 for valid data
                       rather than 1. Defined in CrateHandle.i. Returns a numpy array.

  read24UntilQ0 -- Read a particular slot and subaddress until Q = 0 is
                   returned. Defined in CrateHandle.i. Returns a numpy array.

  read16UntilQ0Q0 -- Read a particular slot and subaddress until Q = 0 is
                     returned twice in a row. Defined in CrateHandle.i.
                     Returns a numpy array.

  stdCMDR      -- Receive the standard response to an ASCII command, in case
                  single-line response is expected. Intended for use with
                  "CMDS". Defined in this file.

  stdCMDSR     -- Standard ASCII command send-recieve operation, in case
                  single-line response is expected. Defined in this file.
                  This should be your normal way of communicating with the
                  crate controller over the ASCII socket. Defined in this file.

  waitForIRQ   -- Wait for a message on the interrupt socket. Declared in
                  CrateHandle.hh.
"""

__author__ = "Igor Volobouev (i.volobouev@ttu.edu)"
__version__ = "0.1"
__date__ = "June 22 2017"

from caencamac import *


class CAEN_C111C(CrateHandle):
    def __init__(self, address=None):
        if address is None:
            CrateHandle.__init__(self)
        else:
            CrateHandle.__init__(self, address)

    def _process_ascii(self, readback):
        words = readback.split()
        status = int(words[0])
        if status == 0:
            return readback[2:]
        else:
            raise RuntimeError("Readback status is %d" % status)

    def stdCMDR(self, maxResponseSize=None):
        if maxResponseSize is None:
            readback = CrateHandle.CMDR(self)
        else:
            readback = CrateHandle.CMDR(self, maxResponseSize)
        return self._process_ascii(readback)

    def stdCMDSR(self, cmd, maxResponseSize=None):
        if maxResponseSize is None:
            readback = CrateHandle.CMDSR(self, cmd)
        else:
            readback = CrateHandle.CMDSR(self, cmd, maxResponseSize)
        return self._process_ascii(readback)

    def mlCMDR(self):
        s = CrateHandle.CMDR(self)
        timeout = CrateHandle.getCRTOUT(self)
        CrateHandle.CRTOUT(self, 1)
        try:
            while (True):
                nextline = CrateHandle.CMDR(self)
                s += "\n"
                s += nextline
        except RuntimeError:
            pass
        finally:
            CrateHandle.CRTOUT(self, timeout)
        return s
