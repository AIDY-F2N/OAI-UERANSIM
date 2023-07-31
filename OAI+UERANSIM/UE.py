import sys
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

def ue_UERANSIM (command):
  """Start a subprocess and read its stdout in a non blocking way""" 
  print(command)  
  child =subprocess.Popen(command, shell = True, stdout = subprocess.PIPE, encoding = 'ascii')
  pipe =Pipe (child .stdout )
  nUE=0
  it=0
  while nUE<1:
    try :
      line =pipe .readline (1.45 )
      print (" %s"%(line [:-1 ]))
      if ("uesimtun" in line):
        nUE=nUE+1
        ue=line.split("[")[5].split("]")[0].split(",")
        print(ue)
        uesimtun=line.split("[")[5].split("]")[0].split(",")[0].split("uesimtun")
        ip=line.split("[")[5].split("]")[0].split(",")[1]
        print("**** uesimtun{}".format(uesimtun[1]))
    except TimeoutError :
      print ("[%d] readline timed out" )
  sim = {}
  sim["a"]="1"
  sim["uesimtun"]=uesimtun[1]
  sim["ip"]=ip
  sim["child"]=child.pid
  filesim = open('text_files/sim.txt', 'w+')
  filesim.write(json.dumps(sim))
  filesim.close()
  del(sim)
  del(pipe)

print("ok")
if (int(sys.argv[1])<10):
  command="exec sudo ./UERANSIM/build/nr-ue -c UERANSIM/build/OAI-ue.yaml -i imsi-00101000000010"+sys.argv[1]
else:
  command="exec sudo ./UERANSIM/build/nr-ue -c UERANSIM/build/OAI-ue.yaml -i imsi-0010100000001"+sys.argv[1]

try:
    ue_UERANSIM (command)
except Exception as e: 
    print("**** error ****")
    print(e)
    print("**** error ****")