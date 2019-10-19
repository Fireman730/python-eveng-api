"""
This file contains constants for python-eveng-api project

"""

__author__ = "Dylan Hamel"
__maintainer__ = "Dylan Hamel"
__version__ = "1.0"
__email__ = "dylan.hamel@protonmail.com"
__status__ = "Production"
__copyright__ = "Copyright 2019"
__license__ = "MIT"

# ###########################################################################
#
# General
#
# ###########################################################################

EVENG_LAB_EXTENSION = '.unl'

# ###########################################################################
#
# BACKUP YAML FILE
#
# ###########################################################################

#### BACKUP YAML file keys ####
BACKUP_LABNAME_KEY = 'labname'
BACKUP_POD_KEY = 'pod'
BACKUP_PATH_KEY = 'bck_path'
BACKUP_TYPE_KEY = 'bck_type'
BACKUP_HOSTNAME_KEY = 'hostname'
BACKUP_VERBOSE_KEYWORD = 'verbose'
BACKUP_SIMPLE_KEYWORD = 'simple'

# ###########################################################################
#
# DEPLOY YAML FILE
#
# ###########################################################################
#### YAML file keys ####
YAML_PROJECT_KEY = 'project'
YAML_DEVICES_KEY = 'devices'
YAML_LINKS_KEY = 'links'
YAML_CONFIGS_KEY = 'configs'
YAML_ANSIBLE_KEY = 'ansible'

#### Project keys ####
PROJECT_NAME_KEY = 'name'
PROJECT_PATH_KEY = 'path'
PROJECT_VERSION_KEY = 'version'
PROJECT_AUTHOR_KEY = 'author'
PROJECT_DESCRIPTION_KEY = 'description'
PROJECT_BODY_KEY = 'body'

#### Devices keys ####
DEVICES_TYPE_VIRT_KEY = 'type'
DEVICES_TEMPLATE_KEY = 'tempalte'
DEVICES_CONFIG_KEY = 'config'
DEVICES_DELAY_KEY = 'delay'
DEVICES_ICON_KEY = 'icon'
DEVICES_IMAGE_KEY = 'image'
DEVICES_NAME_KEY = 'name'
DEVICES_LEFT_POSIT_KEY = 'left'
DEVICES_TOP_POSIT_KEY = 'top'
DEVICES_RAM_KEY = 'ram'
DEVICES_CONSOLE_KEY = 'console'
DEVICES_CPU_KEY = 'cpu'
DEVICES_ETHERNET_KEY = 'ethernet'
DEVICES_UUID_KEY = 'uuid'

#### Links keys ####
LINKS_DST_KEY = 'dst'
LINKS_SRC_KEY = 'src'
LINKS_NETWORK_KEY = 'network'
LINKS_TYPE_KEY = 'type'
LINKS_ID_KEY = 'id'
LINKS_DEST_PORT_KEY = 'dport'
LINKS_SRC_PORT_KEY = 'sport'
LINKS_IP_EVE_KEY = 'ip_eve'
LINKS_IP_PUB_KEY = 'ip_pub'

#### OOB keys ####
OOB_NAT_KEY = 'nat'
OOB_HOST_KEY = 'host'
OOB_IP_MGMT_KEY = 'ip_mgmt'
OOB_SSH_KEY = 'ssh'
OOB_PORT_KEY = 'port'

#### CONFIGS keys ####
CONFIG_NODE_KEY = 'node'
CONFIG_CONFIG_KEY = 'config'
CONFIG_TYPE_KEY = 'type'

#### ANSIBLE keys ####
ANSIBLE_GROUPS_KEY = 'groups'
