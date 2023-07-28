import os
import sys
import time
import subprocess 
from queue import Queue ,Empty 
from threading import Thread 
import json
class TimeoutError (Exception ):
  pass 

class Pipe (object ):
  """A wrapper around a pipe opened for reading"""
  def __init__ (o ,pipe ):
    o .pipe =pipe 
    o .queue =Queue ()
    o .thread =Thread (target =o ._loop )
    o .thread .start ()
  def readline (o ,timeout =None ):
    "A non blocking readline function with a timeout"
    try :
      return o .queue .get (True ,timeout )
    except Empty :
      raise TimeoutError 
  def _loop (o ):
    try :
      while True :
        line =o .pipe .readline ()
        o .queue .put (line )
    except (ValueError ,IOError ):# pipe was closed
      pass 
  def close (o ):
    o .pipe .close ()
    o .thread .join ()

namespace='oai'
nb_pods=8
number_of_UEs=int(sys.argv[1])
seconds=int(sys.argv[2])
retour=os.popen("kubectl get pods -n "+namespace).read() 
Running=0
if (retour.count('Running')==nb_pods):
    Running=1
    SMF_POD_NAME=os.popen("kubectl get pods --namespace "+namespace+" -l 'app.kubernetes.io/name=oai-smf' -o jsonpath='{.items[0].metadata.name}'").read()
    SPGWU_TINY_POD_NAME=os.popen("kubectl get pods --namespace "+namespace+" -l 'app.kubernetes.io/name=oai-spgwu-tiny' -o jsonpath='{.items[0].metadata.name}'").read()
    ok1=0
    ok2=0
    it=0
    while((ok1==0 or ok2==0)and it<600):
        ok1=int(os.popen("kubectl logs -c spgwu "+SPGWU_TINY_POD_NAME +" -n "+namespace+" | grep 'Received SX HEARTBEAT REQUEST' | wc -l").read())
        ok2=int(os.popen("kubectl logs -c smf "+SMF_POD_NAME+" -n "+namespace+" | grep 'handle_receive(16 bytes)' | wc -l").read())
        it=it+1
    if (ok1>0 and ok2>0):
        sim={}
        slice={}
        slice["uesimtun_id"]={}
        slice["child"]={}
        slice["ok"]={}
        slice["ping"]={}
        slice["ip"]={}
        slice["processus"]={}
        slice["iperf_processus"]={}
        i=0
        while (i<number_of_UEs):  
            slice["ok"][i]=0
            sim["a"]="0"
            filesim = open('sim.txt', 'w+')
            filesim.write(json.dumps(sim))
            filesim.close()
            start=time.time()
            end=time.time()
            slice["processus"][i]=subprocess.Popen(['python3', 'UE.py', str(i)])
            time.sleep(1)
            while ((end-start)<20 and sim["a"]=="0"):
                try:
                    filesim = open('sim.txt', 'r')
                    sim = json.loads(filesim.read())
                    filesim.close()
                except Exception as e: 
                    print("**** error ****\n{}\n**** error ****".format(e))
                end=time.time()
            if (sim["a"]=="1"):
                slice["uesimtun_id"][i]=sim["uesimtun"]
                slice["child"][i]=sim["child"]
                slice["ok"][i]=1
                slice["ip"][i]=sim["ip"]
                i=i+1
            else:
                os.system("sudo pkill -9 -P " + str(sim["child"]))
                slice["processus"][i].kill()
        ip2=os.popen("kubectl get pod iperf3 --template '{{.status.podIP}}'").read()
        port=5200
        i=0
        while (i < number_of_UEs):
            if (slice["ok"][i]==1):  
                port=port+1
                #slice["iperf_processus"][i]=subprocess.Popen(['./UERANSIM/build/nr-binder', str(slice["ip"][i]) ,'iperf3 -c', str(ip2),"-p",str(port),"-i 1 -t",str(1)])
                slice["iperf_processus"][i]=subprocess.Popen('exec ./UERANSIM/build/nr-binder '+ str(slice["ip"][i]) + ' iperf3 -c '+ str(ip2)+ ' -p '+str(port)+' -i 1 -t '+str(1)+" 2>&1 | tee pp.txt",shell = True, stdout = subprocess.PIPE, encoding = 'ascii')
                output = slice["iperf_processus"][i].communicate()[0]
                with open('pp.txt', 'r') as f:
                    last_line = f.readlines()[-1]
                while ("refused" in last_line):
                    print("killll")
                    os.system("sudo pkill -9 -P " + str(slice["iperf_processus"][i].pid))#kill ping process
                    port=port+1
                    slice["iperf_processus"][i]=subprocess.Popen('exec ./UERANSIM/build/nr-binder '+ str(slice["ip"][i]) + ' iperf3 -c '+ str(ip2)+ ' -p '+str(port)+' -i 1 -t '+str(1)+" 2>&1 | tee pp.txt",shell = True, stdout = subprocess.PIPE, encoding = 'ascii')
                    output = slice["iperf_processus"][i].communicate()[0]
                    os.system("sudo pkill -9 -P " + str(slice["iperf_processus"][i].pid))#kill ping process
                    with open('pp.txt', 'r') as f:
                        last_line = f.readlines()[-1]
                slice["iperf_processus"][i]=subprocess.Popen('exec ./UERANSIM/build/nr-binder '+ str(slice["ip"][i]) + ' iperf3 -c '+ str(ip2)+ ' -p '+str(port)+' -i 1 -t '+str(seconds),shell = True, stdout = subprocess.PIPE, encoding = 'ascii')
                """output = slice["iperf_processus"][i].communicate()[0]
                if ("refused" in output):
                    print("killll")
                    os.system("sudo pkill -9 -P " + str(slice["iperf_processus"][i].pid))#kill ping process
                    ppp="sudo kill -9 $(sudo lsof -t -i:"+ str(port)+ ")"
                    try:
                        p = subprocess.Popen(ppp,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    except:
                        pass
                    p.kill()"""
                    #slice["iperf_processus"][i]=subprocess.Popen('exec ./UERANSIM/build/nr-binder '+ str(slice["ip"][i]) + ' iperf3 -c '+ str(ip2)+ ' -p '+str(port)+' -i 1 -t '+str(seconds),shell = True, stdout = subprocess.PIPE, encoding = 'ascii')
            i=i+1           
        time.sleep(seconds+60)
        for i in range(0,number_of_UEs):
            os.system("sudo pkill -9 -P " + str(slice["child"][i]))#kill ue process
            slice["processus"][i].kill()
            os.system("sudo pkill -9 -P " + str(slice["iperf_processus"][i].pid))#kill ping process

file1 = open("go.txt","w")
file1.write("1")
file1.close()


