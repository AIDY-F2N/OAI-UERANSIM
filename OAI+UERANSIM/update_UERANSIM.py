import os

namespace='oai'
ip_adress="10.244.0.1"
nb_pods=10
network="cni0"

retour=os.popen("kubectl get pods -n "+namespace).read() 
Running=0
if (retour.count('Running')==nb_pods):
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
    print("UERANSIM files configuration updated")
else:
    print("UERANSIM files configuration not updated")