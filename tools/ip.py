#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NEW CLASS FOR CONVERT NETMASK AND MGMT IP ADDRESS
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
    import ipaddress
except ImportError as importError:
    print("Error import [ip.py] ipaddress")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import random
except ImportError as importError:
    print("Error import [ip.py] random")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import time
except ImportError as importError:
    print("Error import [ip.py] time")
    print(importError)
    exit(EXIT_FAILURE)

try:
    import sys
except ImportError as importError:
    print("Error import [ip.py] sys")
    print(importError)
    exit(EXIT_FAILURE)
######################################################
#
# Constantes
#

######################################################
#
# Functions
#

def generateRandomIPAddressInSubnetBothWithAsk (ipAddress, netmask) :
    """

    :param ipAddress:
    :param netmask:
    :return:
    """
    print("========================================================================")
    print("[generateRandomIPAddressInSubnetBothWithAsk] Receive - |", ipAddress, "| and |", netmask, "|")

    assert ipaddress.IPv4Address(ipAddress)
    assert isValideNetmask(netmask)

    ipAddressBits = convertInBitFormat(ipAddress)
    netmaskBits = convertInBitFormat(netmask)

    print("[generateRandomIPAddressInSubnetBothWithAsk] ipAddressBits - |", ipAddressBits, "|")
    print("[generateRandomIPAddressInSubnetBothWithAsk] netmaskBits - |", netmaskBits, "|")

    indexOfLast1 = (netmaskBits.find("0"))
    hostPartOfIPAddress = ipAddressBits[indexOfLast1:]
    lengthHostPartOfIPAddress = hostPartOfIPAddress.__len__()

    print("[generateRandomIPAddressInSubnetBothWithAsk] hostPartOfIPAddress - |", hostPartOfIPAddress, "|")
    print("[generateRandomIPAddressInSubnetBothWithAsk] lengthHostPartOfIPAddress - |", lengthHostPartOfIPAddress, "|")

    # we generate a random number. This number is index of bit will be changed
    indexOfBitWillBeChanged = (random.randint(1, lengthHostPartOfIPAddress)) - 1
    listIPAddressBits = list(ipAddressBits)

    if listIPAddressBits[(indexOfLast1 + indexOfBitWillBeChanged - 1)] == "1":
        listIPAddressBits[(indexOfLast1 + indexOfBitWillBeChanged - 1)] = "0"
    else:
        listIPAddressBits[(indexOfLast1 + indexOfBitWillBeChanged - 1)] = "1"

    ipAddressBits = ''.join(listIPAddressBits)

    print("[generateRandomIPAddressInSubnetBothWithAsk] ipAddressBits - |", ipAddressBits, "|")

    ipAddress = convertBitInIPAddress(ipAddressBits)

    print("[generateRandomIPAddressInSubnetBothWithAsk] ipAddress     - |", ipAddress, "|")

    ok = input("[ipAddress] - This IP is Ok for you ? [y=yes/n=NoAndEnterManually]")

    while ok != "y" or ok != "n":
        ok = input("Please answer by [y/n]")

    if ok == "y":
        return ipAddress
    else:
        valideIP = False
        while valideIP:
            ipAddress = input("Enter your IP address")
            return ipAddress
#
#
#
#
def generateRandomIPAddressInSubnetBoth (ipAddress, netmask) :
    """

    :param ipAddress:
    :param netmask:
    :return:
    """
    print("========================================================================")
    print("[generateRandomIPAddressInSubnetBoth] Receive - |", ipAddress, "| and |",netmask, "|")

    assert ipaddress.IPv4Address(ipAddress)
    assert isValideNetmask(netmask)

    ipAddressBits = convertInBitFormat(ipAddress)
    netmaskBits = convertInBitFormat(netmask)

    print("[generateRandomIPAddressInSubnetBoth] ipAddressBits - |", ipAddressBits, "|")
    print("[generateRandomIPAddressInSubnetBoth] netmaskBits   - |", netmaskBits, "|")

    indexOfLast1 = (netmaskBits.find("0"))
    hostPartOfIPAddress = ipAddressBits[indexOfLast1:]
    lengthHostPartOfIPAddress = hostPartOfIPAddress.__len__()

    print("[generateRandomIPAddressInSubnet] hostPartOfIPAddress - |", hostPartOfIPAddress, "|")
    print("[generateRandomIPAddressInSubnet] lengthHostPartOfIPAddress - |", lengthHostPartOfIPAddress, "|")

    # we generate a random number. This number is index of bit will be changed
    indexOfBitWillBeChanged = (random.randint(1, lengthHostPartOfIPAddress)) - 1
    listIPAddressBits = list(ipAddressBits)


    if listIPAddressBits[(indexOfLast1 + indexOfBitWillBeChanged - 1)] == "1":
        listIPAddressBits[(indexOfLast1 + indexOfBitWillBeChanged - 1)] = "0"
    else:
        listIPAddressBits[(indexOfLast1 + indexOfBitWillBeChanged - 1)] = "1"

    ipAddressBits = ''.join(listIPAddressBits)

    print("[generateRandomIPAddressInSubnetBoth] - |", ipAddressBits, "|")
    print("========================================================================")
    return convertBitInIPAddress(ipAddressBits)



