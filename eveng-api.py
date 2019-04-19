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
    import json
    import ast
    import xmltodict
    from xmljson import badgerfish as bf
    from shutil import copyfile
except ImportError as importError:
    print("Error import json, ast, xmltodict, xmljson, shutil")
    print(importError)
    exit(EXIT_FAILURE)

try:
    from EveYAMLValidate import validateYamlFileForPyEVENG
except ImportError as importError:
    print("Error import EveYAMLValidate")
    print(importError)
    exit(EXIT_FAILURE)

try:
    from exceptions.EveExceptions import EVENG_Exception
except ImportError as importError:
    print("Error import EVENG_Exception")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import PyEVENG
except ImportError as importError:
    print("Error import PyEVE-NG")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import click
except ImportError as importError:
    print("Error import click")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import yaml
except ImportError as importError:
    print("Error import yaml")
    print(importError)
    exit(EXIT_FAILURE)

try:
    from EveYAMLValidate import validateYamlFileForPyEVENG
except ImportError as importError:
    print("Error import eveng-yaml-validation")
    print(importError)
    exit(EXIT_FAILURE)
######################################################
#
# Constantes
#
NETWORK_TEMPLATE = dict({
    "@color": "",
    "@id": 99999,
    "@label": "",
    "@left": 519,
    "@linkstyle": "Straight",
    "@name": "Net-Spine01iface_1",
    "@style": "Solid",
    "@top": 193,
    "@type": "bridge",
    "@visibility": 0
})

INTERFACE_TEMPLATE = dict({
    '@id': 99999,
    '@name': 'eth0',
    '@type': 'ethernet',
    '@network_id': 99999
})

######################################################
#
# Functions
#

#### Print JSON files with indexation####
def pjson(jsonPrint):
    print(json.dumps(jsonPrint, indent=4, sort_keys=True))
    print("---------------------------------------------------------------------------------")

#### Main function ####
@click.command()
@click.option('--deploy', default="#", help='Path to yaml file that contains topology to deploy.')
@click.option('--start', default="#", help='Labname you want to start')
@click.option('--backup', default="#", help='Path to yaml file that contains informations about backups.')
@click.option('--stop', default="#", help='Labname you want to stop')
@click.option('--remove', default="#", help='Labname you want to remove')
def main(deploy, start, backup, stop, remove):

    if deploy != "#":
        ymlF, vmInfo = open_files(deploy)
        validateYamlFileForPyEVENG(ymlF, vmInfo)
        deploy_all(ymlF, vmInfo)
        exit(EXIT_SUCCESS)

    if backup != "#":
        backup_lab(backup)
        exit(EXIT_SUCCESS)

    if start != "#":
        i = start.find(',')

        vmInfo = open_all(str(start[i+1:]))
        try:
            api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                              vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
            api.startLabAllNodes(start[:i])
        except Exception as e:
            print(e)

    if stop != "#":
        i = stop.find(',')
    
        vmInfo = open_all(str(stop[i+1:]))
        try:
            api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                                  vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
            api.stopLabAllNodes(stop[:i])
        except Exception as e:
            print(e)

    if remove != "#":
        i = remove.find(',')
        
        vmInfo = open_all(str(remove[i+1:]))
        try:
            api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                                  vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
            api.deleteLab(remove[:i])
        except Exception as e:
            print(e)
    
    
    exit(EXIT_SUCCESS)
# -----------------------------------------------------------------------------------------------------------------------------
#### Create a Lab based on a YAML File ####
def create_lab(labToCreate, vmInfo):
    api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                          vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
    api.createLab(labToCreate['project'])

# -----------------------------------------------------------------------------------------------------------------------------
#
#
def startLab(ymlF,vmInfo):
    api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                          vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
    api.startLabAllNodes(ymlF['project']['name']+".unl")

# -----------------------------------------------------------------------------------------------------------------------------
#
#
def stopLab(ymlF, vmInfo):
    api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                          vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
    api.stopLabAllNodes(ymlF['project']['name'] + ".unl")

# -----------------------------------------------------------------------------------------------------------------------------
#
#
def removeLab(ymlF, vmInfo):
    api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                          vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
    api.deleteLab(ymlF['project'])

# -----------------------------------------------------------------------------------------------------------------------------
#### Create a Topology (devices, links) based on a YAML File ####
def deploy_all (ymlF, vmInfo):
    #api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
    #                      vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
    #print(api.getLabsInFolder())

    try:
        if "project" in ymlF.keys():
            create_lab(ymlF, vmInfo)
        
        if "devices" in ymlF.keys():
            deploy_device(ymlF, vmInfo)
        
        if "links" in ymlF.keys():
            deploy_links(ymlF, vmInfo)
        # start hosts for create folders
        startLab(ymlF, vmInfo)
        stopLab(ymlF, vmInfo)
        
        if "configs" in ymlF.keys():
            deploy_config(ymlF, vmInfo)
        
        startLab(ymlF, vmInfo)
    except EVENG_Exception as eve:
        print(eve._message)
        if eve._error != 12:
            removeLab(ymlF, vmInfo)
    except Exception as e:
        print(e)
        print("[eveng-api - deploy_all] - error during la creation !")
        removeLab(ymlF, vmInfo)
        


# -----------------------------------------------------------------------------------------------------------------------------
#
#
def deploy_config(configToDeploy, vmInfo):
    print("[deploy_config]")

    api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                          vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
    api.addConfigToNodesLab(configToDeploy['configs'],
                            configToDeploy['project']['name']+".unl")
