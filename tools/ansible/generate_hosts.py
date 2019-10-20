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
ERROR_IMPORT = "Error import [generate_hosts]"
HEADER = "[generate_hosts -"
######################################################
#
# Import Library
#
try:
    import jinja2
except ImportError as importError:
    print(f"{ERROR_IMPORT} jinja2")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import yaml
except ImportError as importError:
    print(f"{ERROR_IMPORT} yaml")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import pprint
    PP = pprint.PrettyPrinter(indent=4)
except ImportError as importError:
    print(f"{ERROR_IMPORT} pprint")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import logging
    logging.getLogger(__name__)
    logging.basicConfig(
    level=logging.DEBUG,
    filename="./logs/genAnsible.log",
    format='[%(asctime)s] - %(levelname)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
    )
except ImportError as importError:
    print(f"{ERROR_IMPORT} logging")
    print(importError)
    exit(EXIT_FAILURE)
######################################################
#
# Constantes
#
HOSTS_FILE_DIRECTORY = "./tools/ansible/templates"
HOSTS_FILE_TEMPLATE = "hosts.j2"
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
    logging.debug(f"[{HEADER} open_file] Open {path}...")
    with open(path, 'r') as yamlFile:
        try:
            logging.debug(f"[{HEADER} open_file] Retrieve content of {path}...")
            data = yaml.load(yamlFile)
        except yaml.YAMLError as exc:
            print(exc)

    logging.debug(f"[{HEADER} open_file] Return data :")
    logging.debug(f"[{HEADER} open_file] {data} :")
    return data


# ----------------------------------------------------
#
#
def write_string_in_file(data: str(), path=ANSIBLE_HOSTFILE, *, mode="w+"):
    logging.debug(f"[{HEADER} write_string_in_file] Open {path}...")
    file = open(path, mode)
    logging.debug(f"[{HEADER} write_string_in_file] Write data...")
    file.write(data)
    logging.debug(f"[{HEADER} write_string_in_file] Close {path}...")
    file.close()

# ----------------------------------------------------
#
#
def generate(data:dict()):

    logging.debug(f"[{HEADER} generate] Your dynamic hosts file is being created ...")
    print(f"[{HEADER} generate] Your dynamic hosts file is being created ...")

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(
        HOSTS_FILE_DIRECTORY), trim_blocks=False, lstrip_blocks=True)
    template = env.get_template(HOSTS_FILE_TEMPLATE)

    result = template.render(data)

    logging.debug(f"[{HEADER} generate] file content :")
    logging.debug(f"{result}")

    write_string_in_file(data=result)

    logging.debug(f"[{HEADER} generate] Your dynamic hosts file has been created ...")
    print(f"[{HEADER} generate] Your dynamic hosts file has been created ...")
# -----------------------------------------------------------------------------------------------------------------------------
#
#
if __name__ == "__main__":
    data = open_file(ARCHITECTURE_TEST_FILE)
    generate(data)
