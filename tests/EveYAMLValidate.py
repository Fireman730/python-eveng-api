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
HEADER_ERR = "Error import [EveYamlValidate.py]"
HEADER = "[EveYamlValidate.py -"
######################################################
#
# Import Library
#
try:
    from exceptions.EveExceptions import EVENG_Exception
except ImportError as importError:
    print(f"{HEADER_ERR} EVENG_Exception")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import yaml
except ImportError as importError:
    print(f"{HEADER_ERR}  yaml")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import api.PyEVENG as PyEVENG
except ImportError as importError:
    print(f"{HEADER_ERR}  PyEVENG")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import pprint
    PP = pprint.PrettyPrinter(indent=4)
except ImportError as importError:
    print(f"{HEADER_ERR}  pprint")
    print(importError)
    exit(EXIT_FAILURE)

try:
    from const.constantes import  *
except ImportError as importError:
    print(f"{HEADER_ERR} const.constantes")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import logging
    val_log = logging
    val_log.getLogger(__name__)
    val_log.basicConfig(
        level=logging.DEBUG,
        filename="./logs/EveYAMLValidate.log",
        format='[%(asctime)s] - %(levelname)s - %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
except ImportError as importError:
    print(f"{HEADER_ERR} logging")
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


def validateYamlFileForPyEVENG(api: PyEVENG.PyEVENG, yaml_content: dict(), vm_info, *, pipeline=False, file_path=""):

    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG] Start function with {file_path}!")

    return_value = True

    # Check that project:path doesn't start or end with "/"
    # assert check_project_path_not_start_or_end_with_slash(yaml_content)
    # Check that path_to_vm info value is a yaml file
    # assert CheckIfPathToVMKeyGoToYAMLfile(yaml_content)
    # Check that YAML file contains project:, devices: and links: keys
    assert checkifKeysAreInYamlFile(yaml_content)
    # Check that YAML file keys are corrects
    assert checkIfYamlFileKeysAreCorrect(yaml_content)
    # Check that each links have an different ID
    assert checkIfDuplicateParam(yaml_content, YAML_LINKS_KEY, LINKS_ID_KEY)
    # Check that each devices have an different name
    assert checkIfDuplicateParam(yaml_content, YAML_DEVICES_KEY, DEVICES_NAME_KEY)
    # Check that each devices have a different UUID
    if DEVICES_UUID_KEY in yaml_content[YAML_DEVICES_KEY]:
        assert checkIfDuplicateParam(yaml_content, YAML_DEVICES_KEY, DEVICES_UUID_KEY)
    
    
    # Check that RAM allowd to each device is allowed
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_ram_is_allowed - start check!")
    if check_if_ram_is_allowed(yaml_content) is False:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_ram_is_allowed is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_ram_is_allowed is SUCCESS !!!!")
    

    # Check that Ansible:groups: <hostname> are defined in devices:
    if YAML_ANSIBLE_KEY in yaml_content.keys():
        if check_ansible_groups_devices(yaml_content) is False:
            val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ansible_groups_devices is FAILED !!!!")
            return_value = False
        else:
            val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ansible_groups_devices is SUCCESS !!!!")

    
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
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_port_value - start check!")
    if check_port_value(yaml_content) is False:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_port_value is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_port_value is SUCCESS !!!!")
    
    # Check that each device has a unique IP address in OOB NETWORK
    assert checkDeviceIPAddressInOOB(yaml_content)
    
    # Check that links:node is in devices:name
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_links_host_exists - start check!")
    if check_if_links_host_exists(yaml_content) is False:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_links_host_exists is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_links_host_exists is SUCCESS !!!!")

    # Check that devices type is in IMAGE_TYPES
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_links_host_exists - start check!")
    if check_device_element(IMAGE_TYPES, yaml_content) is False:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_element(IMAGE_TYPES) is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_element(IMAGE_TYPES) is SUCCESS !!!!")

    # Check that devices console is in CONSOLE_TYPES
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_element - start check!")
    if check_device_element(CONSOLE_TYPES, yaml_content, param_to_verify=DEVICES_CONSOLE_KEY) is False:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_element(CONSOLE_TYPES) is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_element(CONSOLE_TYPES) is SUCCESS !!!!")

    # Check that configs type is in CONFIG_TYPES
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_element(CONFIG_TYPES) - start check!")
    if YAML_CONFIGS_KEY in yaml_content.keys():
        if check_device_element(CONFIG_TYPES, yaml_content, dict_to_verify=YAML_CONFIGS_KEY, param_to_verify=CONFIG_TYPE_KEY) is False:
            val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_element(CONFIG_TYPES) is FAILED !!!!")
            return_value = False
        else:
            val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_element(CONFIG_TYPES) is SUCCESS !!!!")

    # Check that device image is available in the EVE-NG
    if pipeline is False:
        assert checkIfImageIsAvaiable(api, yaml_content)
    # Check memory available vs memery asked by devices
    if pipeline is False:
        assert checkVMMemoryFreeVSDevicesMemoryAsked(api, yaml_content)
    
    # Check that nodes in configs: node is in devices added
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_configs_nodes_exists - start check!")
    if YAML_CONFIGS_KEY in yaml_content.keys():
        if check_if_configs_nodes_exists(yaml_content) is False:
            val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_configs_nodes_exists is FAILED !!!!")
            return_value = False
        else:
            val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_configs_nodes_exists is SUCCESS !!!!")

    # Check that ip_eve or ip_pub doesn't exist if there is not port-forwarding
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ip_pub_if_not_port_fowrading - start check!")
    if check_ip_pub_if_not_port_fowrading(yaml_content) is False:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ip_pub_if_not_port_fowrading is FAILED !!!!")
        return_value = False
    else:
            val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ip_pub_if_not_port_fowrading is SUCCESS !!!!")

    return return_value
