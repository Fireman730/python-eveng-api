--deploy = déployer votre réseau.

Récupère les IP des équipements dans le fichier YAML.
    => Obliger à donner les IP ?
    => Obliger à donner les IP si ``--ansible_deploy=``
        -> à Rajouter dans le YAML Validator
        

Si ``--ansible_deploy=``
    => Vérifier que les switches sont en oob ?
    Accepter d'écraser la configuration ?


Besoin :

Inventory files
Playbooks Ansible

```yaml
# Ansible will be installed on eve-ng
ansible:
  
  localhost: true
  inventory: ./ansible/inventory
  playbooks:
    - ./ansible/deploy_spine.yml
    - ./ansible/deploy_leaf.yml
    - ./ansible/deploy_exit.yml
    - ./ansible/deploy_oob_srv.yml
  
  cfg: ./ansible/ansible.cfg

```
