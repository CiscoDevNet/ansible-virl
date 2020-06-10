from ansible.module_utils.basic import env_fallback
# pylint: disable=wrong-import-order
from virl2_client import ClientLibrary


def virl_argument_spec():
    return dict(host=dict(type='str', required=True, fallback=(env_fallback, ['VIRL_HOST'])),
                user=dict(type='str', required=True, fallback=(env_fallback, ['VIRL_USERNAME'])),
                password=dict(type='str', required=True, fallback=(env_fallback, ['VIRL_PASSWORD'])),
                validate_certs=dict(type='bool', required=False, default=False),
                timeout=dict(type='int', default=30))


class virlModule(object):
    def __init__(self, module, function=None):
        self.module = module
        self.params = module.params
        self.result = dict(changed=False)
        self.headers = dict()
        self.function = function
        self.cookies = None
        self.json = None

        self.method = None
        self.path = None
        self.response = None
        self.status = None
        self.url = None
        self.params['force_basic_auth'] = True
        self.user = self.params['user']
        self.password = self.params['password']
        self.host = self.params['host']
        self.timeout = self.params['timeout']
        self.modifiable_methods = ['POST', 'PUT', 'DELETE']

        self.client = None

        self.login()

    def login(self):
        self.client = ClientLibrary('https://{0}'.format(self.host), self.user, self.password, ssl_verify=False)

    def get_lab_by_name(self, name):
        for lab in self.client.all_labs():
            if lab.name == name:
                return lab
        return None

    def get_node_by_name(self, lab, name):
        for node in lab.nodes():
            if node.label == name:
                return node
        return None

    def get_lab_by_id(self, lab_id):
        try:
            lab = self.client.join_existing_lab(lab_id, sync_lab=True)
        except Exception:
            lab = None

        return lab

    def exit_json(self, **kwargs):

        self.result.update(**kwargs)
        self.module.exit_json(**self.result)

    def fail_json(self, msg, **kwargs):

        self.result.update(**kwargs)
        self.module.fail_json(msg=msg, **self.result)
