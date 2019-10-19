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
 14: Check if Memory on EVE-NG VM is suffisant
 15: Check if NAT port are correct and are between MAX_NAT_PORT & MIN_NAT_PORT
 16: Check if project:path exist
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
    print("Error import [EveYamlValidate.py] EVENG_Exception")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import yaml
except ImportError as importError:
    print("Error import [EveYamlValidate.py] yaml")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import api.PyEVENG as PyEVENG
except ImportError as importError:
    print("Error import [EveYamlValidate.py] PyEVENG")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import pprint
    PP = pprint.PrettyPrinter(indent=4)
except ImportError as importError:
    print("Error import [EveYamlValidate.py] pprint")
    print(importError)
    exit(EXIT_FAILURE)

######################################################
#
# Constantes
#
HEADER = "[EveYAMLValidate.py -"
KEYWORD_TO_TELL_THAT_A_LINK_IS_OOB = "OOB-NETWORK"

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


#### YAML file keys ####
YAML_PROJECT_KEY = 'project'
YAML_DEVICES_KEY = 'devices'
YAML_LINKS_KEY = 'links'
YAML_CONFIGS_KEY = 'configs'
YAML_ANSIBLE_KEY = 'ansible'

#### Project keys ####
PROJECT_NAME_KEY = 'name'
PROJECT_PATH_KEY = 'path'
PROJECT_VERSION_KEY = 'version'
PROJECT_AUTHOR_KEY = 'author'
PROJECT_DESCRIPTION_KEY = 'description'
PROJECT_BODY_KEY = 'body'

#### Links keys ####
LINKS_DST_KEY = 'dst'
LINKS_SRC_KEY = 'src'


#### OOB keys ####
OOB_NAT_KEY = 'nat'
OOB_HOST_KEY = 'host'
OOB_IP_MGMT_KEY = 'ip_mgmt'

######################################################
#
# MAIN Functions
#
# Runs all test functins
# Call test functions below ...
#
def pprintline(data: dict()) -> None:
    print("==================================================================")
    PP.pprint(data)
    print("==================================================================")

def pprintline(data: str()) -> None:
    print("==================================================================")
    print(data)
    print("==================================================================")


def test_function(pipeline):
    validateYamlFileForPyEVENG(api=PyEVENG.PyEVENG, yaml=dict, vm_info="null", pipeline=True)

def validateYamlFileForPyEVENG(api: PyEVENG.PyEVENG, yaml_content: dict(), vm_info, * , pipeline):

    # Check that project:path doesn't start or end with "/"
    # assert check_project_path_not_start_or_end_with_slash(yaml_content)
    # Check that path_to_vm info value is a yaml file
    # assert CheckIfPathToVMKeyGoToYAMLfile(yaml_content)
    # Check that YAML file contains project:, devices: and links: keys
    assert checkifKeysAreInYamlFile(yaml_content)
    # Check that YAML file keys are corrects
    assert checkIfYamlFileKeysAreCorrect(yaml_content)
    # Check that each links have an different ID
    assert checkIfDuplicateParam(yaml_content, "links", "id")
    # Check that each devices have an different name
    assert checkIfDuplicateParam(yaml_content, "devices", "name")
    # Check that each devices have a different UUID
    if "uuid" in yaml_content['devices']:
        assert checkIfDuplicateParam(yaml_content, "devices", "uuid")
    # Check that RAM allowd to each device is allowd
    assert checkIfRamIsAllowed(yaml_content)
    # Check that ansible: keys are allowed
    assert checkAnsibleKeys(yaml_content)
    assert checkAnsibleKeysGroupsExistIfPlaybooksExist(yaml_content)
    # Check that links is connected to existing devices
    # assert checkIfLinkConnectedToExistingDevice(yaml_content)
    # Check that each device ports are used only one time - not connected to many devices
    assert checkIfPortUseManyTime(yaml_content)
    # Check that each EVENG port used to NAT is unique
    assert checkNatPort(yaml_content)
    # Check port-forwarding is between 10000 et 30000
    assert checkPortValue(yaml_content)
    # Check that each device has a unique IP address in OOB NETWORK
    assert checkDeviceIPAddressInOOB(yaml_content)
    # Check that links:node is in devices:name
    assert checkIfLinksHostIsExisting(yaml_content)
    # Check that devices type is in IMAGE_TYPES
    assert checkDeviceElement(IMAGE_TYPES, yaml_content)
    # Check that devices console is in CONSOLE_TYPES
    assert checkDeviceElement(
        CONSOLE_TYPES, yaml_content, param_to_verify="console")
    # Check that configs type is in CONFIG_TYPES
    if "configs" in yaml_content.keys():
        assert checkDeviceElement(
            CONFIG_TYPES, yaml_content, dict_to_verify="configs", param_to_verify="type")
    # Check that device image is available in the EVE-NG
    if pipeline is False:
        assert checkIfImageIsAvaiable(api, yaml_content)
    # Check memory available vs memery asked by devices
    if pipeline is False:
        assert checkVMMemoryFreeVSDevicesMemoryAsked(api, yaml_content)
    # Check that nodes in configs: node is in devices added
    if "configs" in yaml_content.keys():
        assert checkIfConfigsNodesExists(yaml_content)


