"""                                                                             
This example config file tells which ADC channels are connected
"""

def configureDAQ(h):
    config = dict()
    config["connected_channels"] = ((16, 0), (16, 1))
    return config
