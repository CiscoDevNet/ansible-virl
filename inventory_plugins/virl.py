from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import re
import requests

# from ansible.errors import AnsibleError, AnsibleParserError
# from ansible.module_utils.six import string_types
from ansible.plugins.inventory import BaseInventoryPlugin


VIRLRC_FILES = [
    '.virlrc',
    '~/.virlrc'
]

class InventoryModule(BaseInventoryPlugin):

    NAME = 'virl'

    def _read_virlrc(self):

        for config_file in VIRLRC_FILES:
            if config_file[0] == '~':
                config_file = os.path.expanduser(config_file)
            if os.path.exists(config_file):
                break
        else:
            sys.stdout.write('unable to locate .virlrc\n')
            sys.exit(-1)

        envre = re.compile(r'''^([^\s=]+)=(?:[\s"']*)(.+?)(?:[\s"']*)$''')
        result = {}
        with open(config_file) as ins:
            for line in ins:
                match = envre.match(line)
                if line.startswith('#'):
                    continue
                if match is not None:
                    result[match.group(1)] = match.group(2)

        # print(result)

        # host = os.environ['VIRL_HOST'] or result['VIRL_HOST']
        # username = os.environ['VIRL_USERNAME'] or result['VIRL_USERNAME']
        # password = os.environ['VIRL_PASSWORD'] or result['VIRL_PASSWORD']

        self.virl_host = result['VIRL_HOST']
        self.virl_username = result['VIRL_USERNAME']
        self.virl_password = result['VIRL_PASSWORD']

    def _get_simulation(self):

        vm = play.get_variable_manager()
        extra_vars = vm.extra_vars

        if extra_vars['simulation'] is defined:
            self.simulation = extra_vars['simulation']
        else:
            if os.path.exists('.virl/default/id'):
                with open('.virl/default/id') as file:
                    self.simulation = file.read()

    def verify_file(self, path):

        # if super(InventoryModule, self).verify_file(path):
        #     endings = ('virl.yaml', 'virl.yml')
        #     if any((path.endswith(ending) for ending in endings)):
        #         return True
        # return False
        return True

    def parse(self, inventory, loader, path, cache=True):

        # call base method to ensure properties are available for use with other helper methods
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # this method will parse 'common format' inventory sources and
        # update any options declared in DOCUMENTATION as needed
        # config = self._read_config_data(self, path)

        # if NOT using _read_config_data you should call set_options directly,
        # to process any defined configuration for this plugin,
        # if you dont define any options you can skip
        # self.set_options()

        self._read_virlrc()
        self._get_simulation()

        url = "http://%s:19399/simengine/rest/interfaces/%s" % (self.virl_host, self.simulation)

        # print "Fetching: %s" % url

        # perform REST operation
        simulations = requests.get(url, auth=(self.virl_username, self.virl_password))
        if simulations.status_code == 200:

            interfaces = simulations.json()[self.simulation]
            try:
                group = self.inventory.add_group('virl_hosts')
            except AnsibleError as e:
                raise AnsibleParserError("Unable to add group %s: %s" % (group, to_text(e)))


            for key, value in interfaces.items():
                self.inventory.add_host(key)
                self.inventory.set_variable(key, 'ansible_host', value['management']['ip-address'].split('/')[0])

