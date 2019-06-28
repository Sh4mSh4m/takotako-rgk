#! /usr/bin/env python3
# coding: utf-8
from django.test import TestCase
from parameterized import parameterized
from takotako.nornir2.tasks_parser.task_support import detail


class Test_task_support(TestCase):
    @parameterized.expand(
        [
            [
                "gi1/0/1", {'module': '1', 'row': 'odd'}
            ],
            [
                "gi2/0/2", {'module': '2', 'row': 'even'}
            ],
            [
                "gig1/0/3", {'module': '1', 'row': 'odd'}
            ],
            [
                "fa0/2", {'module': '1', 'row': 'even'}
            ]
        ]
    )
    def test_detail(self, interface, expected):
        """
        Based on interface name returns switch position
        """
        result = detail(interface)
        assert result == expected