######################################################
#
# Test functions
#
# Create test functions below ...
#
def check_project_path_not_start_or_end_with_slash(yaml_content:dict()) -> bool:

    if str(yaml_content[YAML_PROJECT_KEY][PROJECT_PATH_KEY]).startswith('/') or \
        str(yaml_content[YAML_PROJECT_KEY][PROJECT_PATH_KEY]).endswith('/'): 
        pprintline(f"{yaml_content[YAML_PROJECT_KEY][PROJECT_PATH_KEY]}")
        raise EVENG_Exception(
            f"[EveYAMLValidate.py - check_project_path_not_start_or_end_with_slash] Error ! 'project:path' starts or ends with a / (slash).", 903)

    else:
        return True


def checkVMMemoryFreeVSDevicesMemoryAskedWithPath(api: PyEVENG.PyEVENG, pat_to_yaml_file: str()) -> bool:
    return checkVMMemoryFreeVSDevicesMemoryAsked(api, open_yaml_files(pat_to_yaml_file))

# Check memory available vs memery asked by devices


def checkVMMemoryFreeVSDevicesMemoryAsked(api: PyEVENG.PyEVENG, yaml_content: dict()) -> bool:
    total_memory = 0
    coefficient = 1.2

    if "devices" in yaml_content.keys():
        for device in yaml_content['devices']:
            total_memory = total_memory + device['ram']

        vm_memory = api.get_vm_memory()

        if int(vm_memory) < int(total_memory / coefficient):
            return False

    return True

# Check that Ansible keys are allowd


def checkAnsibleKeysGroupsExistIfPlaybooksExist(yaml_content: dict()) -> bool:
    if "ansible" in yaml_content.keys():
        if "playbooks" in yaml_content['ansible'].keys() and "groups" not in yaml_content['ansible'].keys():
                raise EVENG_Exception(
                    "[EveYAMLValidate.py - checkAnsibleKeysGroupsExistIfPlaybooksExist] - ansible: groups: is mandatory if you use ansible: playbooks:", 100)
    return True


def checkAnsibleKeysWithPath(pat_to_yaml_file: str()) -> bool:
    return checkAnsibleKeys(open_yaml_files(pat_to_yaml_file))


def checkAnsibleKeys(yaml_content: dict()) -> bool:
    if "ansible" in yaml_content.keys():
        for key in yaml_content['ansible'].keys():
            if str(key) not in KEYS_IN_ANSIBLE:
                raise EVENG_Exception(
                    f"[EveYAMLValidate.py - checkAnsibleKeys] - <{key}> is not a allowed keys for ansible:", 100)

    return True

## Check that ram of each node is correct


def checkIfRamIsAllowedWithPath(pat_to_yaml_file: str()) -> bool:
    return checkIfRamIsAllowed(open_yaml_files(pat_to_yaml_file))


def checkIfRamIsAllowed(yaml_content: dict()) -> bool:
    if "devices" in yaml_content.keys():
        for device in yaml_content['devices']:
            if str(device['ram']) not in RAM_ALLOWED:
                return False
        return True
    return False

## Check that nodes in configs: node is in devices added


def checkIfConfigsNodesExistsWithPath(pat_to_yaml_file: str()) -> bool:
    return checkIfConfigsNodesExists(open_yaml_files(pat_to_yaml_file))


