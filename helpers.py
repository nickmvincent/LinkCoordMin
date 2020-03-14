from urllib.parse import urlparse
from collections import defaultdict

def extract(x):
    domain = urlparse(x.href).netloc
    return domain

infinite_defaultdict = lambda: defaultdict(infinite_defaultdict)
def recurse_print_infinitedict(d, prefix=''):
    if type(d) != defaultdict:
        print(prefix, d)
        return
    for k, v in d.items():
        print(prefix, k)
        recurse_print_infinitedict(v, prefix + ' ')

def is_mobile(device_name):
    """ is this device_name a mobile device"""
    return device_name in [
        'iPhone X', 'Galaxy S5',
    ]