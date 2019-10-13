#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""
Description ...

"""


__author__ = "Dylan Hamel"
__maintainer__ = "Dylan Hamel"
__version__ = "1.0"
__email__ = "dylan.hamel@protonmail.com"
__status__ = "Production"
__copyright__ = "Copyright 2019"
__license__ = "MIT"

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
######################################################
#
# Import Library
#
try:
    from os import listdir
    from os.path import isfile, join
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
    import paramiko
except ImportError as importError:
    print("Error import paramiko")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import devices.abstract_device
except ImportError as importError:
    print("Error import abc - Cumulus abstractmethod")
    print(importError)
    exit(EXIT_FAILURE)

try:
    from exceptions.EveExceptions import EVENG_Exception
except ImportError as importError:
    print("Error import listdir")
    print(importError)
    exit(EXIT_FAILURE)
######################################################
#
# Constantes
#

######################################################
#
# Class
#


class AristaDevice(devices.abstract_device.DeviceQEMUAbstract):
    
    # ------------------------------------------------------------------------------------------------------------
    #
    # Class variables
    #

    _configFiles = yaml.load(
        open("./commands/arista/config_files.yml"))
    _pushConfigFiles = yaml.load(
        open("./commands/arista/push_config_files.yml"))
    _shellCommandsMountNBD = yaml.load(
        open("./commands/arista/command_mount_nbd.yml"))

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def mount_nbd(self, sshClient: paramiko.SSHClient):
        first = True
        for command in self._shellCommandsMountNBD:
            print("[EVE-NG mount_nbd]", command)
            stdin, stdout, stderr = sshClient.exec_command(command)
            output = "".join(stdout.readlines())
            if first:
                print("[EVE-NG mount_nbd]", "sudo qemu-nbd -c /dev/nbd0 /opt/unetlab/tmp/" + str(
                    self._pod) + "/" + str(self._labID) + "/" + str(self._nodeID) + "/hda.qcow2")
                stdin, stdout, stderr = sshClient.exec_command(
                    "sudo qemu-nbd -c /dev/nbd0 /opt/unetlab/tmp/" + str(self._pod) + "/" + str(self._labID) + "/" + str(self._nodeID) + "/hda.qcow2")
                output = stdout.readlines()
                first = False

            if "error adding partition 1" in output:
                raise EVENG_Exception(
                    "[AristaDevice - mount_nbd] - Error during partition sudo partx -a /dev/nbd0", 802)

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def pushOOB(self):
        self.pushConfig()


    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def pushConfig(self):
        configFiles = [f for f in listdir(
            self._path) if "DS" not in f and isfile(join(self._path, f))]

        ssh = self.sshConnect()
        self.mountNBD(ssh)
        self.checkMountNBD(ssh)

        ftp_client = ssh.open_sftp()

        for file in configFiles:
            try:
                print("[AristaDevice - pushConfig] copy",
                      str(self._path+"/"+file), "to", str(self._pushConfigFiles[file])+file)
                ftp_client.put(localpath=(str(self._path+"/"+file)),
                               remotepath=(str(self._pushConfigFiles[file])+file))
            except Exception as e:
                print(e)

        self.umountNBD(ssh)

        ftp_client.close()
        ssh.close()

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def getConfigSimple(self):
        self.getConfigVerbose()

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def getConfigVerbose(self):
        self.getConfig(self._configFiles, True)

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def getConfig(self, commands: list(), v):
        ssh = self.sshConnect()

        print("[AristaDevice - getConfig]", self._labName, self._nodeName)

        self.umountNBDWithOutCheck(ssh)
        self.mountNBD(ssh)
        self.checkMountNBD(ssh)

        ftp_client = ssh.open_sftp()

        try:
            for file in commands:
                ftp_client.get(
                    file, str(self._path+"/"+str(file[file.rfind("/")+1:])))
 
        except Exception as e:
            print(e.with_traceback)
            self.umountNBD(ssh)
        finally:
            self.umountNBD(ssh)

        print("[AristaDevice - getConfig]",
              self._nodeName, "has been backuped")
        self.umountNBD(ssh)
        ssh.close()
    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def __init__(self, ip, root, pwd, path, pod, labName, labID, nodeName, nodeID):
        super().__init__(ip, root, pwd, path, pod, labName, labID, nodeName, nodeID)