def checkIfConfigsNodesExists(yaml_content: dict()) -> bool:
    # Retrieve all devices: hostname
    allDevices = list()

    for device in yaml_content['devices']:
        allDevices.append(device['name'])

    for node in yaml_content['configs']:
        if node['node'] not in allDevices:
            raise EVENG_Exception(
                str("[EveYAMLValidate.py - checkIfConfigsNodesExists] - Node "+str(node['node'])+" but node in your devices to add."), 900)
    return True

## Check if path_to_vm info value is a yaml file ###


def CheckIfPathToVMKeyGoToYAMLfileWithPath(pat_to_yaml_file: str()) -> bool:
    return CheckIfPathToVMKeyGoToYAMLfile(open_yaml_files(pat_to_yaml_file))


def CheckIfPathToVMKeyGoToYAMLfile(yaml_content: dict()) -> bool:
    if ("yml" == str(yaml_content['path_vm_info'])[-3:]):
        return True
    else:
        raise EVENG_Exception(str("[EveYAMLValidate.py - CheckIfPathToVMKeyGoToYAMLfile] - path_to_vm need to be a yaml file. Change your value ("+str(
            str(yaml_content['path_vm_info']))+"."), 900)


### Check that keys devices:, project: and links: are in your YAML file. Configs: is not mandatory ###
def checkifKeysAreInYamlFileWithPath(pat_to_yaml_file: str()) -> bool:
    return checkifKeysAreInYamlFile(open_yaml_files(pat_to_yaml_file))


def checkifKeysAreInYamlFile(yaml_content: dict()) -> bool:
    allKeys = yaml_content.keys()
    for mandatoryKey in MANDATORY_YAML_KEYS:
        if mandatoryKey not in allKeys:
            raise EVENG_Exception(str("[EveYAMLValidate.py - checkifKeysAreInYamlFile] - Key ("+str(
                mandatoryKey)+") is missing please add all mandatory keys (path_vm_info, project, devices, links."), 900)
    return True
#
### Check that keys is corrects ###
#


def checkIfYamlFileKeysAreCorrectWithPath(pat_to_yaml_file: str()) -> bool:
    return checkIfYamlFileKeysAreCorrect(open_yaml_files(pat_to_yaml_file))


def checkIfYamlFileKeysAreCorrect(yaml_content: dict()) -> bool:
    for key in yaml_content.keys():
        if key not in YAML_KEYS:
            raise EVENG_Exception(str("[EveYAMLValidate.py - checkIfYamlFileKeysAreCorrect] - "+str(
                key)+" is not a key accepted in your YAML file."), 900)
    return True

#
#### Check Type (QEMU, IOL, DYNAMIPS) ####
#


def checkDeviceElementWithPath(element_lst: list(), pat_to_yaml_file: str(), dict_to_verify: str() = "devices", param_to_verify: str() = "type") -> bool:
    return checkDeviceElement(element_lst, open_yaml_files(pat_to_yaml_file), dict_to_verify, param_to_verify)


def checkDeviceElement(element_lst: list(), yaml_content: dict(), dict_to_verify: str() = "devices", param_to_verify: str() = "type") -> bool:

    for device in yaml_content[dict_to_verify]:

        if param_to_verify not in device.keys():
            pprintline(device)
            raise EVENG_Exception(
                f"[EveYAMLValidate.py - checkDeviceElement] Error ! Key {param_to_verify} is missing in {dict_to_verify}: !", 931)
        else:
            if device[param_to_verify] not in element_lst:
                raise EVENG_Exception(str("[EveYAMLValidate.py - checkDeviceElement] - Type "+str(dict_to_verify)+":"+str(param_to_verify)+": \""+str(
                    device[param_to_verify])+"\" is not available on this EVE-NG."), 932)
    return True
#
#### Check Image (Cumulus, Extreme, Cisco, Arista, ...) ####
#


def checkIfImageIsAvaiableWithPath(availableImages: dict(), pat_to_yaml_file: str(), dict_to_verify: str() = "devices", param_to_verify: str() = "image") -> bool:
    return checkIfImageIsAvaiable(availableImages, open_yaml_files(pat_to_yaml_file), dict_to_verify, param_to_verify)


