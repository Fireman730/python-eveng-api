#!/usr/bin/env python3
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

"""

__author__ = "Dylan Hamel"
__version__ = "1.0"
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
    from const.constantes import  *
except ImportError as importError:
    print(f"{HEADER_ERR} const.constantes")
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
RAM_ALLOWED = ["64", "128", "256", "512", "768", "1024", "2048", "2560",
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


def validateYamlFileForPyEVENG(api: PyEVENG.PyEVENG, yaml_content: dict(), vm_info, *, pipeline=False, file_path="") -> None:

    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG] Start function with {file_path}!")

    return_value = True

    # Check that project:path doesn't start or end with "/"
    # assert check_project_path_not_start_or_end_with_slash(yaml_content)
    # Check that path_to_vm info value is a yaml file

    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_ram_is_allowed - start check!")
    if check_if_path_to_vm_key_go_to_yaml_file(yaml_content) is False:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_path_to_vm_key_go_to_yaml_file is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_path_to_vm_key_go_to_yaml_file is SUCCESS !!!!")
    # Check that YAML file contains project:, devices: and links: keys

    # Check that YAML file contains project:, devices: and links: keys
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_ram_is_allowed - start check!")
    if check_if_keys_are_in_yaml_file(yaml_content) is False:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_keys_are_in_yaml_file is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_keys_are_in_yaml_file is SUCCESS !!!!")

    # Check that YAML file keys are corrects
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_yaml_keys_are_correct - start check!")
    if check_if_yaml_keys_are_correct(yaml_content) is False:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_yaml_keys_are_correct is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_yaml_keys_are_correct is SUCCESS !!!!")
    # Check that each links have an different ID
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path})[link:id] check_if_duplicate_param - start check!")
    if check_if_duplicate_param(yaml_content, YAML_LINKS_KEY, LINKS_ID_KEY) is False:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path})[link:id] check_if_duplicate_param is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path})[link:id] check_if_duplicate_param is SUCCESS !!!!")
    # Check that each devices have an different name
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path})[device:name] check_if_duplicate_param - start check!")
    if check_if_duplicate_param(yaml_content, YAML_DEVICES_KEY, DEVICES_NAME_KEY) is False:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path})[device:name] check_if_duplicate_param is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path})[device:name] check_if_duplicate_param is SUCCESS !!!!")
    # Check that each devices have a different UUID
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path})[uuid] check_if_duplicate_param - start check!")
    if check_if_duplicate_param(yaml_content, YAML_DEVICES_KEY, DEVICES_UUID_KEY) is False:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path})[uuid] check_if_duplicate_param is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path})[uuid] check_if_duplicate_param is SUCCESS !!!!")
        
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
    if yaml_content is not None:
        if YAML_ANSIBLE_KEY in yaml_content.keys():
            if check_ansible_groups_devices(yaml_content) is False:
                val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ansible_groups_devices is FAILED !!!!")
                return_value = False
            else:
                val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ansible_groups_devices is SUCCESS !!!!")

    
    # Check that ansible: keys are allowed
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ansible_keys - start check!")
    if check_ansible_keys(yaml_content) is False:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ansible_keys is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ansible_keys is SUCCESS !!!!")
    
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ansible_keys_groups_exist_if_playbooks_exist - start check!")
    if check_ansible_keys_groups_exist_if_playbooks_exist(yaml_content) is False:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ansible_keys_groups_exist_if_playbooks_exist is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_ansible_keys_groups_exist_if_playbooks_exist is SUCCESS !!!!")

    # Check that links is connected to existing devices
    # assert checkIfLinkConnectedToExistingDevice(yaml_content)
    # Check that each device ports are used only one time - not connected to many devices
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_nat_port - start check!")
    if check_if_port_use_many_time(yaml_content) is False:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_port_use_many_time is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_port_use_many_time is SUCCESS !!!!")


    # Check that each EVENG port used to NAT is unique
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_nat_port - start check!")
    if check_nat_port(yaml_content) is False:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_nat_port is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_nat_port is SUCCESS !!!!")
    
    # Check port-forwarding is between 10000 et 30000
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_port_value - start check!")
    if check_port_value(yaml_content) is False:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_port_value is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_port_value is SUCCESS !!!!")
    
    # Check that each device has a unique IP address in OOB NETWORK
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_ip_address_in_oob - start check!")
    if check_device_ip_address_in_oob(yaml_content) is False:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_ip_address_in_oob is FAILED !!!!")
        return_value = False
    else:
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_ip_address_in_oob is SUCCESS !!!!")
    
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
    if yaml_content is not None:
        if YAML_CONFIGS_KEY in yaml_content.keys():
            if check_device_element(CONFIG_TYPES, yaml_content, dict_to_verify=YAML_CONFIGS_KEY, param_to_verify=CONFIG_TYPE_KEY) is False:
                val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_element(CONFIG_TYPES) is FAILED !!!!")
                return_value = False
            else:
                val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_device_element(CONFIG_TYPES) is SUCCESS !!!!")

    # Check that device image is available in the EVE-NG
    if pipeline is False:
        val_log.debug("================================================================================================")
        val_log.debug(
            f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_image_is_available - start check!")
        if check_if_image_is_available(api, yaml_content) is False:
                val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_image_is_available is FAILED !!!!")
                return_value = False
        else:
            val_log.debug(
                f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_image_is_available is SUCCESS !!!!")

    # Check memory available vs memery asked by devices
    if pipeline is False:
        val_log.debug("================================================================================================")
        val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_vm_memory_free_vs_devices_memory_asked - start check!")
        if check_vm_memory_free_vs_devices_memory_asked(api, yaml_content) is False:
            val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_vm_memory_free_vs_devices_memory_asked is FAILED !!!!")
            return_value = False
        else:
            val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_vm_memory_free_vs_devices_memory_asked is SUCCESS !!!!")  
    
    # Check that nodes in configs: node is in devices added
    val_log.debug("================================================================================================")
    val_log.debug(f"{HEADER} - validateYamlFileForPyEVENG]({file_path}) check_if_configs_nodes_exists - start check!")
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

    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_ip_pub_if_not_port_fowrading] yaml_content is EMPTY (NoneType)!")
        return False

    port_forwarding = False
    return_value = True

    if YAML_LINKS_KEY in yaml_content.keys():
        for link in yaml_content[YAML_LINKS_KEY]:
            if LINKS_DST_KEY in link.keys():
                if link[LINKS_DST_KEY] == KEYWORD_TO_TELL_THAT_A_LINK_IS_OOB:
                    val_log.debug(f"{HEADER} check_ip_pub_if_not_port_fowrading] link_id {link[LINKS_ID_KEY]} is OOB !")
                    if LINKS_SRC_KEY in link.keys():
                        for oob_interface in link[LINKS_SRC_KEY]:
                            if OOB_IP_MGMT_KEY in oob_interface.keys() and OOB_SSH_KEY in oob_interface.keys() and OOB_NAT_KEY in oob_interface.keys():
                                val_log.debug(f"{HEADER} check_ip_pub_if_not_port_fowrading] There are port-forwarding !")
                                port_forwarding = True
                            else:
                                val_log.debug(f"{HEADER} check_ip_pub_if_not_port_fowrading] There are NOT port-forwarding !")

                    if port_forwarding is False:
                        if LINKS_IP_EVE_KEY in  link.keys() or LINKS_IP_PUB_KEY in link.keys():
                            val_log.debug(f"{HEADER} check_ip_pub_if_not_port_fowrading] ip_pub: or ip_eve are present...")
                            print(f"{HEADER} check_ip_pub_if_not_port_fowrading] Error ip_eve or ip_pub can not exist if there are no port-forwarding")
                            return_value = False

    val_log.debug(f"{HEADER} check_ip_pub_if_not_port_fowrading] Return value is {return_value} !")
    return return_value

# =========================================================================================================================================================
#
# Check that projet:name doesn't start or end with /
#
def check_project_path_not_start_or_end_with_slash(yaml_content:dict()) -> bool:

    val_log.debug(f"{HEADER} check_project_path_not_start_or_end_with_slash] Start function !")

    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_project_path_not_start_or_end_with_slash] yaml_content is EMPTY (NoneType)!")
        return False

    return_value = True

    if YAML_PROJECT_KEY in yaml.keys():
        if PROJECT_PATH_KEY in yaml_content[YAML_PROJECT_KEY].keys():
            val_log.debug(
                f"{HEADER} - check_project_path_not_start_or_end_with_slash] Project path in EVE-NG = {yaml_content[YAML_PROJECT_KEY][PROJECT_PATH_KEY]}!")
            if str(yaml_content[YAML_PROJECT_KEY][PROJECT_PATH_KEY]).startswith('/') or \
                    str(yaml_content[YAML_PROJECT_KEY][PROJECT_PATH_KEY]).endswith('/'): 
                pprintline(f"{yaml_content[YAML_PROJECT_KEY][PROJECT_PATH_KEY]}")
                val_log.debug(
                    f"[EveYAMLValidate.py - check_project_path_not_start_or_end_with_slash] Error ! 'project:path' starts or ends with a / (slash).")
                return_value = False
    else:
        val_log.debug(f"{HEADER} - check_project_path_not_start_or_end_with_slash] keys '{YAML_PROJECT_KEY}' is not in the YAML file!")

    val_log.debug(f"{HEADER} - check_project_path_not_start_or_end_with_slash] return_value={return_value}!")
    if return_value is False:
        val_log.debug(f"{HEADER} - check_project_path_not_start_or_end_with_slash] Error with the EVE-NG path!")
        val_log.debug(f"\t\t==>> {yaml_content[YAML_PROJECT_KEY][PROJECT_PATH_KEY]}")
        print(f"{HEADER} - check_project_path_not_start_or_end_with_slash] Error with the EVE-NG path!")
        print(f"\t\t==>> {yaml_content[YAML_PROJECT_KEY][PROJECT_PATH_KEY]}")

    return return_value


def check_vm_memory_free_vs_devices_memory_asked_with_path(api: PyEVENG.PyEVENG, path_to_yaml_file: str()) -> bool:
    return check_vm_memory_free_vs_devices_memory_asked(
        api,
        open_yaml_files(
            path_to_yaml_file
        )
    )

# =========================================================================================================================================================
#
# Check memory available vs memery asked by devices
#
def check_vm_memory_free_vs_devices_memory_asked(api: PyEVENG.PyEVENG, yaml_content: dict()) -> bool:

    val_log.debug(f"{HEADER} - check_vm_memory_free_vs_devices_memory_asked] Start function !")

    total_memory = 0
    coefficient = 1.2
    return_value = True

    val_log.debug(f"{HEADER} - check_vm_memory_free_vs_devices_memory_asked](1) total_memory={total_memory}!")
    val_log.debug(f"{HEADER} - check_vm_memory_free_vs_devices_memory_asked](1) coefficient={coefficient}!")

    if YAML_DEVICES_KEY in yaml_content.keys():
        for device in yaml_content[YAML_DEVICES_KEY]:
            
            val_log.debug(f"{HEADER} - check_vm_memory_free_vs_devices_memory_asked] device[DEVICES_RAM_KEY]={device[DEVICES_NAME_KEY]}!")
            val_log.debug(f"{HEADER} - check_vm_memory_free_vs_devices_memory_asked] RAM used={device[DEVICES_RAM_KEY]}!")
            total_memory = total_memory + device[DEVICES_RAM_KEY]

        vm_memory = api.get_vm_memory()

        val_log.debug(f"{HEADER} - check_vm_memory_free_vs_devices_memory_asked](1) total_memory={total_memory}!")
        val_log.debug(f"{HEADER} - check_vm_memory_free_vs_devices_memory_asked](1) vm_memory={vm_memory}!")
        val_log.debug(f"{HEADER} - check_vm_memory_free_vs_devices_memory_asked](1) total_memory / coefficient={int(total_memory / coefficient)}!")
        val_log.debug(f"{HEADER} - check_vm_memory_free_vs_devices_memory_asked](1) int(vm_memory) < int(total_memory / coefficient)={int(vm_memory) < int(total_memory / coefficient)}!")
        
        if int(vm_memory) < int(total_memory / coefficient):
            return_value = False

    val_log.debug(f"{HEADER} - check_vm_memory_free_vs_devices_memory_asked] return_value={return_value} !")

    return return_value

# =========================================================================================================================================================
#
# Check that groups: key exists in ansible: key
#
def check_ansible_keys_groups_exist_if_playbooks_exist(yaml_content: dict()) -> bool:
    
    val_log.debug(f"{HEADER} - check_ansible_keys_groups_exist_if_playbooks_exist] Start function !")

    if yaml_content is None:
        val_log.debug(
            f"{HEADER} - check_ansible_keys_groups_exist_if_playbooks_exist] yaml_content is EMPTY (NoneType)!")
        return False

    return_value = True
    error_playbook_lst = list()

    if "ansible" in yaml_content.keys():
        if "playbooks" in yaml_content['ansible'].keys() and "groups" not in yaml_content['ansible'].keys():
                return_value = False
    

    val_log.debug(f"{HEADER} - check_ansible_keys_groups_exist_if_playbooks_exist] return_value={return_value} !")
    if return_value is False:
        val_log.debug(f"{HEADER} - check_ansible_keys_groups_exist_if_playbooks_exist] ansible: groups: is mandatory if you use ansible: playbooks::")
        print(f"{HEADER} - check_ansible_keys_groups_exist_if_playbooks_exist] ansible: groups: is mandatory if you use ansible: playbooks:")

    return_value

# =========================================================================================================================================================
#
# Check that Ansible keys are allowd
#
def check_ansible_keys_with_path(path_to_yaml_file: str()) -> bool:
    val_log.debug(f"{HEADER} - check_ansible_keys] check_ansible_keys_with_path function !")
    return check_ansible_keys(
        open_yaml_files(
            path_to_yaml_file
        )
    )

def check_ansible_keys(yaml_content: dict()) -> bool:
    
    val_log.debug(f"{HEADER} - check_ansible_keys] check_ansible_keys function !")

    if yaml_content is None:
        val_log.debug(
            f"{HEADER} - check_ansible_keys] yaml_content is EMPTY (NoneType)!")
        return False
    
    return_value = True
    error_key_lst = list()

    if "ansible" in yaml_content.keys():
        for key in yaml_content['ansible'].keys():
            val_log.debug(f"{HEADER} - check_ansible_keys] key={key}!")
            if str(key) not in KEYS_IN_ANSIBLE:
                error_key_lst.append(str(key))
                return_value = False

    val_log.debug(f"{HEADER} - check_ansible_keys] return_value={return_value} !")
    if return_value is False:
        val_log.debug(f"{HEADER} - check_ansible_keys] - Error with the following Ansible key(s) :")
        val_log.debug(f"\t\t==>> {error_key_lst}")
        print(f"{HEADER} - check_ansible_keys] - Error with the following Ansible key(s) :")
        print(f"\t\t==>> {error_key_lst}")

    return_value


# =========================================================================================================================================================
#
# Check that ram of each node is correct
#
def check_if_ram_is_allowed_with_path(path_to_yaml_file: str()) -> bool:
    return check_if_ram_is_allowed(
        open_yaml_files(
            path_to_yaml_file
        )
    )

def check_if_ram_is_allowed(yaml_content: dict()) -> bool:
    
    val_log.debug(f"{HEADER} - check_if_ram_is_allowed] Start function !")

    if yaml_content is None:
        val_log.debug(
            f"{HEADER} - check_if_yaml_keys_are_correct] yaml_content is EMPTY (NoneType)!")
        return False

    return_value = True
    error_res_dict = dict()

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
def check_if_configs_nodes_exists_with_path(path_to_yaml_file: str()) -> bool:
    return check_if_configs_nodes_exists(
        open_yaml_files(
            path_to_yaml_file
        )
    )

def check_if_configs_nodes_exists(yaml_content: dict()) -> bool:

    val_log.debug(f"{HEADER} - check_if_configs_nodes_exists] Start function !")

    if yaml_content is None:
        val_log.debug(
            f"{HEADER} - check_if_yaml_keys_are_correct] yaml_content is EMPTY (NoneType)!")
        return False

    # Retrieve all devices: hostname
    all_devices_lst = list()
    return_value = True


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

# =========================================================================================================================================================
#
# Check if path_to_vm info value is a yaml file
#
def Ccheck_if_path_to_vm_key_go_to_yaml_file_with_path(path_to_yaml_file: str()) -> bool:
    return check_if_path_to_vm_key_go_to_yaml_file(
        open_yaml_files(
            path_to_yaml_file
        )
    )

def check_if_path_to_vm_key_go_to_yaml_file(yaml_content: dict()) -> bool:
    
    val_log.debug(f"{HEADER} - check_if_path_to_vm_key_go_to_yaml_file] Start function !")
    
    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_if_keys_are_in_yaml_file] yaml_content is EMPTY (NoneType)!")
        return False
    
    return_value = True

    if YAML_PATH_TO_VM_INFO in yaml_content.keys():
        if not ("yml" == str(yaml_content[YAML_PATH_TO_VM_INFO])[-3:] or "yaml" == str(yaml_content[YAML_PATH_TO_VM_INFO])[-4:]):
            val_log.debug(f"{HEADER} - check_if_path_to_vm_key_go_to_yaml_file] {yaml_content[YAML_PATH_TO_VM_INFO]} is NOT a YAML file !")
            val_log.debug(f"{HEADER} - check_if_path_to_vm_key_go_to_yaml_file] return_value pass to FALSE !")
            return_value = False

        else:
            val_log.debug(f"{HEADER} - check_if_path_to_vm_key_go_to_yaml_file] {yaml_content[YAML_PATH_TO_VM_INFO]} is a YAML file !")

    val_log.debug(f"{HEADER} - check_if_path_to_vm_key_go_to_yaml_file] return_value={return_value} !")
    if return_value is False:
        val_log.debug(f"{HEADER} - check_if_path_to_vm_key_go_to_yaml_file] The path doesn't point on a YAML file.")
        val_log.debug(f"\t\t==>> {yaml_content[YAML_PATH_TO_VM_INFO]}")
        print(f"{HEADER} - check_if_path_to_vm_key_go_to_yaml_file] The path doesn't point on a YAML file.")
        print(f"\t\t==>> {yaml_content[YAML_PATH_TO_VM_INFO]}")

    return return_value

# =========================================================================================================================================================
#
# Check that keys devices:, project: and links: are in your YAML file.
#   Configs: is not mandatory
#
def check_if_keys_are_in_yaml_file_with_path(path_to_yaml_file: str()) -> bool:
    return check_if_keys_are_in_yaml_file(
        open_yaml_files(
            path_to_yaml_file
        )
    )

def check_if_keys_are_in_yaml_file(yaml_content: dict()) -> bool:

    val_log.debug(f"{HEADER} - check_if_keys_are_in_yaml_file] Start function !")

    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_if_keys_are_in_yaml_file] yaml_content is EMPTY (NoneType)!")
        return False

    all_keys = yaml_content.keys()
    return_value = True
    error_key_missing_lst = list()
    
    val_log.debug(f"{HEADER} - check_if_keys_are_in_yaml_file] All keys in YAML file = all_keys{all_keys} !")

    for mandatory_key in MANDATORY_YAML_KEYS:
        if mandatory_key not in all_keys:
            val_log.debug(f"{HEADER} - check_if_keys_are_in_yaml_file] {mandatory_key} is NOT in the YAML file !")
            val_log.debug(f"{HEADER} - check_if_keys_are_in_yaml_file] return_value pass to FALSE !")
            error_key_missing_lst.append(mandatory_key)
            return_value = False

        else:
            val_log.debug(f"{HEADER} - check_if_keys_are_in_yaml_file] {mandatory_key} is in the YAML file !")

    val_log.debug(f"{HEADER} - check_if_keys_are_in_yaml_file] return_value={return_value} !")
    if return_value is False:
        val_log.debug(f"{HEADER} - check_if_keys_are_in_yaml_file] - Error with the following key(s) :")
        val_log.debug(f"\t\t==>> {error_key_missing_lst}")
        print(f"{HEADER} - check_if_keys_are_in_yaml_file] - Error with the following key(s) :")
        print(f"\t\t==>> {error_key_missing_lst}")

    return return_value

# =========================================================================================================================================================
#
# Check that keys is corrects
#
def check_if_yaml_keys_are_correct_with_path(path_to_yaml_file: str()) -> bool:
    return check_if_yaml_keys_are_correct(
        open_yaml_files(
            path_to_yaml_file
        )
    )

def check_if_yaml_keys_are_correct(yaml_content: dict()) -> bool:

    val_log.debug(f"{HEADER} check_if_yaml_keys_are_correct] Start function !")

    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_if_yaml_keys_are_correct] yaml_content is EMPTY (NoneType)!")
        return False

    return_value = True
    error_key_missing_lst = list()

    val_log.debug(f"{HEADER} check_if_yaml_keys_are_correct] YAML_KEYS={YAML_KEYS} !")

    for key in yaml_content.keys():
        val_log.debug(f"{HEADER} check_if_yaml_keys_are_correct] Key=({key}) is in YAML_KEYS ???")
        val_log.debug(f"\t\t==>> {key not in YAML_KEYS} // if confition is if key not in YAML_KEYS = {key not in YAML_KEYS}")
        if key not in YAML_KEYS:
            val_log.debug(f"{HEADER} check_if_yaml_keys_are_correct] return_value set to FALSE")
            error_key_missing_lst.append(key)
            return_value

    val_log.debug(f"{HEADER} check_if_yaml_keys_are_correct] return_value={return_value}")
    if return_value is False:
        val_log.debug(f"{HEADER} check_if_yaml_keys_are_correct] Error with the following key(s) :")
        val_log.debug(f"\t\t==> {error_key_missing_lst}")
        print(f"{HEADER} check_if_yaml_keys_are_correct] Error with the following key(s) :")
        print(f"\t\t==> {error_key_missing_lst}")

    return return_value

# =========================================================================================================================================================
#
# Check Type (QEMU, IOL, DYNAMIPS)
#
def check_device_element_with_path(element_lst: list(), path_to_yaml_file: str(), dict_to_verify: str() = "devices", param_to_verify: str() = "type") -> bool:
    return check_device_element(
        element_lst,
        open_yaml_files(
            path_to_yaml_file
        ), 
        dict_to_verify,
        param_to_verify)

def check_device_element(element_lst: list(), yaml_content: dict(), dict_to_verify: str() = "devices", param_to_verify: str() = "type") -> bool:

    val_log.debug(f"{HEADER} check_device_element] Start function !")

    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_device_element] yaml_content is EMPTY (NoneType)!")
        return False

    return_value = True
    error_missing = False
    error_not_list = False

    val_log.debug(f"{HEADER} check_device_element] element_lst={element_lst}")
    val_log.debug(f"{HEADER} check_device_element] dict_to_verify={dict_to_verify}")
    val_log.debug(f"{HEADER} check_device_element] param_to_verify={param_to_verify}")

    if dict_to_verify in yaml_content.keys():
        for device in yaml_content[dict_to_verify]:
            if not(device['type']=='iol' and param_to_verify=='console'):
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

# =========================================================================================================================================================
#
# Check Image (Cumulus, Extreme, Cisco, Arista, ...)
#
def check_if_image_is_available_with_path(availableImages: dict(), path_to_yaml_file: str(), dict_to_verify: str() = "devices", param_to_verify: str() = "image") -> bool:
    return check_if_image_is_available(
            availableImages, 
            open_yaml_files(
                path_to_yaml_file
            ), 
            dict_to_verify,
            param_to_verify
    )

def check_if_image_is_available(pyeveng, yaml_content: dict(), 
    dict_to_verify: str() = "devices", 
    param_to_verify: str() = "image"
    ) -> bool:

    val_log.debug(f"{HEADER} check_if_image_is_available] Start function !")

    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_if_image_is_available] yaml_content is EMPTY (NoneType)!")
        return False

    return_value = True
    error_dict = dict()

    if YAML_DEVICES_KEY in yaml_content.keys():
        for device in yaml_content[YAML_DEVICES_KEY]:
            images = pyeveng.get_image_version_by_model(device[DEVICES_TEMPLATE_KEY])    

            val_log.debug(f"{HEADER} - check_if_image_is_available] device={device}!")
            val_log.debug(f"{HEADER} - check_if_image_is_available] images={images}!")
            val_log.debug(f"{HEADER} - check_if_image_is_available] device[param_to_verify] not in images={device[param_to_verify] not in images}!")

            if device[param_to_verify] not in images:
                val_log.debug(f"{HEADER} - check_if_image_is_available] - Image {str(device[param_to_verify])} is NOT available on this EVE-NG")
                val_log.debug(f"\t\t => Error can be in your YAML file [template: or image:]")
                error_dict[device] = images
                return_value = False
            else:
                val_log.debug(f"{HEADER} - check_if_image_is_available] - Image {str(device[param_to_verify])} is available on this EVE-NG")

    val_log.debug(f"{HEADER} check_if_image_is_available] return_value={return_value}")
    if return_value is False:
        val_log.debug(f"{HEADER} check_if_yaml_keys_are_correct] Error with the following images(s) :")
        val_log.debug(f"\t\t==> {error_dict}")
        print(f"{HEADER} check_if_yaml_keys_are_correct] Error with the following images(s) :")
        PP.pprint(error_dict)

    return return_value

# =========================================================================================================================================================
#
# Check if a link is connected to a existing device
#
"""
def checkIfLinkConnectedToExistingDeviceWithPath(path_to_yaml_file: str(), devicesToVerify: str() = "devices", linksToVerify: str() = "links", deviceParamToVerify: str() = "name", linksDeviceToVerify: list = ['src', 'dst']):
    return checkIfLinkConnectedToExistingDevice(
        open_yaml_files(
            path_to_yaml_file
        ),
        devicesToVerify,
        linksToVerify,
        deviceParamToVerify,
        linksDeviceToVerify
    )


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

