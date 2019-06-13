First describe your VM infos in ``./vm/vm_info.yml`` :
```yaml
# No default IP address
ip: 172.16.194.239
# Default admin
https_username: admin
# Default eve
https_password: eve
# Mandatory with no community version
https_port: 443
# Mandatory with no community version
https_ssl: true
# Default root
ssh_root: root
# Default eve
ssh_pass: eve
# Community Version
community: false
```
If your VM infos are in this file ``./vm/vm_info.yml`` it's not necessary to specify ``--vm=`` vaule.


Test connection with your EVE-NG VM (username, password, IP, port, etc.)
```shell
./eveng-api.py --vm=./vm/vm_info.yml --test=True
```

Get all availables images on your EVE-NG VM :
```shell
./eveng-api.py --vm=./vm/vm_info.yml --images=True
```

Get port names for a device type.
```shell
./eveng-api.py --vm=./vm/vm_info.yml --ports=True
```
This function can be interessting if you need to write your ``./architecture/lab.yml`` file.


Get telnet connection - mapped to Serial / Consol port - **ONLY IF YOUR DEVICE RUN !**.
```shell
./eveng-api.py --vm=./vm/vm_info.yml --telnet=True
```

If you deployed a lab with port forwarding from public EVE-NG ip address to your devices virtualized in EVE-NG.
You can get infortmation about how connect to devices.
https://gitlab.com/DylanHamel/python-eveng-api/wikis/Write-your-YAML-file-that-describes-your-netwrok-(part-4)
```shell
./eveng-api.py --vm=./vm/vm_info.yml --connexion=True
```

Deploy your lab in EVE-NG.
```shell
./eveng-api.py --vm=./vm/vm_info.yml --deploy=./architecture/4spines_12leaves.yml
```

If a lab with same name already exists on your EVE-NG VM you will not be able to deploy a seond lab.
You can force the deploiement. The lab in EVE-NG will be remove and your new lab deployed.
```shell
./eveng-api.py --vm=./vm/vm_info.yml --deploy=./architecture/4spines_12leaves.yml --force=True
```

Shutdown your lab.
```shell
./eveng-api.py --vm=./vm/vm_info.yml --stop=4spines_12leaves.unl

# If your lab is not in "Users" folder. Example lab is in "network/cisco/" folder
./eveng-api.py --vm=./vm/vm_info.yml --stop=4spines_12leaves.unl --folder=network
```


Start your lab.
```shell
./eveng-api.py --vm=./vm/vm_info.yml --start=4spines_12leaves.unl

# If your lab is not in "Users" folder. Example lab is in "network/cisco/" folder
./eveng-api.py --vm=./vm/vm_info.yml --start=4spines_12leaves.unl --folder=network
```

Remove your lab. Will automatcally stop all nodes.
You don't need stop first.
```shell
./eveng-api.py --vm=./vm/vm_info.yml --remove=4spines_12leaves.unl

# If your lab is not in "Users" folder. Example lab is in "network/cisco/" folder
./eveng-api.py --vm=./vm/vm_info.yml --remove=4spines_12leaves.unl --folder=network
```

If you modify device configuraitosn in your EVE-NG lab you can backup device new configurations.
Firstly you need to describe how do you want backup your lab in a YAML file ``./backup/dmvpn.yml``.
```yaml
- labname: dmvpn-ospf-qos.unl
    pod: 0
    folder: Network
    bck_path: /data/python-eveng-api/backup
    bck_type: verbose
    hostname: 
      - all
```

Backup device configurations :
```shell
./eveng-api.py --vm=./vm/vm_info.yml --backup=./backup/dmvpn.yml
```

