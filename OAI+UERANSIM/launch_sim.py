import os
import time
import psutil
import subprocess

os.system("chmod +x UERANSIM/build/nr-binder")

for i in range (1,10):
    file1 = open("text_files/go.txt","w")
    file1.write("0")
    file1.close()
    try:
        os.system("sudo kill -9 $(ps -elf|pgrep nr-ue)")
    except:
        pass
    try:
        os.system("sudo kill -9 $(pgrep -f UE.py)")
    except:
        pass
    processus=subprocess.Popen(['python3', 'UEs_iperf3.py', str(i*5),str(300)])
    a="0"
    while a=="0":
        try:
            file1 = open("text_files/go.txt","r+")
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
    