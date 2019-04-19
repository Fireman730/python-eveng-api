#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""
 This file is used for validate the yaml architecture syntaxe.
 When you want deploy automaticly a topology in your EVE-NG VM you have to write a YAML file that contains
 * Lab to create
 * Devives to create
 * Links to create
 * Config to push in devices

 There are some YAML file examples in this repo in ./architecture/...
 These examples have been tested.
 Please, check documentation about VM setup for use this script
 If doesn't work feel free to open an issue

 Tests done by this script
 00. Check if YAML file contains path_vm_info:, project:, devices: and links: keys
 01. Check if YAML file keys are corrects
 02. Check if a port is connected to two network
 03. Check if each devices have a different name
 04. Check if each devices have a different UUID
 05. Check if image type is qemu, iol or dynamips (devices: - type: qemu)
 06. Check if console: is telnet or vnc
 07. Check if each links have a different ID
 08. Check if each links are connected to a existing device
 09. Check if device image is available in the EVE-NG
 10. Check if configs: type is in
 11. Check if path_to_vm value is a yaml file
 12. Check if ethernet: number is higher that port connection number
 13. Check if links:node is in devices:name
"""

__author__ = "Dylan Hamel"
__version__ = "0.1"
__email__ = "dylan.hamel@protonmail.com"
__status__ = "Prototype"

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
try:
    from exceptions.EveExceptions import EVENG_Exception
except ImportError as importError:
    print("Error import EVENG_Exception")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import yaml
except ImportError as importError:
    print("Error import yaml")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import PyEVENG
except ImportError as importError:
    print("Error import PyEVENG")
    print(importError)
    exit(EXIT_FAILURE)

######################################################
#
# Constantes
#
IMAGE_TYPES = ["iol", "dynamips", "qemu"]
CONSOLE_TYPES = ["telnet", "vnc"]
CONFIG_TYPES = ["full", "oob"]
YAML_KEYS = ["path_vm_info", "project", "devices", "links", "configs"]
MANDATORY_YAML_KEYS = ["path_vm_info", "project", "devices", "links"]
######################################################
#
# MAIN Functions
#
# Runs all test functins
# Call test functions below ...
#
def validateYamlFileForPyEVENG(yamlContent: dict(), vmInfo):

    apiEVENG = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                               vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])

    # Check that path_to_vm info value is a yaml file
    assert CheckIfPathToVMKeyGoToYAMLfile(yamlContent)
    # Check that YAML file contains project:, devices: and links: keys
    assert checkifKeysAreInYamlFile(yamlContent)
    # Check that YAML file keys are corrects
    assert checkIfYamlFileKeysAreCorrect(yamlContent)
    # Check that each links have an different ID
    assert checkIfDuplicateParam(yamlContent, "links", "id")
    # Check that each devices have an different name
    assert checkIfDuplicateParam(yamlContent, "devices", "name")
    # Check that each devices have a different UUID
    assert checkIfDuplicateParam(yamlContent, "devices", "uuid")
    # Check that links is connected to existing devices
    # assert checkIfLinkConnectedToExistingDevice(yamlContent)
    # Check that each device ports are used only one time - not connected to many devices
    assert checkIfPortUseManyTime(yamlContent)
    # Check that links:node is in devices:name
    assert checkIfLinksHostIsExisting(yamlContent)
    # Check that devices type is in IMAGE_TYPES
    assert checkDeviceElement(IMAGE_TYPES, yamlContent)
    # Check that devices console is in CONSOLE_TYPES
    assert checkDeviceElement(
        CONSOLE_TYPES, yamlContent, paramToVerify="console")
    # Check that configs type is in CONFIG_TYPES
    assert checkDeviceElement(
        CONFIG_TYPES, yamlContent, dictToVerify="configs", paramToVerify="type")
    # Check that device image is available in the EVE-NG
    assert checkIfImageIsAvaiable(apiEVENG, yamlContent)
    # Check that nodes in configs: node is in devices added
    assert checkIfConfigsNodesExists(yamlContent)


######################################################
#
# Test functions
#
# Create test functions below ...
#
## Check that nodes in configs: node is in devices added
def checkIfConfigsNodesExistsWithPath(pathToYamlFile: str()) -> bool:
    return checkIfConfigsNodesExists(open_yaml_files(pathToYamlFile))

def checkIfConfigsNodesExists(yamlContent: dict()) -> bool:
    # Retrieve all devices: hostname
    allDevices = list()

    for device in yamlContent['devices']:
        allDevices.append(device['name'])

    for node in yamlContent['configs']:
        if node['node'] not in allDevices:
            raise EVENG_Exception(
                str("[EveYAMLValidate.py - checkIfConfigsNodesExists] - Node "+str(node['node'])+" but node in your devices to add."), 900)
    return True

## Check if path_to_vm info value is a yaml file ###
def CheckIfPathToVMKeyGoToYAMLfileWithPath(pathToYamlFile: str()) -> bool:
    return CheckIfPathToVMKeyGoToYAMLfile(open_yaml_files(pathToYamlFile))

def CheckIfPathToVMKeyGoToYAMLfile(yamlContent: dict()) -> bool:
    if ("yml" == str(yamlContent['path_vm_info'])[-3:]):
        return True
    else:
        raise EVENG_Exception(str("[EveYAMLValidate.py - CheckIfPathToVMKeyGoToYAMLfile] - path_to_vm need to be a yaml file. Change your value ("+str(
            str(yamlContent['path_vm_info']))+"."), 900)


### Check that keys devices:, project: and links: are in your YAML file. Configs: is not mandatory ###
def checkifKeysAreInYamlFileWithPath(pathToYamlFile: str()) -> bool:
    return checkifKeysAreInYamlFile(open_yaml_files(pathToYamlFile))


def checkifKeysAreInYamlFile(yamlContent: dict()) -> bool:
    allKeys = yamlContent.keys()
    for mandatoryKey in MANDATORY_YAML_KEYS:
        if mandatoryKey not in allKeys:
            raise EVENG_Exception(str("[EveYAMLValidate.py - checkifKeysAreInYamlFile] - Key ("+str(
                mandatoryKey)+") is missing please add all mandatory keys (path_vm_info, project, devices, links."), 900)
    return True
#
### Check that keys is corrects ###
#
def checkIfYamlFileKeysAreCorrectWithPath(pathToYamlFile: str()) -> bool:
    return checkIfYamlFileKeysAreCorrect(open_yaml_files(pathToYamlFile))

def checkIfYamlFileKeysAreCorrect(yamlContent: dict()) -> bool:
    for key in yamlContent.keys():
        if key not in YAML_KEYS:
            raise EVENG_Exception(str("[EveYAMLValidate.py - checkIfYamlFileKeysAreCorrect] - "+str(
                key)+" is not a key accepted in your YAML file."), 900)
    return True

#
#### Check Type (QEMU, IOL, DYNAMIPS) ####
#
def checkDeviceElementWithPath(listElement: list(), pathToYamlFile: str(), dictToVerify: str() = "devices", paramToVerify: str() = "type") -> bool:
    return checkDeviceElement(listElement, open_yaml_files(pathToYamlFile), dictToVerify, paramToVerify)

def checkDeviceElement(listElement: list(), yamlContent: dict(), dictToVerify: str() = "devices", paramToVerify: str() = "type") -> bool:
    for device in yamlContent[dictToVerify]:
        if device[paramToVerify] not in listElement:
            raise EVENG_Exception(str("[EveYAMLValidate.py - checkDeviceElement] - Virtualization type "+str(
                device[paramToVerify])+" is not available on this EVE-NG (qemu, iol, dynamips)."), 900)
    return True
#
#### Check Image (Cumulus, Extreme, Cisco, Arista, ...) ####
#
def checkIfImageIsAvaiableWithPath(availableImages: dict(), pathToYamlFile: str(), dictToVerify: str() = "devices", paramToVerify: str() = "image") -> bool:
    return checkIfImageIsAvaiable(availableImages, open_yaml_files(pathToYamlFile), dictToVerify, paramToVerify)


def checkIfImageIsAvaiable(pyeveng, yamlContent: dict(), dictToVerify: str() = "devices", paramToVerify: str() = "image") -> bool:
    
    for device in yamlContent['devices']:
        images = pyeveng.getImageVersionByModel(device['template'])
        if device[paramToVerify] not in images:
            raise EVENG_Exception(str("[EveYAMLValidate.py - checkIfImageIsAvaiable] - Image "+str(
                device[paramToVerify])+" is not available on this EVE-NG."), 900)
    return True

#
#### Check if a link is connected to a existing device ####
#
"""
def checkIfLinkConnectedToExistingDeviceWithPath(pathToYamlFile: str(), devicesToVerify: str() = "devices", linksToVerify: str() = "links", deviceParamToVerify: str() = "name", linksDeviceToVerify: list = ['src', 'dst']):
    return checkIfLinkConnectedToExistingDevice(open_yaml_files(pathToYamlFile), devicesToVerify, linksToVerify, deviceParamToVerify, linksDeviceToVerify)


