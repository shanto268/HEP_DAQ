from paramiko import SSHClient
import time


def analyzeOnQuanah(fileName):
    host = "quanah.hpcc.ttu.edu"
    user = "sshanto"
    client = SSHClient()
    client.load_system_host_keys()
    client.connect(host, username=user)
    path2data = "/lustre/work/sshanto/proto1/CAMAC/CrateCode/data_sets/"
    path2file = "/home/sshanto/proto1b/CAMAC/CrateAnalysis/"
    command1 = "cd {}".format(path2file)
    command2 = "python3 quanah_analysis.py junk {}{}".format(
        path2data, fileName)
    command = command1 + ";" + command2
    stdin, stdout, stderr = client.exec_command(command)
    #  print("stderr: ", stderr.readlines())
    for i in stdout.readlines():
        print(i)
    time.sleep(5)
