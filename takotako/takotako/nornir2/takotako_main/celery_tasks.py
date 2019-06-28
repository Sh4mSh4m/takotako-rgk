#! /usr/bin/env python3
# coding: utf-8
import os
from nornir import InitNornir
from celery import task, current_task
from celery.contrib import rdb

from takotako.nornir2.tasks_main.read_only import show_interface_description2, show_interface_running2
from takotako.nornir2.tasks_main.change import chg_conf_lines, chg_write_memory


@task
def orchestrate_simple(inv_pool, order_list):
    """
    Celery task that connects to device and push orders in sequence to switches
    Input is order_list 
    Result is JSON object
    """
    path = "takotako/nornir2/takotako_run/inventory/"
    nr = InitNornir(
        core={"num_workers": 10},
        inventory={
            "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
            "options": {
                "host_file": path + "hosts.yaml",
                "group_file": path + "groups.yaml",
            },
        },
    )
    if order_list == [] or len(order_list) == 0:
        order_list = ['description']
    for order in order_list:
        task_map = {
            'description': show_interface_description2,
            'running': show_interface_running2,
            # 'status': show_interface_status,
            # 'mac': show_mac_address_table,
            # 'neighbors': show_cdp_neighbors
        }
        task_chosen = task_map[order]
        # rdb.set_trace()
        nr.run(task=task_chosen, inventory_pool=inv_pool)
    return inv_pool


@task
def orchestrate_change(inv_pool, inv_selection, conf_lines):
    """
    Celery task that connects to device to push config lines on interfaces
    Input is conf_lines and inv_selection
    Result is JSON object
    """
    path = "takotako/nornir2/takotako_run/inventory/"
    nr = InitNornir(
        core={"num_workers": 10},
        inventory={
            "plugin": "nornir.plugins.inventory.simple.SimpleInventory",
            "options": {
                "host_file": path + "hosts.yaml",
                "group_file": path + "groups.yaml",
            },
        },
    )
    nr.run(task=chg_conf_lines, inventory_selection=inv_selection,
           conf_lines=conf_lines)

    # run a read job to check that conf lines have been applied
    nr.run(task=show_interface_running2, inventory_pool=inv_pool)
    return inv_pool
