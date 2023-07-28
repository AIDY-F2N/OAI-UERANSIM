import os

namespace='oai'
ip_adress="10.244.0.1"
nb_pods=8
network="cni0"

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
        print("Core is ok")    
        #get amf ip adress
        amf_ip=os.popen("kubectl get pod -n "+namespace+" $(kubectl get pods --namespace "+namespace+" -l "+"app.kubernetes.io/name=oai-amf"+" -o jsonpath="+"{.items[0].metadata.name}"+") --template '{{.status.podIP}}'").read()
        os.system("sudo ifconfig "+network+":"+str(1)+" "+str(ip_adress)+" up")
        #update OAI-gnb file for UERANSIM 
        with open(r'OAI-gnb.yaml', 'r') as file:
            data = file.read()
            file.close()
        data = data.replace("xxx", str(ip_adress))
        data = data.replace("yyy", str(amf_ip))
        with open(r'UERANSIM/build/OAI-gnb.yaml', 'w') as file:
            file.write(data)
            file.close()
        #update OAI-ue file for UERANSIM 
        with open(r'OAI-ue.yaml', 'r') as file:
            data = file.read()
            file.close()
        data = data.replace("xxx", str(ip_adress))
        data = data.replace("yyy", namespace)
        with open(r'UERANSIM/build/OAI-ue.yaml', 'w') as file:
            file.write(data)
            file.close()