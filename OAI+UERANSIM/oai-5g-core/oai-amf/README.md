# Helm Chart for OAI Access and Mobility Function (AMF)

The helm-chart is tested on [Minikube](https://minikube.sigs.k8s.io/docs/) and [Red Hat Openshift](https://www.redhat.com/fr/technologies/cloud-computing/openshift) 4.10 and 4.12. There are no special resource requirements for AMF. 

**NOTE**: All the extra interfaces/multus interfaces created inside the pod are using `macvlan` mode. If your environment does not allow using `macvlan` then you need to change the multus definations.

## Introduction

OAI-AMF follows 3GPP release 16, more information about the feature set can be found on [AMFs WiKi page](https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-amf/-/wikis/home). The source code be downloaded from [GitLab](https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-amf)

OAI [Jenkins Platform](https://jenkins-oai.eurecom.fr/job/OAI-CN5G-AMF/) publishes every `develop` and `master` branch image of OAI-AMF on [docker-hub](https://hub.docker.com/r/oaisoftwarealliance/oai-amf) with tag `develop` and `latest` respectively. Apart from that you can find tags for every release `VX.X.X`. We only publish Ubuntu 18.04/20.04/22.04 images. We do not publish RedHat/UBI images. These images you have to build from the source code on your RedHat systems or Openshift Platform. You can follow this [tutorial](../../../openshift/README.md) for that.

The helm chart of OAI-AMF creates multiples Kubernetes resources,

1. Service
2. Role Base Access Control (RBAC) (role and role bindings)
3. Deployment
4. Configmap (Contains the configuration file for AMF)
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


|Parameter                    |Allowed Values                 |Remark                                   |
|-----------------------------|-------------------------------|-----------------------------------------|
|kubernetesType               |Vanilla/Openshift              |Vanilla Kubernetes or Openshift          |
|nfimage.repository           |Image Name                     |                                         |
|nfimage.version              |Image tag                      |                                         |
|nfimage.pullPolicy           |IfNotPresent or Never or Always|                                         |
|imagePullSecrets.name        |String                         |Good to use for docker hub               |
|serviceAccount.create        |true/false                     |                                         |
|serviceAccount.annotations   |String                         |                                         |
|serviceAccount.name          |String                         |                                         |
|podSecurityContext.runAsUser |Integer (0,65534)              |Mandatory to use 0                       |
|podSecurityContext.runAsGroup|Integer (0,65534)              |Mandatory to use 0                       |
|multus.create                |true/false                     |default false                            |
|multus.n2IPadd               |IPV4                           |NA                                       |
|multus.n2Netmask             |Netmask                        |NA                                       |
|multus.defaultGateway        |IPV4                           |Default route inside container (optional)|
|multus.hostInterface         |HostInterface Name             |NA                                       |


### Configuration parameter

|Parameter                      |Mandatory/Optional          |Remark                                      |
|-------------------------------|----------------------------|--------------------------------------------|
|config.mcc                     |Mandatory                   |Mobile Country Code                         |
|config.mnc                     |Mandatory                   |Mobile Network Code                         |
|config.regionId                |Mandatory                   |Region ID                                   |
|config.amfSetId                |Mandatory                   |AMF SetID                                   |
|config.logLevel                |Optional                    |Default info, select info/debug/error       |
|config.tac                     |Hexadecimal/Mandatory       |Tracking aread code                         |
|config.sst0                    |Integer 1-256/Mandatory     |Slice Service Type 0                        |
|config.sd0                     |Integer/Hexadecimal/Optional|                                            |
|config.sst1                    |Optional                    |                                            |
|config.sd1                     |Optional                    |                                            |
|config.amfInterfaceNameForNGAP |eth0/net1/Mandatory         |net1 when multus is used                    |
|config.amfInterfaceNameForSBI  |eth0/Mandatory              |                                            |
|config.amfInterfaceSBIHTTPPort |Integer/Mandatory           |Standard port 80                            |
|config.amfInterfaceSBIHTTP2Port|Integer/Mandatory           |8080 if 80 is already inused                |
|config.smfFqdn                 |Mandatory                   |SMF ip-address/FQDN                         |
|config.nrfFqdn                 |Mandatory                   |NRF ip-address/FQDN                         |
|config.ausfFqdn                |Mandatory                   |AUSF ip-address/FQDN                        |
|config.nfRegistration          |Mandatory                   |yes/no                                      |
|config.nrfSelection            |Optional                    |yes/no                                      |
|config.smfSelection            |Mandatory                   |It helps in selecting the SMF via NRF       |
|config.externalAusf            |Mandatory                   |Always yes when using AUSF                  |
|config.useHttp2                |Mandatory (yes/no)          |if using HTTP/2 change the port for HTTP/1.1|
|config.mySqlServer             |Optional                    |if not using AUSF                           |
|config.mySqlUser               |Optional                    |if not using AUSF                           |
|config.externalNssf            |Optional                    |if not using AUSF                           |
|config.mySqlPass               |Optional                    |if not using AUSF                           |

## Advanced Debugging Parameters

Only needed if you are doing advanced debugging


|Parameter                        |Allowed Values                 |Remark                                        |
|---------------------------------|-------------------------------|----------------------------------------------|
|start.amf                        |true/false                     |If true amf container will go in sleep mode   |
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