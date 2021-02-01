# Usage: ./ana.sh run_number event_num

scp daq@10.188.32.133:/home/daq/CAMAC/CrateCode_sas/CrateCode/data_sets/run$1_$2.bin ../CrateCode
mv ../CrateCode/run$1_$2.bin ../CrateCode/run$1.bin
python3 sas_analysis.py junk ../CrateCode/run$1.bin
python3 crateAnalysisPlotter.py processed_data/events_data_frame_$1.h5 True
#open events_data_frame_$1.pdf
#open channel1.pdf


#scp -P14188 daq@4.tcp.ngrok.io:/home/daq/CAMAC/CrateCode_sas/CrateCode/data_sets/run$1_$2.bin ../CrateCode
#mv ../CrateCode/run$1_$2.bin ../CrateCode/run$1.bin
#python3 sas_analysis.py junk ../CrateCode/run$1.bin
#python3 crateAnalysisPlotter.py processed_data/events_data_frame_$1.h5 True
#open events_data_frame_$1.pdf
