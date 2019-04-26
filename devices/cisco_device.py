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
class CiscoDevice(devices.abstract_device.DeviceQEMUAbstract):

    # ------------------------------------------------------------------------------------------------------------
    #
    # Class variables
    #
    _configFilesSimple = yaml.load(
        open("./commands/cisco/config_files.yml"))
    _shellCommandsMountNBD = yaml.load(
        open("./commands/cisco/command_mount_nbd.yml"))

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def mountNBD(self, sshClient: paramiko.SSHClient):
        first = True
        for command in self._shellCommandsMountNBD:
            print("[EVE-NG Cisco shell mount]", command)
            stdin, stdout, stderr = sshClient.exec_command(command)
            output = "".join(stdout.readlines())
            if first:
                print("[EVE-NG Cisco shell mount]", "sudo qemu-nbd -c /dev/nbd0 /opt/unetlab/tmp/" + str(
                    self._pod) + "/" + str(self._labID) + "/" + str(self._nodeID) + "/virtioa.qcow2")
                stdin, stdout, stderr = sshClient.exec_command(
                    "sudo qemu-nbd -c /dev/nbd0 /opt/unetlab/tmp/" + str(
                        self._pod) + "/" + str(self._labID) + "/" + str(self._nodeID) + "/virtioa.qcow2")
                output = stdout.readlines()
                first = False

            if "error adding partition 1" in output:
                raise EVENG_Exception(
                    "[CiscoDevice - mountNBD] - Error during partition sudo partx -a /dev/nbd0", 802)
    
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
        configFiles = [f for f in listdir(self._path) if "DS" not in f and isfile(join(self._path, f))]
        
        ssh = self.sshConnect()
        self.mountNBD(ssh)
        self.checkMountNBD(ssh)
        ftp_client = ssh.open_sftp()

        for file in configFiles:
            try:
                print("[CiscoDevice - getConfig] copy",
                      str(self._path+"/"+file), "to", str("/mnt/disk/"+file))
                ftp_client.put(localpath=(str(self._path+"/"+file)), remotepath=(str("/mnt/disk/"+file)))
            except Exception as e:
                print(e)
        self.umountNBD(ssh)
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

        print("[CiscoDevice - getConfig]", self._labName, self._nodeName)

        self.umountNBDWithOutCheck(ssh)
        self.mountNBD(ssh)
        self.checkMountNBD(ssh)

        ftp_client = ssh.open_sftp()
    
        try:
            print("[CiscoDevice - getConfig]",
                  self._nodeName, "src -", str("/opt/unetlab/tmp/" + str(self._pod) + "/" + str(self._labID) + "/" + str(self._nodeID) + "/virtioa.qcow2"))
            print("[CiscoDevice - getConfig]",
                  self._nodeName, "dst -", str(self._path + "/virtioa.qcow2"))
            ftp_client.get(
                str("/opt/unetlab/tmp/" + str(self._pod) + "/" + str(self._labID) + "/" + str(self._nodeID) + "/virtioa.qcow2"), str(self._path +"/virtioa.qcow2"))

            for file in commands:
                print("[CiscoDevice - getConfig]",
                      self._nodeName, "src -", file)
                print("[CiscoDevice - getConfig]", self._nodeName,
                      " dst -", str(self._path+"/"+str(file[file.rfind("/")+1:])))

                ftp_client.get(
                    file, str(self._path+"/"+str(file[file.rfind("/")+1:])))
                    
        except Exception as e:
            print(e.with_traceback)
            self.umountNBD(ssh)
        finally:
            self.umountNBD(ssh)

        print("[CiscoDevice - getConfig]",
              self._nodeName, "has been backuped")
        self.umountNBD(ssh)
        ssh.close()


    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def __init__(self, ip, root, pwd, path, pod, labName, labID, nodeName, nodeID):
        super().__init__(ip, root, pwd, path, pod, labName, labID, nodeName, nodeID)


