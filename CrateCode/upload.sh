# usage: . upload.sh name_of_file_to_upload
scp $1 sshanto@quanah.hpcc.ttu.edu:/lustre/work/sshanto/proto1/CAMAC/CrateCode/data_sets
rm $1
