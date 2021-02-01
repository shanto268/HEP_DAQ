# useage: source compile.sh runNum
p3 sas_analysis.py junk ../CrateCode/run$1.bin
p3 crateAnalysisPlotter.py processed_data/events_data_frame_$1.h5 True
