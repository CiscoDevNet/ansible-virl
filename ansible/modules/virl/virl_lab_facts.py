#!/usr/bin/env python

from ansible.module_utils.basic import AnsibleModule
# pylint: disable=no-name-in-module,import-error
from ansible.module_utils.virl import virlModule, virl_argument_spec

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = virl_argument_spec()
    argument_spec.update(lab=dict(type='str', required=True), )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    virl = virlModule(module)
    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    virl.result = dict(changed=False, original_message='', message='')

    virl_facts = {}
    labs = virl.client.find_labs_by_title(virl.params['lab'])
    if len(labs):
        # Just take the first lab until we figure out how we want
        # to handle duplicates
        lab = labs[0]
        lab.sync()
        virl_facts['details'] = lab.details()
        virl_facts['nodes'] = {}
        for node in lab.nodes():
            virl_facts['nodes'][node.label] = {
                'state': node.state,
                'image_definition': node.image_definition,
                'node_definition': node.node_definition,
                'cpus': node.cpus,
                'ram': node.ram,
                'config': node.config,
                'data_volume': node.data_volume,
                'tags': node.tags(),
                'interfaces': {}
            }
            ansible_host = None
            for interface in node.interfaces():
                if interface.discovered_ipv4 and not ansible_host:
                    ansible_host = interface.discovered_ipv4[0]
                virl_facts['nodes'][node.label]['interfaces'][interface.label] = {
                    'state': interface.state,
                    'ipv4_addresses': interface.discovered_ipv4,
                    'ipv6_addresses': interface.discovered_ipv6,
                    'mac_address': interface.discovered_mac_address
                }
            virl_facts['nodes'][node.label]['ansible_host'] = ansible_host
    virl.result['virl_facts'] = virl_facts
    virl.exit_json(**virl.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