def generateRandomIPAddressInSubnet (ipAddressWithMask) :

    """
    :param ipAddressWithMask: a String as "192.168.10.11 255.255.255.128"
    :return: ipAddress without netmask in same subnet as ip address give in parameter
    """
    print("========================================================================")
    print("[generateRandomIPAddressInSubnet] Receive - ", ipAddressWithMask, "|")

    netmaskBytes = extractNetmaskFromIPAddress(ipAddressWithMask)
    ipAddressBytes = extractIPAddress(ipAddressWithMask)

    print("[generateRandomIPAddressInSubnet] netmaskBytes - ", netmaskBytes, "|")
    print("[generateRandomIPAddressInSubnet] ipAddressBytes - ", ipAddressBytes, "|")

    assert ipaddress.IPv4Address(ipAddressBytes)
    assert isValideNetmask(netmaskBytes)

    ipAddressBits = convertInBitFormat(ipAddressBytes)
    netmaskBits = convertInBitFormat(netmaskBytes)

    print("[generateRandomIPAddressInSubnet] ipAddressBits - |", ipAddressBits, "|")
    print("[generateRandomIPAddressInSubnet] netmaskBits - |", netmaskBits, "|")

    indexOfLast1 = (netmaskBits.find("0"))
    hostPartOfIPAddress = ipAddressBits[indexOfLast1:]
    lengthHostPartOfIPAddress = hostPartOfIPAddress.__len__()

    print("[generateRandomIPAddressInSubnet] hostPartOfIPAddress - |", hostPartOfIPAddress, "|")
    print("[generateRandomIPAddressInSubnet] lengthHostPartOfIPAddress - |", lengthHostPartOfIPAddress, "|")

    # we generate a random number. This number is index of bit will be changed
    indexOfBitWillBeChanged = (random.randint(1, lengthHostPartOfIPAddress))-1
    listIPAddressBits = list(ipAddressBits)

    if listIPAddressBits[(indexOfLast1+indexOfBitWillBeChanged-1)] == "1" :
        listIPAddressBits[(indexOfLast1+indexOfBitWillBeChanged-1)] = "0"
    else :
        listIPAddressBits[(indexOfLast1+indexOfBitWillBeChanged-1)] = "1"

    ipAddressBits = ''.join(listIPAddressBits)

    print("[isInSameSubnet] ipAddressBits(2) - |", ipAddressBits, "|")
    print("[isInSameSubnet] Return  - |", convertBitInIPAddress(ipAddressBits), "|")
    print("========================================================================")
    return convertBitInIPAddress(ipAddressBits)
#
#
#
#
def isInSameSubnet (ipAddress, ipAddressWithMask) :
    """
    :param ipAddress: a String as "192.168.10.200
    :param ipAddressWithMask: a String as "192.168.10.11 255.255.255.128"
    :return:
    """

    print("========================================================================")
    print("[isInSameSubnet] Receive - ", ipAddress, " and ", ipAddressWithMask)
    assert ipaddress.IPv4Address(ipAddress)

    isInSame = True
    netmaskBytes = extractNetmaskFromIPAddress(ipAddressWithMask)
    ipAddressBytes = extractIPAddress(ipAddressWithMask)

    print("[isInSameSubnet] - |", ipAddressBytes, "|")
    print("[isInSameSubnet] - |", netmaskBytes, "|")

    assert ipaddress.IPv4Address(ipAddressBytes)
    assert isValideNetmask(netmaskBytes)


    ipAddressInBits = convertInBitFormat(ipAddress)
    ipAddressBits = convertInBitFormat(ipAddressBytes)
    netmaskBits = convertInBitFormat(netmaskBytes)

    print("[isInSameSubnet] ipAddressInBits - |",ipAddressInBits,"|")
    print("[isInSameSubnet] ipAddressBits   - |",ipAddressBits,"|")
    print("[isInSameSubnet] netmaskBits     - |",netmaskBits,"|")

    indexOfLast1 = (netmaskBits.find("0"))

    only1InNetmask = netmaskBits[:indexOfLast1]

    index = 0
    while index < indexOfLast1 and isInSame:
        if ipAddressInBits[index] != ipAddressBits[index] :
            print(ipAddressInBits[index], " == ", ipAddressBits[index], "?")
            isInSame = False

        index = index + 1

    print("[isInSameSubnet] Return  - ", isInSame, "|")
    print("========================================================================")
    return isInSame



