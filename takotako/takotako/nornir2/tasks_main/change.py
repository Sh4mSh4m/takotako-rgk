#! /usr/bin/env python3
# coding: utf-8

from nornir.plugins.tasks.networking import netmiko_send_command, netmiko_send_config
from takotako.nornir2.tasks_parser.parsers import parsesShowIntDesc, parsesShowRunInt
from takotako.nornir2.tasks_parser.task_support import detail
from takotako.nornir2.tasks_parser.list_converter import optimizesWithRange
from celery import task, current_task


def chg_write_memory(task, inventory_selection):
    """
    Simple write memory
    """
    task.run(
        task=netmiko_send_command, command_string="write memory", expect_string="[OK]"
    )


def chg_conf_lines(task, inventory_selection, conf_lines):
    """
    Based on selected interfaces(LIST) in the playbook
    push conf_lines(LIST)
    """
    config_commands = []
    hostname = task.host.name

    interface_list = inventory_selection[hostname]
    #interfaces_range = optimizesWithRange(interface_list)
    interfaces_range = interface_list
    for interface in interfaces_range:
        config_commands += [f"interface {interface}"] + conf_lines + ["exit"]

    task.run(task=netmiko_send_config, config_commands=config_commands)
