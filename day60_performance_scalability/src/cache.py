from collections import OrderedDict
from time import monotonic

class TTLCache:
    """Bounded TTL/LRU cache for safe, deterministic derived values."""
    def __init__(self, max_entries=128, ttl_seconds=60):
        if max_entries < 1 or ttl_seconds <= 0:
            raise ValueError("max_entries and ttl_seconds must be positive")
        self.max_entries, self.ttl_seconds = max_entries, ttl_seconds
        self.data = OrderedDict()
        self.hits = self.misses = 0
    def get(self, key):
        entry = self.data.get(key)
        if entry is None or entry[1] <= monotonic():
            self.data.pop(key, None); self.misses += 1
            return None
        self.data.move_to_end(key); self.hits += 1
        return entry[0]
    def set(self, key, value):
        self.data[key] = (value, monotonic() + self.ttl_seconds)
        self.data.move_to_end(key)
        while len(self.data) > self.max_entries:
            self.data.popitem(last=False)
    @property
    def size(self): return len(self.data)
    @property
    def hit_rate(self):
        total = self.hits + self.misses
        return self.hits / total if total else 0.0
