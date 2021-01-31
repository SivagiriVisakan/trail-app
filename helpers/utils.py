"""
This module will hold some commonly used funtions that are used
in multiple places in the project
"""

import datetime
from typing import Dict, Iterable, Union


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


def parse_date_from_timestamp(timestamp: str) -> Union[None, datetime.datetime]:
    '''
        Helper function to parse the date  from `timestamp` and retun a approprite date
        It adds one day to the timestamp.
        This is to get the date we actually desire.

        Returns None if timestamp is not valid

    '''
    if not timestamp:
        return None
    try:
        timestamp = float(timestamp)
    except ValueError as e:
        return None

    time = datetime.datetime.utcfromtimestamp(timestamp)

    # This one is added to keep the date uniform.
    # If this is not added, then the timestamp from the client doesn't correspond with the date we 
    # want it to be.

    time += datetime.timedelta(days=1)
    return time



def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
