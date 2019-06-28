#! /usr/bin/env python3
# coding: utf-8
import pdb
from django.test import TestCase, tag
from takotako.nornir2.takotako_main.inventory import Inventory


class Test_Inventory(TestCase):
    @classmethod
    def setUp(self):
        with open("takotako/tests/inputs/test_inventory.csv", "r") as f:
            csv = f.read()
        self.inv = Inventory()
        self.inv.load_csv(csv)

    def test_load_csv(self):
        """
        Check CSV loader 
        """
        expected = {
            "home-sw01": {
                "groups": ["home"],
                "hostname": "192.168.128.100",
                "username": "admin",
                "password": "cisco",
                "platform": "cisco_ios",
                "data": {
                    "location": "fontenay-city",
                    "model": "2960",
                    "option1": "to-keep",
                    "option2": "blue"
                },
                "modules": ["1"]
            },
            "home-sw02": {
                "groups": ["home"],
                "hostname": "192.168.128.101",
                "username": "admin",
                "password": "cisco",
                "platform": "cisco_ios",
                "data": {
                    "location": "fontenay-city",
                    "model": "2960S",
                    "option1": "to-keep",
                    "option2": "green"
                },
                "modules": ["1"]
            },
            "home-sw03": {
                "groups": ["home"],
                "hostname": "192.168.128.102",
                "username": "admin",
                "password": "cisco",
                "platform": "cisco_ios",
                "data": {
                    "location": "fontenay-city",
                    "model": "2960S",
                    "option1": "trash",
                    "option2": "red"
                },
                "modules": ["1"]
            },
            'failed_lines': ['wrongly-formatted-line']
        }
        result = self.inv.pool
        assert result == expected

    def test_export_nornir2(self):
        """
        Checks files are properly output as yaml files
        failed_lines are not in output file
        Checks entries are in the file
        No need to test yaml.dump function
        """
        self.inv.export_nornir2()
        with open("takotako/nornir2/takotako_run/inventory/hosts.yaml", "r") as f:
            file = f.read()
        for host in self.inv.pool:
            if host != 'failed_lines':
                assert host in file
                for key in self.inv.pool[host]:
                    if key != 'data' and type(self.inv.pool[host][key]) != list:
                        assert self.inv.pool[host][key] in file
                    elif key != 'data' and type(self.inv.pool[host][key]) == list:
                        for elt in self.inv.pool[host][key]:
                            assert elt in file
                    else:
                        for data in self.inv.pool[host]['data']:
                            assert self.inv.pool[host]['data'][data] in file
            else:
                assert host not in file

    def test_filter_host_hostname(self):
        """
        filter func returns inventory attribute selection
        type dict with hostname as key and list of interfaces as value
        CASE:
            - ip provided ONLY
        EXPECTED:
            - matching host empty int selection
        """
        self.inv.filter(hostname='192.168.128.100')
        assert self.inv.selection == {
            'home-sw01': [],
        }

    def test_filter_host_hostname2(self):
        """
        filter func returns inventory attribute selection
        type dict with hostname as key and list of interfaces as value
        CASE:
            - ip provided ONLY
        EXPECTED:
            - matching host empty int selection
        """
        self.inv.filter(hostname='192.168.128.100', option1='trash')
        assert self.inv.selection == {
            'home-sw01': [],
            'home-sw03': []
        }

    def test_filter_host_data_crit(self):
        """
        filter func returns inventory attribute selection
        type dict with hostname as key and list of interfaces as value
        CASE:
            - hosts data crit ONLY
        EXPECTED:
            - matching host empty int selection
        """
        self.inv.filter(option1='to-keep')
        assert self.inv.selection == {
            'home-sw01': [],
            'home-sw02': [],
        }

    def test_filter_MULTI_host_data_crit(self):
        """
        filter func returns inventory attribute selection
        type dict with hostname as key and list of interfaces as value
        CASE:
            - hosts data crit ONLY
        EXPECTED:
            - matching host empty int selection
        """
        self.inv.filter(option1='trash', model='2960S')
        assert self.inv.selection == {
            'home-sw03': [],
        }

    def test_filter_host_no_filter(self):
        """
        filter func returns inventory attribute selection
        type dict with hostname as key and list of interfaces as value
        CASE:
            - bogus criteria
        EXPECTED:
            - empty selection
        """
        self.inv.filter(option4='non existant search field')
        assert self.inv.selection == None

    def test_filter_int_desc(self):
        """
        filter func returns inventory attribute selection
        type dict with hostname as key and list of interfaces as value
        CASE:
            - interface criteria ONLY
            - not all hosts have interfaces details
        EXPECTED:
            - Only host with matching interfaces 
        """
        self.inv.pool['home-sw02'].update({
            'interfaces': {
                'gi1/0/1': {
                    'description': 'target',
                },
                'gi1/0/2': {
                    'description': 'bogus'
                },
                'gi1/0/3': {
                    'running': [],
                    'description': 'target',
                },
                'gi1/0/4': {
                    'description': 'bogus'
                },
            },
        })
        self.inv.filter(description='target')
        assert self.inv.selection == {
            'home-sw02': ['gi1/0/1', 'gi1/0/3'],
        }

    def test_filter_MULTI_MULTI(self):
        """
        filter func returns inventory attribute selection
        type dict with hostname as key and list of interfaces as value
        CASE:
            - multi interface criteria 
            - multi host data criteria
        EXPECTED:
            - Only host with matching interfaces 
        """
        self.inv.pool['home-sw02'].update({
            'interfaces': {
                'gi1/0/1': {
                    'description': 'target',
                    'status': 'down',
                    'running': ['switchport mode access', 'bogus config']
                },
                'gi1/0/2': {
                    'description': 'bogus'
                },
                'gi1/0/3': {
                    'description': 'target',
                    'status': 'down',
                    'running': ['switchport mode access', 'port-security']
                },
                'gi1/0/4': {
                    'description': 'bogus'
                },
            },
        })
        self.inv.filter(option1='to-keep', model='2960S',
                        description='target', status='down', running=['switchport mode access', 'port-security'])
        assert self.inv.selection == {
            'home-sw02': ['gi1/0/3'],
        }

    @tag('target')
    def test_filter_MULTI_MULTI2(self):
        """
        filter func returns inventory attribute selection
        type dict with hostname as key and list of interfaces as value
        CASE:
            - multi interface criteria 
            - multi host data criteria
        EXPECTED:
            - Only host with matching interfaces 
        """
        self.inv.pool['home-sw02'].update({
            'interfaces': {
                'gi1/0/1': {
                    'running': ['switchport mode access', 'bogus config']
                },
                'gi1/0/2': {
                    'running': ['switchport mode access', 'port-security']
                },
                'gi1/0/3': {
                    'description': 'target',
                    'status': 'down',
                    'running': ['switchport mode access', 'port-security']
                },
                'gi1/0/4': {
                    'description': 'bogus'
                },
            },
        })
        self.inv.pool['home-sw03'].update({
            'interfaces': {
                'gi1/0/1': {
                    'description': 'target',
                    'status': 'down',
                },
                'gi1/0/2': {
                    'description': 'bogus',
                },
                'gi1/0/3': {
                    'description': 'target',
                    'status': 'down',
                },
                'gi1/0/4': {
                    'description': 'bogus'
                },
            },
        })
        self.inv.filter(model='2960S',
                        running=['switchport mode access', 'port-security'])
        assert self.inv.selection == {
            'home-sw02': ['gi1/0/2', 'gi1/0/3'],
        }

    def test_filter_misc_w_int_data(self):
        pass
