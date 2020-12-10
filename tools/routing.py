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
# Constantes
#
IPTABLES_INSTALL = "sudo apt-get install - y iptables"

IPTABLES_DNAT = "iptables -{} PREROUTING -t nat -i $(ip route show | grep {} | awk '{{print $3}}') -p tcp --dport {} -j DNAT --to {}:{}"
IPTABLES_ALLOWED = "iptables -{} FORWARD -p tcp -d {} --dport {} -j ACCEPT"
IPTABLES_SNAT = "iptables -{} POSTROUTING -t nat -o {} -p tcp --dport 22 -j SNAT --to {}"


#print(tools.routing.IPTABLES_DNAT.format("22022", "10.0.5.201", "22"))
#print(tools.routing.IPTABLES_ALLOWED.format("22022"))
#print(tools.routing.IPTABLES_SNAT.format("pnet5", "10.0.5.1"))

# hostname -I | awk '{print $1}' = 172.16.194.239
# ip route show | grep $(hostname -I | awk '{print $1}') | awk '{print $3}' = pnet0

# iptables -A PREROUTING -t nat -i $(ip route show | grep $(hostname -I | awk '{print $1}') | awk '{print $3}') -p tcp --dport 22022 -j DNAT --to 10.0.5.201:22
# iptables -A FORWARD -p tcp -d $(hostname -I | awk '{print $1}') --dport 22022 -j ACCEPT
# iptables -A POSTROUTING -t nat -o pnet5 -p tcp --dport 22 -j SNAT --to 10.0.5.1

# ####################################################################################
# LISTE DES INTERFACES
# ifconfig | grep encap | awk '{print $1}' | grep -vi "vunl\|vnet"

# ####################################################################################
#
# INFORMATIONS 
#
#iptables -A PREROUTING -t nat -i pnet0 -p tcp --dport 22022 -j DNAT --to 10.0.5.201:22
#iptables -A FORWARD -p tcp -d 172.16.194.239 --dport 22022 -j ACCEPT
#iptables -A POSTROUTING -t nat -o pnet5 -p tcp - dport 22 -j SNAT --to 10.0.5.1
#iptables -A POSTROUTING -t nat -o pnet5 -p tcp --dport 22 -j SNAT --to 172.16.194.239

#### REMOVE #### WITH ERROR MESSAGE ####
#root@eve-ng:~# iptables -D PREROUTING -t nat -i pnet0 -p tcp --dport 22022 -j DNAT --to 10.0.5.201:22
#root@eve-ng: ~# iptables -D PREROUTING -t nat -i pnet0 -p tcp --dport 22022 -j DNAT --to 10.0.5.201:22
#iptables: No chain/target/match by that name.

#root@eve-ng:~# iptables -D FORWARD -p tcp -d 172.16.194.239 --dport 22022 -j ACCEPT
#root@eve-ng: ~  # iptables -D FORWARD -p tcp -d 172.16.194.239 --dport 22022 -j ACCEPT
#iptables: Bad rule(does a matching rule exist in that chain?).

#root@eve-ng:~# iptables -D POSTROUTING -t nat -o pnet5 -p tcp --dport 22 -j SNAT --to 10.0.5.1
#root@eve-ng: ~  # iptables -D POSTROUTING -t nat -o pnet5 -p tcp --dport 22 -j SNAT --to 10.0.5.1
#iptables: No chain/target/match by that name.
