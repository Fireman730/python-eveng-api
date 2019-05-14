# Plateforme de déploiement de réseaux

###### Dylan Hamel - Mai 2019

## Actuellement

EVE-NG est un outil basé sur Debian qui permet de virtualisé des équipements réseaux. EVE-NG utilise des outils tels que QEMU ou Dynamips.

Afin d'utiliser un équipement réseau, il suffit d'ajouter le QCOW2 ou l'ISO de ce dernier dans EVE-NG et de lancer quelques commandes

#### Installation de l'OS Cumulus Linux

Télécharger l'image de Cumulus directement sur leur site WEB officiel.

* https://cumulusnetworks.com/products/cumulus-vx/download/

Copier via SCP le fichier sur la machine EVE-NG. Il est possible d'exécuter directement un ``wget`` sur la machine EVE-NG

```shell
scp ./cumulus-linux-3.7.5-vx-amd64-qemu.qcow2 root@172.16.194.239:/tmp
```

Se connecter sur la VM en SSH

```shell
ssh -l root 172.16.194.239
```

Créer un répertoire pour Cumulus avec le numéro de version

```shell
mkdir /opt/unetlab/addons/qemu/cumulus-vx-3.7.5
```

Déplacer et renommer le fichier QCOW2

```shell
mv /tmp/cumulus-linux-3.7.5-vx-amd64-qemu.qcow2 /opt/unetlab/addons/qemu/cumulus-vx-3.7.5/virtioa.qcow2
```

Fixer les permissions

```shell
/opt/unetlab/wrappers/unl_wrapper -a fixpermissions
```



#### Présentation du script

Ce script a été pensé afin de réaliser l'étape de "Build" et "Test" d'une Pipeline CI/CD pour le réseau. La tendance actuellement penche fortement vers le "As Code". Le réseau n'échappe pas à cette règle.
Les modifications ainsi que le déploiement des réseaux doit être automatisé au maximum. Afin de pouvoir automatiser complètement le réseau il faut passer par une étape de test dans un environnement virtuel. Cette étape doit permettre de valider que cette modification, poussée en production, n'aura pas d'effets colatéraux.

Ce script permet donc de déployer automatiquement un réseau dans l'environnement EVE-NG. Il permet également de se connecter directement aux équipements et donc de leur appliquer des modifications.

L'idée est de décrire son propre réseau dans un fichier YAML. 

Le script permet également de copier une configuration directement sur les équipements. Afin de réaliser cela, il suffit de donner le chemin vers les fichiers de configuration pour chaque équipement.

Actuellement, deux types de déploiement sont mis à disposition.

1. Utile pour tester le déploiement complet de la configuration "D1" —>> ``oob``

   L'idée est d'utiliser un outil tel qu'Ansible, générer les template et de les déployer directement sur les équipements. Afin de réaliser cela, il suffit que les équipements soient joignables en SSH. Ce mode va donc pousser uniquement les fichiers nécessaires à configurer l'IP de management

   * Sur Cumulus Network qui est un debian, uniquement le fichier ``interface`` sera copié sur l'équipement.
   * Sur Cisco, qui contient uniquement un fichier de config "show run", il n'y a pas deux modes. Chaque équipement possède donc de sa propre implémentation

2. Utile pour tester les modifications des équipements "D2" —>> ``full``

   L'idée est d'écrire des scripts Ansible, Python, SaltStack modifiant la configuration du réseau. Afin de réaliser cela, il faut que le script déploie la configuration complète. Il suffit donc de donner le path jusqu'au dossier contenant les fichiers de configuration.

   Plusieurs modes de stockage des fichiers de configurations sont possibles et sont à réfléchir pour le futur.

   * Sur Cumulus, les fichiers suivants seront remplacés :
     Les fichiers poussés sont évidement à discuter et adaptable en modifiant un simple fichier YAML !

     ```
     /etc/hostname
     /etc/resolv.conf
     /etc/ntp.conf
     /etc/motd
     /etc/passwd
     /etc/hosts
     /etc/network/interfaces
     /etc/frr/frr.conf
     /etc/frr/daemons.conf
     /etc/frr/daemons
     /etc/snmp/snmpd.conf
     /etc/cumulus/switchd.conf
     /etc/cumulus/ports.conf
     /etc/cumulus/datapath/traffic.conf
     /etc/cumulus/etc.replace/os-release
     /etc/cumulus/etc.replace/lsb-release
     /etc/cumulus/acl/policy.d/00control_plane.rules
     /etc/cumulus/acl/policy.d/99control_plane_catch_all.rules
     ```

   * Sur Cisco c'est également le fichier de configuration qui sera poussé. Des équipements tels que Cisco ne possède donc pas les deux modes.



Exemple :

* Définition du Laboratoire

```yaml
project:
  path: /Users/
  name: spine-leaf
  version: 1
  author: DylanHamel
  description: Spine and Leaf architecture for test befor prod
  body: Actual label
```

* Définition d'un équipement