######################################################
#
# Test functions
#
# Create test functions below ...
#
def get_devices_name(yaml_content: dict()) -> list:

    device_name_lst = list()

    if YAML_DEVICES_KEY in yaml_content.keys():
        for device in yaml_content[YAML_DEVICES_KEY]:
            if DEVICES_CONFIG_KEY in device.keys():
                device_name_lst.append(device[DEVICES_NAME_KEY])
    
    return device_name_lst

# =========================================================================================================================================================
#
# Check that ram of each node is correct
#
def check_ansible_groups_devices(yaml_content: dict()) -> bool:

    return_value = True
    error_device_name_lst = list()

    val_log.debug(f"{HEADER} check_ansible_groups_devices] Start function !")

    if YAML_ANSIBLE_KEY in yaml_content.keys():
        if ANSIBLE_GROUPS_KEY in yaml_content[YAML_ANSIBLE_KEY].keys():

            # Retrieve all devices names
            device_name_lst = get_devices_name(yaml_content)
            val_log.debug(f"{HEADER} check_ansible_groups_devices] All devices name ({YAML_DEVICES_KEY}:{DEVICES_NAME_KEY}) :")
            val_log.debug(f"==>> {device_name_lst}")

            for group in yaml_content[YAML_ANSIBLE_KEY][ANSIBLE_GROUPS_KEY]:
                for device_name_in_group in yaml_content[YAML_ANSIBLE_KEY][ANSIBLE_GROUPS_KEY][group]:
                    val_log.debug(f"{HEADER} check_ansible_groups_devices] {device_name_in_group} is in the list above ??")
                    val_log.debug(f"==>> {device_name_in_group in device_name_lst} // if confition is device_name_in_group not in device_name_lst = {device_name_in_group not in device_name_lst}")
                    if device_name_in_group not in device_name_lst:
                        error_device_name_lst.append(device_name_in_group)
                        return_value = False
        else:
            val_log.debug(f"{HEADER} check_ansible_groups_devices] {ANSIBLE_GROUPS_KEY} key is not in the yaml file {YAML_ANSIBLE_KEY}:!")
            print(f"{HEADER} check_ansible_groups_devices] Please set the groups key ({YAML_ANSIBLE_KEY}:{ANSIBLE_GROUPS_KEY}:)")
            return_value = False

    else:
        val_log.debug(f"{HEADER} check_ansible_groups_devices] {YAML_ANSIBLE_KEY} key is not in the yaml file!")

    val_log.debug(
        f"{HEADER} check_ansible_groups_devices] return_value={return_value} ??")
    if return_value is False:
        val_log.debug(f"{HEADER} check_ansible_groups_devices] The following device(s) is/are not in ({YAML_DEVICES_KEY}:{DEVICES_NAME_KEY})")
        print(f"{HEADER} check_ansible_groups_devices] The following device(s) is/are not in ({YAML_DEVICES_KEY}:{DEVICES_NAME_KEY})")
        print(f"\t\t ==> {error_device_name_lst}")

    return return_value



