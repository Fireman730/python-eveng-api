#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# Default value used for exit()


EXIT_SUCCESS = 0
EXIT_FAILURE = 1

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

class PyEVENG:
    """
    This class is a Python client for retrieve information about your EVE-NG VM.
    The main aim is provided an Python script for automate an deploy your network un EVE-NG    
    """



    # ------------------------------------------------------------------------------------------
    # Getters (project, labs, node, config, ...)
    # Using REST API only
    
    def getBackupConfig(self, project_name, node_id):
        nodeImage = self.getNodeImage(project_name, node_id)
        nodeImage = nodeImage.upper()
    
        if "CUMULUS" in nodeImage :
            return self.getCumulusNodeConfigFilesByProjectIDAndNodeID(project_name, node_id)


    def getCumulusNodeConfigFilesByProjectIDAndNodeID(self, project_name, node_id):
        """
        This function will return a list that contains node configuration according to project_name and name_uid given in parameter
        This function only works with Cumulus Network Nodes !!

        Args:
            param1 (str): EVE-NG Project Name.
            param2 (str): EVE-NG Node ID.
        
        Returns:
            list: list of configuration files
        """

        sshClient = paramiko.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshClient.connect(hostname=self._ipAddress,
                        username="root", password=self._password)

        stdin, stdout, stderr = sshClient.exec_command(
            "ls /opt/unetlab/tmp/"+self._pod+"/"+self.getLabID(project_name)+"/"+node_id+"/ | grep qcow2")
        qcow2 = stdout.readlines()
        if qcow2.__len__() is not 0:
            stdin, stdout, stderr = sshClient.exec_command(
                "sudo modprobe nbd max_part=8")
            stdout.readlines()
            stdin, stdout, stderr = sshClient.exec_command(
                "sudo qemu-nbd -c /dev/nbd0 /opt/unetlab/tmp/"+self._pod+"/"+self.getLabID(project_name)+"/"+node_id +"/virtioa.qcow2")
            stdout.readlines()
            stdin, stdout, stderr = sshClient.exec_command(
                "partx -a /dev/nbd0")
            stdout.readlines()
            stdin, stdout, stderr = sshClient.exec_command(
                "mkdir /mnt/disk")
            stdout.readlines()
            stdin, stdout, stderr = sshClient.exec_command(
                "sudo mount /dev/nbd0p4 /mnt/disk/")
            stdout.readlines()
            stdin, stdout, stderr = sshClient.exec_command(
                "sudo ls /mnt/disk/etc/")
            output = stdout.readlines()

            cumulusNetworkConfigurationFilesInETC = list()
            for configFile in output:
                cumulusNetworkConfigurationFilesInETC.append(configFile[:-1])

            stdin, stdout, stderr = sshClient.exec_command(
                "sudo umount /mnt/disk")
            stdout.readlines()
            stdin, stdout, stderr = sshClient.exec_command(
                "sudo qemu-nbd --disconnect /dev/nbd0")
            o = "".join(stdout.readlines())
            if "nbd0" not in o:
                raise Exception("Error during nbd disconnect")

            return cumulusNetworkConfigurationFilesInETC
    

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
            self._url+"/api/labs/Users/"+labName+"/topology", cookies=self._cookies, verify=False)
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
            self._url+"/api/labs/Users/"+labName+"/links", cookies=self._cookies, verify=False)
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
            self._url+"/api/labs/Users/"+labName+"/nodes/"+nodeID, cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)["data"]["image"]

    def getLabNodeInterfaces(self, labName, nodeID):
        """
        This function will return a JSON that contains informations about labs interfaces

        Args:
            param1 (str): EVE-NG lab name
            param2 (str): EVE-NG node ID

        Returns:
            json: That contains interfaces informations
        """
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes/"+nodeID+"/interfaces", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    # def getLabNodesAddressAccessMethod(self, labName):
    # This function is not available for the moment

    def getLabNodesAccessMethod(self, labName):
        """
        This function will return a dictionnary that contains informations access method
        
        Example :
            - {"Spine01": "telnet", "Linux", "vnc"}
            
        Args:
            param1 (str): EVE-NG lab name

        Returns:
            dict: That contains key = hostname, value = access method
        """
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        content = json.loads(response.content)["data"]

        nodesAccessMethod = dict()
        for key, val in content.items():
            nodesAccessMethod[val["name"]] = val["console"]

        return nodesAccessMethod

    def getLabNodesID(self, labName):
        """
        This function will return a list that contains all nodes ID according to the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            list: That contains all node ID
        """
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        content = json.loads(response.content)["data"]

        nodesID = list()
        for key, val in content.items():
            nodesID.append(key)

        return nodesID

    def getLabNodesName(self, labName):
        """
        This function will return a list that contains all nodes name according to the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            list: That contains all node name
        """
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        content = json.loads(response.content)["data"]

        nodesName = list()
        for key, val in content.items():
            nodesName.append(val["name"])
            
        return nodesName

    def getLabNodes(self, labName):
        """
        This function will return a JSON that contains informations about all nodes according to the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            json: That contains nodes informations
        """
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def getLabNode(self, labName, nodeID):
        """
        This function will return a JSON that contains informations about all nodes according to the lab name given in parameter

        Args:
            param1 (str): EVE-NG lab name
            param1 (str): EVE-NG node ID

        Returns:
            json: That contains nodes informations
        """
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes/"+nodeID, cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def getLabDescription(self, labName):
        """
        This function will return a string that contains lab descriptions

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            str: That contains lab description
        """
        response = self.getLab(labName)
        return response["data"]["description"]

    def getLabAuthor(self, labName):
        """
        This function will return a string that contains lab author

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            str: That contains lab author
        """
        response = self.getLab(labName)
        return response["data"]["author"]

    def getLabID(self, labName):
        """
        This function will return a string that contains lab ID

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            str: That contains lab ID
        """
        response = self.getLab(labName)
        return response["data"]["id"]
    
    def getLab(self, labName):
        """
        This function will return a JSON that contains lab informations

        Args:
            param1 (str): EVE-NG lab name

        Returns:
            json: That contains lab informations
        """
        response = requests.get(
            self._url+"/api/labs/Users/"+labName, cookies=self._cookies, verify=False)
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

    def status(self):
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
            self._url+"/api/labs/Users/"+labName+"/nodes/"+nodeID+"/start", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)

    def startLabAllNodes(self, labName):
        """
        This function will start all node of a lab

        Args:
            param1 (str): EVE-NG lab name
        """
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
            self._url+"/api/labs/Users/"+labName+"/nodes/"+nodeID+"/stop", cookies=self._cookies, verify=False)
        # self.requestsError(response.status_code)

    def stopLabAllNodes(self, labName):
        """
        This function will stop all node of a lab

        Args:
            param1 (str): EVE-NG lab name

        """
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes/stop", cookies=self._cookies, verify=False)
    
    # ------------------------------------------------------------------------------------------
    # Authentification, Users and System

    def getNodeInstall(self):
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
        elif status_code == 412:
            raise "HTTP 412 : please login before to make requests \n" + \
                "api= PyEVENG.PyEVENG(login, mdp, ip, port, ssl, user, pod) \n" + \
                    "api.login() \n api.getLabNodes"



    # --------------------------------------------------------------------------------------------------
    #
    #
    #

    def __init__(self, username, password, ipAddress, port=99999, useHTTPS=False, userFolder="Users", pod="0"):
        """
        Constructor of PyEVENG

        :param username:        EVE-NG username
        :param password:        EVE-NG password
        :param ipAddress:       EVE-NG ipAddress
        :param port:            EVE-NG port
        :param useHTTPS:        EVE-NG useHTTPS true if HTTPS is used
        :param userFolder:      EVE-NG userFolder
        """

        self._ipAddress = ipAddress
        self._username = username
        self._password = password
        self._ipAddress = ipAddress
        self._cookies = requests.cookies.RequestsCookieJar()
        self._userFolder = userFolder
        self._pod = pod


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
