"""
Class for parsing LeCroy 3377 TDC readouts. Simply create LC3377Readout instance
using module FIFO readout buffer as an argument.
"""

__author__="Igor Volobouev (i.volobouev@ttu.edu)"
__version__="0.1"
__date__ ="July 3 2020"

class LC3377Header:
    def __init__(self, header):
        if not (header & 32768):
            raise ValueError("Not a valid LeCroy 3377 header word")
        if header & 16384:
            raise ValueError("Expect single word readout")
        self.id = header & 255
        self.resolution = (header & 768) >> 8
        self.bothEdges = bool(header & 1024)
        self.eventNumber = (header & 14336) >> 11

    def __str__(self):
        if self.bothEdges:
            tag = 'BothEdges'
        else:
            tag = 'RisingEdge'
        return "ID %d Res %d %s EvN%%8 %d" % \
            (self.id, self.resolution, tag, self.eventNumber)


class LC3377Datum:
    def __init__(self, datum, usingBothEdges):
        if datum & 32768:
            raise ValueError("Not a valid LeCroy 3377 data word")
        if usingBothEdges:
            self.tdc = datum & 511
            self.fallingEdge = bool(datum & 512)
        else:
            self.tdc = datum & 1023
            self.fallingEdge = False
        self.channel = (datum & 31744) >> 10

    def __str__(self):
        if self.fallingEdge:
            label = "\\"
        else:
            label = "/"
        return "%s ch %d tdc %d" % (label, self.channel, self.tdc)


class LC3377Event:
    def __init__(self, header, data):
        self.header = header
        self.data = data

    def __str__(self):
        separator = ", "
        return str(self.header) + ' ' + "[" + separator.join([str(d) for d in self.data]) + "]"


class LC3377Readout:
    def __init__(self, arr):
        self.events = []
        header = None
        for word in arr:
            if word & 32768:
                # This is a header word
                if header is not None:
                    self.events.append(LC3377Event(header, data))
                header = LC3377Header(word)
                data = []
            else:
                # This is a data word
                if header is None:
                    raise ValueError("Not a valid LeCroy 3377 readout sequence")
                data.append(LC3377Datum(word, header.bothEdges))
        if header is not None:
            self.events.append(LC3377Event(header, data))

    def __str__(self):
        if len(self.events):
            separator = "}, {"
            return "{" + separator.join([str(ev) for ev in self.events]) + "}"
        else:
            return "empty"
