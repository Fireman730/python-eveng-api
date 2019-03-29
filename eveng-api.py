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
@click.option('--vm', default="#", help='Path to yaml file that contains VM informations.')
@click.option('--clab', default="#", help='Path to yaml file that contains labs to create.')
@click.option('--blab', default="#", help='Path to yaml file that contains labs to backup.')
def main(login, mdp, ip, port, ssl, user, pod, root, rmdp, path):

    

    with open(path, 'r') as stream:
        try:
            file = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    nodesToCreate = list()
    for node in file['devices']:
        if node['hostname'] not in nodesToCreate:
            nodesToCreate.append(node['hostname'])
        else:
            raise Exception("Error some nodes have the same hostname")

    print(nodesToCreate)

    print(file['project'])

    
    api = PyEVENG.PyEVENG(login, mdp, ip, port, ssl, user, pod, root, rmdp)
    api.login()
    pjson(api.getNodeInstall())
    api.createLab(file['project'])
    
    #pjson(api.status())
    #pjson(api.getLab("cumulus-spine-leaf.unl"))
    #pjson(api.getLabID("cumulus-spine-leaf.unl"))
    #pjson(api.getLabAuthor("cumulus-spine-leaf.unl"))
    #pjson(api.getLabNodes("cumulus-spine-leaf.unl"))
    #pjson(api.getLabDescription("cumulus-spine-leaf.unl"))
    #pjson(api.getLabNodesID("cumulus-spine-leaf.unl"))
    #pjson(api.getLabNodesName("cumulus-spine-leaf.unl"))
    #pjson(api.getLabNodesAccessMethod("cumulus-spine-leaf.unl"))
    #pjson(api.startlabAllNodes("cumulus-spine-leaf.unl"))
    #pjson(api.getLabNodeInterfaces("cumulus-spine-leaf.unl", "1"))
    #pjson(api.startLabAllNodes("cumulus-spine-leaf.unl"))
    #pjson(api.stopLabNode("cumulus-spine-leaf.unl", "1"))
    #pjson(api.getLabNode("cumulus-spine-leaf.unl", "1"))
    #pjson(api.getNodeImage("cumulus-spine-leaf.unl", "1"))
    #api.getBackupConfig("/Volumes/Data/gitlab/python-eveng-api/backup", "cumulus-spine-leaf.unl", "1")
    #if "/" in path :
    #    write_in_file(config, path)
    #print(api.getBackupConfig("cumulus-spine-leaf.unl", "1"))
# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------

def write_in_file(config:str(), path:str()):
    file=open(path, "w")
    file.write(config)
    file.close()


if __name__ == "__main__":
    main()