def checkIfImageIsAvaiable(pyeveng, yaml_content: dict(), dict_to_verify: str() = "devices", param_to_verify: str() = "image") -> bool:

    for device in yaml_content['devices']:
        images = pyeveng.getImageVersionByModel(device['template'])

        if device[param_to_verify] not in images:
            raise EVENG_Exception(str("[EveYAMLValidate.py - checkIfImageIsAvaiable] - Image "+str(
                device[param_to_verify])+" is not available on this EVE-NG \n\t\t=> Error can be in your YAML file [template: or image:]."), 900)
    return True


#
#### Check if a link is connected to a existing device ####
#
"""
def checkIfLinkConnectedToExistingDeviceWithPath(pat_to_yaml_file: str(), devicesToVerify: str() = "devices", linksToVerify: str() = "links", deviceParamToVerify: str() = "name", linksDeviceToVerify: list = ['src', 'dst']):
    return checkIfLinkConnectedToExistingDevice(open_yaml_files(pat_to_yaml_file), devicesToVerify, linksToVerify, deviceParamToVerify, linksDeviceToVerify)


def checkIfLinkConnectedToExistingDevice(yaml_content: dict(), devicesToVerify: str() = "devices", linksToVerify: str() = "links", deviceParamToVerify: str() = "name", linksDeviceToVerify: list = ['src', 'dst']):
    allDevices = list()

    for device in yaml_content[devicesToVerify]:
        allDevices.append(device[deviceParamToVerify])

    for link in yaml_content[linksToVerify]:
        if link['dst'] != "OOB-NETWORK":
            if link[linksDeviceToVerify[0]] not in allDevices or link[linksDeviceToVerify[1]] not in allDevices:
                raise EVENG_Exception(str("[EveYAMLValidate.py - checkIfLinkConnectedToExistingDevice] - There is a link on "+str(
                    linksHost)+" but this node is not create in devices."), 900)
    return True
"""
#
#### Check if links: node is in devices:name ####
#


