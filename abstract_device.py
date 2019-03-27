#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# Default value used for exit()
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

try:
    from abc import ABC, abstractmethod
except ImportError as importError:
    print("Error import abc - abstractmethod")
    print(importError)
    exit(EXIT_FAILURE)


class DeviceQEMUAbstract(ABC):

    @abstractmethod
    def pushConfig(self):
        pass

    @abstractmethod
    def getConfigVerbose(self):
        pass
    
    @abstractmethod
    def getConfigSimple(self):
        pass

    @abstractmethod
    def getConfig(self, commands):
        pass

    def __init__(self, ip, root, pwd, path, pod, labID, nodeID):
        self._ip = ip
        self._root = root
        self._pwd = pwd
        self._path = path
        self._pod = pod
        self._labID = labID
        self._nodeID = nodeID
