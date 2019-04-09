# EVE-NG for CI/CD pipeline.

###### Development in progress ! 

Every days you hear about "CI/CD", pipeline or DevOps.
Often pipeline is defined as follow 

```
Plan --> Code --> Build --> Test --> Release --> Deploy --> Operate Monitor
```

It's beautiful but in Network case 

* How can we test our Network ??
* How can we virtualize our Network ??
* If I change my underlay eBGP configuration, how I can know that my network still works ??
* How I can detect that my modification works ???

All these questions are current.
In network domain, we can change our pipeline.

1. Code Ansible playbooks that will be modified our Network
2. Create a Virtual network that are the same in production
    In other words, I need to have my production network in a virtual environment.
    I need to deploy a network based on my production backup files

3. Test our network. We have to write some Ansible playbooks for example that can validate that my network works
    Check nodes LLDP neighbors and validate that all my node see their neighbors
    Ping all nodes between them
    Check nodes eBGP neighbors
    Check nodes routing tables
    and so ...

4. If the network works fine we can go in production deployment.


After these informations you can maybe says "Ok but how i can deploy my network ??".
Some tools are here for you.
You can use Vagrant, EVE-NG or GNS3. There are a lot of others tools!

**More difficult thing is define "how do you want work and how do you really need ?"**
This point is very very difficult and is not your own responsability.
You need to discuss about it with your team and define the best pipeline that you need for your infrastructure and organization !!

This repo contains a script that can deploy a virtual network based on your production network.
As say before it is not the best and the only way to vritualize a network and make your tests.
But with this base you can work and advance in your Network as Code and NetOps transformation.

Idea behind this repo is that you can use EVE-NG as a step (virtualize and tests) of your CI/CD pipeline.
Example based on Cumulus.
This repo contains functions for Cumulus Network. If you need more device types you need implement functions for them.

**Your help is welcome**
### Become a contributor !! 

The steps are the following :

1. You create a YAML file that contains all informations about your EVE-NG VM
* IP
* http username and password
* root username and password
* ...

2. You create a YAML file that contains informations on the project that you want create
* labname
* author
* path 
...

3. You create a YAML file that describes your lab infrastructure
* 2 spines with 4 leaves
* Spine01 swp1 is connected to Leaf01 port swp1
* Spine02 swp4 is connected to Leaf04 port swp2
* ... 
* 

4. You write a YAML file that contains informations about how and where save your device configurations

5. 
    You have a configuration files (Example files in /etc/... for Cumulus or a "show run" file for Cisco"
    -> In this case you can copy this configuration directly on your device BEFORE they start
    
    You have Ansible plabooks that will deploy will deploy your network 
    -> In this case you will deploy your plabooks AFTER your nodes started

6. EVE-NG nodes Start

7. Execute your task on them
    --> Playbooks that add a VLAN
    --> Playbooks that modify your BGP configuration
    --> Plabooks that configure BFD through your network
    
    SURE your plabook need to be test locally before run your CI/CD pipeline

8. EVE-NG nodes Stop

9. Remove you lab

For pilote these steps you can use tools as Jenkins and Bamboo.
Idea is create tasks that will run each step and verify that the previous step worked before execute the next one

You will able to run as follow :

```shell

# ---------------------------------------------------------------------------
### 0. Create your Lab - USELESS La creation can be insert into deploy yaml file.
##./eveng-api.py --create=/path/to/yml/lab

# 1. Deploy your topology on your lab
./eveng-api.py --deploy=/path/to/yml/topology

# This step is automatic
# /!\ The directory VM will not be created if the VM have never been started
./eveng-api.py --start=labName.unl,/path/to/vm/info/yaml/file.yml

# ---------------------------------------------------------------------------
# Case 1 copy config file into your devices before your lab start
### 2a. Copy your config into dev
./eveng-api.py --config=/path/to/backup

# Case 2 start nodes and deploy config via Ansible
### 2b. 
## Create your OOB network - you need to create a network that is mapped on
## your laptop/server virtual interface. You can run Ansible script on OOB net.
./eveng-api.py --oob=/path/to/oob.yml
./eveng-api.py --ansible=/path/to/playbooks
# ---------------------------------------------------------------------------

#
# Execute your Ansible playbooks modify test ...
#

# 3. If your network works fine backup nodes !
./eveng-api.py --backup=/path/where/backup 

# 4. Stop nodes
./eveng-api.py --stop=labName.unl,/path/to/vm/info/yaml/file.yml

# 5. Remove lab
./eveng-api.py --remove=labName.unl,/path/to/vm/info/yaml/file.yml

```