#! /usr/bin/env python3
# coding: utf-8
from django.test import TestCase
from unittest.mock import MagicMock, patch

from takotako.nornir2.tasks_main.read_only import show_interface_description2, show_interface_running2


class Test_Roles(TestCase):
    def test_description(self):
        """
        Checks show_interface_description task updates inv.pool
        with expected list of interfaces for device
        """
        with open('takotako/tests/outputs/output_show_int_description.txt', 'r') as f:
            seven_first_lines = [next(f) for _ in range(7)]
        # here ignored the interface vlan descriptions of the output
        output_description = '\n'.join(seven_first_lines[4:])

        # Mocking task ignoring task run method
        mock_task = MagicMock()
        mock_task.return_value.run.return_value = None
        mock_task.results[0].result = output_description
        mock_task.host.name = "home-sw02"

        # Mocking inventory
        mock_inv_pool = MagicMock()
        mock_inv_pool = {
            "home-sw02": {
                'interfaces': {
                    'gi1/0/1': {
                        'description': 'bogus'
                    }
                }
            }
        }
        expected = ['gi1/0/1', 'gi1/0/2', 'gi1/0/3']

        show_interface_description2(mock_task, mock_inv_pool)
        # Simply assert function updated host key in the inv.pool
        # with parsed data i.e. it's got the proper interfaces keys
        # Checks the description has been updated for gi1/0/1
        for interface in expected:
            assert 'Bornes DECT IP' in mock_inv_pool["home-sw02"]['interfaces'][interface]['description']

    def test_running(self):
        """
        Checks show_interface_running task updates inv.pool
        with expected list of interfaces for device
        """
        with open('takotako/tests/outputs/output_show_run_all_int.txt', 'r') as f:
            seven_first_lines = [next(f) for _ in range(39)]
        output_running = '\n'.join(seven_first_lines[0:])

        # Mocking task ignoring task run method
        mock_task = MagicMock()
        mock_task.return_value.run.return_value = None
        mock_task.results[0].result = output_running
        mock_task.host.name = "home-sw02"

        # Mocking inventory
        mock_inv_pool = MagicMock()
        mock_inv_pool = {
            "home-sw02": {
                'interfaces': {
                    'gi1/0/1': {}
                }
            }
        }
        expected_interfaces = ['gi1/0/1', 'gi1/0/2', 'gi1/0/3']
        expected_running = [
            "description Bornes DECT IP",
            "switchport access vlan 100",
            "switchport mode access",
            "switchport voice vlan 300",
            "no logging event link-status",
            "no logging event power-inline-status",
            "srr-queue bandwidth share 1 30 35 5",
            "priority-queue out",
            "no snmp trap link-status",
            "mls qos trust cos",
            "auto qos trust",
        ]
        show_interface_running2(mock_task, mock_inv_pool)
        # Simply assert function updated host key in the inv.pool
        # with parsed data i.e. it's got the proper interfaces keys
        # Checks the description has been updated for gi1/0/1
        for interface in expected_interfaces:
            for config_line in expected_running:
                assert config_line in mock_inv_pool["home-sw02"]['interfaces'][interface]['running']