# =========================================================================================================================================================
#
# Check if links: node is in devices:name 
#
def check_if_links_host_exists_with_path(path_to_yaml_file: str(), dict_to_verify: str() = "links", param_to_verify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    return check_if_links_host_exists(
        open_yaml_files(
            path_to_yaml_file
        ),
        dict_to_verify,
        param_to_verify
    )

def check_if_links_host_exists(yaml_content: dict(), dict_to_verify: str() = "links", param_to_verify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:

    val_log.debug(f"{HEADER} check_if_links_host_exists] Start function !")

    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_if_links_host_exists] yaml_content is EMPTY (NoneType)!")
        return False

    all_values = set()
    return_value = True

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

    if YAML_DEVICES_KEY in yaml_content.keys():
        for device in yaml_content[YAML_DEVICES_KEY]:
            all_devices.append(device[DEVICES_NAME_KEY])

    for value in all_values:
        if value not in all_devices:
            val_log.debug(f"{HEADER} check_if_links_host_exists] Link {value} is not in 'devices:'")
            print(f"{HEADER} check_if_links_host_exists] Link {value} is not in 'devices:'")
            return_value = False

    return return_value

# =========================================================================================================================================================
#
# Check if port is use many time #### 
#


def check_if_port_use_many_time_with_path(path_to_yaml_file: str(), dict_to_verify: str() = "links", param_to_verify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:
    return check_if_port_use_many_time(
        open_yaml_files(
            path_to_yaml_file
        ), 
        dict_to_verify, 
        param_to_verify
    )

def check_if_port_use_many_time(yaml_content: dict(), dict_to_verify: str() = "links", param_to_verify: list() = ['src', 'sport', 'dst', 'dport']) -> bool:

    val_log.debug(f"{HEADER} check_if_port_use_many_time] Start function !")

    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_if_port_use_many_time] yaml_content is EMPTY (NoneType)!")
        return False

    all_hosts_in_links = dict()
    error_port_dict = dict()
    return_value = True

    if dict_to_verify in yaml_content.keys():
        for link in yaml_content[dict_to_verify]:
            if link[param_to_verify[2]] != KEYWORD_TO_TELL_THAT_A_LINK_IS_OOB:
                if link[param_to_verify[0]] not in all_hosts_in_links.keys():
                    all_hosts_in_links[link[param_to_verify[0]]] = list()
                if link[param_to_verify[2]] not in all_hosts_in_links.keys():
                    all_hosts_in_links[link[param_to_verify[2]]] = list()

            else:
                for oobConnection in link[param_to_verify[0]]:
                    if oobConnection[LINKS_SRC_HOST_KEY] not in all_hosts_in_links.keys():
                        all_hosts_in_links[oobConnection[LINKS_SRC_HOST_KEY]] = list()

        for link in yaml_content[dict_to_verify]:
            if link[LINKS_DST_KEY] != KEYWORD_TO_TELL_THAT_A_LINK_IS_OOB:
                if link[param_to_verify[1]] in all_hosts_in_links[link[param_to_verify[0]]]:
                    val_log.debug(
                        f"{HEADER} check_if_port_use_many_time] Port {link[param_to_verify[1]]} on {link[LINKS_SRC_KEY]} is use several times")
                    error_port_dict[link[param_to_verify[1]]] = link[LINKS_SRC_KEY]
                    return_value = False
                else:
                    all_hosts_in_links[link[param_to_verify[0]]].append(
                        link[param_to_verify[1]])

                if link[param_to_verify[3]] in all_hosts_in_links[link[param_to_verify[2]]]:
                    val_log.debug(
                        f"{HEADER} check_if_port_use_many_time] Port {link[param_to_verify[1]]} on {link[LINKS_SRC_KEY]} is use several times")
                    error_port_dict[link[param_to_verify[1]]] = link[LINKS_SRC_KEY]
                    return_value = False
                else:
                    all_hosts_in_links[link[param_to_verify[2]]].append(
                        link[param_to_verify[3]])

            else:
                for oobConnection in link[LINKS_SRC_KEY]:
                    if LINKS_SRC_PORT_KEY in oobConnection.keys():
                        if oobConnection[LINKS_SRC_PORT_KEY] in all_hosts_in_links[oobConnection[LINKS_SRC_HOST_KEY]]:
                            val_log.debug(
                                f"{HEADER} check_if_port_use_many_time] Port {link[param_to_verify[1]]} on {link[LINKS_SRC_KEY]} is use several times")
                            error_port_dict[link[paracheck_if_port_use_many_timem_to_verify[1]]] = link[LINKS_SRC_KEY]
                            return_value = False
                        else:
                            all_hosts_in_links[oobConnection[LINKS_SRC_HOST_KEY]].append(oobConnection[LINKS_SRC_PORT_KEY])

    val_log.debug(f"{HEADER} check_if_port_use_many_time] return_value={return_value}")
    if return_value is False:
        val_log.debug(f"{HEADER} check_if_port_use_many_time] Error with the following port :")
        val_log.debug(f"\t\t==>> {error_port_dict}")
        print(f"{HEADER} check_if_port_use_many_time] Error with the following port :")
        PP.pprint(error_port_dict)

    return return_value

# =========================================================================================================================================================
#
# Check port-forwarding is between 10000 et 30000
#
def check_port_value(yaml_content: dict()):

    val_log.debug(f"{HEADER} check_port_value] Start function !")

    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_port_value] yaml_content is EMPTY (NoneType)!")
        return False

    return_value = True
    list_error = list()

    if YAML_LINKS_KEY in yaml_content.keys():
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

    return return_value


