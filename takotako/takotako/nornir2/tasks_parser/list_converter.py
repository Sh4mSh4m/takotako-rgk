#! /usr/bin/env python3
# coding: utf-8
MAX_STACK_LENGTH = 8


def optimizesWithRange(interfacesList):
    """
    Main function.
    Takes a list of interfaces as input
    returns a set of ranges command
    """
    interfacesList = [interface.lower() for interface in interfacesList]
    modulesDict = sortsModuleInterfaces(interfacesList)
    interfaceCmdList = []
    for key, interfaces in modulesDict.items():
        resultList, prefixe = convertsSameModule(interfaces)
        for cmd in returnsInterfaceCmdList(resultList, prefixe):
            interfaceCmdList.append(cmd)
    return interfaceCmdList


def sortsModuleInterfaces(interfacesList):
    """
    Sorts interfaces per stack module
    Returns a dict with stack member id  as key and interfaces list as value
    """
    modules = {}
    resultDict = {}
    for i in range(1, MAX_STACK_LENGTH + 1):
        modules[i] = "gi{}/0/".format(i)
    for key, module in modules.items():
        resultDict[key] = [
            interface for interface in interfacesList if module in interface
        ]
        if resultDict[key] == []:
            del resultDict[key]
        else:
            continue
    return resultDict


def convertsSameModule(interfacesList):
    """
    Input is interface list
    Returns duplets of corresponding range indexes or simplet of index
    """
    sOrdered, prefixe = processes(interfacesList)
    if len(sOrdered) == 1:  # simplet case
        return [sOrdered], prefixe
    inputList = sOrdered
    destList = []
    resultList = []
    candidate = inputList.pop(0)
    last, candidate = rotates(candidate, inputList, destList)
    while len(inputList) != 0:
        if (candidate == (last + 1)) and (len(destList) == 1):
            last, candidate = rotates(candidate, inputList, destList)
        elif (candidate == (last + 1)) and (len(destList) != 1):
            destList.pop()  # consequent index case, keeping duplet
            last, candidate = rotates(candidate, inputList, destList)
        elif (candidate != (last + 1)) and (len(destList) == 1):
            resultList.append(destList)  # simplet complete case, reinit
            destList = []
            last, candidate = rotates(candidate, inputList, destList)
        elif (candidate != (last + 1)) and (len(destList) != 1):
            resultList.append(destList)  # duplet complete case, reinit
            destList = []
            last, candidate = rotates(candidate, inputList, destList)
    if candidate == (last + 1) and (len(destList) != 1):
        destList.pop()
        destList.append(candidate)
        resultList.append(destList)
    elif candidate == (last + 1) and (len(destList) == 1):
        destList.append(candidate)
        resultList.append(destList)
    else:
        resultList.append(destList)
        resultList.append([candidate])
    return resultList, prefixe


def rotates(candidate, inputList, destList):
    """
    Input are the two lists
    Returns candidate and last selection
    """
    destList.append(candidate)
    return destList[-1], inputList.pop(0)


def processes(interfacesList):
    """
    Input is interfaces list
    Parses interfaces list and returns only last digit interface index
    Returns list of those indexes and prefixe
    """
    sList = set()  # initiates an empty set
    for item in interfacesList:
        sList.update(item.split("/"))
    # Isolating numbers only
    sOrdered = []
    for item in sorted(sList):
        try:
            sOrdered.append(int(item))
        except ValueError:
            prefixe = item
    # Removing 0 which cannot be interface index
    sOrdered.remove(0)
    return sorted(sOrdered), prefixe


def returnsInterfaceCmdList(resultList, prefixe):
    """
    Formats properly the range commands based on resultList
    """
    interfaceCmdList = []
    for item in resultList:
        if len(item) == 1:
            index = str(item.pop())
            interfaceCmd = prefixe + "/0/" + index
        elif len(item) == 2:
            indexEnd = str(item.pop())
            indexStart = str(item.pop())
            interfaceCmd = "range " + prefixe + "/0/" + indexStart + " - " + indexEnd
        else:
            print("Error, not a duplet")
        interfaceCmdList.append(interfaceCmd)
    return interfaceCmdList
