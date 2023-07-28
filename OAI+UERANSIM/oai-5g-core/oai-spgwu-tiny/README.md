# Helm Chart for OAI Serving and Packet Data Network Gateway User Plane (SPGW-U)

The helm-chart is tested on [Minikube](https://minikube.sigs.k8s.io/docs/) and [Red Hat Openshift](https://www.redhat.com/fr/technologies/cloud-computing/openshift) 4.10 and 4.12. There are no special resource requirements for SPGWU except `privileged` flag to be true. SPGWU needs to create tunnel interface for GTP and it creates NAT rules for packets to go towards internet from N6. 

**NOTE**: All the extra interfaces/multus interfaces created inside the pod are using `macvlan` mode. If your environment does not allow using `macvlan` then you need to change the multus definations. 

## Introduction

[OAI-SPGWU-TINY](https://github.com/OPENAIRINTERFACE/openair-spgwu-tiny) is the 4G CUPS S/PGWU. We modified it to work for 5G deployments with GTP-U extension header. 

OAI [Jenkins Platform](https://jenkins-oai.eurecom.fr/job/OAI-CN-SPGWU-TINY/) publishes every `develop` and `master` branch image of OAI-SPGWU-TINY on [docker-hub](https://hub.docker.com/r/oaisoftwarealliance/oai-spgwu-tiny) with tag `develop` and `latest` respectively. Apart from that you can find tags for every release `VX.X.X`. We only publish Ubuntu 18.04/20.04/22.04 images. We do not publish RedHat/UBI images. These images you have to build from the source code on your RedHat systems or Openshift Platform. You can follow this [tutorial](../../../openshift/README.md) for that. 

The helm chart of OAI-SPGWU-TINY creates multiples Kubernetes resources,

1. Service
2. Role Base Access Control (RBAC) (role and role bindings)
3. Deployment
4. Configmap (Contains the configuration file for SPGWU)
5. Service account
6. Network-attachment-definition (Optional only when multus is used)

The directory structure

```
├── Chart.yaml
├── README.md
├── templates
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── _helpers.tpl
│   ├── multus.yaml
│   ├── NOTES.txt
│   ├── rbac.yaml
│   ├── serviceaccount.yaml
│   └── service.yaml
└── values.yaml (Parent file contains all the configurable parameters)
```

## Parameters

[Values.yaml](./values.yaml) contains all the configurable parameters. Below table defines the configurable parameters. 


|Parameter                       |Allowed Values                 |Remark                               |
|--------------------------------|-------------------------------|-------------------------------------|
|kubernetesType                  |Vanilla/Openshift              |Vanilla Kubernetes or Openshift      |
|nfimage.repository              |Image Name                     |                                     |
|nfimage.version                 |Image tag                      |                                     |
|nfimage.pullPolicy              |IfNotPresent or Never or Always|                                     |
|imagePullSecrets.name           |String                         |Good to use for docker hub           |
|serviceAccount.create           |true/false                     |                                     |
|serviceAccount.annotations      |String                         |                                     |
|serviceAccount.name             |String                         |                                     |
|podSecurityContext.runAsUser    |Integer (0,65534)              |                                     |
|podSecurityContext.runAsGroup   |Integer (0,65534)              |                                     |
|multus.n3Interface.create       |true/false                     |                                     |
|multus.n3Interface.Ipadd        |Ip-Address                     |                                     |
|multus.n3Interface.Netmask      |Netmask                        |                                     |
|multus.n3Interface.Gateway      |Ip-Address                     |                                     |
|multus.n3Interface.routes       |Json                           |Routes if you want to add in your pod|
|multus.n3Interface.hostInterface|host interface                 |Host interface on which pod will run |
|multus.n4Interface.create       |true/false                     |                                     |
|multus.n4Interface.Ipadd        |Ip-Address                     |                                     |
|multus.n4Interface.Netmask      |Netmask                        |                                     |
|multus.n4Interface.Gateway      |Ip-Address                     |This interface is used to communicate with NRF |
|multus.n4Interface.routes       |Json                           |Routes if you want to add in your pod|
|multus.n4Interface.hostInterface|host interface                 |Host interface on which pod will run |
|multus.n6Interface.create       |true/false                     |                                     |
|multus.n6Interface.Ipadd        |Ip-Address                     |                                     |
|multus.n6Interface.Netmask      |Netmask                        |                                     |
|multus.n6Interface.Gateway      |Ip-Address                     |                                     |
|multus.n6Interface.routes       |Json                           |Routes if you want to add in your pod|
|multus.n6Interface.hostInterface|host interface                 |Host interface on which pod will run |
|multus.defaultGateway           |Ip-Address                     |Default route inside pod             |


### Configuration parameter

All the parameters in `config` block of values.yaml are explained with a comment.

## Advanced Debugging Parameters

|Parameter                        |Allowed Values                 |Remark                                        |
|---------------------------------|-------------------------------|----------------------------------------------|
|start.spgwu                      |true/false                     |If true spgwu container will go in sleep mode   |
|start.tcpdump                    |true/false                     |If true tcpdump container will go in sleepmode|
|includeTcpDumpContainer          |true/false                     |If false no tcpdump container will be there   |
|tcpdumpimage.repository          |Image Name                     |                                              |
|tcpdumpimage.version             |Image tag                      |                                              |
|tcpdumpimage.pullPolicy          |IfNotPresent or Never or Always|                                              |
|persistent.sharedvolume          |true/false                     |Save the pcaps in a shared volume with NRF    |
|resources.define                 |true/false                     |                                              |
|resources.limits.tcpdump.cpu     |string                         |Unit m for milicpu or cpu                     |
|resources.limits.tcpdump.memory  |string                         |Unit Mi/Gi/MB/GB                              |
|resources.limits.nf.cpu          |string                         |Unit m for milicpu or cpu                     |
|resources.limits.nf.memory       |string                         |Unit Mi/Gi/MB/GB                              |
|resources.requests.tcpdump.cpu   |string                         |Unit m for milicpu or cpu                     |
|resources.requests.tcpdump.memory|string                         |Unit Mi/Gi/MB/GB                              |
|resources.requests.nf.cpu        |string                         |Unit m for milicpu or cpu                     |
|resources.requests.nf.memory     |string                         |Unit Mi/Gi/MB/GB                              |
|readinessProbe                   |true/false                     |default true                                  |
|livenessProbe                    |true/false                     |default false                                 |
|terminationGracePeriodSeconds    |5                              |In seconds (default 5)                        |
|nodeSelector                     |Node label                     |                                              |
|nodeName                         |Node Name                      |                                              |

## Installation

Better to use the parent charts from:

1. [oai-5g-basic](../oai-5g-basic/README.md) for basic deployment of OAI-5G Core
2. [oai-5g-mini](../oai-5g-mini/README.md) for mini deployment (AMF, SMF, NRF, UPF) of OAI-5G Core. In this type of deployment AMF plays the role of AUSF and UDR
3. [oai-5g-slicing](../oai-5g-slicing/README.md) for basic deployment with NSSF extra 

## Note

1. If you are using multus then make sure it is properly configured and if you don't have a gateway for your multus interface then avoid using gateway and defaultGateway parameter. Either comment them or leave them empty. Wrong gateway configuration can create issues with pod networking and pod will not be able to resolve service names.
2. If you are using tcpdump container to take pcaps automatically (`start.tcpdump` is true) you can enable `persistent.sharedvolume` and [presistent volume](./oai-nrf/values.yaml) in NRF. To store the pcaps of all the NFs in one location. It is to ease the automated collection of pcaps.