# =========================================================================================================================================================
#
# Check that each EVENG port used to NAT is unique
#
def check_nat_port(yaml_content: dict()):

    val_log.debug(f"{HEADER} check_nat_port] Start function !")

    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_nat_port] yaml_content is EMPTY (NoneType)!")
        return False

    nat_port_lst = list()
    error_port_lst = list()
    return_value = True

    if YAML_LINKS_KEY in yaml_content.keys():
        for link in yaml_content[YAML_LINKS_KEY]:
            if KEYWORD_TO_TELL_THAT_A_LINK_IS_OOB in link[LINKS_DST_KEY]:
                for oob_link in link[LINKS_SRC_KEY]:
                    if OOB_NAT_KEY in oob_link.keys():
                        logging.debug(
                            f"{HEADER} check_nat_port] Link with port {oob_link[OOB_NAT_KEY]} already in list ??? ")
                        logging.debug(
                            f"==>> {oob_link[OOB_NAT_KEY] in nat_port_lst} ")
                        if oob_link[OOB_NAT_KEY] in nat_port_lst:
                            logging.debug(f"{HEADER} check_nat_port] ERROR with port {oob_link[OOB_NAT_KEY]}.")
                            error_port_lst.append(oob_link[OOB_NAT_KEY])
                            return_value = False
                        else:
                            logging.debug(f"{HEADER} check_nat_port] port {oob_link[OOB_NAT_KEY]} added in list.")
                            nat_port_lst.append(oob_link[OOB_NAT_KEY])

    logging.debug(f"{HEADER} check_nat_port] return_value={return_value}")
    if return_value is False:
        logging.debug(f"{HEADER} check_nat_port] ERROR the following port are present twice !!")
        logging.debug(f"\t\t==>> {error_port_lst}")
        print(f"{HEADER} check_nat_port] ERROR the following port are present twice !!")
        print(f"\t\t==>> {error_port_lst}")

    return return_value

