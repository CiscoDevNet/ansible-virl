#!/usr/bin/env python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

import requests
from ansible.module_utils.basic import AnsibleModule, json
from ansible.module_utils.virl import virlModule, virl_argument_spec


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = virl_argument_spec()
    argument_spec.update(state=dict(type='str', choices=['absent', 'present'], default='present'),
                        name=dict(type='str', required=True),
                        lab_name=dict(type='str'),
                        lab_id=dict(type='str'),
                        node_id=dict(type='str'),
                        node_definition=dict(type='str'),
                        image_definition=dict(type='str'),
                        config=dict(type='str'),
                        tags=dict(type='list'),
                        x=dict(type='int'),
                        y=dict(type='int'),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(argument_spec=argument_spec,
                           supports_check_mode=True,
                           )
    virl = virlModule(module)

    if virl.params['lab_id']:
        lab = virl.get_lab_by_id(virl.params['lab_id'])
    else:
        lab = virl.get_lab_by_name(virl.params['lab_name'])

    if lab == None:
        virl.fail_json("Cannot find specified lab.")

    if virl.params['state'] == 'present':
        node = virl.get_node_by_name(lab, virl.params['name'])
        if node == None:
            node = lab.create_node(label=virl.params['name'], node_definition=virl.params['node_definition'])
            virl.result['changed'] = True

        virl.result['lab_id'] = lab.id
        virl.result['lab_name'] = lab.name
            

    virl.exit_json(**virl.result)

def main():
    run_module()

if __name__ == '__main__':
    main()