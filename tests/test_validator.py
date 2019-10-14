#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

"""
This file is used by Gitlab CI.
It will call EveYAMLValidate.py to test if topology.yml files are working fine

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
    import api.PyEVENG
except ImportError as importError:
    print("Error import [test_validator] api.PyEVENG")
    print(importError)
    exit(EXIT_FAILURE)

try:
    from tests.EveYAMLValidate import validateYamlFileForPyEVENG
except ImportError as importError:
    print("Error import [test_validator] tests.EveYAMLValidate")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import os
except ImportError as importError:
    print("Error import [test_validator] os")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import yaml
except ImportError as importError:
    print("Error import [test_validator] yaml")
    print(importError)
    exit(EXIT_FAILURE)

######################################################
#
# Constantes
#
FILES_TO_TEST_PATH = "./../architecture/tests"
FILE_EXTENSION_YML = ".yml"
FILE_EXTENSION_YAML = ".yaml"
VM_INFO_PATH_GHOST = "./../vm/vm_info.yml"

######################################################
#
# Funcions
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

######################################################
#
# MAIN Functions
#
def main():
    
    ghost_api = api.PyEVENG.PyEVENG

    for r, d, f in os.walk(FILES_TO_TEST_PATH):
        for file in f:
            if FILE_EXTENSION_YML in file or FILE_EXTENSION_YAML in file: 
                validateYamlFileForPyEVENG(
                    ghost_api, 
                    open_file(os.path.join(r, file)),
                    vm_info=VM_INFO_PATH_GHOST,
                    pipeline=True
                )

# -----------------------------------------------------------------------------------------------------------------------------
#
#
if __name__ == "__main__":
    main()