# =========================================================================================================================================================
#
# Check that each device has a unique IP address in OOB NETWORK
#
def check_device_ip_address_in_oob(yaml_content: dict()):

    val_log.debug(f"{HEADER} check_device_ip_address_in_oob] Start function !")

    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_device_ip_address_in_oob] yaml_content is EMPTY (NoneType)!")
        return False

    return_value = True
    error_oob_lst = list()
    list_nat_port = list()

    if YAML_LINKS_KEY in yaml_content.keys():
        for link in yaml_content[YAML_LINKS_KEY]:
            if KEYWORD_TO_TELL_THAT_A_LINK_IS_OOB in link[LINKS_DST_KEY]:
                for oob_link in link[LINKS_SRC_KEY]:
                    if OOB_NAT_KEY in oob_link.keys():
                        val_log.debug(f"{HEADER} - check_device_ip_address_in_oob] IP_MGMT={oob_link[OOB_IP_MGMT_KEY]}!")
                        if oob_link[OOB_IP_MGMT_KEY] in list_nat_port:
                            error_oob_lst.append(oob_link[OOB_IP_MGMT_KEY])
                            return_value = False
                        else:
                            list_nat_port.append(oob_link[OOB_IP_MGMT_KEY])
    
    logging.debug(f"{HEADER} check_device_ip_address_in_oob] return_value={return_value}")
    if return_value is False:
        logging.debug(f"{HEADER} check_device_ip_address_in_oob] ERROR the following ip addresses are duplicate !!")
        logging.debug(f"\t\t==>> {error_oob_lst}")
        print(f"{HEADER} check_device_ip_address_in_oob] ERROR the following ip addresses are duplicate !!")
        print(f"\t\t==>> {error_oob_lst}")

    return return_value

