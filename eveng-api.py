#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description ...

"""

__author__     = "Dylan Hamel"
__maintainer__ = "Dylan Hamel"
__version__    = "1.0"
__email__      = "dylan.hamel@protonmail.com"
__status__     = "Production"
__copyright__  = "Copyright 2019"
__license__    = "MIT"

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
    import traceback
except ImportError as importError:
    print("Error import [eveng-api] traceback")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import time
except ImportError as importError:
    print("Error import [eveng-api] time")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import pexpect
except ImportError as importError:
    print("Error import [eveng-api] pexpect")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import tools.ansible.generate_hosts
except ImportError as importError:
    print("Error import [eveng-api] tools.ansible.generate_hosts")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import tools.routing
except ImportError as importError:
    print("Error import [eveng-api] tools.routing")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import json
except ImportError as importError:
    print("Error import [eveng-api] json")
    print(importError)
    exit(EXIT_FAILURE)

try:
    from tests.EveYAMLValidate import validateYamlFileForPyEVENG
except ImportError as importError:
    print("Error import [eveng-api] EveYAMLValidate")
    print(importError)
    exit(EXIT_FAILURE)

try:
    from exceptions.EveExceptions import EVENG_Exception
except ImportError as importError:
    print("Error import [eveng-api] EVENG_Exception")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import api.PyEVENG as PyEVENG
except ImportError as importError:
    print("Error import [eveng-api] PyEVENG")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import click
except ImportError as importError:
    print("Error import [eveng-api] click")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import yaml
except ImportError as importError:
    print("Error import [eveng-api] yaml")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import pprint
    PP = pprint.PrettyPrinter(indent=4)
except ImportError as importError:
    print("Error import [eveng-api] pprint")
    print(importError)
    exit(EXIT_FAILURE)
######################################################
#
# Constantes
#

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


######################################################
#
# Functions
#

# ----------------------------------------------------
#
#
def printline():
    print("==================================================================")

def pjson(jsonPrint: dict()):
    """
    Print JSON files with indexation

    Args:
        param1 (dict): JSON/dict() to print with indentation.

    """
    print(json.dumps(jsonPrint, indent=4, sort_keys=True))
    print("---------------------------------------------------------------------------------")

def exit_success():
    print("\n\n[eveng-api - exit_success] - Did you love this tool ?")
    print("Give a STAR https://gitlab.com/DylanHamel/python-eveng-api \n\n")
    exit(EXIT_SUCCESS)

######################################################
#
# MAIN Functions
#
@click.command()
@click.option('--deploy', default="#", help='Path to yaml file that contains topology to deploy.')
@click.option('--inventory', default="#", help='Generate Ansible virtual inventory hosts file.')
@click.option('--vm', default="./vm/vm_info.yml", help='Path to yaml file that contains EVE-NG VM informations.')
@click.option('--force', default="False", help='If --force=True, if a lab exists on the EVE-NG VM it will be remove.')
@click.option('--backup', default="#", help='Path to yaml file that contains informations about backups.')
@click.option('--start', default="#", help='Labname you want to start')
@click.option('--stop', default="#", help='Labname you want to stop')
@click.option('--nodes_id', default="#", help='Node that you want start/stop (1) or (1,3,4,5)')
@click.option('--remove', default="#", help='Labname you want to remove')
@click.option('--test', default=False, help='This argument will test your VM parameter in --vm.')
@click.option('--images', default=False, help='This argument will list images available on EVE-NG VM.')
@click.option('--ports', default="null", help='This argument will print port name for you can create your architecture YAML.')
@click.option('--connexion', default="null", help='This argument will return a dict with devices informations connexions <--connexion=mylab.unl>.')
@click.option('--telnet', default="null", help='This argument will return a dict with telnet informations connexions lab need LAB HAS TO BE STARTED.')
@click.option('--pod', default="0", help='This argument defines a on which POD the is stored.')
@click.option('--folder', default="Users", help='This argument defines a on which FOLDER lab is stored.')
@click.option('--debug', default=False, help='Enter in debug mode.')
def main(deploy, inventory, vm, force, backup, start, stop, nodes_id,remove, test, images, ports, connexion, telnet, pod, folder, debug):
    """
    This function is the main function of this project.
    It will retrieve arguments and run Functions

    """

    # Open files and retrieve informations
    # VM IP, username, password, etc.
    # [and]
    # ymlF that contains lab to deploy informations
    #
    if inventory == "#":
        vmInfo = open_file(vm)

        #
        # Create the object that is connected with EVE-NG API
        #
        cliVerbose = connexion is "null" and telnet is "null"

        api = PyEVENG.PyEVENG(vmInfo['https_username'],
                        vmInfo['https_password'],
                        vmInfo['ip'],
                        vmInfo['https_port'],
                        vmInfo['https_ssl'],
                        pod=pod,
                        userFolder=folder,
                        root=vmInfo['ssh_root'],
                        rmdp=vmInfo['ssh_pass'],
                        community=vmInfo['community'],
                        verbose=cliVerbose
        )

    # ======================================================================================================
    if telnet is not "null":
        try:
            PP.pprint(api.get_nodes_url(telnet))
        except EVENG_Exception as e:
            print(e)
        finally:
            api.logout()

        exit(EXIT_SUCCESS)

    if connexion is not "null":
        try:
            PP.pprint(api.get_remote_connexion_file(connexion))
            api.logout()
            exit(EXIT_SUCCESS)
        except FileNotFoundError as e:
            print(
                "[eveng-api - main] - Connection informations file not found !")
            print(
                "[eveng-api - main] - You probably don't use the right syntax of OOB links...")
            print(
                "eveng-api - main] - Please see https://gitlab.com/DylanHamel/python-eveng-api/wikis/Write-your-YAML-file-that-describes-your-netwrok-(part-4)")
            printline()
            PP.pprint(open_file("./tools/oob_iptables_ex.yml"))
            printline()


    if ports is not "null":
        printline()
        PP.pprint(open_file("./devices/_port_device.yml")[ports])
        printline()

    if test:
        PP.pprint(api.status())
        api.logout()

    if images:
        deviceTypes = api.getNodeInstall()
        result = dict()
        for deviceType in deviceTypes.keys():
            versions = api.getNodeVersionInstall(deviceType)
            if len(versions):
                result[deviceType] = versions

        printline()
        PP.pprint(result)
        printline()
        api.logout()

    if inventory!= "#":
        ymlF = open_file(inventory)
        if "ansible" in ymlF.keys():
            if "groups" in ymlF['ansible'].keys():
                tools.ansible.generate_hosts.generate(ymlF)

            if "playbooks"in ymlF['ansible'].keys():
                pass
        exit_success()


    if deploy != "#":
        ymlF = open_file(deploy)
        try:

            #
            # Validate your yaml file
            #
            valide = validateYamlFileForPyEVENG(api, ymlF, vmInfo)
            if valide:
                print(f"Your YAML file is OK :) !")
            else:
                print(f"Your YAML file is NOK :) !")
                exit(EXIT_FAILURE)
            #
            # Call function that will create Lab, deploy devices, deploy links and push config
            #
            deploy_all(api, ymlF, vmInfo, force, debug)
            api.logout()

            if "ansible" in ymlF.keys():
                if "groups" in ymlF['ansible'].keys():
                    tools.ansible.generate_hosts.generate(ymlF)

                if "playbooks"in ymlF['ansible'].keys():
                    pass

            exit_success()

        except EVENG_Exception as eveError:
            print(eveError._message)

    # ======================================================================================================
    if backup != "#":
        try:
            ymlF = open_file(backup)
        except FileNotFoundError as e:
            print(
                "[eveng-api - main] - Check if labname exists ...")

            # api.check_if_lab_exists(labName)

        api.get_backup_nodes_config(ymlF)
        api.logout()
        exit_success()

    # ======================================================================================================
    if start != "#":
        api.startLabAllNodes(start, nodes_id)
        api.logout()
        exit_success()

    if stop != "#":
        api.stopLabAllNodes(stop, nodes_id)
        api.logout()
        exit_success()

    if remove != "#":
        api.delete_lab(remove)
        api.logout()
        exit_success()

    exit_success()

# ----------------------------------------------------
#
#
#### Create a Topology (devices, links) based on a YAML File ####
def deploy_all (api: PyEVENG.PyEVENG, ymlF: dict(), vmInfo: dict(), force: str(), debug=False):
    """
    This function will create your network step by step.

    1st it will create project with information contained in your YAML files ['project] with REST API calls
    2nd it will create devives with information contained in your YAML files ['devices'] with REST API calls
    3th it will create links and networks with information contained in your YAML files ['links'] with REST API calls

    Then the devices will be started and stopped.
    These actions is mandatory to create {/opt/unetlab/tmp/0/{LAB_ID}/{NODE_ID}/} directoies

    4th it will push the config files contains in your YAML files ['configs'] with SSH connexion and mount NBD.

    Finally devices will be started.

    """
    try:

        api._set_folder(ymlF[YAML_PROJECT_KEY][PROJECT_PATH_KEY])

        #
        # Remove the lab if option --force=True
        #
        if str(force).upper() == "TRUE":
            api.delete_lab(ymlF[YAML_PROJECT_KEY][PROJECT_NAME_KEY]+".unl")
            print(
                f"[eveng-api - deploy_all] - lab {str(ymlF[YAML_PROJECT_KEY][PROJECT_NAME_KEY])}.unl has been removed !")

        #
        # Step to Create the lab
        #
        if YAML_PROJECT_KEY in ymlF.keys():
            print(f"[eveng-api - deploy_all] - deploy projects")
            api.create_lab(ymlF[YAML_PROJECT_KEY])

        if YAML_DEVICES_KEY in ymlF.keys():
            print(f"[eveng-api - deploy_all] - deploy devices")
            api.addNodesToLab(ymlF[YAML_DEVICES_KEY],
                              ymlF[YAML_PROJECT_KEY][PROJECT_NAME_KEY]+".unl")

        if YAML_LINKS_KEY in ymlF.keys():
            print(f"[eveng-api - deploy_all] - deploy links")
            api.addNetworksLinksToLab(ymlF[YAML_LINKS_KEY],
                                      ymlF[YAML_PROJECT_KEY][PROJECT_NAME_KEY]+".unl")

        #
        # Start hosts to create folders in
        # /opt/unetlab/tmp/0/{LAB_ID}/{NODE_ID}/*
        #
        api.startLabAllNodes(ymlF[YAML_PROJECT_KEY][PROJECT_NAME_KEY]+".unl")

        if YAML_CONFIGS_KEY in ymlF.keys():

            #
            # Stop hosts to push config with mount NBD
            #
            api.stopLabAllNodes(ymlF[YAML_PROJECT_KEY][PROJECT_NAME_KEY]+".unl")

            print("[eveng-api - deploy_all] - push configs")
            api.addConfigToNodesLab(ymlF[YAML_CONFIGS_KEY],
                                    ymlF[YAML_PROJECT_KEY][PROJECT_NAME_KEY]+".unl")

            #
            # Restart hosts when config files are pushed
            #
            api.startLabAllNodes(
                ymlF[YAML_PROJECT_KEY][PROJECT_NAME_KEY]+".unl", enable=True)

    except EVENG_Exception as eve:
        print(eve._message)
        if eve._error != 12:
            api.delete_lab(ymlF[YAML_PROJECT_KEY][PROJECT_NAME_KEY]+".unl")


    except Exception as e:
        print(e)
        if debug:
            traceback.print_exc()
        print("[eveng-api - deploy_all] - error during la creation !")
        api.delete_lab(ymlF[YAML_PROJECT_KEY][PROJECT_NAME_KEY]+".unl")

# ----------------------------------------------------
#
#
#### Open a YAML File and open VM_path contains into YAML file ####
def open_file(path: str()) -> dict():
    """
    This function  will open a yaml file and return is data

    Args:
        param1 (str): Path to the yaml file

    Returns:
        str: Node name
    """
    
    with open(path, 'r') as yamlFile:
        try:
            data = yaml.load(yamlFile)
        except yaml.YAMLError as exc:
            print(exc)

    return data

# -----------------------------------------------------------------------------------------------------------------------------
#
#
def test():
    address_ip = "192.168.31.1"
    print(f"=> cat /proc/sys/net/ipv4/conf/$(ip route show | grep {address_ip} | awk '{{print $3}}')/forwarding")

# -----------------------------------------------------------------------------------------------------------------------------
#
#
if __name__ == "__main__":
    #test()
    main()
