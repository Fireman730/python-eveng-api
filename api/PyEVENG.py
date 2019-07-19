#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""
This file contains a Class (PyEVENG) thah contains REST API Call to EVE-NG VM.
Some functionalities use a SSH connection.

You can create a object as with the followind code:
```
api = PyEVENG.PyEVENG(username=httpsUsername, password=httpsPassword, ipAddress=ipAddress, port=myPort, useHTTPS=httpsSSL,          
            userFolder=myFolder, pod=myPod,  root=sshRoot, rmdp=sshPass, community=myCommunity)
```

With your PyEVENG object you can GET and PUT some informations to/from the EVE-NG devices.

Below any features :

* login()
* get_backup_nodes_config()
* get_backup_config()
* add_config_to_nodes_lab()

Backup are implemented for :
* Cisco IOS L3/l2
* Cumulus Linux
* VyOS
* Cisco Nexus 9k
* Extreme Network

Push Config are implemented for:
* Cisco IOS L3/l2
* Cumulus Linux
* Extreme Network

"""

__author__     = "Dylan Hamel"
__maintainer__ = "Dylan Hamel"
__version__    = "1.0"
__email__      = "dylan.hamel@protonmail.com"
__status__     = "Production"
__copyright__  = "Copyright 2019"
__license__    = "MIT"


######################################################
#
# Default value used for exit()
#

EXIT_SUCCESS = 0
EXIT_FAILURE = 1

######################################################
#
# Import Library
#
try:
    import time
except ImportError as importError:
    print("Error import [PyEVENG] time")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import yaml
except ImportError as importError:
    print("Error import [PyEVENG] yaml")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import pexpect
except ImportError as importError:
    print("Error import [PyEVENG] pexpect")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import pprint
    PP = pprint.PrettyPrinter(indent=4)
except ImportError as importError:
    print("Error import [PyEVENG] pprint")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import tools.ip
except ImportError as importError:
    print("Error import [PyEVENG] tools.ip")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import tools.routing
except ImportError as importError:
    print("Error import [PyEVENG] tools.routing")
    print(importError)
    exit(EXIT_FAILURE)

try:
    from exceptions.EveExceptions import EVENG_Exception
except ImportError as importError:
    print("Error import [PyEVENG] listdir")
    print(importError)
    exit(EXIT_FAILURE)

try:
    from os import listdir
    from os.path import isfile, join
    from os import mkdir
except ImportError as importError:
    print("Error import [PyEVENG] listdir")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import devices.cumulus_device as cumulus_device
    import devices.extreme_device as extreme_device
    import devices.cisco_device as cisco_device
    import devices.vyos_device as vyos_device
    import devices.nexus_device as nexus_device
    import devices.arista_device as arista_device
except ImportError as importError:
    print("Error import [PyEVENG] xyz_device")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import paramiko
except ImportError as importError:
    print("Error import [PyEVENG] paramiko")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import urllib3
except ImportError as importError:
    print("Error import [PyEVENG] urllib3")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import requests
except ImportError as importError:
    print("Error import [PyEVENG] requests")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import json
except ImportError as importError:
    print("Error import [PyEVENG] json")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import sphinx
except ImportError as importError:
    print("Error import [PyEVENG] sphinx")
    print(importError)
    exit(EXIT_FAILURE)

######################################################
#
# Class
#
class PyEVENG:
    """
    
    This class is a Python client for retrieve information about your EVE-NG VM.
    The main aim is provided an Python script for automate an deploy your network un EVE-NG    
    
    """
    

    # ----------------------------------------------------------
    #
    #
    def get_backup_nodes_config(self, yamlFiles: dict()):
        """
        This function will recover all devices that need to be backed up.
        

        ```
          - labname: dmvpn-ospf-qos.unl
            pod: 0
            folder: Network
            bck_path: /Volumes/Data/gitlab/python-eveng-api/backup
            bck_type: verbose
            hostname:               # <<== This list
              - all
        ```

        This function will not execute the backup !
        It will also call the function for execute the backup for each devices.

        Args:
            param1 (dict): YAML that contains informations about backup
                            => Example in ./backup/lab_to_backup.yml
        
        """
        for lab in yamlFiles['labs']:
            self._folder = lab['folder']

            if lab['labname'] not in self.get_labs_in_folder():
                raise EVENG_Exception(
                    "[PyEVENG - get_backup_nodes_config]"+str(lab['labname'])+" doesn't exist in "+str(lab['folder']), 910)

            if "all" in lab['hostname']:
                for hostname in self.get_lab_nodes_name(lab['labname']):
                    self.get_backup_config(lab['bck_path'], lab['labname'], hostname)
            else:
                for hostname in lab['hostname']:
                    self.get_backup_config(lab['bck_path'], lab['labname'], hostname)


    # ----------------------------------------------------------
    #
    #
    def get_backup_config(self, path:str(), project_name: str(), nodeName: str()):
        """
        This function will find the node image.
        According to the image. this function will call the function for backup the device.

        Each device type need to extend the ``./devices/abstract_device.py`` class and implement backup functions.
        When device are implemented you can add a condition.

        Example:
          lif "NEW_DEVICE" in nodeImage:
            self.get_newDevice_backup(path, project_name, nodeName, nodeID)

        You also need to implement the get_newDevice_backup(...) function for create a object of your new class.

        Args:
            param1 (str): Path where store the device backups.
            param2 (str): EVE-NG Project Name.
            param3 (str): EVE-NG Node Name.
        
        Returns:
            str: Device image
        """
        allNodesID = self.get_lab_nodes_id(project_name)
        allNodes = self.get_lab_nodes(project_name)
        for node in allNodes['data'].values():
            if node['name'] == nodeName:
                nodeImage = node['image']
                nodeID = node['id']
            
        nodeImage = nodeImage.upper()

        try:
            mkdir(path+"/"+project_name)
        except OSError as e:
            print("[PyEVENG - get_backup_config] create project folder", e)

        try:
            mkdir(path+"/"+project_name+"/"+nodeName)
        except OSError as e:
            print("[PyEVENG - get_backup_config] create node folder", e)

        path = path+"/"+project_name+"/"+nodeName

        print("*************",nodeImage, "***************")
        # CUMULUS LINUX
        if "CUMULUS" in nodeImage :
            self._get_cumulus_backup(path, project_name, nodeName, nodeID)
        # EXTREME NETWORK
        elif "EXTREME" in nodeImage:
            self._get_extreme_backup(path, project_name, nodeName, nodeID)
        # CISCO
        elif "VIOS" in nodeImage:
            self._get_cisco_backup(path, project_name, nodeName, nodeID)
        # CISCO NEXUS
        elif "NXOS" in nodeImage:
            self._get_nexus_backup(path, project_name, nodeName, nodeID)
        # VYOS VYATTA
        elif "VYOS" in nodeImage:
            self._get_vyos_backup(path, project_name, nodeName, nodeID)
        # VEOS ARISTA
        elif "VEOS" in nodeImage:
            self._get_arista_backup(path, project_name, nodeName, nodeID)


    # ----------------------------------------------------------
    #
    #
    def _get_arista_backup(self, path, projectName, nodeName, nodeID):
        """
        This function backup Arista configuration files in path  given in parameter
        Files will be retrieve with paramiko SFTP

        Args:
            param1 (str): Path where save configuration files.
            param2 (str): EVE-NG Project Name.
            param3 (str): EVE-NG Node Name.
            param4 (str): EVE-NG Node ID.
        
        """
        arista = arista_device.AristaDevice(
            self._ip, self._root, self._pwd, path,
            self._pod, projectName, self.get_lab_id(projectName), nodeName, nodeID)

        arista.getConfigVerbose()


    # ----------------------------------------------------------
    #
    #
    def _get_vyos_backup(self, path, projectName, nodeName, nodeID):
        """
        This function backup VyOS configuration files in path  given in parameter
        Files will be retrieve with paramiko SFTP

        Args:
            param1 (str): Path where save configuration files.
            param2 (str): EVE-NG Project Name.
            param3 (str): EVE-NG Node Name.
            param4 (str): EVE-NG Node ID.
        
        """
        vyos = vyos_device.VyosDevice(
            self._ip, self._root, self._pwd, path,
            self._pod, projectName, self.get_lab_id(projectName), nodeName, nodeID)

        vyos.getConfigVerbose()


    # ----------------------------------------------------------
    #
    #
    def _get_nexus_backup(self, path, projectName, nodeName, nodeID):
        """
        This function backup Cisco Nexus configuration files in path given in parameter
        Files will be retrieve with paramiko SFTP

        Args:
            param1 (str): Path where save configuration files.
            param2 (str): EVE-NG Project Name.
            param3 (str): EVE-NG Node Name.
            param4 (str): EVE-NG Node ID.
        
        """
        nexus = nexus_device.NexusDevice(
            self._ip, self._root, self._pwd, path,
            self._pod, projectName, self.get_lab_id(projectName), nodeName, nodeID)

        nexus.getConfigVerbose()


    # ----------------------------------------------------------
    #
    #
    def _get_cisco_backup(self, path, projectName, nodeName, nodeID):
        """
        This function backup Cisco configuration files in path given in parameter
        Files will be retrieve with paramiko SFTP

        Args:
            param1 (str): Path where save configuration files.
            param2 (str): EVE-NG Project Name.
            param3 (str): EVE-NG Node Name.
            param4 (str): EVE-NG Node ID.
        
        """
        cisco = cisco_device.CiscoDevice(
            self._ip, self._root, self._pwd, path,
            self._pod, projectName, self.get_lab_id(projectName), nodeName, nodeID)

        cisco.getConfigVerbose()


    # ----------------------------------------------------------
    #
    #
    def _get_extreme_backup(self, path, projectName, nodeName, nodeID):
        """
        This function backup Extreme Network configuration files in path given in parameter
        Files will be retrieve with paramiko SFTP

        Args:
            param1 (str): Path where save configuration files.
            param2 (str): EVE-NG Project Name.
            param3 (str): EVE-NG Node Name.
            param4 (str): EVE-NG Node ID.
        
        """
        extreme = extreme_device.ExtremeDevice(
            self._ip, self._root, self._pwd, path,
            self._pod, projectName, self.get_lab_id(projectName), nodeName, nodeID)

        extreme.getConfigVerbose()


    # ----------------------------------------------------------
    #
    #
    def _get_cumulus_backup(self, path, projectName, nodeName, nodeID):
        """
        This function backup Cumulus Network configuration files in path given in parameter
        Files will be retrieve with paramiko SFTP

        Args:
            param1 (str): Path where save configuration files.
            param2 (str): EVE-NG Project Name.
            param3 (str): EVE-NG Node Name.
            param4 (str): EVE-NG Node ID.
        
        """
        cumulus = cumulus_device.CumulusDevice(
            self._ip, self._root, self._pwd, path, 
            self._pod, projectName, self.get_lab_id(projectName), nodeName, nodeID)

        cumulus.getConfigVerbose()


    # ------------------------------------------------------------------------------------------
    #
    #
    #
    def add_config_to_nodes_lab(self, configToDeploy:dict(), labName:str()):
        for config in configToDeploy:
            nodeImage = self.get_node_image_and_node_id(labName, config['node'])
            if config['type'] == "full":
                if "CUMULUS" in nodeImage[0]:
                    self._push_cumulus_full_config(config, labName)
                # CISCO
                elif "VIOS" in nodeImage[0]:
                    self._push_cisco_config(config, labName)
                # CISCO NEXUS
                elif "NXOS" in nodeImage[0]:
                    self._push_nexus_config(config, labName)
                # EXTREME NETWORK
                elif "EXTREME" in nodeImage[0]:
                    self._push_extreme_config(config, labName)
                # ARISTA VEOS
                elif "VEOS" in nodeImage[0]:
                    self._push_arista_config(config, labName)
                # Others ELIF
                #

            elif config['type'] == "oob":
                if "CUMULUS" in nodeImage[0]:
                    self._push_cumulus_oob_config(config, labName)
                elif "NXOS" in nodeImage[0]:
                    self._push_nexus_config(config, labName)
                elif "VIOS" in nodeImage[0]:
                    self._push_cisco_config(config, labName)
                elif "EXTREME" in nodeImage[0]:
                    self._push_extreme_config(config, labName)
                # ARISTA VEOS
                elif "VEOS" in nodeImage[0]:
                    self._push_arista_config(config, labName)
                        
                # Others ELIF
                # elif "EXTREME in nodeImage "
                #


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _push_arista_config(self, configToDeploy: dict(), labName: str()):
        """
        This function will call arista_device.py for push Full configuration

        Args:
            param1 (dict): Informations about config
            param2 (str): Lab name
        """
        arista = arista_device.AristaDevice(
            self._ip, self._root, self._pwd, configToDeploy['config'],
            self._pod, labName, self.get_lab_id(labName), configToDeploy['node'], self.get_node_id_by_node_name(labName, configToDeploy['node']))

        arista.pushConfig()


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _push_extreme_config(self, configToDeploy: dict(), labName: str()):
        """
        This function will call extreme_device.py for push Full configuration

        Args:
            param1 (dict): Informations about config
            param2 (str): Lab name
        """
        extreme = extreme_device.ExtremeDevice(
            self._ip, self._root, self._pwd, configToDeploy['config'],
            self._pod, labName, self.get_lab_id(labName), configToDeploy['node'], self.get_node_id_by_node_name(labName, configToDeploy['node']))

        extreme.pushConfig()


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _push_nexus_config(self, configToDeploy: dict(), labName: str()):
        """
        This function will call nexus_device.py for push Full configuration

        Args:
            param1 (dict): Informations about config
            param2 (str): Lab name
        """
        nexus = nexus_device.NexusDevice(
            self._ip, self._root, self._pwd, configToDeploy['config'],
            self._pod, labName, self.get_lab_id(labName), configToDeploy['node'], self.get_node_id_by_node_name(labName, configToDeploy['node']))

        nexus.pushConfig()


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _push_cisco_config(self, configToDeploy: dict(), labName: str()):
        """
        This function will call cisco_device.py for push Full configuration

        Args:
            param1 (dict): Informations about config
            param2 (str): Lab name
        """
        cisco = cisco_device.CiscoDevice(
            self._ip, self._root, self._pwd, configToDeploy['config'],
            self._pod, labName, self.get_lab_id(labName), configToDeploy['node'], self.get_node_id_by_node_name(labName, configToDeploy['node']))
                
        cisco.pushConfig()


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _push_cumulus_full_config(self, configToDeploy: dict(), labName: str()):
        """
        This function will call cumulus_device.py for push Full configuration

        Args:
            param1 (dict): Informations about config
            param2 (str): Lab name
        """
        cumulus = cumulus_device.CumulusDevice(
            self._ip, self._root, self._pwd, configToDeploy['config'],
            self._pod, labName, self.get_lab_id(labName), configToDeploy['node'], self.get_node_id_by_node_name(labName, configToDeploy['node']))
                
        cumulus.pushConfig()


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _push_cumulus_oob_config(self, configToDeploy: dict(), labName: str()):
        """
        This function will call xxx_device.py for push OOB configuration

        Args:
            param1 (dict): Informations about config
            param2 (str): Lab name
        """
        cumulus = cumulus_device.CumulusDevice(
            self._ip, self._root, self._pwd, configToDeploy['config'],
            self._pod, labName, self.get_lab_id(labName), configToDeploy['node'], self.get_node_id_by_node_name(labName, configToDeploy['node']))

        cumulus.pushOOB()


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _push_cumulus_oob(self, pathToConfigFileOOB, labName, nodeName, nodeID):

        print("[PyEVENG - _push_cumulus_oob]")
        cumulus = cumulus_device.CumulusDevice(
            self._ip, self._root, self._pwd, pathToConfigFileOOB,
            self._pod, labName, self.get_lab_id(labName), nodeName, nodeID)

        cumulus.pushOOB()


    # ##################################################################################################
    #
    #   Call via SSH or Telnet directly to EVE-NG VM or devices via telnet port (console)
    #
    # ##################################################################################################

    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def enable_port(self, labName: str(), ipAddress: str(), telnetPort: str(), nodeID: str(), nodeName: str()):
        """
        This function enable interface through a telnet session.
        Use EXPECT library

        Args:
            param1 (str): Lab name
            param2 (str): Address IP 
            param3 (str): Telnet port
            param4 (str): Node ID
            param5 (str): Node name
        """

        with open("./commands/cisco/no_shut_commands.yml", 'r') as yamlFile:
            try:
                data = yaml.load(yamlFile)
            except yaml.YAMLError as exc:
                print(exc)
        try:
            telnet = pexpect.spawn("telnet {} {}".format(ipAddress, telnetPort))
            telnet.expect("\r\n")
            #print("0)", telnet.before)
            telnet.sendline("\r\n")
            telnet.expect("Connected")
            #print("1)", telnet.before)
            telnet.sendline("enable")
            telnet.expect("{}".format(nodeName))
            #print("2)", telnet.before)
            telnet.sendline("conf t")
            telnet.expect("(config)")
            #print("3)", telnet.before)

            for interface in self.get_node_interfaces(labName, nodeID):
                 telnet.sendline("interface {}".format(interface))
                 telnet.expect("(config)")
                 #print(telnet.before)
                 telnet.sendline("no shut")
                 telnet.expect("(config)")
                 #print(telnet.before)

            telnet.sendline("end")
            telnet.expect("#")
            #print(telnet.before)
            telnet.sendline("exit")
        except pexpect.exceptions.TIMEOUT as e:
            print(e)

    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def remove_remote_connexion_file(self, labName):
        """
        This function will remove file on eve-ng vm

        Args:
            param1 (str): Lab name to delete
        """
       
        ssh = self._ssh_connect()
        sftp = ssh.open_sftp()
        try:
            
            stdin, stdout, stderr = ssh.exec_command(
                "sudo sh /root/.eveng/{}".format(labName))
            o = "".join(stdout.readlines())
            

            print(
                "[PyEVENG - remove_remote_connexion_file] - remove root/.eveng/connexion_{} ...".format(labName))
            sftp.remove("/root/.eveng/connexion_{}".format(labName))

            print(
                "[PyEVENG - remove_remote_connexion_file] - remove root/.eveng/connexion_{} OK !".format(labName))
        except FileNotFoundError:
            print(
                "[PyEVENG - remove_remote_connexion_file] - remove root/.eveng/connexion_{} doesn't exist !".format(labName))


        try: 
            print(
                "[PyEVENG - remove_remote_connexion_file] - remove root/.eveng/{} ...".format(labName))
            sftp.remove("/root/.eveng/{}".format(labName))
            
            print(
                "[PyEVENG - remove_remote_connexion_file] - remove root/.eveng/{} OK !".format(labName))
        except FileNotFoundError:
            print(
                "[PyEVENG - remove_remote_connexion_file] - remove root/.eveng/{} doesn't exist !".format(labName))

        ssh.close()
    


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def write_in_remote_file(self, ssh:paramiko.SSHClient(), content, path:str(), *, mode="a"):
        """
        This function will write devices connection informations in a file on EVE-NG VM.

        Args:
            param1 (str): SSH Connexion to EVE-NG VM
            param2 (str): Content to write in the file
            param3 (str): Path where store informations
        """
        print("[PyEVENG - write_in_remote_file] - create new files {} ...".format(path))

        sftp = ssh.open_sftp()
        f = sftp.open(path, mode)
        f.write(json.dumps(content))
        f.close()
        sftp.close()
        print("[PyEVENG - write_in_remote_file] - create new files OK ! ")


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_remote_connexion_file(self, labName) -> dict:
        """ 
        This function will retrieve data from a connexion_labname file

        Args:
            param1 (str): Labname of which one you want retrieve data
        """

        ssh = self._ssh_connect()

        sftp = ssh.open_sftp()
        f = sftp.open("/root/.eveng/connexion_{}".format(labName), "rb")

        data = json.loads(f.read())
        
        sftp.close()
        ssh.close()

        return data

    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def create_iptables_nat(self, ssh: paramiko.SSHClient(), evengIP: str(), interface: str(), hostsIP: str(), sshMgmt: str(), eveIP: str(), eveSsh: str()):
        """
        This function will create iptables on the EVE-NG VM
            * SNAT
            * ALLOWED
            * DNAT

        Args:
            param1 (str): SSH Connexion to EVE-NG VM
            param2 (str): EVE-NG interface on which one devices are connected
            param3 (str): device ip address
            param4 (str): device ssh management port
        """
        commands = list()

        #
        # Create Folder
        #
        stdin, stdout, stderr = ssh.exec_command("mkdir -p ~/.eveng")
        o = "".join(stdout.readlines())

        #
        # Create file
        #
        print("[PyEVENG - create_iptables_nat] - create file", self._project)
        stdin, stdout, stderr = ssh.exec_command(
            "touch ~/.eveng/"+self._project)
        o = "".join(stdout.readlines())

        #
        # DNAT
        #
        print("[PyEVENG - create_iptables_nat] -",
              tools.routing.IPTABLES_DNAT.format("A", evengIP, eveSsh, hostsIP, sshMgmt))
        stdin, stdout, stderr = ssh.exec_command(
            tools.routing.IPTABLES_DNAT.format("A", evengIP, eveSsh, hostsIP, sshMgmt))
        o = "".join(stdout.readlines())
       
        commands.append(tools.routing.IPTABLES_DNAT.format("D", evengIP, eveSsh, hostsIP, sshMgmt))
        
        #
        # FIREWALL
        #
        print("[PyEVENG - create_iptables_nat] -",
              tools.routing.IPTABLES_ALLOWED.format("A", evengIP, eveSsh))
        stdin, stdout, stderr = ssh.exec_command(
            tools.routing.IPTABLES_ALLOWED.format("A", evengIP, eveSsh))
        o = "".join(stdout.readlines())

        commands.append(tools.routing.IPTABLES_ALLOWED.format("D", evengIP, eveSsh))

        #
        # SNAT
        #
        print("[PyEVENG - create_iptables_nat] -",
              tools.routing.IPTABLES_SNAT.format("A", interface, eveIP))
        stdin, stdout, stderr = ssh.exec_command(
            tools.routing.IPTABLES_SNAT.format("A", interface, eveIP))
        o = "".join(stdout.readlines())
        
        commands.append(tools.routing.IPTABLES_SNAT.format("D", interface, eveIP))

        sftp = ssh.open_sftp()
        f = sftp.open("/root/.eveng/"+self._project, 'a')
        for command in commands:
            f.write(command+"\n")
        
        f.close()
        sftp.close()



    # ##################################################################################################
    #
    #   Call to get informations as nodes, networks, ... from labs !!
    #
    # ##################################################################################################


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_nodes_id(self, labName: str()) -> list():
        """
        This function will return a list that contains all nodes ID according to the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            list: That contains all node ID
        """

        #self.check_param_type_str(labName)

        response = requests.get(
            self._url+"/api/labs/"+self._folder+"/"+labName+"/nodes", cookies=self._cookies, verify=False)

        if response.status_code == 404:
            raise EVENG_Exception(
                "[PyEVENG - get_lab_nodes_id] - Lab doesn't exist or devices are down", 7081)

        self._requests_error(response.status_code)
        content = json.loads(response.content)["data"]

        nodesID = list()

        if len(content) is not 0:
            for key, val in content.items():
                nodesID.append(key)

        return nodesID


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_nodes_name(self, labName: str()) -> list():
        """
        This function will return a list that contains all nodes name according to the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            list: That contains all node name
        """

        #self.check_param_type_str(labName)

        response = requests.get(
            self._url+"/api/labs/"+self._folder+"/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        content = json.loads(response.content)["data"]

        nodesName = list()
        if content.__len__() == 0:
            return nodesName
        for key, val in content.items():
            nodesName.append(val["name"])

        return nodesName


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_nodes(self, labName: str()) -> dict():
        """
        This function will return a JSON that contains informations about all nodes according to the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            json: That contains nodes informations
        """

        #self.check_param_type_str(labName)

        response = requests.get(
            self._url+"/api/labs/"+self._folder+"/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        return json.loads(response.content)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_node(self, labName: str(), nodeID: str()) -> dict():
        """
        This function will return a JSON that contains informations about all nodes according to the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param1 (str): EVE-NG node ID

        Returns:
            json: That contains nodes informations
        """

        #self.check_param_type_str(labName)
        #self.check_param_type_str(nodeID)

        response = requests.get(
            self._url+"/api/labs/"+self._folder+"/"+labName+"/nodes/"+nodeID, cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        return json.loads(response.content)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_id_by_node_name(self, labName: str(), nodeName: str()) -> str():
        """
        This function will nodeID regarding to the nodeName given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): Node name

        Returns:
            str: nodeID
        """
        nodeID = str()
        allNodesID = self.get_lab_nodes_id(labName)
        allNodes = self.get_lab_nodes(labName)
        for node in allNodes['data'].values():
                if node['name'] == nodeName:
                    nodeID = node['id']
        return nodeID


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_interface_id(self, labName: str(), nodeID: str(), interfaceName: str()) -> str():
        """
        This function will return a str that contains node interface ID

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): EVE-NG node ID
            param3 (str): Node interface name

        Returns:
            string: Node Interface ID
        """
        data = self.get_lab_node_interfaces(labName, nodeID)
        for index, value in enumerate(data['data']['ethernet']):
            if value['name'] == interfaceName:
                return index


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_interfaces(self, labName: str(), nodeID: str()) -> list():
        """
        This function will return a list that contains all ethernet interface names

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): EVE-NG node ID

        Returns:
            list: That contains nodes interface names
        """
        data = self.get_lab_node_interfaces(labName, nodeID)
        result = list()
        for interface in data['data']['ethernet']:
            result.append(interface['name'])

        return result


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_node_interfaces(self, labName: str(), nodeID: str()) -> dict():
        """
        This function will return a JSON that contains informations about labs interfaces

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): EVE-NG node ID

        Returns:
            json: That contains interfaces informations
        """
        ##self.check_param_type_str(labName)
        ##self.check_param_type_str(nodeID)

        response = requests.get(
            self._url+"/api/labs/"+self._folder+"/"+str(labName)+"/nodes/"+str(nodeID)+"/interfaces", cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        return json.loads(response.content)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_status(self, labName: str(), nodeID: str()) -> str():
        """
        This function will return a string that contains nodes status according to node ID and the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): EVE-NG node ID

        Returns:
            str: That contains node status
        """
        return str(self.get_lab_node(labName, nodeID)['data']['status'])

    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_image(self, labName: str(), nodeID: str()) -> str():
        """
        This function will return a string that contains nodes image according to node ID and the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): EVE-NG node ID

        Returns:
            str: That contains node image
        """
        response = requests.get(
            self._url+"/api/labs/"+str(self._folder)+"/"+str(labName)+"/nodes/"+str(nodeID), cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        return json.loads(response.content)["data"]["image"]


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_telnet_port(self, labName: str(), nodeID: str()) -> str():
        """
        This function will return telnet port

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): EVE-NG node ID

        Returns:
            str: Telnet port
        """

        telnetInfo = self.get_node_url(labName, nodeID)
        index = telnetInfo.rfind(":")
        return telnetInfo[index+1:]


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_telnet_ip(self, labName: str(), nodeID: str()) -> str():
        """
        This function will return telnet port

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): EVE-NG node ID

        Returns:
            str: Telnet port
        """

        telnetInfo = self.get_node_url(labName, nodeID)
        indexEnd = telnetInfo.rfind(":")
        indexStart = telnetInfo.rfind("/")
        return telnetInfo[indexStart+1:indexEnd]


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_nodes_url(self, labName: str()) -> dict():
        """
        This function will return telnet connection informations.

        Args:
            param1 (str): EVE-NG lab name
        
        Returns:
            dict: Telnet connection informations    hostname: url_connection
        """

        # Exception is lab doesn't exist is raise in the below function
        nodesID = self.get_lab_nodes_id(labName)
        result = dict()

        if len(nodesID) is not 0:
            for nodeID in nodesID:
                result[self.get_node_name_by_id(labName, nodeID)] = self.get_node_url(
                    labName, nodeID)

        return result


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_url(self, labName: str(), nodeID: str()) -> str():
        """
        This function will return telnet connection informations.

        "1": {
            "console": "telnet",
            "delay": 0,
            "id": 1,
            "left": 177,
            "icon": "Switch L3.png",
            "image": "viosl2-adventerprisek9-m.03.2017",
            "name": "GVA10",
            "ram": 1024,
            "status": 0,
            "template": "viosl2",
            "type": "qemu",
            "top": 288,
            "url": "telnet://172.16.194.239:0",             <<<======
            "config_list": [],
            "config": "0",
            "cpu": 1,
            "ethernet": 8,
            "uuid": "0c5f57ad-fcff-47b1-b43b-4ba39b8545dd",
            "firstmac": "50:00:00:01:00:00"
        },

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): EVE-NG node ID

        """

        data = self.get_lab_node(labName, nodeID)
        return data['data']['url']


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_networks_name(self, labName: str()) -> list():
        """
        This function will return a LIST that contains all network name in lab given in parameter

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            list: That contains networks name
        """
        data = self.get_lab_networks(labName)

        networkName = list()

        for network in data['data']:
            networkName.append(data['data'][network]['name'])

        return networkName


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_networks(self, labName: str()) -> dict():
        """
        This function will return a JSON that contains informations about labs networks

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            json: That contains networks informations
        """
        response = requests.get(
            self._url+"/api/labs/"+self._folder+"/"+str(labName)+"/networks", cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        return json.loads(response.content)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_nodes_access_method(self, labName: str()) -> dict():
        """
        This function will return a dictionnary that contains informations access method
        
        Example :
            - {"Spine01": "telnet", "Linux", "vnc"}
            
        Args:
            param1 (str): EVE-NG lab name

        Returns:
            dict: That contains key = hostname, value = access method
        """

        #self.check_param_type_str(labName)

        response = requests.get(
            self._url+"/api/labs/"+self._folder+"/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        content = json.loads(response.content)["data"]

        nodesAccessMethod = dict()
        for key, val in content.items():
            nodesAccessMethod[val["name"]] = val["console"]

        return nodesAccessMethod


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_topology(self, labName):
        """
        This function will return a JSON that contains informations about labs topology

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            json: That contains topology informations
        """
        response = requests.get(
            self._url+"/api/labs/"+self._folder+"/"+labName+"/topology", cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        return json.loads(response.content)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_links(self, labName):
        """
        This function will return a JSON that contains informations about labs links

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            json: That contains links informations
        """
        response = requests.get(
            self._url+"/api/labs/"+self._folder+"/"+labName+"/links", cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        return json.loads(response.content)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_name_by_id(self, labName: str(), nodeID: str()) -> str():
        """
        This function will return a string that contains node name regarding node ID and labname given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param1 (str): Node ID

        Returns:
            str: Node name
        """
        return self.get_lab_node(labName, nodeID)['data']['name']


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_image_and_node_id(self,labName:str(), nodeName:str()) -> str():
        """
        This function will return a string that contains image type of nodes given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param1 (str): Node name

        Returns:
            str: Node image type
        """
        allNodesID = self.get_lab_nodes_id(labName)
        allNodes = self.get_lab_nodes(labName)

        for node in allNodes['data'].values():
            if node['name'] == nodeName:
                return node['image'].upper(), node['id']


    # ##################################################################################################
    #
    #   Call to add links, nodes, networks, ... to labs !!
    #
    # ##################################################################################################


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _add_networks_and_links_to_lab(self, interfacesToAdd: dict(), labName: str()):
        """
        This function will connect a node to a Network.
        Firstly they will create Network.
        2 nodes have to be connected on the same netwrok for communicate

        -X PUT - d '{"0":1}'127.0.0.1/api/labs/Users/Lab.unl/nodes/1/interfaces'

        Args:
            param1 (str): Lab Names
            param1 (str): Nodes Names
            param2 (str): Node interface ID
            param3 (str): Network ID
        """
        self._add_networks_to_lab(interfacesToAdd, labName)
        self._add_links_to_lab(interfacesToAdd, labName)
        self._set_network_visibility_to_0(interfacesToAdd, labName)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _add_networks_to_lab(self, networksToAdd: dict(), labName:str()):
        """
        This function add some network to a Lab

        curl -s -c /tmp/cookie -b /tmp/cookie -X POST -d '{"count":1,"name":"Net-R1iface_0","type":"bridge","left":441,"top":658,"visibility":1,"postfix":0}' 
        -H 'Content-type: application/json' http://127.0.0.1/api/labs/User1/Folder 2/Different Lab.unl/networks

        Args:
            param1 (dict): Nodes Informamations
            param2 (str): Labname
        """
        data = dict()
        networkName = self.get_lab_networks_name(labName)

        for link in networksToAdd:
            if link['dst'] == "OOB-NETWORK":
                data['name'] = str("OOB-NETWORK")
            else:
                data['name'] = str(link['src']+"("+link['sport']+")--"+link['dst']+"("+link['dport'] + ")")

            if data['name'] not in networkName:
                data['type'] = str(link['network'])
                data['visibility'] = 1
                self._add_network_to_lab(data, labName)
            else:
                print("[PyEVENG _add_networks_to_lab] -",
                      data['name'], " is already deployed!")


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _set_network_visibility_to_0(self, network: dict(), labName: str()):
        """
        This function will set network visibility to 0
        The network will not be show in GUI

        curl -s -c /tmp/cookie -b /tmp/cookie -X PUT -d '{"visibility":0}' 
        -H 'Content-type: application/json' http://127.0.0.1/api/labs/User1/Folder 2/Different Lab.unl/networks/1

        Args:
            param1 (str): Labname
            param2 (str): NetworkID
        """
        for networkID in network:
            response = requests.put(
                self._url+"/api/labs/"+self._folder+"/"+str(labName)+"/networks/"+str(networkID['id']), data="{\"visibility\":0}", cookies=self._cookies, verify=False)
            self._requests_error(response.status_code)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _add_network_to_lab(self, networkToAdd: dict(), labName: str()) -> str():
        """
        This function add some links to a Lab

        Args:
            param1 (dict): Nodes Informamations
            param2 (str): Labname
        """
        print("[PyEVENG _add_network_to_lab] -",
              networkToAdd['name'], "is deploying...")

        self.lock_lab()
        response = requests.post(
            self._url+"/api/labs/"+self._folder+"/"+labName+"/networks", data=json.dumps(networkToAdd), cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)

        print("[PyEVENG _add_network_to_lab] -",
              networkToAdd['name'], "(", str(response.status_code), ") has been deployed!")

        return (json.loads(response.content)['data']['id'])
        

    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _add_links_to_lab(self, interfaceToAdd: dict(), labName: str()):
        """
        This function add some links to a Lab

        Args:
            param1 (dict): Nodes Informamations
            param2 (str): Labname
        """
        ssh = self._ssh_connect()
        connexionInformations = dict()

        for link in interfaceToAdd:
            if link['dst'] == "OOB-NETWORK":
                #
                # Create The new interface
                #

                if "ip_eve" in link.keys():
                    index = link['ip_eve'].find("/")
                    ipMgmtEve = link['ip_eve'][:index]
                    ipMaskEveCidr = link['ip_eve'][index+1:]
                    ipMaskEve = tools.ip.convertCIDRtoNetmask(
                        ipMaskEveCidr)

                    print(
                        "[PyEVENG - _add_links_to_lab] - sudo ifconfig {} up && sudo ifconfig {} {} netmask {}".format(link['network'], link['network'], ipMgmtEve, ipMaskEve))
                    stdin, stdout, stderr = ssh.exec_command(
                        "sudo ifconfig {} up && sudo ifconfig {} {} netmask {}".format(link['network'], link['network'], ipMgmtEve, ipMaskEve))
                    o = "".join(stdout.readlines())

                for oobInterface in link['src']:

                    if "ip_eve" in link.keys():

                        connexionInformations[oobInterface['host']] = {
                            "ip_address_eve": self._ip,
                            "ip_address_host": oobInterface['ip_mgmt'],
                            "con_ext_port": oobInterface['nat'],
                            "con_int_port": oobInterface['ssh'],
                            "url": "ssh -p {} -l <username> {}".format(oobInterface['nat'], self._ip)
                        }

                        self.create_iptables_nat(
                            ssh, link['ip_pub'], link['network'], oobInterface['ip_mgmt'], oobInterface['ssh'], ipMgmtEve, oobInterface['nat'])
                    #

                    self._add_link_to_lab(link['id'], self.getNodeIDby_node_name(labName, oobInterface['host']), self.get_node_interface_id(
                        labName, self.get_node_id_by_node_name(labName, oobInterface['host']), oobInterface['port']), labName)

            else:
                self._add_link_to_lab(link['id'], self.get_node_id_by_node_name(labName, link['src']),
                                      self.get_node_interface_id(labName, self.get_node_id_by_node_name(labName, link['src']), link['sport']), labName)
                self._add_link_to_lab(link['id'], self.get_node_id_by_node_name(labName, link['dst']),
                                      self.get_node_interface_id(labName, self.get_node_id_by_node_name(labName, link['dst']), link['dport']), labName)

        self.write_in_remote_file(
            ssh, connexionInformations, "/root/.eveng/connexion_{}".format(labName), mode='w')
        ssh.close()


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _add_link_to_lab(self, networkID: str(), nodeID: str(), interfaceID: str(), labName: str()):
        """
        This function will connect a node to a Network.
        2 nodes have to be connected on the same netwrok for communicate

        -X PUT - d '{"0":1}'127.0.0.1/api/labs/Users/Lab.unl/nodes/1/interfaces'

        Args:
            param1 (str): Lab Names
            param2 (str): Nodes Names
            param3 (str): Node interface ID
            param4 (str): Network ID
        """
        print("[PyEVENG _add_link_to_lab] -",
              nodeID, interfaceID, "is deploying...")

        print(self._url+"/api/labs/"+self._folder+"/" +
              str(labName)+"/nodes/"+str(nodeID)+"/interfaces - data={\""+str(interfaceID)+"\":\""+str(networkID)+"\"}")
        self.lock_lab()
        response = requests.put(
            self._url+"/api/labs/"+self._folder+"/"+str(labName)+"/nodes/"+str(nodeID)+"/interfaces", data="{\""+str(interfaceID)+"\":\""+str(networkID)+"\"}", cookies=self._cookies, verify=False)
        
        self._requests_error(response.status_code)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _add_nodes_to_lab(self, nodesToAdd: dict(), labName: str()):
        """
        This function add some nodes to a Lab
        It uses _add_node_to_lab

        Args:
            param1 (dict): Nodes Informamations
            param2 (str): Labname
        """
        for node in nodesToAdd:
            self._add_node_to_lab(node, labName)

        if nodesToAdd.__len__() == self.get_lab_nodes_name(labName).__len__():
            print("[PyEVENG _add_nodes_to_lab] - all nodes have been deployed!")
        else:
            print("[PyEVENG _add_nodes_to_lab] - some nodes haven't been deployed!")
            raise EVENG_Exception(
                str("[PyEVENG _add_nodes_to_lab] - Nodes deployment error !"), 21)


    # --------------------------------------------------------------------------------------------------
    #
    # 
    #
    def _add_node_to_lab(self, nodesToAdd: dict(), labName: str()):
        """
        This function add a node to a Lab

        Args:
            param1 (dict): Node Informamations
            param2 (str): Labname to add nodes
        """
        print("[PyEVENG _add_node_to_lab] -",
              nodesToAdd['name'], "is deploying...")

        nodeNameAlreadyInLab = self.get_lab_nodes_name(labName)

        if nodesToAdd['name'] in nodeNameAlreadyInLab:
            print("[PyEVENG _add_node_to_lab] - a node with the name \"",
                  nodesToAdd['name'], "\" is already deployed!")

        else:
            self.lock_lab()
            PP.pprint(json.dumps(nodesToAdd))
            response = requests.post(
                self._url+"/api/labs/"+str(self._folder)+"/"+str(labName)+"/nodes", data=json.dumps(nodesToAdd), cookies=self._cookies, verify=False)

            self._requests_error(response.status_code)
            print("[PyEVENG _add_node_to_lab] -",
                  nodesToAdd['name'], "has been deployed!")




    # ##################################################################################################
    #
    #   Call to make general action on lab (start, stop, remove, create)
    #
    # ##################################################################################################
    

    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def start_lab_node(self, labName, nodeID):
        """
        This function will start a node of a lab according to lab name and node id given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param1 (str): EVE-NG node ID
        """
        if self.get_node_status(labName, nodeID) != "2":
            print("[PyEVENG start_lab_node] -",
                  labName, self.get_node_name_by_id(labName, nodeID), "is starting...")

            response = requests.get(
                self._url+"/api/labs/"+self._folder+"/"+labName+"/nodes/"+nodeID+"/start", cookies=self._cookies, verify=False)
            self._requests_error(response.status_code)

            if self.get_node_status(labName, nodeID) == "2":
                print("[PyEVENG start_lab_node] -", labName,
                      self.get_node_name_by_id(labName, nodeID), "is started !")


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def start_lab_all_nodes(self, labName: str(), *, enable=False):
        """
        This function will start all node of a lab

        Args:
            param1 (str): EVE-NG lab name
        """

        #self.check_param_type_str(labName)

        nodesID = self.get_lab_nodes_id(labName)

        # First Start Device
        for nodeID in nodesID:
          self.start_lab_node(labName, nodeID)

        if enable:
            first = True
            print("[PyEVENG start_lab_all_nodes] - no shutdown interfaces ...")
            for nodeID in nodesID:
                nodeName = self.get_node_name_by_id(labName, nodeID)
                nodeImage = self.get_node_image_and_node_id(labName, nodeName)
                if "VIOS" in nodeImage[0]:
                    telnetPort = self.get_node_telnet_port(labName, nodeID)
                    telnetIP = self.get_node_telnet_ip(labName, nodeID)
                    if first:
                        time.sleep(60)
                        first = False
                    self.enable_port(labName, telnetIP,
                                     telnetPort, nodeID, nodeName)
            print("[PyEVENG start_lab_all_nodes] - no shutdown interfaces done !")


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def stop_lab_node(self, labName, nodeID):
        """
        This function will stop a node of a lab according to lab name and node id given in parameter

        for EVE-NG PRO
        https://127.0.0.1/api/labs/Users/spine-leaf.unl/nodes/2/stop/stopmode=3

        for EVE-NG Community
        https://127.0.0.1/api/labs/Users/spine-leaf.unl/nodes/2/stop

        Args:
            param1 (str): EVE-NG lab name
            param1 (str): EVE-NG node ID

        """

        print("[PyEVENG stop_lab_node] -",
              labName, self.get_node_name_by_id(labName, nodeID), "is stopping...")

        if self.get_node_status(labName, nodeID) != "0":

            if self._community is False:
                print(self._url+"/api/labs/"+self._folder+"/" +
                      labName+"/nodes/"+nodeID+"/stop/stopmode=3")

                response = requests.get(
                    self._url+"/api/labs/"+self._folder+"/"+labName+"/nodes/"+nodeID+"/stop/stopmode=3", cookies=self._cookies, verify=False)

            else:
                print(self._url+"/api/labs/"+self._folder+"/" +
                      labName+"/nodes/"+nodeID+"/stop")
                response = requests.get(
                    self._url+"/api/labs/"+self._folder+"/"+labName+"/nodes/"+nodeID+"/stop", cookies=self._cookies, verify=False)

            self._requests_error(response.status_code)

            if self.get_node_status(labName, nodeID) == "0":
                print("[PyEVENG stop_lab_node] -",
                      labName, self.get_node_name_by_id(labName, nodeID), "is stopped !")


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def stop_lab_all_nodes_1(self, labName):
        """
        This function will stop all node of a lab

        Args:
            param1 (str): EVE-NG lab name

        """
        response = requests.get(
            self._url+"/api/labs/"+self._folder+"/"+labName+"/nodes/stop/stopmode=3", cookies=self._cookies, verify=False)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def stop_lab_all_nodes(self, labName):
        """
        This function will stop all node of a lab

        Args:
            param1 (str): EVE-NG lab name

        """

        #self.check_param_type_str(labName)

        nodesID = self.get_lab_nodes_id(labName)

        if len(nodesID) is not 0:
            for nodeID in nodesID:
                self.stop_lab_node(labName, nodeID)


    # --------------------------------------------------------------------------------------------------
    #
    # 
    #
    def create_lab(self, labInformations:dict()):
        """
        This function will create a Lab

        Args:
            param1 (dict): All lab informations
        """
        if str(labInformations['name']+".unl") in self.get_labs_in_folder():
            raise EVENG_Exception(str("[EXCEPTION][PyEVENG - create_lab] - Lab ("+labInformations['name']+") already exists in this folder"), 12)
        
        self._project = labInformations['name']+".unl"
        print("[PyEVENG create_lab] -",
              labInformations['name'], "is creating...")
        
        response = requests.post(
            self._url+"/api/labs", data=json.dumps(labInformations), cookies=self._cookies, verify=False)

        self._requests_error(response.status_code)
        print("[PyEVENG create_lab] -",
              labInformations['name'], "has been created...")


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def delete_lab(self, labName: dict()):
        """
        This function will delete a Lab

        Args:
            param1 (str): Lab name to delete
        """
        call = True
        print("[PyEVENG - delete_lab] -",
              labName, "is deleting...")
        try:
            self.stop_lab_all_nodes(labName)

        except EVENG_Exception as e:
            print(
                "[PyEVENG - delete_lab] - lab doesn't exist ... check for remove files")
            call = False

        self.remove_remote_connexion_file(labName)

        if call:
            response = requests.delete(self._url+"/api/labs/"+str(
                self._folder)+"/"+str(labName), cookies=self._cookies, verify=False)
            self._requests_error(response.status_code)

            print("[PyEVENG delete_lab] -",
                  labName, "has been deleted...")


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_description(self, labName: str()) -> str():
        """
        This function will return a string that contains lab descriptions

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            str: That contains lab description
        """

        #self.check_param_type_str(labName)

        response = self.get_lab(labName)
        return response["data"]["description"]

    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_author(self, labName: str()) -> str():
        """
        This function will return a string that contains lab author

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            str: That contains lab author
        """

        #self.check_param_type_str(labName)

        response = self.get_lab(labName)
        return response["data"]["author"]


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab_id(self, labName: str()) -> str():
        """
        This function will return a string that contains lab ID

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            str: That contains lab ID
        """

        #self.check_param_type_str(labName)

        response = self.get_lab(labName)
        return response["data"]["id"]


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_lab(self, labName: str()) -> dict():
        """
        This function will return a JSON that contains lab informations

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            json: That contains lab informations
        """
        #self.check_param_type_str(labName)

        response = requests.get(
            self._url+"/api/labs/"+self._folder+"/"+labName, cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        return json.loads(response.content)



    # ##################################################################################################
    #
    #   Call to make general action on EVE-NG VM
    #
    # ##################################################################################################

    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_labs_in_folder(self) -> list():
        """
        This function will return a list that contains all lab name in the folder

        Returns:
            list: That contains all lab name
        """
        response = requests.get(self._url+"/api/folders/"+str(self._folder),
                                cookies=self._cookies, verify=False)

        self._requests_error(response.status_code)
        data = json.loads(response.content)

        labsInFolder = list()
        for lab in data['data']['labs']:
            labsInFolder.append(lab['file'])

        return labsInFolder


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_users(self):
        """
        This function will return a JSON that contains user informations

        Returns:
            json: That contains user informations
        """
        response = requests.get(self._url+"/api/users/",
                                cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        return json.loads(response.content)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_template_by_model(self, deviceType):
        """
        This function will return a list that contains all installed nodes

        Args:
            param1 (str): Device type - Example "cumulus"

        Returns:
            list: Information about device type
        """
        response = requests.get(
            self._url+"/api/list/templates/"+str(deviceType), cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)

        return json.loads(response.content)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_image_version_by_model(self, deviceType):
        """
        This
         function will return a list that contains all installed nodes

        Args:
            param1 (str): Device type - Example "cumulus"

        Returns:
            list: Information about device type
        """
        response = requests.get(
            self._url+"/api/list/templates/"+str(deviceType), cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)

        content = json.loads(response.content)

        listResult = list()
        if "image" in content['data']['options'].keys():
            if len(content['data']['options']['image']['list']) != 0:
                for value in content['data']['options']['image']['list'].values():
                    listResult.append(value)

        return listResult


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_available(self):
        """
        This function will return a list that contains all available nodes

        Returns:
            list: That contains all available nodes
        """
        response = requests.get(
            self._url+"/api/list/templates/", cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        return json.loads(response.content)

    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_user_info(self):
        """
        This function will return a JSON that contains user informations

        Returns:
            json: That contains user informations
        """
        response = requests.get(self._url+"/api/auth",
                                cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        return json.loads(response.content)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_version_install(self, deviceType: str()):
        """
        This function will return a list that contains all installed nodes


        Returns:
            list: That contains all installed nodes
        """
        data = self.get_image_version_by_model(deviceType)
        return data


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_node_install(self) -> dict():
        """
        This function will return a list that contains all installed nodes

        Returns:
            list: That contains all installed nodes
        """
        response = requests.get(
            self._url+"/api/list/templates/", cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        data = json.loads(response.content)["data"]

        toRemove = list()
        for key, val in data.items():
            if ("missing" in val):
                toRemove.append(key)

        for key in toRemove:
            del data[key]

        return data


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def status(self) -> dict:
        """
        This function will return a JSON that contains vm infromations

        Returns:
            json: That contains vm informations
        """
        response = requests.get(self._url+"/api/status",
                                cookies=self._cookies, verify=False)
        self._requests_error(response.status_code)
        return json.loads(response.content)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def get_vm_memory(self) -> str():
        """
        This function will return a str that contains vm memory (RAM)
        Use SSH

        Returns:
            str: That contains vm mermory
        """
        GET_MEMORY_COMMAND = "free -m | grep -i mem | awk '{print $2}'"

        ssh = self._ssh_connect()

        stdin, stdout, stderr = ssh.exec_command(GET_MEMORY_COMMAND)
        return ("".join(stdout.readlines()))


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def login(self):
        """
        This function login to EVE-NG
        Store Cookie

        """
        # For avoid InsecureRequestWarning error
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if self._verbose:
            print("[PyEVENG - login] ...")

        response = requests.post(
            self._url+"/api/auth/login", data='{"username":"'+self._user+'","password":"'+self._pwd+'", "html5": "0"}', verify=False)

        self._requests_error(response.status_code)

        if self._verbose:
            print(f"[PyEVENG - login] ({response.status_code}) logged !")

        self._cookies = response.cookies


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def logout(self):
        """
        This function logout to EVE-NG        
        """
        if self._verbose:
            print("[PyEVENG - logout] ...")
        response = requests.get(
            self._url+"/api/auth/logout", cookies=self._cookies, verify=False)

        self._requests_error(response.status_code)

        if self._verbose:
            print(
                f"[PyEVENG - logout] ({response.status_code}) EVE-NG says Byyye :) !")




    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _requests_error(self, status_code):
        """
        This function will check if there is an error in the status code
        In progress

        Args:
            param1 (str): Request status code

        """
        if status_code == 400:
            raise "HTTP 400 : Bad Request"
        if status_code == 404:
            raise EVENG_Exception("HTTP 404 : Not Found", 708)
        elif status_code == 500:
            raise "HTTP 500 : Internal Server Error"
        elif status_code == 412:
            raise "HTTP 412 : please login before to make requests \n" + \
                "api= PyEVENG.PyEVENG(login, mdp, ip, port, ssl, user, pod) \n" + \
                    "api.login() \n api.get_lab_nodes"


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def check_param_type_str(self, param:str()):
        """
        This function will check if the parameter is correct

        Args:
            param1 (str): 

        """
        if type(param) is not type(str()):
            raise TypeError(
                "For <getlab(labName:str())> function you need to give a string in parameter !")


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def lock_lab(self):
        ssh = self._ssh_connect()
        stdin, stdout, stderr = ssh.exec_command(
            "find /opt/unetlab/labs/ -name '*.lock' -exec rm {} \; && echo 'LOCK LAB!'")
        o = "".join(stdout.readlines())

        if "LOCK" not in o:
            raise Exception("Error during lock_lab")
        ssh.close
        

    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def _ssh_connect(self) -> paramiko.SSHClient():
        try:
            sshClient = paramiko.SSHClient()
            sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            sshClient.connect(hostname=self._ip,
                              username=self._root, password=self._rpwd)

            return sshClient
        except paramiko.AuthenticationException as e:
            print("[PyEVENG - _ssh_connect] - Authentication issue during the SSH connection to EVE-NG VM")
        except paramiko.BadHostKeyException as e:
            print("[PyEVENG - _ssh_connect] - Bad Host Key issue during the SSH connection to EVE-NG VM")
        except paramiko.ChannelException as e:
            print("[PyEVENG - _ssh_connect] - Channel issue during the SSH connection to EVE-NG VM")
        except paramiko.SSHException as e:
            print("[PyEVENG - _ssh_connect] - SSH issue during the SSH connection to EVE-NG VM : {str(e)}")
        except TimeoutError as e:
            print(
                "[PyEVENG - _ssh_connect] - Timeout during the SSH conenction to EVE-NG VM")
    

    # --------------------------------------------------------------------------------------------------
    #
    #
    #

    def __init__(self, username, password, ipAddress, port=99999, useHTTPS=False, folder="Users", pod="0", root="root", rmdp="eve", community=True, verbose=True):
        """
        Constructor / Initializer of PyEVENG

        :param username:        EVE-NG username
        :param password:        EVE-NG password
        :param ipAddress:       EVE-NG ipAddress
        :param port:            EVE-NG port
        :param useHTTPS:        EVE-NG useHTTPS true if HTTPS is used
        :param userFolder:      EVE-NG userFolder
        :param pod:             EVE-NG project POD number
        :param root:            EVE-NG user with root privilege
        :param rmdp:            EVE-NG user with root privilege password
        :param community:       True is you use EVE-NG community version
        :param verbose:         If True logout and login message will be printed
        """

        self._ip = ipAddress
        self._user = username
        self._pwd = password
        self._cookies = requests.cookies.RequestsCookieJar()
        self._folder = folder
        self._pod = pod
        self._root = root
        self._rpwd = rmdp
        self._community = community
        self._project = ""
        self._verbose = verbose

        if useHTTPS:
            self._url = "https://" + ipAddress
            if port == 99999:
                self._port = 443
            else:
                self._port = port

        else:
            self._url = "http://" + ipAddress
            if port == 99999:
                self._port = 80
            else:
                self._port = port

        self.login()


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def __repr__(self):
        return f"<PyEVENG url={self._url}  ip={self._ip} port={self._port} user={self._user} pwd={self._pwd} \
            folder={self._folder} pod={self._pod} community={self._community} verbose={self._verbose} \
            root={self._root} rpwd={self._rpwd} cookies={self._cookies}>\n"
