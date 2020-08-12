"""                                                                             
This example config file tells which ADC channels are connected
"""

def configureDAQ(h):
    config = dict()
    config["connected_channels"] = ((17, 0), (17, 1), (17, 2), (17, 3), (17, 4),
                                    (17, 5), (17, 6), (17, 7), (17, 8), (17, 9),
                                    (17, 10), (17, 11),
                                    (10, 0), (10, 1), (10, 2), (10, 3),
                                    (10, 4), (10, 5), (10, 6), (10, 7))
    return config
