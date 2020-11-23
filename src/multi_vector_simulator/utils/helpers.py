"""
Util functions that are useful throughout the MVS

Including:
- find_valvue_by_key(): Finds value of a key in a nested dictionary.
"""


def find_value_by_key(data, target, result=None):
    """
    Finds value of a key in a nested dictionary.

    Parameters
    ----------
    data: dict
        Dict to be searched for target key

    target: str
        Key for which the value should be found in data

    result: None, value or list
        Only provided if function loops in itself

    Returns
    -------
    value if the key is only once in data
    list of values if it appears multiple times.
    """
    # check each item-value pair in the level
    for k, v in data.items():
        # if target in keys of level
        if k == target:
            if result is None:
                result = v
            elif isinstance(result, list):
                # Expands list of key finds
                result.append(v)
            else:
                # creates list for multiple key finds
                previous_result = result
                result = []
                result.append(previous_result)
                result.append(v)
        # Check next level for target
        if isinstance(v, dict):
            result = find_value_by_key(data=v, target=target, result=result)
    return result
