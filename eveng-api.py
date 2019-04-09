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
    from dicttoxml import dicttoxml
    import xmltodict
    import pprint
    from json2xml import json2xml, readfromurl, readfromstring, readfromjson
    from xml.dom import minidom
    from xmljson import badgerfish as bf
    from xml.etree.ElementTree import fromstring
    from shutil import copyfile
except ImportError as importError:
    print("Error import json")
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
@click.option('--create', default="#", help='Path to yaml file that contains lab to create.')
@click.option('--deploy', default="#", help='Path to yaml file that contains topology to deploy.')
@click.option('--oob', default="#", help='Path to yaml file that contains path to VM info, path to file config and devices.')
@click.option('--config', default="#", help='Path to directory that contains nodes configuration files.')
@click.option('--start', default="#", help='Labname you want to start')
@click.option('--modify', default="#", help='Path to Ansible playbooks to execute.')
@click.option('--backup', default="#", help='Path to yaml file that contains informations about backups.')
@click.option('--stop', default="#", help='Labname you want to stop')
@click.option('--remove', default="#", help='Labname you want to remove')
def main(create, deploy, oob, config, start, modify, backup, stop, remove):

    if create != "#":
        #create_lab(create)
        exit(EXIT_SUCCESS)

    if deploy != "#":
        #yamlF, vm = open_files(deploy)
        #deploy_device(yamlF, vm)
        #deploy_links(deploy)
        #assert validateYamlFileForPyEVENG(open_all(deploy))
        deploy_all(deploy)
        exit(EXIT_SUCCESS)

    if oob != "#":
        pushOOBConf(oob)
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
    
    
    exit(EXIT_SUCCESS)
# -----------------------------------------------------------------------------------------------------------------------------
#### Push Out-of-Band configuration ####
def pushOOBConf(path):
    ymlF, vmInfo = open_files(path)

    try:
        api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                              vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
        
        api.pushOOBConfiFile(ymlF)
    except Exception as e:
        print(e)



# -----------------------------------------------------------------------------------------------------------------------------
#### Create a Lab based on a YAML File ####
def create_lab(labToCreate, vmInfo):
    #labToCreate, vmInfo = open_files(path)
    print("[create_lab]")
    try:
        api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                          vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
        api.createLab(labToCreate['project'])
    except Exception as e:
        print(e)

# -----------------------------------------------------------------------------------------------------------------------------
#### Create a Topology (devices, links) based on a YAML File ####
def deploy_all (path):
    ymlF, vmInfo = open_files(path)

    create_lab(ymlF, vmInfo)
    deploy_device(ymlF, vmInfo)
    old_deploy_links(ymlF, vmInfo)
    
    
def deploy_device(deviceToDeploy, vmInfo):
    # deviceToDeploy, vmInfo = open_files(path)
    print("[deploy_device]")
    print(deviceToDeploy['project'])

    api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                              vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
    api.addNodesToLab(deviceToDeploy['devices'],
                      deviceToDeploy['project']['name']+".unl")


def deploy_links(linksToDeploy, vmInfo):
    print("[deploy_links]")

    api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                          vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])

    api.addNetworksLinksToLab(linksToDeploy['links'],
                              linksToDeploy['project']['name']+".unl")


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


if __name__ == "__main__":
    main()