# =========================================================================================================================================================
#
# Check If Hostname are duplicate (Spine01, Core01, Leaf01, ...) 
#
def check_if_duplicate_param_with_path(path_to_yaml_file: str(), dict_to_verify: str() = "devices", param_to_verify: str() = "name") -> bool:
    return check_if_duplicate_param(
        open_yaml_files(
            path_to_yaml_file
        ), 
        dict_to_verify, 
        param_to_verify
    )


def check_if_duplicate_param(yaml_content: dict(), dict_to_verify: str() = "devices", param_to_verify: str() = "name") -> bool:
    
    val_log.debug(f"{HEADER} - check_if_duplicate_param] Start function !")

    if yaml_content is None:
        val_log.debug(f"{HEADER} - check_if_duplicate_param] yaml_content is EMPTY (NoneType)!")
        return False
    
    return_value = True
    error_dup_lst = list()

    val_log.debug(f"{HEADER} - check_if_duplicate_param] param_to_verify={param_to_verify} !")
    val_log.debug(f"{HEADER} - check_if_duplicate_param] dict_to_verify={dict_to_verify} !")
    
    list_param = list()
    
    if dict_to_verify in yaml_content.keys():
        for node in yaml_content[dict_to_verify]:
            if not(node['type']=='iol' and param_to_verify=='uuid'):
                val_log.debug(f"{HEADER} - check_if_duplicate_param] node={node} !")
                val_log.debug(f"{HEADER} - check_if_duplicate_param] node[param_to_verify]={node[param_to_verify]} !")
                val_log.debug(f"{HEADER} - check_if_duplicate_param] node[param_to_verify] in list_param={node[param_to_verify] in list_param} !")
                if node[param_to_verify] in list_param:
                    error_dup_lst.append(node[param_to_verify])
                    return_value = False

                list_param.append(node[param_to_verify])
            
    if return_value is False:
        logging.debug(f"{HEADER} check_if_duplicate_param] ERROR the following values are duplicate in {dict_to_verify}:{param_to_verify} !!")
        logging.debug(f"\t\t==>> {error_dup_lst}")
        print(f"{HEADER} check_if_duplicate_param] ERROR the following values are duplicate in {dict_to_verify}:{param_to_verify} !!")
        print(f"\t\t==>> {error_dup_lst}")

    return return_value

# =========================================================================================================================================================
#
# Open a YAML file and return the content in a dict
#
def open_yaml_files(path: str()) -> dict():
    with open(path, "r") as f:
        return yaml.load(
            f.read()
        )


######################################################
if __name__ == "__main__":
    exit(EXIT_FAILURE)
