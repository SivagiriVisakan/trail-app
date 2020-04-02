"""
This module will hold some commonly used funtions that are used
in multiple places in the project
"""

from typing import Dict, Iterable


def check_missing_keys(dictionary: Dict, keys: Iterable):
    '''
    An utility function to check if the specified keys are present
    in the dictionary

    Args:
        dictionary (Dict): The dictionary in which the keys are to be checked
        keys (Iterable): The keys to be checked

    Returns:
        A list of missing keys or an empty list if every thing is present
    '''
    keys = set(keys)
    missing = keys - dictionary.keys()
    if missing:
        return missing
    return []
