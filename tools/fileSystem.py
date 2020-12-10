#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Dylan Hamel"
__version__ = "0.1"
__email__ = "dylan.hamel@protonmail.com"
__status__ = "Prototype"

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
    import click
except ImportError as importError:
    print("Error import [fileSystem.py - click]")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import os
except ImportError as importError:
    print("Error import [fileSystem.py - os]")
    print(importError)
    exit(EXIT_FAILURE)

######################################################
#
# Functions
#
def plist(objToPrint: list()):
    for obj in objToPrint:
        print(obj)


######################################################
#
# Main Functions
#
def getAllFilesInDirectory(path:str()) -> list():
    """
    This function will return all files contains in a directory and them subdirectory
    
    Args:
            param1 (str): Path to folder. This functions will go to sub-directory

        Returns:
            list: All files in directory and subdirectory
    """

    files = list()
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))

    return files

def getAllDirectoriesInDirectory(path: str()) -> list():
    """
    This function will return all directories contains in a directory
    
    Args:
            param1 (str): Path to folder. This functions will go to sub-directory

        Returns:
            list: All directories in directory
    """

    directories = list()
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for directory in d:
            directories.append(os.path.join(r, directory))

    return directories

#if __name__ == "__main__":
#    getAllDirectoriesInDirectory()
