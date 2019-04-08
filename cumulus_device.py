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
    import abstract_device
except ImportError as importError:
    print("Error import abc - abstractmethod")
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
class CumulusDevice(abstract_device.DeviceQEMUAbstract):
    
    # ------------------------------------------------------------------------------------------------------------
    #
    # Class variables
    #
    _shellCommandsCatFiles = yaml.load(
        open("./commands/cumulus/config_files_verbose_shell.yml"))
    _configFilesVerbose = yaml.load(
        open("./commands/cumulus/config_files_verbose.yml"))
    _configFilesSimple = yaml.load(
        open("./commands/cumulus/config_files_simple.yml"))
    _pushConfigFiles = yaml.load(
        open("./commands/cumulus/push_config_files.yml"))
    _noPushConfigFiles = yaml.load(
        open("./commands/cumulus/push_no_config_files.yml"))
    _shellCommandsMountNBD = yaml.load(
        open("./commands/cumulus/command_mount_nbd.yml"))

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def mountNBD(self, sshClient: paramiko.SSHClient):
        first = True
        for command in self._shellCommandsMountNBD:
            print("[EVE-NG shell mount]", command)
            stdin, stdout, stderr = sshClient.exec_command(command)
            output = "".join(stdout.readlines())
            if first:
                print("[EVE-NG shell mount]", "sudo qemu-nbd -c /dev/nbd0 /opt/unetlab/tmp/" + str(
                    self._pod) + "/" + str(self._labID) + "/" + str(self._nodeID) + "/virtioa.qcow2")
                stdin, stdout, stderr = sshClient.exec_command(
                    "sudo qemu-nbd -c /dev/nbd0 /opt/unetlab/tmp/" + str(self._pod) + "/" + str(self._labID) + "/" + str(self._nodeID) + "/virtioa.qcow2")
                output = stdout.readlines()
                first = False

            if "cat" in command:
                output = output[:-1]
                if output is self._nodeName:
                    raise Exception("Wrong qcow2 is mount in /mnt/disk")

    
    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def pushConfig(self):
        configFiles = [f for f in listdir(self._path) if "DS" not in f and isfile(join(self._path, f))]
        
        ssh = self.sshConnect()
        self.mountNBD(ssh)
        ftp_client = ssh.open_sftp()

        for file in configFiles:
            try:
                if file not in self._noPushConfigFiles:
                    ftp_client.put(localpath=(str(self._path+"/"+file)), remotepath=(str(self._pushConfigFiles[file])+file))
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
        self.getConfig(self._configFilesVerbose, True)

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def getConfig(self, commands:list(), v):
        ssh = self.sshConnect()

        print("[ExtremeCumulus - getConfig]", self._labName, self._nodeName)
        self.umountNBDWithOutCheck(ssh)
        self.mountNBD(ssh)        
        ftp_client = ssh.open_sftp()

        try:
            for file in commands:
                ftp_client.get(
                    file, str(self._path+"/"+str(file[file.rfind("/")+1:])))

            if v:
                for filename, command in self._shellCommandsCatFiles.items():
                    stdin, stdout, stderr = ssh.exec_command(command)
                    ftp_client.get("/tmp/"+filename, self._path+"/"+filename)
        except Exception as e:
            print(e.with_traceback)
            self.umountNBD(ssh)
        finally:
            self.umountNBD(ssh)

        print("[CumulusDevice - getConfig]", self._nodeName, "has been backuped")
        self.umountNBD(ssh)
        ssh.close()
        
    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def __init__(self, ip, root, pwd, path, pod, labName, labID, nodeName, nodeID):
        super().__init__(ip, root, pwd, path, pod, labName, labID, nodeName, nodeID)
        
