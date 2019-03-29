Idea behind this repo is that you can use EVE-NG for your CI/CD pipeline.
Example based on Cumulus.
This repo contains functions for Cumulus Networ. If you need more device types you need implement functions for them.

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

4. 
    You have a configuration files (Example files in /etc/... for Cumulus or a "show run" file for Cisco"
    -> In this case you can copy this configuration directly on your device BEFORE they start
    
    You have Ansible plabooks that will deploy will deploy your network 
    -> In this case you will deploy your plabooks AFTER your nodes started

5. EVE-NG nodes Start

6. Execute your task on them

7. You write a YAML file that contains informations about how and where save your device configurations

8. EVE-NG nodes Stop

9. Remove you lab