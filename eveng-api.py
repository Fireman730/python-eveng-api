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


def pjson(jsonPrint):
    print(json.dumps(jsonPrint, indent=4, sort_keys=True))
    print("---------------------------------------------------------------------------------")


@click.command()
@click.option('--login', default="admin", help='EVE-NG username.')
@click.option('--mdp', default="eve", help='EVE-NG password.')
@click.option('--ip', default="localhost", help='EVE-NG IPv4 address.')
@click.option('--port', default="443", help='EVE-NG http/s port.')
@click.option('--ssl', default=True, help='EVE-NG connection with SSL.')
@click.option('--user', default="Users", help='EVE-NG folder where found the lab.')
@click.option('--pod', default="0", help='EVE-NG POD number.')
def main(login, mdp, ip, port, ssl, user, pod):

    print("[eveng-api - main] -", login, mdp, ip, port, ssl, user, pod)
    api = PyEVENG.PyEVENG(login, mdp, ip, port, ssl, user, pod)

    api.login()
    #pjson(api.getNodeInstall())
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
    #pjson(api.getLabNodes("cumulus-spine-leaf.unl"))
    #pjson(api.getLabNodeInterface("cumulus-spine-leaf.unl", "1"))
    #pjson(api.startLabAllNodes("cumulus-spine-leaf.unl"))
    #pjson(api.stopLabNode("cumulus-spine-leaf.unl", "1"))
    #pjson(api.getLabNode("cumulus-spine-leaf.unl", "1"))
    #pjson(api.getNodeImage("cumulus-spine-leaf.unl", "1"))
    #pjson(api.getLabNodes("cumulus-spine-leaf.unl"))
    #pjson(api.getLab("cumulus-spine-leaf.unl"))
    #print(api.getCumulusNodeConfigFilesByProjectIDAndNodeID("cumulus-spine-leaf.unl", "1"))
    print(api.getBackupConfig("cumulus-spine-leaf.unl", "1"))
# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
