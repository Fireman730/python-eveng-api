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


######################################################
#
# Functions
#

def validateYamlFileForPyEVENG(yamlContent: dict(), apiEVENG):
    assert checkIfDuplicateParam(yamlContent, "links", "id")
    assert checkIfDuplicateParam(yamlContent, "devices", "name")
   
    try: 
        assert checkIfDuplicateParam(yamlContent, "devices", "uuid")
    except KeyError:
        print("No UUID in your YAML file. UUID will be generate automaticly")

    assert checkIfLinkConnectedToExistingDevice(yamlContent)
    assert checkIfPortUseManyTime(yamlContent)

    assert checkVMType(yamlContent)
    assert checkIfImageIsAvaiable(apiEVENG.getNodeInstall(), yamlContent)


#### Check Type (QEMU, IOL, DYNAMIPS) ####
def checkVMTypeWithPath(pathToYamlFile: str(), dictToVerify: str()="devices", paramToVerify: str() = "type") -> bool:
    return checkIfImageIsAvaiable(open_yaml_files(pathToYamlFile), dictToVerify, paramToVerify)

def checkVMType(yamlContent: dict(), dictToVerify: str() = "devices", paramToVerify: str() = "type") -> bool:
    for device in yamlContent[dictToVerify]:
        if device[paramToVerify] not in IMAGE_TYPES:
            return False
    return True

#### Check Image (Cumulus, Extreme, Cisco, Arista, ...) ####
def checkIfImageIsAvaiableWithPath(availableImages: dict(), pathToYamlFile: str(), dictToVerify: str()="devices", paramToVerify: str() = "image") -> bool:
    return checkIfImageIsAvaiable(availableImages, open_yaml_files(pathToYamlFile), dictToVerify, paramToVerify)

def checkIfImageIsAvaiable(availableImages: dict(), yamlContent: dict(), dictToVerify: str() = "devices", paramToVerify: str() = "image") -> bool:
    images = availableImages.values()

    for image in yamlContent[dictToVerify]:
        if image[paramToVerify] not in images:
            return False
    return True

#### Check if a link is connected to a existing device ####
def checkIfLinkConnectedToExistingDeviceWithPath(pathToYamlFile: str(), devicesToVerify:str()="devices", linksToVerify:str()="links", deviceParamToVerify:str()="name", linksDeviceToVerify:list=['src','dst']):
    return checkIfLinkConnectedToExistingDevice(open_yaml_files(pathToYamlFile), devicesToVerify, linksToVerify, deviceParamToVerify, linksDeviceToVerify)

def checkIfLinkConnectedToExistingDevice(yamlContent: dict(), devicesToVerify: str() = "devices", linksToVerify: str() = "links", deviceParamToVerify: str() = "name", linksDeviceToVerify: list = ['src', 'dst']):
    allDevices = list()

    for device in yamlContent[devicesToVerify]:
        allDevices.append(device[deviceParamToVerify])
    
    for link in yamlContent[linksToVerify]:
        if link[linksDeviceToVerify[0]] not in allDevices or link[linksDeviceToVerify[1]] not in allDevices:
            return False
    return True

#### Check if port is use many time ####
def checkIfPortUseManyTimeWithPath(pathToYamlFile: str(), dictToVerify: str() = "links", paramToVerify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    return checkIfPortUseManyTime(open_yaml_files(pathToYamlFile), dictToVerify, paramToVerify)

def checkIfPortUseManyTime(yamlContent: dict(), dictToVerify: str() = "links", paramToVerify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    result = dict()

    for link in yamlContent[dictToVerify]:
        result[link[paramToVerify[0]]] = list()
        result[link[paramToVerify[2]]] = list()

    for link in yamlContent[dictToVerify]:
        if link[paramToVerify[1]] in result[link[paramToVerify[0]]]:
            return False
        else:
            result[link[paramToVerify[0]]].append(link[paramToVerify[1]])

        if link[paramToVerify[3]] in result[link[paramToVerify[2]]]:
            return False
        else:
            result[link[paramToVerify[2]]].append(link[paramToVerify[3]])
    
    return True

#### Check If Hostname are duplicate (Spine01, Core01, Leaf01, ...) ####
def checkIfDuplicateParamWithPath(pathToYamlFile: str(), dictToVerify: str() = "devices", paramToVerify: str() = "name") -> bool:    
    return checkIfDuplicateParam(open_yaml_files(pathToYamlFile), dictToVerify, paramToVerify)

def checkIfDuplicateParam(yamlContent: dict(), dictToVerify: str() = "devices", paramToVerify: str() = "name") -> bool:
    listParam = list()
    for node in yamlContent[dictToVerify]:
        if node[paramToVerify] in listParam:
            return False
        listParam.append(node[paramToVerify])    
    return True

#### Open a YAML file and return the content in a dict ####
def open_yaml_files(path:str()) -> dict():
    with open(path, "r") as f:
        return yaml.load(f.read())

######################################################
if __name__ == "__main__":
    #image = dict({'docker': 'Docker.io', 'csr1000v': 'Cisco CSR 1000V', 'vios': 'Cisco vIOS', 'viosl2': 'Cisco vIOS L2', 'cumulus': 'Cumulus VX',
    #              'extremexos': 'ExtremeXOS', 'linux': 'Linux', 'ostinato': 'Ostinato', 'esxi': 'VMWare ESXi', 'vpcs': 'Virtual PC (VPCS)'})
    print(checkIfDuplicateParamWithPath("/Volumes/Data/gitlab/python-eveng-api/architecture/all.yml", "links", "id"))
    #print(checkIfImageIsAvaiableWithPath(image, "/Volumes/Data/gitlab/python-eveng-api/architecture/all.yml"))
    #print(checkIfPortUseManyTimeWithPath("/Volumes/Data/gitlab/python-eveng-api/architecture/all.yml"))
    #print(checkIfLinkConnectedToExistingDeviceWithPath("/Volumes/Data/gitlab/python-eveng-api/architecture/all.yml"))
    
