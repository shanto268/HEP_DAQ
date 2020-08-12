import unittest
import random
from LC3377 import *

class TestLC3377(unittest.TestCase):
    def test_LC3377Header(self):
        for cycle in range(100):
            id = int(random.random()*256)
            reso = int(random.random()*4)
            edges = int(random.random()*2)
            eventNumber = int(random.random()*8)
            word = (1 << 15) + (eventNumber << 11) + (edges << 10) + (reso << 8) + id
            h = LC3377Header(word)
            self.assertEqual(id, h.id)
            self.assertEqual(reso, h.resolution)
            self.assertEqual(bool(edges), h.bothEdges)
            self.assertEqual(eventNumber, h.eventNumber)

    def test_LC3377Datum(self):
        for cycle in range(100):
            usingBothEdges = random.random() > 0.5
            if usingBothEdges:
                tdc = int(random.random()*512)
                fEdge = int(random.random()*2)
            else:
                tdc = int(random.random()*1024)
                fEdge = 0
            ch = int(random.random()*32)
            word = (ch << 10) + (fEdge << 9) + tdc
            d = LC3377Datum(word, usingBothEdges)
            self.assertEqual(tdc, d.tdc)
            self.assertEqual(bool(fEdge), d.fallingEdge)
            self.assertEqual(ch, d.channel)

    def test_LC3377Readout(self):
        for cycle in range(100):
            data = []
            idlist = []
            resolist = []
            edgeslist = []
            tdcvalues = dict()
            tdcedges = dict()

            nEvents = int(random.random()*32)
            for ev in range(nEvents):
                id = int(random.random()*256)
                idlist.append(id)
                reso = int(random.random()*4)
                resolist.append(reso)
                edges = int(random.random()*2)
                edgeslist.append(edges)
                evnum = ev // 8
                word = (1 << 15) + (evnum << 11) + (edges << 10) + (reso << 8) + id
                data.append(word)
                for ch in range(32):
                    if edges:
                        tdc = int(random.random()*512)
                        fEdge = int(random.random()*2)
                    else:
                        tdc = int(random.random()*1024)
                        fEdge = 0
                    word = (ch << 10) + (fEdge << 9) + tdc
                    data.append(word)
                    tdcvalues[(ev, ch)] = tdc
                    tdcedges[(ev, ch)] = fEdge
            rd = LC3377Readout(data)
            self.assertEqual(nEvents, len(rd.events))
            for cnt, ev in enumerate(rd.events):
                self.assertEqual(cnt // 8, ev.header.eventNumber)
            for reso, ev in zip(resolist, rd.events):
                self.assertEqual(reso, ev.header.resolution)
            for id, ev in zip(idlist, rd.events):
                self.assertEqual(id, ev.header.id)
            for edge, ev in zip(edgeslist, rd.events):
                self.assertEqual(edge, ev.header.bothEdges)
            tdcread = dict()
            edgeread = dict()
            for cnt, ev in enumerate(rd.events):
                for d in ev.data:
                    tdcread[(cnt, d.channel)] = d.tdc
                    edgeread[(cnt, d.channel)] = d.fallingEdge
            self.assertEqual(tdcvalues, tdcread)
            self.assertEqual(tdcedges, edgeread)

suite = unittest.TestLoader().loadTestsFromTestCase(TestLC3377)
unittest.TextTestRunner(verbosity=2).run(suite)
