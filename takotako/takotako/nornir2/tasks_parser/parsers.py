#! /usr/bin/env python3
# coding: utf-8
import pdb
import textfsm


#####################
# Interfaces parser #
#####################
def parsesShowIntStatus(task_result):
    """
    Extracts information from raw output
    show interface status
    Push elements into JSON like object
    {
        'gi1/0/2': {
            'status_global': 'notconnect|connect',
            'vlan': '1',
            'duplex': 'auto',
            'speed': 'auto'
        }
        ...
    }
    """
    with open("takotako/nornir2/takotako_run/parser_templates/template_status.txt", "r") as f:
        template = textfsm.TextFSM(f)
    fsm_result = template.ParseText(task_result)
    outputProcessed = {}
    for line in fsm_result:
        outputProcessed[line[0].lower()] = {
            "status_global": line[2].strip(),
            "vlan": line[3].strip(),
            "duplex": line[4].strip(),
            "speed": line[5].strip(),
        }
    outputProcessed.pop("", None)
    return outputProcessed


def parsesShowIntDesc(task_result):
    """
    Extracts information from raw output
    show interface description
    Push elements into JSON like object
    {
        'gi1/0/2': {
            'status': 'notconnect|connect',
            'protocol': '1',
            'description': 'Port ToIP',
        }
        ...
    }
    """
    with open("takotako/nornir2/takotako_run/parser_templates/template_description.txt", "r") as f:
        template = textfsm.TextFSM(f)
    fsm_result = template.ParseText(task_result)
    outputProcessed = {}
    for elt in fsm_result:
        outputProcessed[elt[0].lower().strip()] = {
            "status": elt[1].strip(),
            "protocol": elt[2].strip(),
            "description": elt[3].strip(),
        }
    outputProcessed.pop("", None)
    return outputProcessed


def parsesShowRunInt(task_result):
    """
    Extracts information from raw output
    show running-configuration | s interface
    Push elements into JSON like object
    {
        'gi1/0/2': {
            'running': ['description Port ToIP',...]
        }
        ...
    }
    """
    with open("takotako/nornir2/takotako_run/parser_templates/template_interface.txt", "r") as f:
        template = textfsm.TextFSM(f)
    fsm_result = template.ParseText(task_result)
    outputProcessed = {}
    for elt in fsm_result:
        outputProcessed[(elt[0][0:2] + elt[1]).lower()] = {
            "running": [line.strip() for line in elt[2]]
        }
    outputProcessed.pop("", None)
    return outputProcessed
# track


def parsesShowMac(task_result):
    """
    Extracts information from raw output
    show mac address-table
    Push elements into JSON like object
    {
        'gi1/0/2': {
            'mac_list': [
                {
                    'mac': 'xxxx.xxxx.xxxx'
                    'vlan': '14'
                    'type': 'DYNAMIC|STATE'
                },
                ...
            ],
        },
        ...
    }
    """
    with open("takotako/nornir2/takotako_run/parser_templates/template_mac.txt", "r") as f:
        template = textfsm.TextFSM(f)
    fsm_result = template.ParseText(task_result)
    outputProcessed = {}
    for elt in fsm_result:
        interface = elt[-1].strip().lower()
        data = {
            'mac': elt[0].strip(),
            'vlan': elt[2].strip(),
            'type': elt[1].strip()
        }
        if interface in outputProcessed:
            outputProcessed[interface]['mac_list'].append(data)
        else:
            outputProcessed[interface] = {
                'mac_list': [data]
            }
    return outputProcessed

####################
# Host data parser #
####################


def parsesShowCdpNeighbors(task_result):
    """
    Extracts information from raw output
    show cdp neighbors
    Push elements into JSON like object
    {
        'neighbors': {
            'gi1/0/2': {
                {
                    'neighbor': 'hostname2',
                    'capability': 'R S I',
                    'platform': 'C2960X',
                    'remote_interface': 'gi1/0/4',
                },
            ...    
            },
        },
    }
    """
    with open("takotako/nornir2/takotako_run/parser_templates/template_cdp_neighbors.txt", "r") as f:
        template = textfsm.TextFSM(f)
    fsm_result = template.ParseText(task_result)
    outputProcessed = {
        'neighbors': {
        }
    }
    for elt in fsm_result:
        interface = elt[1].replace(' ', '').lower().strip()
        data = {
            interface: {
                "neighbor": elt[0].strip(),
                "capability": elt[2].strip(),
                "remote_interface": elt[-1].strip()
            }
        }
        outputProcessed["neighbors"].update(data)
    # For future test presentation
    #print(f'{{\n    "neighbors": {{\n')
    # for elt in outputProcessed['neighbors']:
    #    print(f'        "{elt}": {{\n            {outputProcessed["neighbors"][elt]}\n    }},')
    # print(f'\n}}')
    return outputProcessed
