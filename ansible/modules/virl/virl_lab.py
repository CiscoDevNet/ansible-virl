#!/usr/bin/env python

from ansible.module_utils.basic import AnsibleModule, env_fallback
# pylint: disable=no-name-in-module,import-error
from ansible.module_utils.virl import virlModule, virl_argument_spec

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}


def run_module():
    # define available arguments/parameters a user can pass to the module
    argument_spec = virl_argument_spec()
    argument_spec.update(
        state=dict(type='str', choices=['absent', 'present', 'started', 'stopped', 'wiped'], default='present'),
        lab=dict(type='str', required=True, fallback=(env_fallback, ['VIRL_LAB'])),
        file=dict(type='str'),
    )

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

    labs = virl.client.find_labs_by_title(virl.params['lab'])
    if len(labs) > 0:
        lab = labs[0]
    else:
        lab = None

    if virl.params['state'] == 'present':
        if lab is None:
            if virl.params['file']:
                lab = virl.client.import_lab_from_path(virl.params['file'], title=virl.params['lab'])
            else:
                lab = virl.client.create_lab(title=virl.params['lab'])
            lab.title = virl.params['lab']
            virl.result['changed'] = True

    elif virl.params['state'] == 'absent':
        if lab:
            virl.result['changed'] = True
            if lab.state == "STARTED":
                lab.stop(wait=True)
                lab.wipe(wait=True)
            elif lab.state == "STOPPED":
                lab.wipe(wait=True)
            lab.remove()
    elif virl.params['state'] == 'stopped':
        if lab:
            virl.result['changed'] = True
            lab.stop(wait=True)
    elif virl.params['state'] == 'wiped':
        if lab:
            virl.result['changed'] = True
            lab.wipe(wait=True)

    virl.exit_json(**virl.result)


def main():
    run_module()


if __name__ == '__main__':
    main()