```Yaml
devices:
  - type: qemu
    template: cumulus
    config: Unconfigured
    delay: 0
    icon: router.png
    image: cumulus-vx-3.7.5
    name: Spine01
    left: 45%
    top: 20%
    ram: 1024
    console: telnet
    cpu: 1
    ethernet: 8
    uuid: 641a4800-1b19-427c-ae87-5555590b7790
```

* Définition des liens entre les équipements

```Yaml
links:
  - id: 1
    type: ethernet
    network: bridge
    src: Spine01
    sport: swp1
    dst: Leaf01
    dport: swp1
```

* Définition des configurations

```yaml
configs:
  - node: Spine01
    type: full
    config: /Volumes/Data/gitlab/python-eveng-api/backup/cumulus-spine-leaf.unl/Spine01
```



> Un exemple complet de déploiement d'un réseau de data center "spine and leaf" est joint à ce document.



#### Connexion aux équipements

Acutellement, cet outil s'utilise sur principalement sur la machine locale.
Ce script s'exécute directement sur la machine EVE-NG (Debian) ou sur une machine virtualisée sur des outils tels que VirtualBox ou VMWare Fusion.

Afin de se connecter sur les équipements, un réseau de management est déployer dans l'environnement virtuel. Ce réseau est "mappé" sur une interface de la machine EVE-NG. Grâce à cela, il est possible d'accéder directement aux équipements virtualisés depuis la machine hôte.

Afin de mapper cela, il suffit de connaître la carte de la machine virtuelle mappée avec la machine locale et d'ajouter un lien ``OOB-NETWORK`` dans le fichier YAML :

```YAML
  - id: 9
    network: pnet4
    src:
      - host: Spine01
        port: eth0
      - host: Spine02
        port: eth0
      - host: Leaf01
        port: eth0
      - host: Leaf02
        port: eth0
      - host: Leaf03
        port: eth0
      - host: Leaf04
        port: eth0
    dst: OOB-NETWORK
    dport: oob
```



#### Déployer le réseau

Afin de déployer un réseau, il suffit donc de lancer une commande en passant en paramètre le fichier YAML décrivant le réseau ainsi qu'un fichier YAML contenant les credentials de la machine EVE-NG :

```shell
./eveng-api.py --vm=./vm/vm_info.yml --deploy=./architecture/2spines_4leafs.yml
```



Exemple du fichier YAML contenant les credentials de la machine EVE-NG :

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





## Évolution afin de devenir un SaaS

Le but final de ce projet est de rendre ce projet comme un service WEB. Les utilisateurs finaux créront un compte sur la plateforme. Grâce à ce compte, il sera possible d'utiliser une plateforme EVE-NG.



## Management des images

Afin d'offrir un maximum d'équipements aux clients, il sera nécessaire de manager les images pour les clients. Mise à disposition de tous les équipements importants

| Extreme Network (VSP) | Extreme Network | Cumulus Network |
| --------------------- | --------------- | --------------- |
| Arista                | Checkpoint      | VyOS            |
| JunOS                 | Fortinet        | Cisco Routers   |
| Cisco Nexus 9k        | Pfsense         | Cisco Switches  |
| Cisco Nexus 7k        | Cisco ASA       | Juniper vMX     |
| Cisco CSR 1000v       | Sophos          | Juniper vSRX    |
| F5 Big-IP             | Palo Alto       | Mikrotik        |

Mettre à disposition également :

* Containers Docker
* Générateur de trafic aléatoire



## Développement d'un container EVE-NG

Afin de rendre ce projet le plus fonctionnel possible, il faudrait disposé de container Docker EVE-NG. Le but est de pouvoir déployer dynamiquement des nouveaux laboratoire dans des environnements isolés.

Le tout serait managé grâce à Kubernetes.

Il faudrait en plus de ça générer des port-forwarding dynamique - à voir si cela est réalisable en utilisant Kubernetes sur google ou AWS.

Si non, l'utilisation d'instance sera privilégiée.

L'utilisation d'un EVE-NG publique sur lesquels plusieurs clients travaillent est également un option.

Pour répondre à ces questions, il faut commencer à tester les différentes fonctionnalités d'AWS, Google Cloud et Azure.

1. Container Docker on demand
2. Instance EVE-NG déployé automatiquement avec IP publique dédié par client
3. Instance EVE-NG partagée pour certains clients à prix plus attractifs.



## Développement d'une solution "on-premise"

Certains entreprises, pourrait refuser catégoriquement de déployer un réseau sur un Cloud. En effet, trop d'informations confidentielles seraient "sorties" de l'entreprise.

Cette plateforme SaaS deviendrait totalement inutile pour eux.

Afin de palier à ce problème de sécurité, il faudrait également offrir au client une solution leur permettant de déployer ce service directement sur un hyperviseur chez eux. Ou alors, si possible, mettre à disposition un container Docker. Le but est d'offrir également une solution interne chez les clients.



## Développement d'API CLI et REST

L'utilisateur final pourra automtiser complètement le déploiement de son infrastructure directement dans le cloud avec une simple requête REST ou une commande CLI.

#### CLI

L'utilisateur final pourra télécharger un SDK  lui mettant à disposition des commandes permettant d'interagir avec la plateforme en ligne de commande directement depuis un shell bash.

