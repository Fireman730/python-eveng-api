#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""
Description ...

"""

__author__ = "Dylan Hamel"
__maintainer__ = "Dylan Hamel"
__version__ = "1.0"
__email__ = "dylan.hamel@protonmail.com"
__status__ = "Production"
__copyright__ = "Copyright 2019"
__license__ = "MIT"

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
    import jinja2
except ImportError as importError:
    print("Error import [generate_hosts] jinja2")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import yaml
except ImportError as importError:
    print("Error import [generate_hosts] yaml")
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
HOSTS_FILE_TEMPLATE = "./templates/hosts.j2"
ARCHITECTURE_TEST_FILE = "./../architecture/2spines_4leafs.yml"
ANSIBLE_HOSTFILE = "./hosts"
######################################################
#
# Functions
#
# ----------------------------------------------------
#
#
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


def write_string_in_file(data: str(), path=ANSIBLE_HOSTFILE, *, mode="w+"):
    file = open(path, mode)
    file.write(data)
    file.close()


# ----------------------------------------------------
#
#
def main():

    data = open_file(ARCHITECTURE_TEST_FILE)
    
    #PP.pprint(data)
    #for link in data['links']:
    #    if "OOB-NETWORK" in link['dst']:
    #        for host in link['src']:
    #            if host['host'] == "Spine01":
    #                print(host)
    
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('./templates'), trim_blocks=False, lstrip_blocks=True)
    template = env.get_template('hosts.j2')
                       
    result = template.render(data)
    write_string_in_file(data=result)
# -----------------------------------------------------------------------------------------------------------------------------
#
#
if __name__ == "__main__":
    main()
