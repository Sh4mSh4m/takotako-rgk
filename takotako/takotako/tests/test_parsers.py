#! /usr/bin/env python3
# coding: utf-8
import textfsm
from django.test import TestCase
from takotako.tests.test_ouputs import *
from takotako.nornir2.tasks_parser.parsers import parsesShowIntStatus, parsesShowIntDesc, parsesShowRunInt, parsesShowMac, parsesShowCdpNeighbors


class Test_Interface_Output_parser(TestCase):
    def test_parsesShowIntStatus(self):
        """
        show interface status
        parsing 
        """
        expected = output_status_processed
        result = parsesShowIntStatus(output_status)
        assert result == expected

    def test_parsesShowIntDesc(self):
        """
        show interface description
        parsing 
        """
        expected = output_description_processed
        result = parsesShowIntDesc(output_description)
        assert result == expected

    def test_parsesShowRunInt(self):
        """
        show running-configuration | s interface
        parsing 
        """
        expected = output_run_all_int_processed
        result = parsesShowRunInt(output_run_all_int)
        assert result == expected

    def test_parseShowMac(self):
        """
        show mac address-table
        parsing
        """
        expected = output_mac_address_processed
        result = parsesShowMac(output_mac_address)
        assert result == expected

    def test_parseShowCdpNeighbors(self):
        """
        show cdp neighbors
        parsing
        """
        expected = output_cdp_neighbors_processed
        result = parsesShowCdpNeighbors(output_cdp_neighbors)
        assert result == expected
