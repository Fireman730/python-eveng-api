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
    import api.PyEVENG as PyEVENG
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
YAML_KEYS = ["project", "devices", "links", "configs", "ansible"]
MANDATORY_YAML_KEYS = ["project", "devices", "links"]
RAM_ALLOWED = ["64", "128", "256", "512", "1024", "2048",
               "3072", "4096", "5120", "6144", "8192", "16384"]
KEYS_IN_ANSIBLE = ["playbooks", "groups"]

MAX_NAT_PORT = 30000
MIN_NAT_PORT = 10000

######################################################
#
# MAIN Functions
#
# Runs all test functins
# Call test functions below ...
#


def validateYamlFileForPyEVENG(api: PyEVENG.PyEVENG, yamlContent: dict(), vmInfo):

    # Check that path_to_vm info value is a yaml file
    # assert CheckIfPathToVMKeyGoToYAMLfile(yamlContent)
    # Check that YAML file contains project:, devices: and links: keys
    assert checkifKeysAreInYamlFile(yamlContent)
    # Check that YAML file keys are corrects
    assert checkIfYamlFileKeysAreCorrect(yamlContent)
    # Check that each links have an different ID
    assert checkIfDuplicateParam(yamlContent, "links", "id")
    # Check that each devices have an different name
    assert checkIfDuplicateParam(yamlContent, "devices", "name")
    # Check that each devices have a different UUID
    if "uuid" in yamlContent['devices']:
        assert checkIfDuplicateParam(yamlContent, "devices", "uuid")
    # Check that RAM allowd to each device is allowd
    assert checkIfRamIsAllowed(yamlContent)
    # Check that ansible: keys are allowed
    assert checkAnsibleKeys(yamlContent)
    assert checkAnsibleKeysGroupsExistIfPlaybooksExist(yamlContent)
    # Check that links is connected to existing devices
    # assert checkIfLinkConnectedToExistingDevice(yamlContent)
    # Check that each device ports are used only one time - not connected to many devices
    assert checkIfPortUseManyTime(yamlContent)
    # Check that each EVENG port used to NAT is unique
    assert checkNatPort(yamlContent)
    # Check port-forwarding is between 10000 et 30000
    assert checkPortValue(yamlContent)
    # Check that each device has a unique IP address in OOB NETWORK
    assert checkDeviceIPAddressInOOB(yamlContent)
    # Check that links:node is in devices:name
    assert checkIfLinksHostIsExisting(yamlContent)
    # Check that devices type is in IMAGE_TYPES
    assert checkDeviceElement(IMAGE_TYPES, yamlContent)
    # Check that devices console is in CONSOLE_TYPES
    assert checkDeviceElement(
        CONSOLE_TYPES, yamlContent, paramToVerify="console")
    # Check that configs type is in CONFIG_TYPES
    if "configs" in yamlContent.keys():
        assert checkDeviceElement(
            CONFIG_TYPES, yamlContent, dictToVerify="configs", paramToVerify="type")
    # Check that device image is available in the EVE-NG
    assert checkIfImageIsAvaiable(api, yamlContent)
    # Check memory available vs memery asked by devices
    assert checkVMMemoryFreeVSDevicesMemoryAsked(api, yamlContent)
    # Check that nodes in configs: node is in devices added
    if "configs" in yamlContent.keys():
        assert checkIfConfigsNodesExists(yamlContent)


######################################################
#
# Test functions
#
# Create test functions below ...
#
def checkVMMemoryFreeVSDevicesMemoryAskedWithPath(api: PyEVENG.PyEVENG, pathToYamlFile: str()) -> bool:
    return checkVMMemoryFreeVSDevicesMemoryAsked(api, open_yaml_files(pathToYamlFile))

# Check memory available vs memery asked by devices


def checkVMMemoryFreeVSDevicesMemoryAsked(api: PyEVENG.PyEVENG, yamlContent: dict()) -> bool:
    total_memory = 0
    coefficient = 1.2

    if "devices" in yamlContent.keys():
        for device in yamlContent['devices']:
            total_memory = total_memory + device['ram']

        vm_memory = api.get_vm_memory()

        if int(vm_memory) < int(total_memory / coefficient):
            return False

    return True

