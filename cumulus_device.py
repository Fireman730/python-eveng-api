#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# Default value used for exit()
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

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

MY_PATH = "/Volumes/Data/gitlab/python-eveng-api/"

class CumulusDevice(abstract_device.DeviceQEMUAbstract):

    _shellCommandsMountNBD = yaml.load(
        open("./commands/command_mount_nbd.yml"))
    _shellCommandsUmountNBD = yaml.load(
        open("./commands/command_umount_nbd.yml"))
    _shellCommandsCatFiles = yaml.load(
        open("./commands/config_files_verbose_shell.yml"))
    _configFilesVerbose = yaml.load(
        open("./commands/config_files_verbose.yml"))
    _configFilesSimple = yaml.load(
        open("./commands/config_files_simple.yml"))
    
    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def mountNBD(self, sshClient:paramiko.SSHClient):
        first = True
        for command in self._shellCommandsMountNBD:
            stdin, stdout, stderr = sshClient.exec_command(command)
            if first:
                stdin, stdout, stderr = sshClient.exec_command(
                    "sudo qemu-nbd -c /dev/nbd0 /opt/unetlab/tmp/" + self._pod + "/" + self._labID + "/" + self._nodeID + "/virtioa.qcow2")
                first = False

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def umountNBD(self, sshClient: paramiko.SSHClient):
        for command in self._shellCommandsUmountNBD:
            stdin, stdout, stderr = sshClient.exec_command(command)
            o = "".join(stdout.readlines())
            
        if "nbd0" not in o:
            raise Exception("Error during nbd disconnect")

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

        self.mountNBD(ssh)

        ftp_client = ssh.open_sftp()

        for file in commands:
            ftp_client.get(
                file, str(self._path+"/"+str(file[file.rfind("/")+1:])))

        if v:
            for filename, command in self._shellCommandsCatFiles.items():
                stdin, stdout, stderr = ssh.exec_command(command)
                ftp_client.get("/tmp/"+filename, self._path+"/"+filename)

        self.umountNBD(ssh)

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def __init__(self, ip, root, pwd, path, pod, labID, nodeID):
        super().__init__(ip, root, pwd, path, pod, labID, nodeID)
        