def checkIfLinkConnectedToExistingDevice(yamlContent: dict(), devicesToVerify: str() = "devices", linksToVerify: str() = "links", deviceParamToVerify: str() = "name", linksDeviceToVerify: list = ['src', 'dst']):
    allDevices = list()

    for device in yamlContent[devicesToVerify]:
        allDevices.append(device[deviceParamToVerify])

    for link in yamlContent[linksToVerify]:
        if link['dst'] != "OOB-NETWORK":
            if link[linksDeviceToVerify[0]] not in allDevices or link[linksDeviceToVerify[1]] not in allDevices:
                raise EVENG_Exception(str("[EveYAMLValidate.py - checkIfLinkConnectedToExistingDevice] - There is a link on "+str(
                    linksHost)+" but this node is not create in devices."), 900)
    return True
"""
#
#### Check if links: node is in devices:name ####
#
def checkIfLinksHostIsExistingWithPath(pathToYamlFile: str(), dictToVerify: str() = "links", paramToVerify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    return checkIfLinksHostIsExisting(open_yaml_files(pathToYamlFile), dictToVerify, paramToVerify)


def checkIfLinksHostIsExisting(yamlContent: dict(), dictToVerify: str() = "links", paramToVerify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    allHostInLinks = set()

    for link in yamlContent[dictToVerify]:
        if link[paramToVerify[2]] != "OOB-NETWORK":
            if link[paramToVerify[0]] not in allHostInLinks:
                allHostInLinks.add([link[paramToVerify[0]]][0])

            if link[paramToVerify[2]] not in allHostInLinks:
                allHostInLinks.add([link[paramToVerify[2]]][0])

        else:
            for oobConnection in link[paramToVerify[0]]:
                if oobConnection['host'] not in allHostInLinks:
                    allHostInLinks.add([oobConnection['host']][0])

    # Retrieve all devices: hostname
    allDevices = list()

    for device in yamlContent['devices']:
        allDevices.append(device['name'])

    for linksHost in allHostInLinks:
        if linksHost not in allDevices:
            raise EVENG_Exception(str("[EveYAMLValidate.py - checkIfLinksHostIsExisting] - There is a link on "+str(linksHost)+" but this node is not create in devices.") , 900)
    return True

#
#### Check if port is use many time ####
#
def checkIfPortUseManyTimeWithPath(pathToYamlFile: str(), dictToVerify: str() = "links", paramToVerify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    return checkIfPortUseManyTime(open_yaml_files(pathToYamlFile), dictToVerify, paramToVerify)


def checkIfPortUseManyTime(yamlContent: dict(), dictToVerify: str() = "links", paramToVerify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    allHostInLinks = dict()

    for link in yamlContent[dictToVerify]:
        if link[paramToVerify[2]] != "OOB-NETWORK":
            if link[paramToVerify[0]] not in allHostInLinks.keys():
                allHostInLinks[link[paramToVerify[0]]] = list()
            if link[paramToVerify[2]] not in allHostInLinks.keys():
                allHostInLinks[link[paramToVerify[2]]] = list()

        else:
            for oobConnection in link[paramToVerify[0]]:
                if oobConnection['host'] not in allHostInLinks.keys():
                    allHostInLinks[oobConnection['host']] = list()

    for link in yamlContent[dictToVerify]:
        if link['dst'] != "OOB-NETWORK":
            if link[paramToVerify[1]] in allHostInLinks[link[paramToVerify[0]]]:
                raise EVENG_Exception(
                    str("[EveYAMLValidate.py - checkIfPortUseManyTime] - Port "+str(link[paramToVerify[1]])+" on "+str(link['src'])+" is use several times"), 900)
            else:
                allHostInLinks[link[paramToVerify[0]]].append(
                    link[paramToVerify[1]])

            if link[paramToVerify[3]] in allHostInLinks[link[paramToVerify[2]]]:
                raise EVENG_Exception(
                    str("[EveYAMLValidate.py - checkIfPortUseManyTime] - Port "+str(link[paramToVerify[3]])+" on "+str(link['dst'])+" is use several times"), 900)
            else:
                allHostInLinks[link[paramToVerify[2]]].append(
                    link[paramToVerify[3]])
        
        else:
            for oobConnection in link['src']:
                if oobConnection['port'] in allHostInLinks[oobConnection['host']]:
                    raise EVENG_Exception(
                        str("[EveYAMLValidate.py - checkIfPortUseManyTime] - Port "+str(
                            oobConnection['port'])+" on "+str(oobConnection['host'])+" is use several times"), 900)
                else:
                    allHostInLinks[oobConnection['host']].append(
                        oobConnection['port'])

    return True


#
#### Check If Hostname are duplicate (Spine01, Core01, Leaf01, ...) ####
#
def checkIfDuplicateParamWithPath(pathToYamlFile: str(), dictToVerify: str() = "devices", paramToVerify: str() = "name") -> bool:
    return checkIfDuplicateParam(open_yaml_files(pathToYamlFile), dictToVerify, paramToVerify)


def checkIfDuplicateParam(yamlContent: dict(), dictToVerify: str() = "devices", paramToVerify: str() = "name") -> bool:
    listParam = list()
    for node in yamlContent[dictToVerify]:
        if node[paramToVerify] in listParam:
            raise EVENG_Exception(
                str("[EveYAMLValidate.py - checkIfDuplicateParam] - Two devices have the name : "+str(node[paramToVerify])), 900)
        listParam.append(node[paramToVerify])
    return True
#
#### Open a YAML file and return the content in a dict ####
#
def open_yaml_files(path: str()) -> dict():
    with open(path, "r") as f:
        return yaml.load(f.read())


######################################################
if __name__ == "__main__":
    #image = dict({'docker': 'Docker.io', 'csr1000v': 'Cisco CSR 1000V', 'vios': 'Cisco vIOS', 'viosl2': 'Cisco vIOS L2', 'cumulus': 'Cumulus VX',
    #              'extremexos': 'ExtremeXOS', 'linux': 'Linux', 'ostinato': 'Ostinato', 'esxi': 'VMWare ESXi', 'vpcs': 'Virtual PC (VPCS)'})
    print(checkIfDuplicateParamWithPath(
        "/Volumes/Data/gitlab/python-eveng-api/architecture/all.yml", "links", "id"))
    #print(checkIfImageIsAvaiableWithPath(image, "/Volumes/Data/gitlab/python-eveng-api/architecture/all.yml"))
    #print(checkIfPortUseManyTimeWithPath("/Volumes/Data/gitlab/python-eveng-api/architecture/all.yml"))
    #print(checkIfLinkConnectedToExistingDeviceWithPath("/Volumes/Data/gitlab/python-eveng-api/architecture/all.yml"))
