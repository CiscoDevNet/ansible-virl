from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import re
import requests

# from ansible.errors import AnsibleError, AnsibleParserError
# from ansible.module_utils.six import string_types
from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils._text import to_native, to_text

DOCUMENTATION = r'''
    name: virl
    plugin_type: inventory
    short_description: Returns Inventory from VIRL server
    description:
        - Retrieves inventory from VIRL server
    options:
        plugin:  
            description: Name of the plugin
            required: true
            choices: ['virl']
        host: 
            description: FQDN of the target host 
            required: false
        username: 
            description: user credential for target system 
            required: false
        password: 
            description: user pass for the target system
            required: false
        simulation:
            description: The name of the VIRL simulation
            required: false
        validate_certs: 
            description: certificate validation
            required: false
            choices: ['yes', 'no']
'''

VIRLRC_FILES = [
    '.virlrc',
    '~/.virlrc'
]

class InventoryModule(BaseInventoryPlugin):

    NAME = 'virl'
    def __init__(self):
        super(InventoryModule, self).__init__()

        # from config 
        self.virl_username = None
        self.virl_password = None
        self.virl_host = None
        self.virl_simulation = None

    def _read_virlrc(self):
        result = {}
        for config_file in VIRLRC_FILES:
            if config_file[0] == '~':
                config_file = os.path.expanduser(config_file)
            if os.path.exists(config_file):
                envre = re.compile(r'''^([^\s=]+)=(?:[\s"']*)(.+?)(?:[\s"']*)$''')
                with open(config_file) as ins:
                    for line in ins:
                        match = envre.match(line)
                        if line.startswith('#'):
                            continue
                        if match is not None:
                            result[match.group(1)] = match.group(2)
                break

        if 'VIRL_HOST' in os.environ and len(os.environ['VIRL_HOST']):
            self.virl_host = os.environ['VIRL_HOST']
        elif self.get_option('host'):
            self.virl_host = self.get_option('host')
        elif 'VIRL_HOST' in result:
            self.virl_host = result['VIRL_HOST']
        else:
            raise AnsibleParserError("VIRL hostname not specified")

        self.display.vvv("virl.py - VIRL_HOST: {0}".format(self.virl_host))

        if 'VIRL_USERNAME' in os.environ and len(os.environ['VIRL_USERNAME']):
            self.virl_username = os.environ['VIRL_USERNAME']
        elif self.get_option('username'):
            self.virl_username = self.get_option('username')             
        elif 'VIRL_USERNAME' in result:
            self.virl_username = result['VIRL_USERNAME']
        else:
            raise AnsibleParserError("VIRL username not specified")

        self.display.vvv("virl.py - VIRL_UERNAME: {0}".format(self.virl_username))

        if 'VIRL_PASSWORD' in os.environ and len(os.environ['VIRL_PASSWORD']):
            self.virl_password = os.environ['VIRL_PASSWORD']
        elif self.get_option('password'):
            self.virl_password = self.get_option('password')                       
        elif 'VIRL_PASSWORD' in result:
            self.virl_password = result['VIRL_PASSWORD']
        else:
            raise AnsibleParserError("VIRL password not specified")

    def _get_simulation(self):

        # vm = play.get_variable_manager()
        # extra_vars = vm.extra_vars
        # if extra_vars['simulation'] is defined:
        #     self.simulation = extra_vars['simulation']

        if 'VIRL_SIMULATION' in os.environ and len(os.environ['VIRL_SIMULATION']):
            self.simulation = os.environ['VIRL_SIMULATION']
        elif self.get_option('simulation'):
            self.virl_simlulation = self.get_option('simulation')                  
        if 'VIRL_SESSION' in os.environ:
            self.simulation = os.environ['VIRL_SESSION']            
        elif os.path.exists('.virl/default/id'):
            with open('.virl/default/id') as file:
                self.simulation = file.read()
        else:
            raise AnsibleParserError("VIRL simulation not specified")

        self.display.vvv("virl.py - VIRL_SIMULATION: {0}".format(self.simulation))

    def verify_file(self, path):

        if super(InventoryModule, self).verify_file(path):
            endings = ('virl.yaml', 'virl.yml')
            if any((path.endswith(ending) for ending in endings)):
                return True
        display.debug("virl inventory filename must end with 'virl.yml' or 'virl.yaml'")
        return False

    def parse(self, inventory, loader, path, cache=True):

        # call base method to ensure properties are available for use with other helper methods
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # this method will parse 'common format' inventory sources and
        # update any options declared in DOCUMENTATION as needed
        # config = self._read_config_data(self, path)
        self._read_config_data(path)

        # if NOT using _read_config_data you should call set_options directly,
        # to process any defined configuration for this plugin,
        # if you dont define any options you can skip
        # self.set_options()

        # self._read_virlrc()
        # self._get_simulation()

        if 'VIRL_HOST' in os.environ and len(os.environ['VIRL_HOST']):
            self.virl_host = os.environ['VIRL_HOST']
        else:
            self.virl_host = self.get_option('host')

        self.display.vvv("virl.py - VIRL_HOST: {0}".format(self.virl_host))

        if 'VIRL_USERNAME' in os.environ and len(os.environ['VIRL_USERNAME']):
            self.virl_username = os.environ['VIRL_USERNAME']
        else:
            self.virl_username = self.get_option('username')

        self.display.vvv("virl.py - VIRL_USERNAME: {0}".format(self.virl_username))

        if 'VIRL_PASSWORD' in os.environ and len(os.environ['VIRL_PASSWORD']):
            self.virl_password = os.environ['VIRL_PASSWORD']
        else:
            self.virl_password = self.get_option('password')


        if 'VIRL_LAB' in os.environ and len(os.environ['VIRL_LAB']):
            self.virl_lab = os.environ['VIRL_LAB']
        else:
            self.virl_lab = self.get_option('lab')

        self.display.vvv("virl.py - VIRL_LAB: {0}".format(self.virl_lab))

        self.inventory.set_variable('all', 'virl_host', self.virl_host)
        self.inventory.set_variable('all', 'virl_username', self.virl_username)
        self.inventory.set_variable('all', 'virl_password', self.virl_password)
        self.inventory.set_variable('all', 'virl_session', self.simulation)
        self.inventory.set_variable('all', 'virl_simulation', self.simulation)

        url = "http://%s:19399/simengine/rest/interfaces/%s" % (self.virl_host, self.simulation)

        # perform REST operation
        simulations = requests.get(url, auth=(self.virl_username, self.virl_password))
        if simulations.status_code == 200:

            interfaces = simulations.json()[self.simulation]
            try:
                group = self.inventory.add_group('virl_hosts')
            except AnsibleError as e:
                raise AnsibleParserError("Unable to add group %s: %s" % (group, to_text(e)))

            for key, value in interfaces.items():
                self.inventory.add_host(key, group='virl_hosts')
                self.inventory.set_variable(key, 'ansible_host', value['management']['ip-address'].split('/')[0])