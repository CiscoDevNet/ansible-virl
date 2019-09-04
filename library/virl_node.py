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
                        lab=dict(type='str', alise='lab_name', required=True),
                        lab_id=dict(type='str'),
                        node_id=dict(type='str'),
                        node_definition=dict(type='str'),
                        image_definition=dict(type='str'),
                        config=dict(type='str'),
                        tags=dict(type='list'),
                        x=dict(type='int'),
                        y=dict(type='int'),
                        wait=dict(type='bool', default=False),
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


    labs = virl.client.find_labs_by_title(virl.params['lab'])
    if len(labs) > 0:
        lab = labs[0]
    else:
        virl.fail_json(f"Cannot find lab {virl.params['lab']}")

    node = virl.get_node_by_name(lab, virl.params['name'])
    if virl.params['state'] == 'present':
        if node == None:
            node = lab.create_node(label=virl.params['name'], node_definition=virl.params['node_definition'])
            virl.result['changed'] = True
    elif virl.params['state'] == 'started':
        if node == None:
            virl.fail_json("Node must be created before it is started")
        if node.state not in ['STARTED','BOOTED']:
            if node.state == 'DEFINED_ON_CORE' and virl.params['config']:
                node.config = virl.params['config']
            node.start(wait=virl.params['wait'])            
            virl.result['changed'] = True
    elif virl.params['state'] == 'stopped':
        if node == None:
            virl.fail_json("Node must be created before it is stopped")
        if node.state not in ['STOPPED','DEFINED_ON_CORE']:
            node.stop(wait=virl.params['wait'])            
            virl.result['changed'] = True                
    elif virl.params['state'] == 'wiped':
        if node == None:
            virl.fail_json("Node must be created before it is wiped")
        if node.state not in ['DEFINED_ON_CORE']:
            node.wipe(wait=virl.params['wait'])            
            virl.result['changed'] = True        
    virl.exit_json(**virl.result)

def main():
    run_module()

if __name__ == '__main__':
    main()