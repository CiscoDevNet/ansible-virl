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
    argument_spec.update(state=dict(type='str', choices=['absent', 'present', 'started', 'stopped', 'wiped'], default='present'),
                         name=dict(type='str', required=True),
                         lab=dict(type='str'),
                         file=dict(type='str'),
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
    labs = virl.client.find_labs_by_title(virl.params['name'])
    if len(labs) > 0:
        lab = labs[0]
    else:
        lan = None

    if virl.params['state'] == 'present':
        if len(labs) == 0:
            lab = virl.client.create_lab(virl.params['name'])
            virl.result['changed'] = True
            if virl.params['file']:
                virl.client.import_lab_from_path(virl.params['file'], virl.params['name'])
    elif virl.params['state'] == 'absent':
        if lab:
            virl.result['changed'] = True
            lab.remove()
    elif virl.params['state'] == 'stopped':
        if lab:
            virl.result['changed'] = True
            lab.stop()
    elif virl.params['state'] == 'wiped':
        if lab:
            virl.result['changed'] = True
            lab.wipe()

    virl.exit_json(**virl.result)

def main():
    run_module()

if __name__ == '__main__':
    main()