```shell
» dhdeploy --login dylan.hamel@protonmail.com
Enter Your Password: 

Login Succeeded
```

Le principe du fichier YAML resterait le même.
L'utilisateur définit son architecture dans un fichier YAML en local sur son ordinateur et lance ce script en passant en paramètre le path jusqu'à son fichier.

La platforme retournerait  à l'utilisateur un JSON contenant toutes les informations permettant de se connecter aux différents équipements définient dans le YAML.

```shell
# Après s'être connnecté
» dhdeploy --deploy=/path/to/my/yamlfile.yml
{
   "leaf01": {
      "ip_addr": "10.10.10.201",
      "protocol": "ssh",
      "port": 33322
   },
   "leaf02": {
      "ip_addr": "10.10.10.202",
      "protocol": "ssh",
      "port": 33323
   },
   "leaf03": {
      "ip_addr": "10.10.10.203",
      "protocol": "ssh",
      "port": 33324
   },
   "leaf04": {
      "ip_addr": "10.10.10.204",
      "protocol": "ssh",
      "port": 33325
   },
   "spine01": {
      "ip_addr": "10.10.10.101",
      "protocol": "ssh",
      "port": 33326
   }
}
```

#### REST

Le principe serait le même à l'exception que ce dernier se ferait via des requêtes HTTP.

Effectuer un ``POST`` pour déployer le réseau qui retourne un JSON contenant toutes les informations de connexions.



## Accès aux équipements

Si la machine est hébergé dans un container dans Google Cloud par exemple, il faudra trouver un moyen de définir un moyen de se connecter automatiquement aux équipements. 

Une possibilité est d'avoir un script générant des port-forwarding dynamiquement sur l'IP publique redirigé automatiquement vers les équipements réseaux.

Une des solutions est l'établissement d'un tunnel au travers duquel les ports seront redirigés.

Ce point est à réfléchir.



## Récupérer les configurations directement sur GIT

Afin d'optimiser l'utilisation une fonctionnalité serait de pouvoir spécifier un compte git (Gitlab, Github, Bitbucket, etc.). Le but est de pouvoir aller directement récupérer les backups dans le git.

Dans le fichier YAML, le block ``configs`` serait à modifier et deviendrait : 

```yaml
configs:
  - node: all_device
    type: full
    path: https://gitlab.com/DylanHamel/my-network-backups
    token: JDBD3H2OIH21I3UELI234B4BRL234BLR23B443
```

L'alogorithme de récupération des fichiers de configuration serait à définir afin d'être complètement d'automatiser.



## Analyse de la concurrence

Après plusieurs recherches aucun service de type SaaS offre actuellement cette possibilité. Ce produit serait donc unique.

Certains entreprises telles que https://cloudmylab.com/eve-ng/ met à disposition un environnement EVE-NG mais n'offre pas la possibilité d'automatiser le déploiement de réseaux.



## Clients potentiels

Tous les clients possédant un réseau et voulant le déployer dans un environnement de test afin d'appliquer les modifications en production.

Des clients voulant posséder son propre pipeline CI/CD pour son réseau pourra utiliser cette plateforme pour tester les modifications dans un environnement virtuel avant de les pousser en production.

D'autres clients pourraient utiliser ce dernier en utilisant simplement le laboratoire de manière simple non automatiser.



## Créer une communauté

Afin de rassembler les gens sur la plateforme, le but est de mettre à disposition des scripts Ansible, SaltStack, Nornir permettant de tester automatiquement un réseau.

Le but est donc de créer également un centre de partage sur le thème du Network As Code ainsi que le Pipeline CI/CD spécialisé dans le réseau.



## Facturation et prix

La facturation pourrait se faire de plusieurs manières :

1. Comme AWS, Azure ou Google, le prix serait calculer en fonction du nombre de mémoire consommer par les équipements ainsi que le temps que ces derniers tournes.

   Cette solution est la meilleure mais pénalise certains équipements.

   * Cisco Nexus 9k tourner avec 8GB de RAM alors que Cumulus Network tourne avec 256MB

   

2. La deuxième solution serait de facturer au build et de donner un temps définit pendant lequel le laboratoire est disponible.

   Cette méthode comporte 2 points faibles :

   1. Les petits environnement ne seront jamais déployer. Il ne sera pas intéressant d'utiliser ce produit pour déployer un réseau de 3 équipements.
   2. Le deuxième désavantage et que la plateforme perdrait le côté laboratoire de tests de modifications directement en CLI. En effet, si le laboratoire est disponible que quelque temps.



3. La dernière solution serait de facture un prix fixe pour le "build" et de facturer la machine "à la pièce" en fonction de ses ressources.



## Problèmes

Il faudra gérer le client qui tente de déployer un réseau contenant un grand nombre d'équipement conssomant beaucoup de mémoire :

- Comment gérer le client qui tente de déployer 80 Cisco Nexus 9k … ?



-> Limitation des ressources maximales - Réduit la puissance et l'utilité de la plateforme.

* Les performances tels que le débit ne sont pas des paramètres fondamentaux - Overbooking OK.