# Check that Ansible keys are allowd


def checkAnsibleKeysGroupsExistIfPlaybooksExist(yamlContent: dict()) -> bool:
    if "ansible" in yamlContent.keys():
        if "playbooks" in yamlContent['ansible'].keys() and "groups" not in yamlContent['ansible'].keys():
                raise EVENG_Exception(
                    "[EveYAMLValidate.py - checkAnsibleKeysGroupsExistIfPlaybooksExist] - ansible: groups: is mandatory if you use ansible: playbooks:", 100)
    return True


def checkAnsibleKeysWithPath(pathToYamlFile: str()) -> bool:
    return checkAnsibleKeys(open_yaml_files(pathToYamlFile))


def checkAnsibleKeys(yamlContent: dict()) -> bool:
    if "ansible" in yamlContent.keys():
        for key in yamlContent['ansible'].keys():
            if str(key) not in KEYS_IN_ANSIBLE:
                raise EVENG_Exception(
                    f"[EveYAMLValidate.py - checkAnsibleKeys] - <{key}> is not a allowed keys for ansible:", 100)

    return True

## Check that ram of each node is correct


def checkIfRamIsAllowedWithPath(pathToYamlFile: str()) -> bool:
    return checkIfRamIsAllowed(open_yaml_files(pathToYamlFile))


def checkIfRamIsAllowed(yamlContent: dict()) -> bool:
    if "devices" in yamlContent.keys():
        for device in yamlContent['devices']:
            if str(device['ram']) not in RAM_ALLOWED:
                return False
        return True
    return False

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
            raise EVENG_Exception(str("[EveYAMLValidate.py - checkDeviceElement] - Type "+str(dictToVerify)+":"+str(paramToVerify)+": \""+str(
                device[paramToVerify])+"\" is not available on this EVE-NG."), 900)
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
                device[paramToVerify])+" is not available on this EVE-NG \n\t\t=> Error can be in your YAML file [template: or image:]."), 900)
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
            raise EVENG_Exception(str("[EveYAMLValidate.py - checkIfLinksHostIsExisting] - There is a link on "+str(
                linksHost)+" but this node is not create in devices."), 900)
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
#### Check port-forwarding is between 10000 et 30000
#
def checkPortValue(yamlContent: dict()):

    error = False
    list_error = list()

    for link in yamlContent['links']:
        if "OOB-NETWORK" in link['dst']:
            for oob_link in link['src']:
                if oob_link['nat'] > MAX_NAT_PORT or oob_link['nat'] < MIN_NAT_PORT:
                    list_error.append(
                        f"{oob_link['host']} - {oob_link['nat']}")
                    error = True

    if error:
        raise EVENG_Exception(
            str(f"[EveYAMLValidate.py - checkPortValue] - Port is > thant {MAX_NAT_PORT} or < {MIN_NAT_PORT} for : {list_error}"), 900)

    return True

#
#### Check that each EVENG port used to NAT is unique ####
#
def checkNatPort(yamlContent: dict()):

    list_nat_port = list()

    for link in yamlContent['links']:
        if "OOB-NETWORK" in link['dst']:
            for oob_link in link['src']:
                if oob_link['nat'] in list_nat_port:
                    raise EVENG_Exception(
                        str("[EveYAMLValidate.py - checkNatPort] - Two devices have the same external NAT port : "+str(oob_link['nat'])), 900)
                else:
                    list_nat_port.append(oob_link['nat'])
    return True

#
#### Check that each device has a unique IP address in OOB NETWORK ####
#


def checkDeviceIPAddressInOOB(yamlContent: dict()):

    list_nat_port = list()

    for link in yamlContent['links']:
        if "OOB-NETWORK" in link['dst']:
            for oob_link in link['src']:
                if oob_link['ip_mgmt'] in list_nat_port:
                    raise EVENG_Exception(
                        str("[EveYAMLValidate.py - checkDeviceIPAddressInOOB] - Two devices have the same OOB IP address : "+str(oob_link['ip_mgmt'])), 900)
                else:
                    list_nat_port.append(oob_link['ip_mgmt'])
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
