#! /usr/bin/env python3
# coding: utf-8

from nornir.plugins.tasks.networking import netmiko_send_command
from takotako.nornir2.tasks_parser.parsers import parsesShowIntDesc, parsesShowRunInt
from takotako.nornir2.tasks_parser.task_support import detail


def show_interface_description(task, inventory):
    """
    Runs nornir task using netmiko_send_command for
    # show interface description
    Parses outputs and updates inventory hostname dict
    """
    index = 0

    cmd_string = f"show interface description"
    task.run(task=netmiko_send_command, command_string=cmd_string)

    output = task.results[index].result
    hostname = task.host.name

    # update host dict with parsed result
    # Updating at the interface level !!!
    int_dct = parsesShowIntDesc(output)
    if 'interfaces' not in inventory.pool[hostname].keys():
        inventory.pool[hostname].update({'interfaces': {}})

    if int_dct != {}:
        for interface in int_dct:
            if interface in inventory.pool[hostname]['interfaces'].keys():
                # interface can have other keys. adding to the existing pool of info
                inventory.pool[hostname]['interfaces'][interface].update(
                    int_dct[interface])
            else:
                # if key does not exist, define and set value
                inventory.pool[hostname]['interfaces'][interface] = int_dct[interface]
                # also add the keys detail (module and row and its selected mark
                # updates the hostname modules list if interface module not there
                interface_mod = detail(interface)['module']
                if interface_mod != "1" and interface_mod not in inventory.pool[hostname]['modules']:
                    inventory.pool[hostname]['modules'].append(interface_mod)
                # adding interface details
                inventory.pool[hostname]['interfaces'][interface].update(
                    detail(interface))
    else:
        pass


def show_interface_description2(task, inventory_pool):
    """
    Runs nornir task using netmiko_send_command for
    # show interface description
    Parses outputs and updates inventory_pool hostname dict
    """
    index = 0

    cmd_string = f"show interface description"
    task.run(task=netmiko_send_command, command_string=cmd_string)

    output = task.results[index].result
    hostname = task.host.name

    # update host dict with parsed result
    # Updating at the interface level !!!
    int_dct = parsesShowIntDesc(output)
    if 'interfaces' not in inventory_pool[hostname].keys():
        inventory_pool[hostname].update({'interfaces': {}})

    if int_dct != {}:
        for interface in int_dct:
            if interface in inventory_pool[hostname]['interfaces'].keys():
                # interface can have other keys. adding to the existing pool of info
                inventory_pool[hostname]['interfaces'][interface].update(
                    int_dct[interface])
            else:
                # if key does not exist, define and set value
                inventory_pool[hostname]['interfaces'][interface] = int_dct[interface]
                # also add the keys detail (module and row and its selected mark
                # updates the hostname modules list if interface module not there
                interface_mod = detail(interface)
                mod = interface_mod['module']
                if mod != "1" and mod not in inventory_pool[hostname]['modules']:
                    inventory_pool[hostname]['modules'].append(mod)
                # adding interface details
                inventory_pool[hostname]['interfaces'][interface].update(
                    detail(interface))
    else:
        pass


def show_interface_running2(task, inventory_pool):
    """
    Runs nornir task using netmiko_send_command for
    # show running | s interface
    Parses outputs and updates inventory_pool hostname dict
    """
    index = 0

    cmd_string = f"show running-config"
    task.run(task=netmiko_send_command, command_string=cmd_string)

    output = task.results[index].result
    hostname = task.host.name

    # update host dict with parsed result
    # Updating at the interface level !!!
    int_dct = parsesShowRunInt(output)
    if 'interfaces' not in inventory_pool[hostname].keys():
        inventory_pool[hostname].update({'interfaces': {}})

    if int_dct != {}:
        for interface in int_dct:
            if interface in inventory_pool[hostname]['interfaces'].keys():
                # interface can have other keys. adding to the existing pool of info
                inventory_pool[hostname]['interfaces'][interface].update(
                    int_dct[interface])
            else:
                # if key does not exist, define and set value
                inventory_pool[hostname]['interfaces'][interface] = int_dct[interface]
                # also add the keys detail (module and row and its selected mark
                # updates the hostname modules list if interface module not there
                interface_mod = detail(interface)
                mod = interface_mod['module']
                if mod != "1" and mod not in inventory_pool[hostname]['modules']:
                    inventory_pool[hostname]['modules'].append(mod)
                # adding interface details
                inventory_pool[hostname]['interfaces'][interface].update(
                    detail(interface))
    else:
        pass
