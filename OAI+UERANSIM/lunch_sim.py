from ast import literal_eval
import os
import time
import psutil
import subprocess

os.system("chmod +x UERANSIM/build/nr-binder")

for i in range (1,10):
    file1 = open("go.txt","w")
    file1.write("0")
    file1.close()
    ppp="sudo kill -9 $(ps -elf|pgrep nr-ue)"
    try:
        p = subprocess.Popen(ppp, shell=True, stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
    except:
        pass
    p.kill()
    ppp="kubectl delete pod iperf3"
    try:
        os.system(ppp)
    except:
        pass
    time.sleep(45)
    ppp="kubectl run iperf3 --image=maitaba/iperf3:latest --restart=Never"
    try:
        os.system(ppp)
    except:
        pass
    time.sleep(30)
    processus=subprocess.Popen(['python3', 'UEs_iperf3.py', str(i*5),str(300)])
    a="0"
    while a=="0":
        try:
            file1 = open("go.txt","r+")
            a=file1.read()
            file1.close()
        except:
            a="0"
        if a=="1":
            processus.kill()
            print("process terminated a=='1'") 
        if round(psutil.virtual_memory()[4]/psutil.virtual_memory()[0]* 100, 2)<6:
            processus.kill()
            print(" memory problem")
            a="1"
        time.sleep(3)
    