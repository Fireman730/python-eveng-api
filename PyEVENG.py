#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# Default value used for exit()


EXIT_SUCCESS = 0
EXIT_FAILURE = 1

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


class PyEVENG:

    # ------------------------------------------------------------------------------------------
    # Getters (project, labs, node, config, ...)
    
    def getLabTopology(self, labName):
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/topology", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def getLabNodeInterface(self, labName, nodeID):
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes/"+nodeID+"/interfaces", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    # def getLabNodesAddressAccessMethod(self, labName):

    def getLabNodesAccessMethod(self, labName):
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        content = json.loads(response.content)["data"]

        nodesAccessMethod = dict()
        for key, val in content.items():
            nodesAccessMethod[val["name"]] = val["console"]

        return nodesAccessMethod

    def getLabNodesID(self, labName):
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        content = json.loads(response.content)["data"]

        nodesID = list()
        for key, val in content.items():
            nodesID.append(key)

        return nodesID

    def getLabNodesName(self, labName):
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        content = json.loads(response.content)["data"]

        nodesName = list()
        for key, val in content.items():
            nodesName.append(val["name"])
            
        return nodesName

    def getLabNodes(self, labName):
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def getLabDescription(self, labName):
        response = self.getLab(labName)
        return response["data"]["description"]

    def getLabAuthor(self, labName):
        response = self.getLab(labName)
        return response["data"]["author"]

    def getLabID(self, labName):
        response = self.getLab(labName)
        return response["data"]["id"]
    
    def getLab(self, labName):
        response = requests.get(
            self._url+"/api/labs/Users/"+labName, cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)


    def getUsers(self):
        response = requests.get(self._url+"/api/users/",
                                cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def status(self):
        response = requests.get(self._url+"/api/status",
                                cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def startLabNode(self, labName, nodeID):
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes/"+nodeID+"/start", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)

    def startLabAllNodes(self, labName):
        nodesID = self.getLabNodesID(labName)

        for nodeID in nodesID:
          self.startLabNode(labName, nodeID)

    def stopLabNode(self, labName, nodeID):
        print(self._url+"/api/labs/Users/"+labName+"/nodes/"+nodeID+"/stop")
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes/"+nodeID+"/stop", cookies=self._cookies, verify=False)
        print(response.content)
        print(response)
        # self.requestsError(response.status_code)

    def stopLabAllNodes(self, labName):
        response = requests.get(
            self._url+"/api/labs/Users/"+labName+"/nodes/stop", cookies=self._cookies, verify=False)
        print(response.content)
        print(response)
        


    # ------------------------------------------------------------------------------------------
    # Authentification, Users and System

    def getNodeInstall(self):
        
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
        response = requests.get(
            self._url+"/api/list/templates/", cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def getUserInfo(self):
        response = requests.get(self._url+"/api/auth",
                                cookies=self._cookies, verify=False)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def login(self):
        # For avoid InsecureRequestWarning error
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.post(
            self._url+"/api/auth/login", data='{"username":"admin","password":"eve"}', verify=False)

        self.requestsError(response.status_code)
        self._cookies = response.cookies

    def logout(self):
        response = requests.post(
            self._url+"/api/auth/logout", cookies=self._cookies, verify=False)
        print(response)
        

    # --------------------------------------------------------------------------------------------------
    #
    #
    #
    def requestsError(self, status_code):

        if status_code == 400:
            raise "HTTP 400 : Bad Request"



    # --------------------------------------------------------------------------------------------------
    #
    #
    #

    def __init__(self, username, password, ipAddress, port=99999, useHTTPS=False, userFolder="Users", ):
        """
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
