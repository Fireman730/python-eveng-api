#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# Default value used for exit()
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

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

    def status(self):
        response = requests.get(self._url+"/api/status", cookies=self._cookies)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def getUserInfo(self):
        response = requests.get(self._url+"/api/auth", cookies=self._cookies)
        self.requestsError(response.status_code)
        return json.loads(response.content)

    def login(self):
        response = requests.post(
            self._url+"/api/auth/login", data='{"username":"admin","password":"eve"}')

        self.requestsError(response.status_code)
        self._cookies = response.cookies

    def logout(self):

        response = requests.post(self._url+"/api/auth/logout")
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
    def __init__(self, username, password, ipAddress, port=99999, useHTTPS=False):
        """
        :param username:        EVE-NG username
        :param password:        EVE-NG password
        :param ipAddress:       EVE-NG ipAddress
        :param port:            EVE-NG port
        :param useHTTPS:        EVE-NG useHTTPS true if HTTPS is used
        """

        self._ipAddress = ipAddress
        self._username = username
        self._password = password
        self._ipAddress = ipAddress
        self._cookies = requests.cookies.RequestsCookieJar()

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