# -----------------------------------------------------------------------------------------------------------------------------
#
#
def deploy_device(deviceToDeploy, vmInfo):
    # deviceToDeploy, vmInfo = open_files(path)
    print("[deploy_device]")
    #print(deviceToDeploy['project'])

    api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                              vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
    api.addNodesToLab(deviceToDeploy['devices'],
                      deviceToDeploy['project']['name']+".unl")

# -----------------------------------------------------------------------------------------------------------------------------
#
#
def deploy_links(linksToDeploy, vmInfo):
    print("[deploy_links]")

    api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                          vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])

    api.addNetworksLinksToLab(linksToDeploy['links'],
                              linksToDeploy['project']['name']+".unl")

# -----------------------------------------------------------------------------------------------------------------------------
#
#
def old_deploy_links(linksToDeploy, vmInfo):
    #linksToDeploy, vmInfo = open_files(path)
    print("[deploy_links]")

    api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                          vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])

    api.retrieveUNL(linksToDeploy['project']['name'],
                    linksToDeploy['path_to_save']+linksToDeploy['project']['name']+".unl")

    copyfile(str(linksToDeploy['path_to_save']+linksToDeploy['project']['name']+".unl"),
             str(linksToDeploy['path_to_save']+linksToDeploy['project']['name']+".xml"))

    with open(str(linksToDeploy['path_to_save']+linksToDeploy['project']['name']+".xml"), 'r') as content_file:
        content = content_file.read()

    data = json.dumps(bf.data(fromstring(content)))
    data = ast.literal_eval(data)

    for link in linksToDeploy['links']:
        newNetwork = dict(NETWORK_TEMPLATE)
        newNetwork['@id'] = link['id']
        newNetwork['@type'] = link['network']
        
        if link['dst'] == "OOB-NETWORK":
            newNetwork['@name'] = str("OOB-NETWORK")
        else:
            newNetwork['@name'] = str(
                link['src']+"("+link['sport']+")--"+link['dst']+"("+link['dport'] + ")")

        try:
            type(data['lab']['topology']['networks'])
        except KeyError:
            print("KEYERROR")
            data['lab']['topology']['networks'] = dict()
            data['lab']['topology']['networks']['network'] = list()

        print(newNetwork)
        data['lab']['topology']['networks']['network'].append(newNetwork)

        print("***************************************")
        for node in data['lab']['topology']['nodes']['node']:
            if link['dst'] == "OOB-NETWORK":
                for nodeConnectedToOOB in link['src']:
                    newInterface = dict(INTERFACE_TEMPLATE)
                    newInterface['@network_id'] = link['id']
                    newInterface['@id'] = nodeConnectedToOOB['port'][-1:]
                    newInterface['@name']=str(nodeConnectedToOOB['port'])+"-OOB"

                    try:
                        type(node['interface'])
                    except KeyError:
                        node['interface'] = list()

                    node['interface'].append(newInterface)

            if node['@name'] == link['src'] :
                newInterface = dict(INTERFACE_TEMPLATE)
                newInterface['@network_id'] = link['id']
                newInterface['@id'] = link['sport'][-1:]
                newInterface['@name'] = link['sport']

                try:
                    type(node['interface'])
                except KeyError:
                    node['interface'] = list()

                node['interface'].append(newInterface)

            if (node['@name'] == link['dst']):
                newInterface = dict(INTERFACE_TEMPLATE)
                newInterface['@network_id'] = link['id']
                newInterface['@id'] = link['dport'][-1:]
                newInterface['@name'] = link['dport']

                try:
                    type(node['interface'])
                except KeyError:
                    node['interface'] = list()

                if type(node['interface']) is dict:
                    node['interface'] = list()
                    node['interface'].append(newInterface)
                else:
                    node['interface'].append(newInterface)

        #xml = dicttoxml(data, root="lab")

    data['lab']['body'] = data['lab']['body']['$']
    data['lab']['description'] = data['lab']['description']['$']
    xml = xmltodict.unparse(data, pretty=True)

    fileXML = open(
        str(linksToDeploy['path_to_save']+linksToDeploy['project']['name']+".xml"), "w")
    fileXML.write(xml)
    print("[Write in XML...]")
    fileXML.close()

    copyfile(str(linksToDeploy['path_to_save']+linksToDeploy['project']['name']+".xml"),
             str(linksToDeploy['path_to_save']+linksToDeploy['project']['name']+".unl"))

    api.replaceUNL(
        linksToDeploy['project']['name'], str(linksToDeploy['path_to_save']+linksToDeploy['project']['name']+".unl"))

# -----------------------------------------------------------------------------------------------------------------------------
#### Backup a Lab based on a YAML File ####
def backup_lab(path):
    labtoBackup, vmInfo = open_files(path)

    try:
        api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'],
                              vmInfo['https_port'], vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
        
        api.getBackupNodesConfig(labtoBackup)
    except Exception as e:
        print(e)
# -----------------------------------------------------------------------------------------------------------------------------
#### Open a YAML File and open VM_path contains into YAML file ####
def open_files(path):
    with open(path, 'r') as s1:
        try:
            lab = yaml.load(s1)
            with open(lab['path_vm_info'], 'r') as s2:
                vmInfo = yaml.load(s2)
        except yaml.YAMLError as exc:
            print(exc)
    
    return lab, vmInfo

# -----------------------------------------------------------------------------------------------------------------------------
#### Create a Lab based on a YAML File ####
def open_all(path):
    with open(path, 'r') as s1:
        try:
            lab = yaml.load(s1)
        except yaml.YAMLError as exc:
            print(exc)
    return lab


# -----------------------------------------------------------------------------------------------------------------------------
#### Write config into a file ####
def write_in_file(config: str(), path: str()):
    file = open(path, "w")
    file.write(config)
    file.close()

# -----------------------------------------------------------------------------------------------------------------------------
#
#
if __name__ == "__main__":
    main()