# =========================================================================================================================================================
#
# Check that ip_eve is not present if there are no port-forwarding
#
def check_ip_pub_if_not_port_fowrading(yaml_content:dict()) -> bool:

    val_log.debug(f"{HEADER} check_ip_pub_if_not_port_fowrading] Start function !")

    port_forwarding = False
    return_value = True

    if YAML_LINKS_KEY in yaml_content.keys():
        for link in yaml_content[YAML_LINKS_KEY]:
            if LINKS_DST_KEY in link.keys():
                if link[LINKS_DST_KEY] == KEYWORD_TO_TELL_THAT_A_LINK_IS_OOB:
                    val_log.debug(
                        f"{HEADER} check_ip_pub_if_not_port_fowrading] link_id {link[LINKS_ID_KEY]} is OOB !")
                    if LINKS_SRC_KEY in link.keys():
                        for oob_interface in link[LINKS_SRC_KEY]:
                            if OOB_IP_MGMT_KEY in oob_interface.keys() and OOB_SSH_KEY in oob_interface.keys() and OOB_NAT_KEY in oob_interface.keys():
                                val_log.debug(
                                    f"{HEADER} check_ip_pub_if_not_port_fowrading] There are port-forwarding !")
                                port_forwarding = True
                            else:
                                val_log.debug(
                                    f"{HEADER} check_ip_pub_if_not_port_fowrading] There are NOT port-forwarding !")

                    if port_forwarding is False:
                        if LINKS_IP_EVE_KEY in  link.keys() or LINKS_IP_PUB_KEY in link.keys():
                            val_log.debug(
                                f"{HEADER} check_ip_pub_if_not_port_fowrading] ip_pub: or ip_eve are present...")
                            return_value = False
                            print(
                                f"{HEADER} check_ip_pub_if_not_port_fowrading] Error ip_eve or ip_pub can not exist if there are no port-forwarding")
                            #raise EVENG_Exception(
                            #    f"{HEADER} check_ip_pub_if_not_port_fowrading] Error ip_eve or ip_pub can not exist \
                            #        if there are no port-forwarding", 903)

    val_log.debug(f"{HEADER} check_ip_pub_if_not_port_fowrading] Return value is {return_value} !")
    return return_value


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


# =========================================================================================================================================================
#
# Check that ram of each node is correct
#
def check_if_ram_is_allowed_with_path(pat_to_yaml_file: str()) -> bool:
    return check_if_ram_is_allowed(open_yaml_files(pat_to_yaml_file))


def check_if_ram_is_allowed(yaml_content: dict()) -> bool:

    return_value = True
    error_res_dict = dict()
    
    val_log.debug(f"{HEADER} - check_if_ram_is_allowed] Start function !")

    if YAML_DEVICES_KEY in yaml_content.keys():
        val_log.debug(f"{HEADER} - check_if_ram_is_allowed] RAM memories allowed are : RAM_ALLOWED{RAM_ALLOWED} !")
        for device in yaml_content[YAML_DEVICES_KEY]:
            val_log.debug(f"{HEADER} - check_if_ram_is_allowed] {device[DEVICES_NAME_KEY]} has {device[DEVICES_RAM_KEY]} RAM!")
            val_log.debug(f"{HEADER} - check_if_ram_is_allowed] This value is allowed ??")
            val_log.debug(f"==>> {str(device[DEVICES_RAM_KEY]) in RAM_ALLOWED}")
            if str(device[DEVICES_RAM_KEY]) not in RAM_ALLOWED:
                logging.debug(f"{HEADER} - check_if_ram_is_allowed] DEVICE ERROR ^^^^^^")
                error_res_dict[device[DEVICES_NAME_KEY]] = device[DEVICES_RAM_KEY]
                return_value = False

    logging.debug(f"{HEADER} - check_if_ram_is_allowed] return_value={return_value}")
    if return_value is False:
        print(f"{HEADER} - check_if_ram_is_allowed] Error with the following device(s):")
        PP.pprint(error_res_dict)

    return return_value

# =========================================================================================================================================================
#
# Check that nodes in configs: node is in devices added
#
def check_if_configs_nodes_exists_with_path(pat_to_yaml_file: str()) -> bool:
    return check_if_configs_nodes_exists(open_yaml_files(pat_to_yaml_file))


