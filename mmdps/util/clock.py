"""Clock and time related utils.

"""

import datetime
from datetime import date

def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))
    
def now():
    """Time string represents now().
    
    No : in the string, can be used in filename.
    The iso time string cannot be used in filename.
    """
    return datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S.%f')

def isofmt():
    """ISO time fmt."""
    return '%Y-%m-%dT%H:%M:%S'

def simplefmt():
    """Simple time fmt."""
    return '%Y%m%d'

def iso_to_time(isostr):
    """ISO time string to time object."""
    return datetime.datetime.strptime(isostr, isofmt())

def time_to_iso(t):
    """Time object to iso time string."""
    return datetime.datetime.strftime(t, isofmt())

def iso_to_simple(isostr):
    """ISO time string to simple time string."""
    t = iso_to_time(isostr)
    return datetime.datetime.strftime(t, simplefmt())

def simple_to_time(simplestr):
    """Simple time string to time object."""
    return datetime.datetime.strptime(simplestr, simplefmt())
