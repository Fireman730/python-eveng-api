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
    from exceptions.EveExceptions import EVENG_Exception
except ImportError as importError:
    print("Error import listdir")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import yaml
except ImportError as importError:
    print("Error import yaml")
    print(importError)
    exit(EXIT_FAILURE)

try:
    from abc import ABC, abstractmethod
except ImportError as importError:
    print("Error import abc - abstractmethod")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import paramiko
except ImportError as importError:
    print("Error import paramiko")
    print(importError)
    exit(EXIT_FAILURE)

######################################################
#
# Class
#
class DeviceQEMUAbstract(ABC):
    
    _shellCommandsUmountNBD = yaml.load(
        open("./commands/common/command_umount_nbd.yml"))
    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #

    @abstractmethod
    def mount_nbd(self, sshClient: paramiko.SSHClient):
        pass

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def checkMountNBD(self, sshClient: paramiko.SSHClient):
        stdin, stdout, stderr = sshClient.exec_command(
            "mount | grep nbd | wc -l")

        o = "".join(stdout.readlines())

        print(f"[DeviceQEMUAbstract - checkMountNBD] {o}")
        
        if str(o[0]) != "1":
            raise EVENG_Exception(
                "[DeviceQEMUAbstract - checkMountNBD] - error with umount nbd", 802)

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def umountNBDWithOutCheck(self, sshClient: paramiko.SSHClient):
        for command in self._shellCommandsUmountNBD:
            stdin, stdout, stderr = sshClient.exec_command(command)
            o = "".join(stdout.readlines())

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def umountNBD(self, sshClient: paramiko.SSHClient):
        for command in self._shellCommandsUmountNBD:
            stdin, stdout, stderr = sshClient.exec_command(command)
            o = "".join(stdout.readlines())

        if "nbd0" not in o:
            raise EVENG_Exception(
                "[DeviceQEMUAbstract - umountNBD] - error with umount nbd", 801)

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def sshConnect(self) -> paramiko.SSHClient():
        sshClient = paramiko.SSHClient()
        sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        sshClient.connect(hostname=self._ip,
                          username=self._root, password=self._pwd)

        return sshClient


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

    def __init__(self, ip, root, pwd, path, pod, labName, labID, nodeName, nodeID):
        self._ip = ip
        self._root = root
        self._pwd = pwd
        self._path = path
        self._pod = pod
        self._labID = labID
        self._nodeID = nodeID
        self._labName = labName
        self._nodeName = nodeName
