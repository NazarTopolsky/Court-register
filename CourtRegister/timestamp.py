from datetime import datetime
from re import findall

def __timestamp__(_datetime):
    if _datetime is not None and _datetime != '' and not isinstance(_datetime, float):
        d = [int(x) for x in findall(r'\d+', _datetime)]
        return datetime(d[2], d[1], d[0], 0, 0, 0).timestamp()
    else:
        return _datetime

def __timestamp__auld(_datetime):
    if _datetime is not None and _datetime != '' and not isinstance(_datetime, float):
        d = [int(x) for x in _datetime.split('.')]
        return datetime(d[2], d[1], d[0], 0, 0, 0).timestamp()
    else:
        return _datetime

print([int(x) for x in findall(r'\d+', '12.02.2004')])
print(str(__timestamp__('12/02/2004')))
print(__timestamp__auld('12/02/2004'))