def check_if_configs_nodes_exists(yaml_content: dict()) -> bool:
    # Retrieve all devices: hostname
    all_devices_lst = list()
    return_value = True

    val_log.debug(f"{HEADER} - check_if_configs_nodes_exists] Start function !")

    if YAML_DEVICES_KEY in yaml_content.keys():
        for device in yaml_content[YAML_DEVICES_KEY]:
            all_devices_lst.append(device['name'])

        val_log.debug(f"{HEADER} - check_if_configs_nodes_exists] All nodes in YAML file !")
        val_log.debug(f"{all_devices_lst}")

    if YAML_CONFIGS_KEY in yaml_content.keys():
        for node in yaml_content[YAML_CONFIGS_KEY]:
            val_log.debug(f"{HEADER} - check_if_configs_nodes_exists] Is {node[CONFIG_NODE_KEY]} in the list ? ")
            val_log.debug(f"{all_devices_lst}")

            if node[CONFIG_NODE_KEY] not in all_devices_lst:
                val_log.debug(f"{HEADER} - check_if_configs_nodes_exists] NOPE {node[CONFIG_NODE_KEY]} is NOT in the list !")
                print(f"{HEADER} check_if_configs_nodes_exists] Node {node[CONFIG_NODE_KEY]} is not in the 'devices:' list ...")
                return_value = False
            else:
                val_log.debug(f"{HEADER} - check_if_configs_nodes_exists] Yes {node[CONFIG_NODE_KEY]} is in the list !")
    return return_value

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


def check_device_element_with_path(element_lst: list(), pat_to_yaml_file: str(), dict_to_verify: str() = "devices", param_to_verify: str() = "type") -> bool:
    return check_device_element(element_lst, open_yaml_files(pat_to_yaml_file), dict_to_verify, param_to_verify)


def check_device_element(element_lst: list(), yaml_content: dict(), dict_to_verify: str() = "devices", param_to_verify: str() = "type") -> bool:

    return_value = True
    error_missing = False
    error_not_list = False


    val_log.debug(f"{HEADER} check_device_element] Start function !")
    val_log.debug(f"{HEADER} check_device_element] element_lst={element_lst}")
    val_log.debug(f"{HEADER} check_device_element] dict_to_verify={dict_to_verify}")
    val_log.debug(f"{HEADER} check_device_element] param_to_verify={param_to_verify}")

    if dict_to_verify in yaml_content.keys():
        for device in yaml_content[dict_to_verify]:
            val_log.debug(
                f"{HEADER} check_device_element] param_to_verify={param_to_verify} is present in device.keys={device.keys()} ???")
            val_log.debug(f"==>> {param_to_verify in device.keys()} // if condition is param_to_verify not in device.keys() = {param_to_verify not in device.keys()}")
            if param_to_verify not in device.keys():
                val_log.debug(
                    f"{HEADER} check_device_element](1) param_to_verify={param_to_verify} is present NOT in device.keys={device.keys()}")
                print(f"{HEADER} check_device_element](1) Error ! Key {param_to_verify} is missing in {dict_to_verify}: !")
                error_missing = True
                return_value = False
            else:
                val_log.debug(f"{HEADER} check_device_element](2) param_to_verify={param_to_verify} is present in device.keys={device.keys()}")
                val_log.debug(f"{HEADER} check_device_element](2) device[param_to_verify]={device[param_to_verify]} is present in element_lst={element_lst} ??? ")
                val_log.debug(f"==>> {device[param_to_verify] in element_lst} // if device[param_to_verify] not in element_lst = {device[param_to_verify] not in element_lst}")
                if device[param_to_verify] not in element_lst:
                    val_log.debug(f"{HEADER} check_device_element](3) device[param_to_verify]={device[param_to_verify]} is NOT present in element_lst={element_lst}")
                    val_log.debug(f"{HEADER} check_device_element](3) ({dict_to_verify}:{param_to_verify}:{device[param_to_verify]}) is not available on this EVE-NG.")
                    error_not_list = True
                    return_value = False

    val_log.debug(f"{HEADER} check_device_element] error_missing={error_missing}")
    if error_missing:
        print(f"{HEADER} check_device_element] Please check that ({dict_to_verify}:{param_to_verify}) exists.")
        print(f"\t\t Please use one of the following possibilities : {element_lst}")

    val_log.debug(f"{HEADER} check_device_element] error_not_list={error_not_list}")
    if error_not_list:
        print(f"{HEADER} check_device_element] Please check your ({dict_to_verify}:{param_to_verify}) values.")
        print(f"\t\t Please use one of the following possibilities : {element_lst}")

    val_log.debug(f"{HEADER} check_device_element] return_value={return_value}")
    return return_value
#
#### Check Image (Cumulus, Extreme, Cisco, Arista, ...) ####
#


def checkIfImageIsAvaiableWithPath(availableImages: dict(), pat_to_yaml_file: str(), dict_to_verify: str() = "devices", param_to_verify: str() = "image") -> bool:
    return checkIfImageIsAvaiable(availableImages, open_yaml_files(pat_to_yaml_file), dict_to_verify, param_to_verify)


