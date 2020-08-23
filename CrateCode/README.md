# Description Of Files

In order to understand how data acquisition works, you should read the
CAEN C111C CAMAC Crate Controller Technical Information Manual, file
name "C111C_user_manual_rev10.pdf". Functional descriptions of various
CAMAC modules are available on the web.

This directory contains the following files:

| File Name  | Description|
| ------------- | ------------- |
| ADCHisto.py          |    Classes which plot ADC and TDC data on-the-fly.

| CAEN_C111C.py        |    Additional high-level methods for operating the
|                      |    CAEN C111C CAMAC crate controller. This file
|                      |    also includes an alphabetical list of all
|                      |    communication methods supported by the software.

| CrateHandle.hh       |    C++ interface to the C111C C library provided
| CrateHandle.cc       |    by CAEN. The main advantage of the C++ interface
|                      |    is that it properly handles all communication
|                      |    errors, input parameter errors, etc., by throwing
|                      |    standard exceptions.


| crate_lib_defs.h     |    C language interface for communicating with
| crate_lib.h          |    the CAEN C111C CAMAC crate controller. This is
| crate_lib.c          |    a slightly modified and extended version of the
|                      |    C111C C library provided by CAEN.


| example.py           |    A few example commands illustrating how to
|                      |    communicate with the CAEN C111C CAMAC crate
|                      |    controller.


| LC3377.py            |    Several classes for unpacking FIFO data received
|                      |    from LeCroy 3377 TDC modules.


| LC3377_test.py       |    Test code for "LC3377.py". Run with
|                      |    "python3 LC3377_test.py".


| Makefile             |    Instructions for the "make" utility: how
|                      |    to compile the "caencamac" Python module.
|                      |    Normally, you only need to type "make" in
|                      |    order to build this module, and "make clean"
|                      |    in order to clean everything up.


| MultipleUpdater.py   |    A utility class for running multiple classes
|                      |    that dynamically update plots, etc. Works with
|                      |    "runCAMAC".


| runCAMAC.py          |    Illustrates running C111C CAMAC crate controller
|                      |    and collecting ADC/TDC data.


| takeData.py          |    Command line parser for "runCAMAC".


| NumpyTypecode.hh     |    Helper functions for converting C++ array and
| vectorToNumpy.hh     |    std::vector array objects into numpy arrays.


| Various files with   |    SWIG definitions for building Python interface
| the .i extension     |    to the functionality provided by the C++ code.
|                      |    All C++ exceptions are automatically translated
|                      |    into Python exceptions. Note that the module is
|                      |    built for Python 3 and will not work with Python 2.


# Principles of Operation

The CAEN C111C Crate Controller runs a miniature version of Linux. It
communicates with the outside world over Ethernet. The software described
here establishes three TCP communication channels with the controller:

a) The ASCII control socket. This channel can be used for sending commands
   and receiving responses in plain text.

b) The binary control socket. This channel can be used for sending commands
   and receiving responses in a more efficient binary format. However, not
   all possible controller commands have binary versions.

c) The "interrupt handling" socket. This channel can be used to convert
   certain controller events (LAM requests, front panel triggers, front
   panel "Default" button presses) into messages that can be processed on
   the remote computer.

It is expected that the user will communicate with the controller
using Python code. The main communication class is called "CAEN_C111C".
A few simple communication examples are provided in the file "example.py".
You can look at them and simply copy-paste the code snippets into the
"python3" prompt.

The list of all ASCII commands is provided in Section 9 of the controller
Technical Information Manual. You can usually send them to the controller
and get the response with the "stdCMDSR" method of the CAEN_C111C class.
The binary commands are mapped into various methods of the CAEN_C111C class
(CCCC, CCLWT, CFSA, etc). The messages on the interrupt handling socket
should be handled with the CAEN_C111C methods "waitForIRQ" and "ackIRQ".


# Software Usage Examples

1) Rebuild everything:
   
   make clean
   make
   
2) Print basic usage instructions for certain executable scripts. By my
   convention, usage instructions are printed when such scripts are invoked
   without any command line arguments.
   
   takeData.py

3) Collect 1000 events (run #7) using additional DAQ configuration from
   file "Configs/connected_16_0_1.py" and save the collected data into file
   "run7.bin".

   takeData.py connected_17_0_1_2 1000 0 7 run7.bin

