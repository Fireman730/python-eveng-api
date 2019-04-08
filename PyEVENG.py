#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

__author__ = "Dylan Hamel"
__version__ = "0.1"
__email__ = "dylan.hamel@protonmail.com"
__status__ = "Prototype"

# Default value used for exit()
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

######################################################
#
# Import Library
#
try:
    from os import listdir
    from os.path import isfile, join
    from os import mkdir
except ImportError as importError:
    print("Error import listdir")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import cumulus_device, extreme_device
except ImportError as importError:
    print("Error import cumulus_device")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import paramiko
except ImportError as importError:
    print("Error import paramiko")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import urllib3
except ImportError as importError:
    print("Error import urllib3")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import requests
except ImportError as importError:
    print("Error import requests")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import json
except ImportError as importError:
    print("Error import json")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import sphinx
except ImportError as importError:
    print("Error import sphinx")
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
    # ------------------------------------------------------------------------------------------
    # Other commands
    # Using SSH
    
    def retrieveUNL(self, labName, pathToXML):
        labPath = "/opt/unetlab/labs/"+self._userFolder+"/"
        print("[PyEVENG - retrieveUNL] -", labPath+labName+".unl")

        try:
            ssh = self.sshConnect()
            ftp_client = ssh.open_sftp()
            ftp_client.get(str(labPath+labName+".unl"), pathToXML)
            ftp_client.close()
            ssh.close()
        except Exception as e:
            print(e)


    def replaceUNL(self, labName, pathToUNL):
        labPath = "/opt/unetlab/labs/"+self._userFolder+"/"
        print("[PyEVENG - replaceUNL] -", labPath+labName)
        try:
            ssh = self.sshConnect()
            ftp_client = ssh.open_sftp()
            ftp_client.put(pathToUNL,
                           str(labPath+labName+".unl"))
            ftp_client.close()
            ssh.close()
        except Exception as e:
            print(e)


    # ------------------------------------------------------------------------------------------
    # Getters (project, labs, node, config, ...)
    # Using REST API only
    def getBackupNodesConfig(self, yamlFiles: dict()):
        for lab in yamlFiles['labs']:
            if "all" in lab['hostname']:
                for hostname in self.getLabNodesName(lab['labname']):
                    self.getBackupConfig(lab['bck_path'], lab['labname'], hostname)
            else:
                for hostname in lab['hostname']:
                    self.getBackupConfig(lab['bck_path'], lab['labname'], hostname)

    
    def getBackupConfig(self, path:str(), project_name: str(), nodeName: str()):
        """
        This function will return a string that defines device image

        Args:
            param1 (str): EVE-NG Project Name.
            param2 (str): EVE-NG Node ID.
        
        Returns:
            str: Device image
        """
        allNodesID = self.getLabNodesID(project_name)
        allNodes = self.getLabNodes(project_name)
        for node in allNodes['data'].values():
            if node['name'] == nodeName:
                nodeImage = node['image']
                nodeID = node['id']
            
        nodeImage = nodeImage.upper()

        try:
            mkdir(path+"/"+project_name)
        except OSError as e:
            print("[PyEVENG - getBackupConfig] create project folder", e)

        try:
            mkdir(path+"/"+project_name+"/"+nodeName)
        except OSError as e:
            print("[PyEVENG - getBackupConfig] create node folder", e)

        path = path+"/"+project_name+"/"+nodeName
    
        if "CUMULUS" in nodeImage :
            self.getCumulusBackup(path, project_name, nodeName, nodeID)
        elif "EXTREME" in nodeImage:
            self.getExtremeBackup(path, project_name, nodeName, nodeID)

    def getExtremeBackup(self, path, projectName, nodeName, nodeID):
        """
        This function backup Extreme Network configuration files in path given in parameter
        Files will be retrieve with paramiko SFTP

        Args:
            param1 (str): Path where save configuration files.
            param2 (str): EVE-NG Project Name.
            param3 (str): EVE-NG Node ID.
        
        """
        extreme = extreme_device.ExtremeDevice(
            self._ipAddress, self._root, self._password, path,
            self._pod, projectName, self.getLabID(projectName), nodeName, nodeID)

        extreme.getConfigVerbose()

    def getCumulusBackup(self, path, projectName, nodeName, nodeID):
        """
        This function backup Cumulus Network configuration files in path given in parameter
        Files will be retrieve with paramiko SFTP

        Args:
            param1 (str): Path where save configuration files.
            param2 (str): EVE-NG Project Name.
            param3 (str): EVE-NG Node ID.
        
        """
        cumulus = cumulus_device.CumulusDevice(
            self._ipAddress, self._root, self._password, path, 
            self._pod, projectName, self.getLabID(projectName), nodeName, nodeID)

        cumulus.getConfigVerbose()

    # ------------------------------------------------------------------------------------------
    # Getters (project, labs, node, config, ...)
    # Using REST API only
    
    def getLabTopology(self, labName):
        """
        This function will return a JSON that contains informations about labs topology

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            json: That contains topology informations
        """
        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/topology", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def getLabLinks(self, labName):
        """
        This function will return a JSON that contains informations about labs links

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            json: That contains links informations
        """
        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/links", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def getNodeImage(self, labName, nodeID):
        """
        This function will return a string that contains nodes image according to node ID and the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): EVE-NG node ID

        Returns:
            str: That contains node image
        """
        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/nodes/"+nodeID, cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)["data"]["image"]

    def getLabNodeInterfaces(self, labName:str(), nodeID:str()) -> dict():
        """
        This function will return a JSON that contains informations about labs interfaces

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): EVE-NG node ID

        Returns:
            json: That contains interfaces informations
        """
        self.check_param_type_str(labName)
        self.check_param_type_str(nodeID)

        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/nodes/"+nodeID+"/interfaces", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    # def getLabNodesAddressAccessMethod(self, labName):
    # This function is not available for the moment

    def getLabNodesAccessMethod(self, labName:str()) -> dict():
        """
        This function will return a dictionnary that contains informations access method
        
        Example :
            - {"Spine01": "telnet", "Linux", "vnc"}
            
        Args:
            param1 (str): EVE-NG lab name

        Returns:
            dict: That contains key = hostname, value = access method
        """

        self.check_param_type_str(labName)

        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        content = json.loads(response.content)["data"]

        nodesAccessMethod = dict()
        for key, val in content.items():
            nodesAccessMethod[val["name"]] = val["console"]

        return nodesAccessMethod

    def getLabNodesID(self, labName:str()) -> list():
        """
        This function will return a list that contains all nodes ID according to the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            list: That contains all node ID
        """

        self.check_param_type_str(labName)

        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        content = json.loads(response.content)["data"]

        nodesID = list()
        for key, val in content.items():
            nodesID.append(key)

        return nodesID

    def getLabNodesName(self, labName:str()) -> list():
        """
        This function will return a list that contains all nodes name according to the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            list: That contains all node name
        """

        self.check_param_type_str(labName)

        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        content = json.loads(response.content)["data"]

        nodesName = list()
        if content.__len__() == 0:
            return nodesName
        for key, val in content.items():
            nodesName.append(val["name"])
            
        return nodesName

    def getLabNodes(self, labName:str()) -> dict():
        """
        This function will return a JSON that contains informations about all nodes according to the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            json: That contains nodes informations
        """

        self.check_param_type_str(labName)

        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)
    
    def getNodeIDbyNodeName(self, labName:str(), nodeName:str()) -> str():
        """
        This function will nodeID regarding to the nodeName given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): Node name

        Returns:
            str: nodeID
        """
        nodeID = str()
        allNodesID = self.getLabNodesID(labName)
        allNodes = self.getLabNodes(labName)
        for node in allNodes['data'].values():
                if node['name'] == nodeName:
                    nodeID = node['id']
        return nodeID
        

    def getLabNode(self, labName:str(), nodeID:str()) -> dict():
        """
        This function will return a JSON that contains informations about all nodes according to the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param1 (str): EVE-NG node ID

        Returns:
            json: That contains nodes informations
        """

        self.check_param_type_str(labName)
        self.check_param_type_str(nodeID)

        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/nodes/"+nodeID, cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def getLabDescription(self, labName:str()) -> str():
        """
        This function will return a string that contains lab descriptions

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            str: That contains lab description
        """

        self.check_param_type_str(labName)

        response = self.getLab(labName)
        return response["data"]["description"]

    def getLabAuthor(self, labName:str()) -> str():
        """
        This function will return a string that contains lab author

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            str: That contains lab author
        """

        self.check_param_type_str(labName)

        response = self.getLab(labName)
        return response["data"]["author"]

    def getLabID(self, labName:str()) -> str():
        """
        This function will return a string that contains lab ID

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            str: That contains lab ID
        """

        self.check_param_type_str(labName)

        response = self.getLab(labName)
        return response["data"]["id"]
    
    def getLab(self, labName:str()) -> dict():
        """
        This function will return a JSON that contains lab informations

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            json: That contains lab informations
        """            
        self.check_param_type_str(labName)

        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName, cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)


    def getUsers(self):
        """
        This function will return a JSON that contains user informations

        Returns:
            json: That contains user informations
        """
        response = requests.get(self._url+"/api/users/",
                                cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def status(self) -> dict:
        """
        This function will return a JSON that contains vm infromations

        Returns:
            json: That contains vm informations
        """
        response = requests.get(self._url+"/api/status",
                                cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def startLabNode(self, labName, nodeID):
        """
        This function will start a node of a lab according to lab name and node id given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param1 (str): EVE-NG node ID
        """
        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/nodes/"+nodeID+"/start", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)

    def startLabAllNodes(self, labName:str()):
        """
        This function will start all node of a lab

        Args:
            param1 (str): EVE-NG lab name
        """

        self.check_param_type_str(labName)

        nodesID = self.getLabNodesID(labName)

        for nodeID in nodesID:
          self.startLabNode(labName, nodeID)

    def stopLabNode(self, labName, nodeID):
        """
        This function will stop a node of a lab according to lab name and node id given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param1 (str): EVE-NG node ID

        """
        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/nodes/"+nodeID+"/stop", cookies=self._cookies, verify=False)
        # self.requestsError(response.status_code)

    def stopLabAllNodes(self, labName):
        """
        This function will stop all node of a lab

        Args:
            param1 (str): EVE-NG lab name

        """
        response = requests.get(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/nodes/stop", cookies=self._cookies, verify=False)
    
    # ------------------------------------------------------------------------------------------
    # Authentification, Users and System
    def getNodeInstall(self) -> dict():
        """
        This function will return a list that contains all installed nodes

        Returns:
            list: That contains all installed nodes
        """
        response = requests.get(
            self._url+"/api/list/templates/", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        data = json.loads(response.content)["data"]

        toRemove = list()
        for key, val in data.items():
            if ("missing" in val):
                toRemove.append(key)

        for key in toRemove:
            del data[key]

        return data

    def getNodeAvailable(self):
        """
        This function will return a list that contains all available nodes

        Returns:
            list: That contains all available nodes
        """
        response = requests.get(
            self._url+"/api/list/templates/", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def getUserInfo(self):
        """
        This function will return a JSON that contains user informations

        Returns:
            json: That contains user informations
        """
        response = requests.get(self._url+"/api/auth",
                                cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def login(self):
        """
        This function login to EVE-NG
        Store Cookie

        """
        # For avoid InsecureRequestWarning error
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.post(
            self._url+"/api/auth/login", data='{"username":"admin","password":"eve"}', verify=False)

        self.requestsError(response.status_code)
        self._cookies = response.cookies

    def logout(self):
        """
        This function logout to EVE-NG        
        """
        response = requests.post(
            self._url+"/api/auth/logout", cookies=self._cookies, verify=False)

    # --------------------------------------------------------------------------------------------------
    #
    # CREATE functions
    #
    def createLab(self, labInformations:dict()):
        """
        This function Will create a Lab

        Args:
            param1 (dict): All lab informations
        """
        print("[PyEVENG addNodeToLab] -", labInformations['name'], "is creating...")
        response = requests.post(
            self._url+"/api/labs", data=json.dumps(labInformations), cookies=self._cookies, verify=False)

        self.requestsError(response.status_code)
        print("[PyEVENG addNodeToLab] -",
              labInformations['name'], "has been created...")
    # --------------------------------------------------------------------------------------------------
    #
    # EDIT (POST) functions
    #

    def addNodeToLab(self, nodesToAdd: dict(), labName: str()):
        """
        This function add a node to a Lab

        Args:
            param1 (dict): Node Informamations
            param2 (str): Labname to add nodes
        """
        print("[PyEVENG addNodeToLab] -", nodesToAdd['name'], "is deploying...")

        nodeNameAlreadyInLab = self.getLabNodesName(labName)
    
        if nodesToAdd['name'] in nodeNameAlreadyInLab:
            print("[PyEVENG addNodeToLab] - a node with the name \"",
                  nodesToAdd['name'], "\" is already deployed!")

        else:
            #self.lock_lab()
            response = requests.post(
                self._url+"/api/labs/"+self._userFolder+"/"+labName+"/nodes", data=json.dumps(nodesToAdd), cookies=self._cookies, verify=False)

            self.requestsError(response.status_code)
            print("[PyEVENG addNodeToLab] -", nodesToAdd['name'], "has been deployed!")
    
    def addNodesToLab(self, nodesToAdd: dict(), labName:str()):
        """
        This function add some nodes to a Lab
        It uses addNodeToLab

        Args:
            param1 (dict): Nodes Informamations
            param2 (str): Labname
        """
        for node in nodesToAdd:
            self.addNodeToLab(node, labName)

        if nodesToAdd.__len__() == self.getLabNodesName(labName).__len__():
            print("[PyEVENG addNodesToLab] - all nodes have been deployed!")
        else:
            print("[PyEVENG addNodesToLab] - some nodes haven't been deployed!")
            raise Exception("[PyEVENG addNodesToLab] - Nodes deployment error !")
        

    def addNetworksToLab(self, networksToAdd: dict(), labName:str()):
        """
        This function add some network to a Lab

        Args:
            param1 (dict): Nodes Informamations
            param2 (str): Labname
        """
        data = dict()

        print(self.getLabTopology(labName))

        for link in networksToAdd:
            data['name'] = str(link['src']+"("+link['sport']+")--"+link['dst']+"("+link['dport'] + ")")
            data['type'] = str(link['network'])
            self.addNetworkToLab(data, labName)
        
        print(self.getLabTopology(labName))

    def addNetworkToLab(self, networkToAdd: dict(), labName: str()):
        """
        This function add some links to a Lab

        Args:
            param1 (dict): Nodes Informamations
            param2 (str): Labname
        """
        print("[PyEVENG addNetworkToLab] -",
              networkToAdd['name'], "is deploying...")

        self.lock_lab()
        response = requests.post(
            self._url+"/api/labs/"+self._userFolder+"/"+labName+"/networks", data=json.dumps(networkToAdd), cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)

        print("[PyEVENG addNetworkToLab] -",
              networkToAdd['name'], "(",str(response.status_code),") has been deployed!")

    def addNetworksLinksToLab(self, interfacesToAdd: dict(), labName: str()):
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
        self.addNetworksToLab(interfacesToAdd, labName)
        self.addLinksToLab(interfacesToAdd, labName)

    def addLinksToLab(self, interfaceToAdd: dict(), labName: str()):
        """
        This function add some links to a Lab

        Args:
            param1 (dict): Nodes Informamations
            param2 (str): Labname
        """
        data = dict()
        nodeSrcID = str()
        nodeDstID = str()
        for link in interfaceToAdd:
            print("******", link)
            nodeSrcID = self.getNodeIDbyNodeName(labName, link['src'])
            nodeDstID = self.getNodeIDbyNodeName(labName, link['dst'])
            
            self.addLinkToLab(link['id'], nodeSrcID,
                              link['sport'][-1:], labName)
            self.addLinkToLab(link['id'], nodeDstID,
                              link['dport'][-1:], labName)

        
    def addLinkToLab(self, networkID: str(), nodeID:str(), interfaceID:str(), labName: str()):
        """
        This function will connect a node to a Network.
        2 nodes have to be connected on the same netwrok for communicate

        -X PUT - d '{"0":1}'127.0.0.1/api/labs/Users/Lab.unl/nodes/1/interfaces'

        Args:
            param1 (str): Lab Names
            param1 (str): Nodes Names
            param2 (str): Node interface ID
            param3 (str): Network ID
        """
        print("[PyEVENG addNetworkToLab] -",
              nodeID, interfaceID, "is deploying...")

        print(self._url+"/api/labs/"+self._userFolder+"/" +
              str(labName)+"/nodes/"+str(nodeID)+"/interfaces")
        print("{\""+str(interfaceID)+"\":\""+str(networkID)+"\"}")
        self.lock_lab()
        response = requests.put(
            self._url+"/api/labs/"+self._userFolder+"/"+str(labName)+"/nodes/"+str(nodeID)+"/interfaces", data="{\""+str(interfaceID)+"\":\""+str(networkID)+"\"}", cookies=self._cookies, verify=False)
        
        self.requestsError(response.status_code)


    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def requestsError(self, status_code):
        """
        This function will check if there is an error in the status code
        In progress

        Args:
            param1 (str): Request status code

        """
        if status_code == 400:
            raise "HTTP 400 : Bad Request"
        if status_code == 400:
            raise "HTTP 404 : Not Found"
        elif status_code == 500:
            raise "HTTP 500 : Internal Server Error"
        elif status_code == 412:
            raise "HTTP 412 : please login before to make requests \n" + \
                "api= PyEVENG.PyEVENG(login, mdp, ip, port, ssl, user, pod) \n" + \
                    "api.login() \n api.getLabNodes"



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
        ssh = self.sshConnect()
        stdin, stdout, stderr = ssh.exec_command(
            "find /opt/unetlab/labs/ -name '*.lock' -exec rm {} \; && echo 'LOCK LAB!'")
        o = "".join(stdout.readlines())

        if "LOCK" not in o:
            raise Exception("Error during lock_lab")
        ssh.close
        

    def sshConnect(self) -> paramiko.SSHClient():
        sshClient = paramiko.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshClient.connect(hostname=self._ipAddress,
                          username=self._root, password=self._rootPassword)

        return sshClient

    def __init__(self, username, password, ipAddress, port=99999, useHTTPS=False, userFolder="Users", pod="0", root="root", rmdp="eve"):
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
        """

        self._ipAddress = ipAddress
        self._username = username
        self._password = password
        self._ipAddress = ipAddress
        self._cookies = requests.cookies.RequestsCookieJar()
        self._userFolder = userFolder
        self._pod = pod
        self._root = root
        self._rootPassword = rmdp

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
