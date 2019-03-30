#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# Default value used for exit()
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

try:
    import json
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
        create_lab(create)
        exit(EXIT_SUCCESS)

    if deploy != "#":
        deploy_lab(deploy)
        exit(EXIT_SUCCESS)

    if backup != "#":
        backup_lab(backup)
        exit(EXIT_SUCCESS)
    


# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------
def create_lab(path):

    with open(path, 'r') as s1:
        try:
            labToCreate = yaml.load(s1)
            with open(labToCreate['path_vm_info'], 'r') as s2:
                vmInfo = yaml.load(s2)
        except yaml.YAMLError as exc:
            print(exc)

    try:
        api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                          vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
        api.createLab(labToCreate['project'])
    except Exception as e:
        print(e)
# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------
def deploy_lab(path):
    with open(path, 'r') as s1:
        try:
            labToDeploy = yaml.load(s1)
            with open(labToDeploy['path_vm_info'], 'r') as s2:
                vmInfo = yaml.load(s2)
        except yaml.YAMLError as exc:
            print(exc)
    
    try:
        api = PyEVENG.PyEVENG(vmInfo['https_username'], vmInfo['https_password'], vmInfo['ip'], vmInfo['https_port'],
                              vmInfo['https_ssl'], root=vmInfo['ssh_root'], rmdp=vmInfo['ssh_pass'])
        api.addNodesToLab(labToDeploy['devices'], labToDeploy['labname'])
    except Exception as e:
        print(e)
        
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

# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------
def write_in_file(config: str(), path: str()):
    file = open(path, "w")
    file.write(config)
    file.close()


if __name__ == "__main__":
    main()
