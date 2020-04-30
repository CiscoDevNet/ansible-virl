# ansible-virl

Ansible Modules for VIRL^2/CML^2

## Requirements


Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.


## Installation

### via ``pip``

```
  pip install ansible-virl
```

### via ``ansible-galaxy``

```
  ansible-galaxy install 'git@github.com:CiscoDevNet/ansible-virl.git'
```

## Environmental Variables

* `VIRL_USERNAME`: Username for the VIRL user (used when `host` not specified)
* `VIRL_PASSWORD`: Password for the VIRL user (used when `password` not specified)
* `VIRL_HOST`: The VIRL host (used when `host` not specified)
* `VIRL_LAB`: The name of the lab

## Inventory

To use the dynamic inventory plugin, the environmental variabiles must be set and a file (e.g. `virl.yml`) placed in the inventory specifying the plugin information:

```
plugin: virl
```

The dynamic inventory script will then return information about the nodes in the
lab:

```
ok: [hq-host1] => {
    "virl_facts": {
        "config": "#cloud-config\npassword: admin\nchpasswd: { expire: False }\nssh_pwauth: True\nhostname: hq-host1\nruncmd:\n - sudo ip address add 10.0.1.10/24 dev enp0s2\n - sudo ip link set dev enp0s2 up\n - sudo ip route add default via 10.0.1.1\n",
        "cpus": null,
        "data_volume": null,
        "image_definition": "ubuntu-18-04",
        "interfaces": [
            {
                "ipv4_addresses": [],
                "ipv6_addresses": [],
                "mac_address": "52:54:00:13:1b:fb",
                "name": "enp0s2",
                "state": "STARTED"
            }
        ],
        "node_definition": "ubuntu",
        "ram": null,
        "state": "BOOTED"
    }
}
```

## Example Playbooks

### Create a Lab
    - name: Create the lab
      virl_lab:
        host: "{{ virl_host }}"
        user: "{{ virl_username }}"
        password: "{{ virl_password }}"
        lab: "{{ virl_lab }}"
        state: present
        file: "{{ virl_lab_file }}"
      register: results

### Start a Node

    - name: Start Node
      virl_node:
        name: "{{ inventory_hostname }}"
        host: "{{ virl_host }}"
        user: "{{ virl_username }}"
        password: "{{ virl_password }}"
        lab: "{{ virl_lab }}"
        state: started
        image_definition: "{{ virl_image_definition | default(omit) }}"
        config: "{{ day0_config | default(omit) }}"

### Collect facts about the Lab
    - name: Collect Facts
      virl_lab_facts:
        host: "{{ virl_host }}"
        user: "{{ virl_username }}"
        password: "{{ virl_password }}"
        lab: "{{ virl_lab }}"
      register: result

## License

GPLv3
