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

    1XY   =   Erro with API call
      -> 101 API Call method Error (GET, PUT, POST, etc)
    
    2XY   =   Error in lab creation
      -> 201 Lab Already Exists
      -> 202 ...

    3XY   =   Error in devices creation
      -> 301 Not all nodes have been created

    4XY   =   Error in links creation

    5XY   =   Error in configs deployement
    
    7XY   =   Error with Call API
        701   = Return code = 404
        702   = Return code = 404 Lab doesn't exist

    8XY   =   Error with SSH command
      -> 801 UMOUNT
      -> 802 MOUNT

    9XY   = Error in YAML file
      -> 900 - Error un "project:"
          -> 901: Key missing ing project:
          -> 902: Value for a key is not in a list
          -> 903: Error in a value
      -> 910 - Error in "devices:"
      -> 920 - Error in "links:"
      -> 930 - Error in "configs:"
          -> 931: Key missing in configs:
          -> 932: Value for a key is not in a list
          -> 933: Error in a value
      -> 940 - Error in "ansible:"

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
