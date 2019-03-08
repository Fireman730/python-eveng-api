#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# Default value used for exit()
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

import json

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
@click.option('--user', default="admin", help='EVE-NG username.')
@click.option('--mdp', default="eve", help='EVE-NG password.')
@click.option('--ip', default="localhost", help='EVE-NG IPv4 address.')
@click.option('--port', default="80", help='EVE-NG http/s port.')
@click.option('--ssl', default=False, help='EVE-NG connection with SSL.')
def main(user, mdp, ip, port, ssl):

    print("[eveng-api - main] -", user, mdp, ip, port, ssl)
    api = PyEVENG.PyEVENG(user, mdp, ip, port, ssl)

    api.login()
    pjson(api.getUsers())
    pjson(api.getLab("cumulus-spine-leaf.unl"))

# -----------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
