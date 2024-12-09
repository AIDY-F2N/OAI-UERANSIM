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
nb_pods=10
number_of_UEs=int(sys.argv[1])
seconds=int(sys.argv[2])
retour=os.popen("kubectl get pods -n "+namespace).read() 
Running=0
if (retour.count('Running')==nb_pods):
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
      filesim = open('text_files/sim.txt', 'w+')
      filesim.write(json.dumps(sim))
      filesim.close()
      start=time.time()
      end=time.time()
      slice["processus"][i]=subprocess.Popen(['python3', 'UE.py', str(i)])
      time.sleep(1)
      while ((end-start)<20 and sim["a"]=="0"):
          try:
              filesim = open('text_files/sim.txt', 'r')
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
          print('exec ./UERANSIM/build/nr-binder '+ str(slice["ip"][i]) + ' iperf3 -c '+ str(ip2)+ ' -p '+str(port)+' -i 1 -t '+str(1)+" 2>&1 | tee text_files/iperf3.txt")
          slice["iperf_processus"][i]=subprocess.Popen('exec ./UERANSIM/build/nr-binder '+ str(slice["ip"][i]) + ' iperf3 -c '+ str(ip2)+ ' -p '+str(port)+' -i 1 -t '+str(1)+" 2>&1 | tee text_files/iperf3.txt",shell = True, stdout = subprocess.PIPE, encoding = 'ascii')
          output = slice["iperf_processus"][i].communicate()[0]
          with open('text_files/iperf3.txt', 'r') as f:
              last_line = f.readlines()[-1]
          while ("refused" in last_line):
              print("killll")
              os.system("sudo pkill -9 -P " + str(slice["iperf_processus"][i].pid))#kill ping process
              port=port+1
              slice["iperf_processus"][i]=subprocess.Popen('exec ./UERANSIM/build/nr-binder '+ str(slice["ip"][i]) + ' iperf3 -c '+ str(ip2)+ ' -p '+str(port)+' -i 1 -t '+str(1)+" 2>&1 | tee text_files/iperf3.txt",shell = True, stdout = subprocess.PIPE, encoding = 'ascii')
              output = slice["iperf_processus"][i].communicate()[0]
              os.system("sudo pkill -9 -P " + str(slice["iperf_processus"][i].pid))#kill ping process
              with open('text_files/iperf3.txt', 'r') as f:
                  last_line = f.readlines()[-1]
          slice["iperf_processus"][i]=subprocess.Popen('exec ./UERANSIM/build/nr-binder '+ str(slice["ip"][i]) + ' iperf3 -c '+ str(ip2)+ ' -p '+str(port)+' -i 1 -t '+str(seconds),shell = True, stdout = subprocess.PIPE, encoding = 'ascii')
      i=i+1           
  time.sleep(seconds+number_of_UEs)
  for i in range(0,number_of_UEs):
      os.system("sudo pkill -9 -P " + str(slice["child"][i]))#kill ue process
      slice["processus"][i].kill()
      os.system("sudo pkill -9 -P " + str(slice["iperf_processus"][i].pid))#kill ping process

file1 = open("text_files/go.txt","w")
file1.write("1")
file1.close()