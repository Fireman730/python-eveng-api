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
    import tarfile
except ImportError as importError:
    print("Error import tarfile")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import devices.abstract_device
except ImportError as importError:
    print("Error import abc - Cisco abstractmethod")
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


class NexusDevice(devices.abstract_device.DeviceQEMUAbstract):
 # ------------------------------------------------------------------------------------------------------------
    #
    # Class variables
    #
    _configFilesSimple = yaml.load(
        open("./commands/nexus/config_files.yml"))
    _shellCommandsMountNBD = yaml.load(
        open("./commands/nexus/command_mount_nbd.yml"))

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def mount_nbd(self, sshClient: paramiko.SSHClient):
        first = True
        for command in self._shellCommandsMountNBD:
            print("[NexusDevice - mount_nbd]", command)
            stdin, stdout, stderr = sshClient.exec_command(command)
            output = "".join(stdout.readlines())
            if first:
                print("[NexusDevice - mount_nbd]", "sudo qemu-nbd -c /dev/nbd0 /opt/unetlab/tmp/" + str(
                    self._pod) + "/" + str(self._labID) + "/" + str(self._nodeID) + "/sataa.qcow2")
                stdin, stdout, stderr = sshClient.exec_command(
                    "sudo qemu-nbd -c /dev/nbd0 /opt/unetlab/tmp/" + str(
                        self._pod) + "/" + str(self._labID) + "/" + str(self._nodeID) + "/sataa.qcow2")
                output = stdout.readlines()
                first = False

            if "error adding partition 1" in output:
                raise EVENG_Exception(
                    "[NexusDevice - mount_nbd] - Error during partition sudo partx -a /dev/nbd0", 802)

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

        ssh = self.sshConnect()
        self.mount_nbd(ssh)
        self.checkMountNBD(ssh)

        ftp_client = ssh.open_sftp()

        try:
            ftp_client.put(localpath=(str(self._path +"/linux_cfg.tar.gz")),
                           remotepath=("/mnt/disk/linux/linux_cfg.tar.gz"))
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
        self.getConfig(self._configFilesSimple, False)

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def getConfigVerbose(self):
        self.getConfig(self._configFilesSimple, True)

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def getConfig(self, commands: list(), v):
        ssh = self.sshConnect()

        print("[NexusDevice - getConfig]", self._labName, self._nodeName)

        self.umountNBDWithOutCheck(ssh)
        self.mount_nbd(ssh)
        self.checkMountNBD(ssh)

        ftp_client = ssh.open_sftp()

        try:
            for file in commands:
                print("[NexusDevice - getConfig]",
                      self._nodeName, "src -", file)
                print("[NexusDevice - getConfig]", self._nodeName,
                      " dst -", str(self._path+"/"+str(file[file.rfind("/")+1:])))

        except Exception as e:
            print(e.with_traceback)
            self.umountNBD(ssh)
        finally:
            self.umountNBD(ssh)

        print("[NexusDevice - getConfig]",
              self._nodeName, "has been backuped")
        self.umountNBD(ssh)
        ssh.close()

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #

    def __init__(self, ip, root, pwd, path, pod, labName, labID, nodeName, nodeID):
        super().__init__(ip, root, pwd, path, pod, labName, labID, nodeName, nodeID)
