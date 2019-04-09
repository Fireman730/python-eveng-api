# EVE-NG for CI/CD pipeline.

###### Development in progress ! 


## Project presentation
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
##### Become a contributor !! 

## Project Structure

- ```eve-ng.py``` is the script with which you will interact and run commands. 

- ```PyEVENG.py``` is a Class for interact with your VM via REST API or SSH.

- ```abstract_device.py``` some actions are differents for each devices.
Exampple :
If you want backup a device you need to backup "show run" for Cisco but,
for a Cumulus Network device you nned to backup a lot of files in ```/etc`/```.
This abstract class implement functions common to all devices and declare as
```@abstractmethod``` functions that have to be implement for each devices

- ```xxx_devcice.py``` (```cumulus_devcice.py```, ```extreme_devcice.py```, ...)
are some method implementations and specifications for execute method
Example ```getConf()```. In Cumulus specification this function will backup 
necessary files in ```/etc/``` and for Extreme it will backup ```config.cfg```
It is important to developp a class per device type.
(There are some modifications to do in PyEVENG.py file - this part need to be 
rethought)

- ```eveng-yaml-validation.py``` is used for validate your yaml topology files.
For example this script avoids that you have 6 nodes called Leaf01...

- ```./vm/vm_info.yml```  describes your EVE-NG VM (ssh user/pass, http user/pass, IP address, ...)

- ```./architecture/all.yml``` contains informations about your lab that you want create
It contains devices and links between them that they have to be creat

- ```lab_to_backup.yml``` contains informations about lab backup.
If you want backup your devices after modifications.

- ```./commands/*``` contains specific commands for device types (Cumulus, Extreme, ...)

## Run the script

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
./eveng-api.py --ansible=/path/to/playbooks

# --> --config is interessting if you want recreate your production network
# in a virtual environnement. Based on your backup you can rebuild your network.
# When your network is up, you can run Ansible/Chef/Python/Salt scripts.
# In this case --config has to deploy network for joining nodes

# Case 2 start nodes and deploy config via Ansible
### 2b. 
## Create your OOB network - you need to create a network that is mapped on
## your laptop/server virtual interface. You can run Ansible script on OOB net.
./eveng-api.py --oob=/path/to/oob.yml
./eveng-api.py --ansible=/path/to/playbooks

# --> --oob is interessting if you want test your scripts for deploy your network
# from scratch. --oob will configure your out-of-band for access to your devices
# and run your Ansible/Chef/Python/Salt scripts

# ---------------------------------------------------------------------------

# 3. If your network works fine backup nodes !
./eveng-api.py --backup=/path/where/backup 

# 4. Stop nodes
./eveng-api.py --stop=labName.unl,/path/to/vm/info/yaml/file.yml

# 5. Remove lab
./eveng-api.py --remove=labName.unl,/path/to/vm/info/yaml/file.yml

```