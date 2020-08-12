#!/usr/bin/env python3

import npstat as ns
from HistoMaker2D import HistoMaker2D

xmin = 0.0
xmax = 2.0
ymin = 0.0
ymax = 4.0
nxbins = 50
nybins = 100

npoints = 10000
u = ns.Uniform1D(xmin, xmax-xmin)
g = ns.Gauss1D(0.0, 0.3)

rng = ns.MersenneTwister()
xpoints = u.generate(rng, npoints)
yshifts = g.generate(rng, npoints)
ypoints = [y + x**2 for x, y in zip(xpoints, yshifts)]

h2 = HistoMaker2D("dummy2", "Example Distro",
                  "X", nxbins, xmin, xmax, lambda x: x[0],
                  "Y", nybins, ymin, ymax, lambda x: x[1])
h3 = HistoMaker2D("dummy3", "Example Distro",
                  "X", nxbins, xmin, xmax, lambda x: x[0],
                  "Y", nybins, ymin, ymax, lambda x: x[1])

for x, y in zip(xpoints, ypoints):
    h2.processEvent(0, 0, [x, y])
    h3.processEvent(0, 0, [y, x])
h2.endJob()
h3.endJob()
