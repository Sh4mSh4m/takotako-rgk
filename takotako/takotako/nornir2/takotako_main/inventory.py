#! /usr/bin/env python3
# coding: utf-8
import pdb
import os
import yaml
import json
import re
from time import time


class Inventory:
    """
    Takotako inventory manager
    attributes and methods to import export devices data
    generators to filter pool of devices
    """

    def __init__(self):
        """
        Several ways to populate the pool
        Defaults to empty
        """
        self.pool = None
        self.selection = None

    def load_csv(self, csv):
        """
        Resets pool
        Translates data from csv into invetory pool
        csv must be as follow:
        group;hostname;ip_address;platform;username;password;location;model;option1;option2;option3
        Wrongly formatted lines are stored in 'failed_lines' key as list of lines
        """
        self.pool = {}
        lines = csv.split('\n')
        lines = list(filter(None, lines))  # cleans list from empty elt
        for line in lines:
            try:
                group, hostname, ip_address, platform, username, password, location, model, option1, option2, option3 = line.split(
                    ';')
                group_list = list(filter(None, group.split(',')))
                inv_elt = {
                    hostname.strip(): {
                        'groups': group_list,
                        'hostname': ip_address.strip(),
                        'username': username.strip(),
                        'password': password,  # unstriped
                        'platform': platform.strip(),
                        'data': {
                            'location': location.strip(),
                            'model': model.strip(),
                            'option1': option1.strip(),
                            'option2': option2.strip(),
                        },
                        'modules': ['1']
                    }
                }
            except:
                if 'failed_lines' in self.pool:
                    self.pool['failed_lines'].append(line)
                else:
                    failed_load = {
                        'failed_lines': [line]
                    }
                self.pool.update(failed_load)
            self.pool.update(inv_elt)

    def export_nornir2(self):
        """
        exports elements in pool to yaml files for nornir2
        """
        path_to_file = "takotako/nornir2/takotako_run/inventory/hosts.yaml"
        # Resets the hosts.yaml file if present
        if os.path.isfile(path_to_file):
            os.remove(path_to_file)
        with open(path_to_file, "w+") as f:
            f.write("---\n")

        for host_key in self.pool:
            if host_key != 'failed_lines':
                with open(path_to_file, "a+") as outputfile:
                    dct = {
                        host_key: {
                            "groups": self.pool[host_key]["groups"],
                            "hostname": self.pool[host_key]["hostname"],
                            "username": self.pool[host_key]["username"],
                            "platform": self.pool[host_key]["platform"],
                            "password": self.pool[host_key]["password"],
                            "data": self.pool[host_key]["data"],
                        }
                    }
                    yaml.dump(dct, outputfile, default_flow_style=False)

    def filter(self, **filter):
        """
        Screens the whole inv.pool and test all criteria
        set as input
        updates the inv.selection dict with
        {
            "home-sw01": [
                'gi1/0/1',
                'fa0/1',
            ]
        }

        As a reminder example of inv element:
        {
            "home-sw01": {
                "groups": [
                    "home"
                ],
                "hostname": "192.168.128.100",
                "username": "admin",
                "password": "cisco",
                "platform": "cisco_ios",
                "data": {
                    "location": "fontenay-city",
                    "model": "2960S",
                    "option1": "to-keep",
                    "option2": "blue"
                },
                "modules": [
                    "1",
                    "2"
                ],
                "interfaces": {
                    "gi1/0/1": {
                        "module": "1",
                        "row": "odd",
                        "status": "up",
                        "protocol": "up",
                        "description": "1 is up",
                        "running": [
                            "switchport mode access",
                            "switchport port-security"
                        ]
                    },
                }
            },
            "home-sw02": {
            ...
        }
        """
        # lists of criteria per category
        hosts_criteria = [
            'groups',
            'hostname',
            'data'
        ]
        hosts_data_criteria = [
            'platform',
            'location',
            'model',
            'option1',
            'option2',
        ]
        hosts_interface_criteria = [
            'description',
            'module',
            'row',
            'status',
            'protocol',
        ]
        hosts_interface_running_criteria = [
            'running'
        ]
        valid_criteria = hosts_criteria + hosts_data_criteria + \
            hosts_interface_criteria + hosts_interface_running_criteria

        if not any([crit not in valid_criteria for crit in filter]):
            host_filter = {
                crit: crit_value for crit, crit_value in filter.items() if crit in hosts_criteria
            }
            host_data_filter = {
                crit: crit_value for crit, crit_value in filter.items() if crit in hosts_data_criteria
            }
            host_interface_filter = {
                crit: crit_value for crit, crit_value in filter.items() if crit in hosts_interface_criteria
            }
            host_interface_running_filter = {
                crit: crit_value for crit, crit_value in filter.items() if crit in hosts_interface_running_criteria
            }
            #############################
            # Fist loop hosts selection #
            #############################
            # First we identify which hosts to select
            # if no crits are about hosts but with interface crit search, all hosts are selected initially
            if host_filter == {} and host_data_filter == {} and host_interface_filter == {}:
                self.selection = {host: []
                                  for host in self.pool if host != 'failed_lines'}
            # host for which crits match in hosts criteria or hosts_data_criteria
            elif host_filter != {} and host_data_filter != {}:
                self.selection = {host: [] for host in self.pool
                                  if host != 'failed_lines' and
                                  (all([crit_value in self.pool[host].get(crit, []) for crit, crit_value in host_filter.items()]) or
                                   all([crit_value in self.pool[host]['data'].get(crit, []) for crit, crit_value in host_data_filter.items()]))
                                  }
            elif host_filter != {} and host_data_filter == {}:
                self.selection = {host: [] for host in self.pool
                                  if host != 'failed_lines' and
                                  all([crit_value in self.pool[host].get(crit, [])
                                       for crit, crit_value in host_filter.items()])
                                  }
            else:
                self.selection = {host: [] for host in self.pool
                                  if host != 'failed_lines' and
                                  all([crit_value in self.pool[host]['data'].get(crit, [])
                                       for crit, crit_value in host_data_filter.items()])
                                  }
            ####################################
            # Second loop interfaces selection #
            ####################################
            if self.selection != {}:
                #                # NOT A CASE
                #                if not any([filter_looked in hosts_interface_criteria for filter_looked in filter]):
                #                    for host in self.selection:
                #                        if host != 'failed_lines' and 'interfaces' in self.pool[host]:
                #                            self.selection[host] = [interface for interface in self.pool[host]['interfaces']
                #                                                    if re.match(r'\S{2}\d/\d(/\d+)*', interface) != []]
                #                        else:
                #                            # do nothing interface list is already [] by default
                #                            pass
                # if search is about interfaces criteria NOT running
                for host in self.selection:
                    if host != 'failed_lines' and 'interfaces' in self.pool[host]:
                        if host_interface_filter != {}:
                            self.selection[host] = [interface for interface in self.pool[host]['interfaces']
                                                    if re.match(r'\S{2}\d/\d(/\d+)*', interface) != [] and
                                                    all([crit_value in self.pool[host]['interfaces'][interface].get(crit, []) for crit, crit_value in host_interface_filter.items()])]
                            # ADDITIONAL LIST SEARCH HERE
                            # if there is running search
                            # Filter the selected interfaces
                            if 'running' in host_interface_running_filter:
                                interfaces = self.selection[host]
                                lines_searched = host_interface_running_filter['running']
                                for interface in interfaces:
                                    config_list = self.pool[host]['interfaces'][interface].get(
                                        'running', [])
                                    match = []
                                    for line in lines_searched:
                                        if line in config_list:
                                            match.append(True)
                                        else:
                                            match.append(False)
                                    if all(match):
                                        self.selection[host].append(interface)
                                    else:
                                        self.selection[host].remove(interface)
                            else:
                                pass
                            # at the end remove hosts without interfaces matched
                            self.selection = {
                                host: value for host, value in self.selection.items() if self.selection[host] != []}
                        # Once first selection is made
                        elif host_interface_filter == {} and 'running' in host_interface_running_filter:
                            # if there were no filter for interfaces, all host interfaces are searched
                            interfaces = [
                                interface for interface in self.pool[host]['interfaces']]
                            lines_searched = host_interface_running_filter['running']
                            for interface in interfaces:
                                config_list = self.pool[host]['interfaces'][interface].get(
                                    'running', [])
                                match = []
                                for line in lines_searched:
                                    if line in config_list:
                                        match.append(True)
                                    else:
                                        match.append(False)
                                if all(match):
                                    if host in self.selection:
                                        self.selection[host].append(interface)
                                    else:
                                        self.selection.update(
                                            {host: [interface]})
                                else:
                                    pass
                            self.selection = {
                                host: value for host, value in self.selection.items() if self.selection[host] != []}
                        else:
                            # at the end remove hosts without interfaces matched
                            self.selection = {
                                host: value for host, value in self.selection.items() if self.selection[host] != []}
                    # if host has no 'interfaces' key yet, pass snapshot must be performed
                    else:
                        pass
        else:
            print('invalid filters')
