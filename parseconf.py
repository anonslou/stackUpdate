#!/usr/bin/env python

import yaml


class ParseConf:

    def __init__(self, config=None):
        if not config:
            config = 'cisco.yaml'
        self.nodes = yaml.load(open(config))
        node = self.nodes['defaults']
        self.username = node['username']
        self.password = node['password']
        self.port = node['port']
        self.device_type = node['device_type']
        self.secret = node['secret']  # enable password

    def get_hosts_by_name(self, hostname):
        netmikobj = {}
        node = self.nodes['devices'][hostname]
        netmikobj['username'] = self.username
        netmikobj['port'] = self.port
        netmikobj['password'] = self.password
        netmikobj['device_type'] = self.device_type
        netmikobj['secret'] = self.secret
        for prop in netmikobj.keys():
            if prop in node:
                netmikobj[prop] = node[prop]
        netmikobj['ip'] = node['ip']
        netmikobj['hostname'] = hostname
        return netmikobj

    def get_all_hosts(self):
        for hostname in self.nodes['devices']:
            yield self.get_hosts_by_name(hostname)

    def set_pass(self, password):
        self.password = password