def checkIfImageIsAvaiable(pyeveng, yaml_content: dict(), dict_to_verify: str() = "devices", param_to_verify: str() = "image") -> bool:

    for device in yaml_content['devices']:
        images = pyeveng.get_image_version_by_model(device['template'])

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


def check_if_links_host_exists_with_path(pat_to_yaml_file: str(), dict_to_verify: str() = "links", param_to_verify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    return check_if_links_host_exists(open_yaml_files(pat_to_yaml_file), dict_to_verify, param_to_verify)


def check_if_links_host_exists(yaml_content: dict(), dict_to_verify: str() = "links", param_to_verify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:

    all_values = set()
    return_value = True

    val_log.debug(f"{HEADER} check_if_links_host_exists] Start function !")
    val_log.debug(f"{HEADER} check_if_links_host_exists] dict_to_verify={dict_to_verify} !")
    val_log.debug(f"{HEADER} check_if_links_host_exists] param_to_verify={param_to_verify} !")
    val_log.debug(f"{HEADER} check_if_links_host_exists] param_to_verify={param_to_verify} !")

    if dict_to_verify in yaml_content.keys():
        for link in yaml_content[dict_to_verify]:
            if link[param_to_verify[2]] != KEYWORD_TO_TELL_THAT_A_LINK_IS_OOB:
                if link[param_to_verify[0]] not in all_values:
                    val_log.debug(
                        f"{HEADER} check_if_links_host_exists] (1) Add {link[param_to_verify[0]]} in all_values !")
                    all_values.add([link[param_to_verify[0]]][0])

                if link[param_to_verify[2]] not in all_values:
                    val_log.debug(
                        f"{HEADER} check_if_links_host_exists] (2) Add {link[param_to_verify[0]]} in all_values !")
                    all_values.add([link[param_to_verify[2]]][0])

            else:
                val_log.debug(f"{HEADER} check_if_links_host_exists] OOB Connexion !")
                for oobConnection in link[param_to_verify[0]]:
                    if oobConnection[OOB_HOST_KEY] not in all_values:
                        val_log.debug(
                            f"{HEADER} check_if_links_host_exists] (3) Add {link[param_to_verify[0]]} in all_values !")
                        all_values.add([oobConnection[OOB_HOST_KEY]][0])

    # Retrieve all devices: hostname
    all_devices = list()

    for device in yaml_content[YAML_DEVICES_KEY]:
        all_devices.append(device[DEVICES_NAME_KEY])

    for value in all_values:
        if value not in all_devices:
            val_log.debug(f"{HEADER} check_if_links_host_exists] Link {value} is not in 'devices:'")
            print(f"{HEADER} check_if_links_host_exists] Link {value} is not in 'devices:'")
            return_value = False
            #raise EVENG_Exception(f"{HEADER} check_if_links_host_exists] - There is a link on "+str(
            #    linksHost)+" but this node is not create in devices."), 900)

    return return_value

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
def check_port_value(yaml_content: dict()):

    return_value = True
    list_error = list()

    val_log.debug(f"{HEADER} check_port_value] Start function !")

    for link in yaml_content[YAML_LINKS_KEY]:
        if KEYWORD_TO_TELL_THAT_A_LINK_IS_OOB in link[LINKS_DST_KEY]:
            val_log.debug(f"{HEADER} check_port_value] link_id {link[LINKS_ID_KEY]} is OOB !")
            for oob_link in link[LINKS_SRC_KEY]:
                if OOB_NAT_KEY in oob_link.keys():
                    val_log.debug(f"{HEADER} check_port_value] Link :")
                    val_log.debug(f"{oob_link}")
                    if oob_link[OOB_NAT_KEY] > MAX_NAT_PORT or oob_link[OOB_NAT_KEY] < MIN_NAT_PORT:
                        val_log.debug(f"{HEADER} check_port_value] ERROR with this LINK !")
                        list_error.append(
                            f"{oob_link[OOB_HOST_KEY]} - {oob_link[OOB_NAT_KEY]}")
                        return_value = False
                    else:
                        val_log.debug(f"{HEADER} check_port_value] This link is OK !")

    if return_value is False:
        val_log.debug(f"{HEADER} check_port_value] Error with the following link(s) :")
        val_log.debug(f"{list_error}")
        print(f"{HEADER} check_port_value] Error with the following link(s) :")
        print(f"{list_error}")
        #raise EVENG_Exception(
        #    str(f"{HEADER} check_port_value] - Port is > thant {MAX_NAT_PORT} or < {MIN_NAT_PORT} for : {list_error}"), 900)

    return return_value

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
