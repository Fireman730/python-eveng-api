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

class EVENG_Exception(Exception):
    """
    This class is used for EVENG Exception

    0XY   =   Erro with API call
    1XY   =   Error in lab creation
      -> 11 Lab Already Exists
      -> 12 ...
    2XY   =   Error in devices creation
      -> 21 Not all nodes have been created
    3XY   =   Error in links creation
    4XY   =   Error in configs deployement
    8XY   =   Error with SSH command
      -> 801 UMOUNT
      -> 802 MOUNT
    9XY   = Error in YAML file
      -> 910 - Lab to backup not in Folder

    """

    def getError(self):
        return self._error

    def getMessage(self):
        return self._message

    def __init__(self, message, error):

        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self._message = message
        self._error = error
