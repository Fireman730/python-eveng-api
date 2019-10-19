#!/bin/bash
nc -w 5 $(grep -ri "ip: " vm_info.yml | awk '{print $2}' | cut -d '/' -f 1) $(grep -ri "https_port: " vm_info.yml | awk '{print $2}')

if [ $? -eq 0 ]
then
  exit 0
else
  exit 1
fi
