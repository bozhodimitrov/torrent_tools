from collections import OrderedDict


class LRU(OrderedDict):
    def __init__(self, maxsize=128, *args, **kwds):
        self.maxsize = maxsize
        super().__init__(*args, **kwds)

    def __contains__(self, key):
        found = super().__contains__(key)
        if found:
            self.move_to_end(key)
        else:
            self[key] = None
        return found

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self.move_to_end(key)
        return value

    def __setitem__(self, key, value):
        if super().__contains__(key):
            self.move_to_end(key)
        else:
            super().__setitem__(key, value)
        if len(self) > self.maxsize:
            oldest = next(iter(self))
            del self[oldest]
