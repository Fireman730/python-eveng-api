#!/usr/bin/env python3.7
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
    import pexpect
except ImportError as importError:
    print("Error import [eveng-api] pexpect")
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

######################################################
#
# Functions
#

# ----------------------------------------------------
#
#
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
@click.option('--vm', default="./vm/vm_info.yml", help='Path to yaml file that contains EVE-NG VM informations.')
@click.option('--force', default=False, help='If --force=True, if a lab exists on the EVE-NG VM it will be remove.')
@click.option('--start', default="#", help='Labname you want to start')
@click.option('--backup', default="#", help='Path to yaml file that contains informations about backups.')
@click.option('--stop', default="#", help='Labname you want to stop')
@click.option('--remove', default="#", help='Labname you want to remove')
@click.option('--test', default=False, help='This argument will test your VM parameter in --vm.')
@click.option('--images', default=False, help='This argument will list images available on EVE-NG VM.')
@click.option('--ports', default="null", help='This argument will print port name for you can create your architecture YAML.')
@click.option('--connexion', default="null", help='This argument will return a dict with devices informations connexions <--connexion=mylab.unl>.')
@click.option('--telnet', default="null", help='This argument will return a dict with telnet informations connexions lab need LAB HAS TO BE STARTED.')
def main(deploy, vm, force, start, backup, stop, remove, test, images, ports, connexion, telnet):
    """
    This function is the main function of this project.
    It will retrieve arguments and run Functions

    """

    # Open files and retrieve informations
    # VM IP, username, password, etc.
    # [and]
    # ymlF that contains lab to deploy informations
    #
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
                        root=vmInfo['ssh_root'],
                        rmdp=vmInfo['ssh_pass'],
                        community=vmInfo['community'],
                        verbose=cliVerbose
    )
    
    # ======================================================================================================
    if telnet is not "null":
        PP.pprint(api.get_nodes_url(telnet))
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
            
            PP.pprint(open_file("./tools/oob_iptables_ex.yml"))
            

    if ports is not "null":
        print("==================================================================")
        PP.pprint(open_file("./devices/_port_device.yml")[ports])
        print("==================================================================")

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
        
        print("==================================================================")
        PP.pprint(result)
        print("==================================================================")
        api.logout()
    
    if deploy != "#":
        ymlF = open_file(deploy)
        try:
        
            #
            # Validate your yaml file
            #
            validateYamlFileForPyEVENG(api, ymlF, vmInfo)
            
            #
            # Call function that will create Lab, deploy devices, deploy links and push config
            #
            deploy_all(api, ymlF, vmInfo, force)
            api.logout()

            exit_success()

        except EVENG_Exception as eveError:
            print(eveError._message)

    # ======================================================================================================
    if backup != "#":
        ymlF = open_file(backup)
        api.getBackupNodesConfig(ymlF)
        api.logout()
        exit_success()

    # ======================================================================================================
    if start != "#":
        api.startLabAllNodes(start)
        api.logout()
        exit_success()

    if stop != "#":
        api.stopLabAllNodes(stop)
        api.logout()
        exit_success()

    if remove != "#":
        api.deleteLab(remove)
        api.logout()
        exit_success()

    exit_success()

# ----------------------------------------------------
#
#
#### Create a Topology (devices, links) based on a YAML File ####
def deploy_all (api: PyEVENG.PyEVENG, ymlF: dict(), vmInfo: dict(), force: bool()):
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

        #
        # Remove the lab if option --force=True
        #
        
        if force is True:
            api.deleteLab(ymlF['project']['name']+".unl")
            print("[eveng-api - deploy_all] - lab"+str(ymlF['project']['name'])+".unl has been removed !")

        # 
        # Step to Create the lab
        #
        if "project" in ymlF.keys():
            print("[eveng-api - deploy_all] - deploy projects")
            api.createLab(ymlF['project'])
        
        if "devices" in ymlF.keys():
            print("[eveng-api - deploy_all] - deploy devices")
            api.addNodesToLab(ymlF['devices'],
                    ymlF['project']['name']+".unl")
        
        if "links" in ymlF.keys():
            print("[eveng-api - deploy_all] - deploy links")
            api.addNetworksLinksToLab(ymlF['links'],
                    ymlF['project']['name']+".unl")
        
        #
        # Start hosts to create folders in
        # /opt/unetlab/tmp/0/{LAB_ID}/{NODE_ID}/*
        #
        api.startLabAllNodes(ymlF['project']['name']+".unl")

        #
        # Stop hosts to push config with mount NBD
        #
        api.stopLabAllNodes(ymlF['project']['name']+".unl")
        
        if "configs" in ymlF.keys():
            print("[eveng-api - deploy_all] - push configs")
            api.addConfigToNodesLab(ymlF['configs'],
                                    ymlF['project']['name']+".unl")
        
        # 
        # Restart hosts when config files are pushed
        #
        api.startLabAllNodes(ymlF['project']['name']+".unl", enable=True)

    except EVENG_Exception as eve:
        print(eve._message)
        if eve._error != 12:
            api.deleteLab(ymlF['project']['name']+".unl")


    except Exception as e:
        print(e)
        print("[eveng-api - deploy_all] - error during la creation !")
        api.deleteLab(ymlF['project']['name']+".unl")

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
if __name__ == "__main__":
    main()
