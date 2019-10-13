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
    import devices.abstract_device
except ImportError as importError:
    print("Error import abc - VYOS abstractmethod")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import tools.fileSystem as fileSystem
except ImportError as importError:
    print("Error import - VYOS fileSystem")
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
HEADER = "[VyosDevice -"

######################################################
#
# Class
#
class VyosDevice(devices.abstract_device.DeviceQEMUAbstract):

    # ------------------------------------------------------------------------------------------------------------
    #
    # Class variables
    #
    _shell_commands_cat_files = yaml.load(
        open("./commands/vyos/config_files_verbose_shell.yml"))
    _config_files_verbose = yaml.load(
        open("./commands/vyos/config_files_verbose.yml"))
    _config_files_simple = yaml.load(
        open("./commands/vyos/config_files_simple.yml"))
    _push_config_files = yaml.load(
        open("./commands/vyos/push_config_files.yml"))
    _no_push_config_files = yaml.load(
        open("./commands/vyos/push_no_config_files.yml"))
    _shell_commands_mount_nbd = yaml.load(
        open("./commands/vyos/command_mount_nbd.yml"))

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def mount_nbd(self, sshClient: paramiko.SSHClient):
        first = True
        for command in self._shell_commands_mount_nbd:
            print(f"{HEADER} mount_nbd]", command)
            stdin, stdout, stderr = sshClient.exec_command(command)
            output = "".join(stdout.readlines())
            if first:
                print(f"{HEADER} mount_nbd] sudo qemu-nbd -c /dev/nbd0 /opt/unetlab/tmp/{str(self._pod)}/{str(self._labID)}/{str(self._nodeID)}/virtioa.qcow2")
                stdin, stdout, stderr = sshClient.exec_command(
                    f"sudo qemu-nbd -c /dev/nbd0 /opt/unetlab/tmp/{str(self._pod)}/{str(self._labID)}/{str(self._nodeID)}/virtioa.qcow2")
                output = stdout.readlines()
                first = False

            if "cat" in command:
                output = output[:-1]
                print(f"{HEADER} mount_nbd] cat hostname - {output}")
                if output is self._nodeName:
                    raise Exception(f"Wrong qcow2 is mount in /mnt/disk")

            if "error adding partition 1" in output:
                raise EVENG_Exception(
                    f"{HEADER} mount_nbd] - Error during partition sudo partx - a / dev/nbd0", 802)
    
    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def pushOOB(self):
        ssh = self.sshConnect()

        self.umountNBDWithOutCheck(ssh)
        self.mount_nbd(ssh)
        self.checkMountNBD(ssh)

        ftp_client = ssh.open_sftp()

        print(self._path)
        try:
            ftp_client.put(localpath=(str(self._path+"/interfaces")),
                           remotepath=(str("/mnt/disk/etc/network/interfaces")))
        except Exception as e:
            print("[VyosDevice - pushOOB] error during sftp put transfert.")
            print(e)

        self.umountNBD(ssh)

        ftp_client.close()
        ssh.close()
    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def pushConfig(self):
        configFiles = [f for f in listdir(
            self._path) if "DS" not in f and isfile(join(self._path, f))]

        ssh = self.sshConnect()
        self.mount_nbd(ssh)
        self.checkMountNBD(ssh)

        ftp_client = ssh.open_sftp()

        for file in configFiles:
            try:
                if file not in self._no_push_config_files:
                    print(f"{HEADER} pushConfig] copy",
                          str(f"{self._path}/{file} to {str(self._push_config_files[file])}{file}"))
                    ftp_client.put(localpath=(str(self._path+"/"+file)),
                                   remotepath=(str(self._push_config_files[file])+file))
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
        self.getConfig(self._config_files_simple, False)

    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def getConfigVerbose(self):
        self.getConfig(self._config_files_verbose, True)
    
    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def getConfig(self, commands: list(), v):
        ssh = self.sshConnect()

        print("[VyosDevice - getConfig]", self._labName, self._nodeName)

        self.umountNBDWithOutCheck(ssh)
        self.mount_nbd(ssh)
        self.checkMountNBD(ssh)

        ftp_client = ssh.open_sftp()

        try:
            for line in commands:
                print(f"[VyosDevice - getConfig] \n{line} \n--> {str(self._path)}/{str(line[line.rfind('/')+1:])}")
                
                if "config.boot" in line:
                    try:
                        ftp_client.get(
                            line, str(self._path+"/"+str(line[line.rfind("/")+1:])))
                    except FileNotFoundError as e:
                        print(f"ERROR - [VyosDevice - getConfig] - config.boot not found VyOS has not configuration ????")
                
                else:
                    ftp_client.get(
                        line, str(self._path+"/"+str(line[line.rfind("/")+1:])))

            """
            if v:
                for filename, command in self._shell_commands_cat_files.items():
                    stdin, stdout, stderr = ssh.exec_command(command)
                    ftp_client.get("/tmp/"+filename, self._path+"/"+filename)
            """

        except Exception as e:
            print(e.with_traceback)
            self.umountNBD(ssh)
        finally:
            self.umountNBD(ssh)

        print("[VyosDevice - getConfig]",
              self._nodeName, "has been backuped")
        self.umountNBD(ssh)
        ssh.close()


    # ------------------------------------------------------------------------------------------------------------
    #
    #
    #
    def __init__(self, ip, root, pwd, path, pod, labName, labID, nodeName, nodeID):
        super().__init__(ip, root, pwd, path, pod, labName, labID, nodeName, nodeID)


