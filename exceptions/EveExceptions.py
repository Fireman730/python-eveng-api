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

    0X   =   Erro with API call
    1X   =   Error in lab creation
      -> 11 Lab Already Exists
      -> 12 ...
    2X   =   Error in devices creation
      -> 21 Not all nodes have been created
    3X   =   Error in links creation
    4X   =   Error in configs deployement


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
