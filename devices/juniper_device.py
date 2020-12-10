#!/usr/bin/env python3
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
######################################################
#
# Import Library
#
try:
    from os import listdir
    from os.path import isfile, join
except ImportError as importError:
    print("Error import listdir")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import yaml
except ImportError as importError:
    print("Error import yaml")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import paramiko
except ImportError as importError:
    print("Error import paramiko")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import devices.abstract_device
except ImportError as importError:
    print("Error import abc - Cumulus abstractmethod")
    print(importError)
    exit(EXIT_FAILURE)

try:
    from exceptions.EveExceptions import EVENG_Exception
except ImportError as importError:
    print("Error import listdir")
    print(importError)
    exit(EXIT_FAILURE)
######################################################
#
# Constantes
#

######################################################
#
# Class
#

class JuniperDevice(devices.abstract_device.DeviceQEMUAbstract):
    raise NotImplementedError
