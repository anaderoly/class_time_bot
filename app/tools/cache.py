from collections import OrderedDict


class Cache:
    def __init__(self, max_size):
        self.cache = OrderedDict()
        self.max_size = max_size

    def set(self, key, values):
        self.cache[key] = values
        self.cache.move_to_end(key)
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def get(self, key):
        return self.cache.get(key)

    def __contains__(self, key):
        return key in self.cache
