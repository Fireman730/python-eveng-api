#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# Default value used for exit()
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

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


def pjson(jsonPrint):
    print(json.dumps(jsonPrint, indent=4, sort_keys=True))
    print("---------------------------------------------------------------------------------")


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

@click.command()
@click.option('--create', default="#", help='Path to yaml file that contains lab to create.')
@click.option('--deploy', default="#", help='Path to yaml file that contains topology to deploy.')
@click.option('--config', default="#", help='Path to directory that contains nodes configuration files.')
@click.option('--start', default="#", help='Labname you want to start')
@click.option('--modify', default="#", help='Path to Ansible playbooks to execute.')
@click.option('--backup', default="#", help='Path to yaml file that contains informations about backups.')
@click.option('--stop', default="#", help='Labname you want to stop')
@click.option('--remove', default="#", help='Labname you want to remove')
def main(create, deploy, config, start, modify, backup, stop, remove):

    if create != "#":
        #create_lab(create)
        exit(EXIT_SUCCESS)

    if deploy != "#":
        #deploy_device(deploy)
        #deploy_links(deploy)
        deploy_all(deploy)
        exit(EXIT_SUCCESS)

    if backup != "#":
        backup_lab(backup)
        exit(EXIT_SUCCESS)
    
    

    
    
    




# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------------------------------------------------------
def deploy_all (path):
    yml, vmInfo = open_files(path)

    create_lab(yml, vmInfo)
    deploy_device(yml, vmInfo)
    deploy_links(yml, vmInfo)
    

def deploy_device(deviceToDeploy, vmInfo):
    # deviceToDeploy, vmInfo = open_files(path)
    print("[deploy_device]")

    api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                              vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
    api.addNodesToLab(deviceToDeploy['devices'],
                      deviceToDeploy['project']['name']+".unl")


def deploy_links(linksToDeploy, vmInfo):
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
        newNetwork['@name'] = str(link['src']+"("+link['sport']+")--"+link['dst']+"("+link['dport'] +")")

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
            if (node['@name'] == link['src']):
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
# -----------------------------------------------------------------------------------------------------------------------------
def backup_lab(path):
    labtoBackup, vmInfo = open_files(path)

    try:
        api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'],
                              vmInfo['https_port'], vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
        
        api.getBackupNodesConfig(labtoBackup)
    except Exception as e:
        print(e)
# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------
def open_files(path):
    with open(path, 'r') as s1:
        try:
            lab = yaml.load(s1)
            with open(lab['path_vm_info'], 'r') as s2:
                vmInfo = yaml.load(s2)
        except yaml.YAMLError as exc:
            print(exc)
    
    return lab, vmInfo


def open_all(path):
    with open(path, 'r') as s1:
        try:
            lab = yaml.load(s1)
        except yaml.YAMLError as exc:
            print(exc)
    return lab


# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------
def write_in_file(config: str(), path: str()):
    file = open(path, "w")
    file.write(config)
    file.close()


if __name__ == "__main__":
    main()
