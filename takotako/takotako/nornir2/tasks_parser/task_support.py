import re


def detail(interface):
    """
    Input is interface
    Returns a dict with 'module' and 'row' as keys:
    {
        'module': "1",
        'row': "even|odd",
    }
    """
    pattern = re.compile('\d')
    indexes = pattern.findall(interface)
    module = int(indexes[0])
    int_index = int(indexes[-1])
    # identifies module
    if module == 0:
        module = 1
    # identifies where the interface sits on module rows
    if int_index % 2 == 0:
        row = 'even'
    else:
        row = 'odd'
    result = {
        'module': str(module),
        'row': row,
    }
    return result
