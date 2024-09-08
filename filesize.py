import sys
from collections import deque


def deep_getsizeof(o, ids=None):
    if ids is None:
        ids = set()

    d = sys.getsizeof
    if id(o) in ids:
        return 0

    ids.add(id(o))
    size = d(o)
    if isinstance(o, (str, bytes, int, float, complex, bool, type(None))):
        pass  # simple data types
    elif isinstance(o, (tuple, list, deque, set, frozenset)):
        size += sum(deep_getsizeof(item, ids) for item in o)
    elif isinstance(o, dict):
        size += sum(deep_getsizeof(k, ids) + deep_getsizeof(v, ids) for k, v in o.items())
    elif hasattr(o, '__dict__'):
        size += deep_getsizeof(o.__dict__, ids)
    elif hasattr(o, '__iter__') and not isinstance(o, (str, bytes)):
        size += sum(deep_getsizeof(i, ids) for i in o)

    return size

        
        
        
        
            
            