def checkIfLinksHostIsExistingWithPath(pat_to_yaml_file: str(), dict_to_verify: str() = "links", param_to_verify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    return checkIfLinksHostIsExisting(open_yaml_files(pat_to_yaml_file), dict_to_verify, param_to_verify)


def checkIfLinksHostIsExisting(yaml_content: dict(), dict_to_verify: str() = "links", param_to_verify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    allHostInLinks = set()

    for link in yaml_content[dict_to_verify]:
        if link[param_to_verify[2]] != "OOB-NETWORK":
            if link[param_to_verify[0]] not in allHostInLinks:
                allHostInLinks.add([link[param_to_verify[0]]][0])

            if link[param_to_verify[2]] not in allHostInLinks:
                allHostInLinks.add([link[param_to_verify[2]]][0])

        else:
            for oobConnection in link[param_to_verify[0]]:
                if oobConnection['host'] not in allHostInLinks:
                    allHostInLinks.add([oobConnection['host']][0])

    # Retrieve all devices: hostname
    allDevices = list()

    for device in yaml_content['devices']:
        allDevices.append(device['name'])

    for linksHost in allHostInLinks:
        if linksHost not in allDevices:
            raise EVENG_Exception(str("[EveYAMLValidate.py - checkIfLinksHostIsExisting] - There is a link on "+str(
                linksHost)+" but this node is not create in devices."), 900)
    return True

#
#### Check if port is use many time ####
#


def checkIfPortUseManyTimeWithPath(pat_to_yaml_file: str(), dict_to_verify: str() = "links", param_to_verify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    return checkIfPortUseManyTime(open_yaml_files(pat_to_yaml_file), dict_to_verify, param_to_verify)


def checkIfPortUseManyTime(yaml_content: dict(), dict_to_verify: str() = "links", param_to_verify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    allHostInLinks = dict()

    for link in yaml_content[dict_to_verify]:
        if link[param_to_verify[2]] != "OOB-NETWORK":
            if link[param_to_verify[0]] not in allHostInLinks.keys():
                allHostInLinks[link[param_to_verify[0]]] = list()
            if link[param_to_verify[2]] not in allHostInLinks.keys():
                allHostInLinks[link[param_to_verify[2]]] = list()

        else:
            for oobConnection in link[param_to_verify[0]]:
                if oobConnection['host'] not in allHostInLinks.keys():
                    allHostInLinks[oobConnection['host']] = list()

    for link in yaml_content[dict_to_verify]:
        if link['dst'] != "OOB-NETWORK":
            if link[param_to_verify[1]] in allHostInLinks[link[param_to_verify[0]]]:
                raise EVENG_Exception(
                    str("[EveYAMLValidate.py - checkIfPortUseManyTime] - Port "+str(link[param_to_verify[1]])+" on "+str(link['src'])+" is use several times"), 900)
            else:
                allHostInLinks[link[param_to_verify[0]]].append(
                    link[param_to_verify[1]])

            if link[param_to_verify[3]] in allHostInLinks[link[param_to_verify[2]]]:
                raise EVENG_Exception(
                    str("[EveYAMLValidate.py - checkIfPortUseManyTime] - Port "+str(link[param_to_verify[3]])+" on "+str(link['dst'])+" is use several times"), 900)
            else:
                allHostInLinks[link[param_to_verify[2]]].append(
                    link[param_to_verify[3]])

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
def checkPortValue(yaml_content: dict()):

    error = False
    list_error = list()

    for link in yaml_content[YAML_LINKS_KEY]:
        if KEYWORD_TO_TELL_THAT_A_LINK_IS_OOB in link[LINKS_DST_KEY]:
            for oob_link in link[LINKS_SRC_KEY]:
                if OOB_NAT_KEY in oob_link.keys():
                    if oob_link[OOB_NAT_KEY] > MAX_NAT_PORT or oob_link[OOB_NAT_KEY] < MIN_NAT_PORT:
                        list_error.append(
                            f"{oob_link[OOB_HOST_KEY]} - {oob_link[OOB_NAT_KEY]}")
                        error = True

    if error:
        raise EVENG_Exception(
            str(f"{HEADER} checkPortValue] - Port is > thant {MAX_NAT_PORT} or < {MIN_NAT_PORT} for : {list_error}"), 900)

    return True


#
#### Check that each EVENG port used to NAT is unique ####
#

def checkNatPort(yaml_content: dict()):

    list_nat_port = list()

    for link in yaml_content[YAML_LINKS_KEY]:
        if KEYWORD_TO_TELL_THAT_A_LINK_IS_OOB in link[LINKS_DST_KEY]:
            for oob_link in link[LINKS_SRC_KEY]:
                if OOB_NAT_KEY in oob_link.keys():
                    if oob_link[OOB_NAT_KEY] in list_nat_port:
                        raise EVENG_Exception(
                            str(f"{HEADER} checkNatPort] - Two devices have the same external NAT port : {str(oob_link['nat'])}"), 900)
                    else:
                        list_nat_port.append(oob_link[OOB_NAT_KEY])
    return True

#
#### Check that each device has a unique IP address in OOB NETWORK ####
#

def checkDeviceIPAddressInOOB(yaml_content: dict()):

    list_nat_port = list()

    for link in yaml_content['links']:
        if KEYWORD_TO_TELL_THAT_A_LINK_IS_OOB in link[LINKS_DST_KEY]:
            for oob_link in link[LINKS_SRC_KEY]:
                if OOB_NAT_KEY in oob_link.keys():
                    if oob_link[OOB_IP_MGMT_KEY] in list_nat_port:
                        raise EVENG_Exception(
                            str(f"{HEADER} - checkDeviceIPAddressInOOB] - Two devices have the same OOB IP address : {str(oob_link['ip_mgmt'])}"), 900)
                    else:
                        list_nat_port.append(oob_link[OOB_IP_MGMT_KEY])
    return True

#
#### Check If Hostname are duplicate (Spine01, Core01, Leaf01, ...) ####
#


def checkIfDuplicateParamWithPath(pat_to_yaml_file: str(), dict_to_verify: str() = "devices", param_to_verify: str() = "name") -> bool:
    return checkIfDuplicateParam(open_yaml_files(pat_to_yaml_file), dict_to_verify, param_to_verify)


def checkIfDuplicateParam(yaml_content: dict(), dict_to_verify: str() = "devices", param_to_verify: str() = "name") -> bool:
    listParam = list()
    for node in yaml_content[dict_to_verify]:
        if node[param_to_verify] in listParam:
            raise EVENG_Exception(
                str("[EveYAMLValidate.py - checkIfDuplicateParam] - Two devices have the name : "+str(node[param_to_verify])), 900)
        listParam.append(node[param_to_verify])
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