def isValideNetmask(netmask):
    """
    We receive a netmask.
    We check if is it compose by 4 bytes
    Check if is it a correct mask and return it if it's correct

    :param netmask:
    :return int: -1 if netmask is incorrect and CIDR notation Lenght
    """
    print("========================================================================")
    # We check if length netmask is 32 (4 bytes)
    print("[isValideNetmask] Receive -" , netmask, "|")
    netmaskBits = convertInBitFormat(netmask)
    assert netmaskBits.__len__() == 32

    # We check if netmask is valid
    indexFirst0 = netmaskBits.find("0")
    if netmaskBits.find("0") != -1:
        if netmaskBits[indexFirst0:].find("1") != -1:
            print("[isValideNetmask] Return  -", False, "|")
            return False

    print("[isValideNetmask] Return  -", True, "|")
    print("========================================================================")
    return True
#
#
#
#
def convertBitInIPAddress (IPAddressInBits) :
    """

    :param IPAddressInBits:
    :return:
    """
    print("========================================================================")

    print("[convertBitInIPAddress] Receive - ", IPAddressInBits, "|")
    print("[convertBitInIPAddress] Return  - ", \
          str(int(IPAddressInBits[:8], 2)) + "." + str(int(IPAddressInBits[8:16], 2)) + \
          "." + str(int(IPAddressInBits[16:24], 2)) + "." + str(int(IPAddressInBits[24:], 2)), "|")

    print("========================================================================")

    return ("" + str(int(IPAddressInBits[:8], 2)) + "." + str(int(IPAddressInBits[8:16], 2)) + \
            "." + str(int(IPAddressInBits[16:24], 2)) + "." + str(int(IPAddressInBits[24:], 2)))

#
#
#
#
def convertInBitFormat (data):
    """
    :param netmask:
    :return:
    """
    print("========================================================================")
    # We put in a list 4 bytes and verify there are exactly 4 bytes
    allBytes = data.split(".")

    print("[convertInBitFormat] Receive  - ", data, "|")
    print("[convertInBitFormat] allBytes -", allBytes, "|")
    assert allBytes.__len__() == 4

    # We put in a string the netmask in bits
    netmaskCIDR = ""
    for bytes in allBytes:
        # [2:] for remove "0b"
        netmaskCIDR = netmaskCIDR + str(bin(int(bytes))[2:].zfill(8))

    print("[convertInBitFormat] Return   - ", netmaskCIDR, "|")
    print("========================================================================")
    return netmaskCIDR

#
#
#
#
def convertNetmaskToCIDR(netmask) :
    """

    :param netmask:
    :return:  Netmask length CIDR Notation. It's only "how many 1 there are"
    """
    print("========================================================================")
    print("[convertNetmaskToCIDR] Receive - ", netmask, "|")
    if isValideNetmask(netmask) :
        netmaskBits = convertInBitFormat(netmask)
        netmaskNotationCIDR = netmaskBits.find("0")
        print("[convertNetmaskToCIDR] Return  - ", netmaskNotationCIDR, "|")
        print("========================================================================")
        return netmaskNotationCIDR


#
#
#
#
def convertCIDRtoNetmask(cidr):
    """

    :param cidr:
    :return:  Netmask length CIDR Notation. It's only "how many 1 there are"

    """
    print("[ip - convertNetmaskToCIDR] Receive - ", cidr, "|")

    bits = 0
    for i in range(32-int(cidr), 32):
        bits |= (1 << i)
    return "%d.%d.%d.%d" % ((bits & 0xff000000) >> 24, (bits & 0xff0000) >> 16, (bits & 0xff00) >> 8, (bits & 0xff))

#
#
#
#
def extractNetmaskFromIPAddress(ipv4WithNetmask) :
    """
    :param ipv4WithNetmask:
    :return
    """

    # We receive in parameter an ipv4 address and mask as "192.168.10.11 255.255.255.0"

    # We will extract only the netmask from ip parameter
    # There is not check in this function
    print("========================================================================")
    print("[extractNetmaskFromIPAddress] Receive - ", ipv4WithNetmask, "|")
    indexNetmask = (ipv4WithNetmask.find(" ") + 1)
    netmask = ipv4WithNetmask[indexNetmask:]

    print("[extractNetmaskFromIPAddress] Return  - ", netmask, "|")
    print("========================================================================")
    return netmask
#
#
#
#
def extractIPAddress(ipv4WithNetmask) :
    """
    :param ipv4WithNetmask:
    :return
    """

    # We receive in parameter an ipv4 address and mask as "192.168.10.11 255.255.255.0"

    # We will extract only the ip address
    # There is not check in this function only separation
    print("========================================================================")
    print("[extractIPAddress] Receive - ", ipv4WithNetmask, "|")

    indexEndIPv4Address = (ipv4WithNetmask.find(" "))
    ipAddres = ipv4WithNetmask[:indexEndIPv4Address]

    print("[extractIPAddress] Return  - ", ipAddres, "|")
    print("========================================================================")
    return ipAddres
#
#
#
#
