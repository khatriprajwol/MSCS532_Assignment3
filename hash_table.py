"""
Hash Table with Chaining
MSCS-532 Assignment 3, Part 2

The table resolves collisions by chaining. Each slot holds a singly linked
list built from scratch with a small _Node class, not a Python list of
tuples, so the chaining mechanics are explicit.

The hash function comes from the universal family
    h(k) = ((a * k + b) mod p) mod m
where p is a prime larger than any key hash, and a, b are random with
1 <= a < p and 0 <= b < p. Picking a and b at random when the table is
built means no fixed input can force a bad collision pattern on every run.

The table resizes itself. When the load factor n/m goes above 0.75 the
slot count doubles, and every element is rehashed with fresh random
parameters. That keeps the expected chain length constant, so insert,
search, and delete stay O(1) on average.
"""

import random


class _Node:
    """One link in a chain: a key, its value, and the next node."""

    __slots__ = ("key", "value", "next")

    def __init__(self, key, value, nxt):
        self.key = key
        self.value = value
        self.next = nxt


class HashTable:
    # A large prime, bigger than any 61-bit key hash we will produce.
    _P = (1 << 61) - 1  # 2^61 - 1, a Mersenne prime

    def __init__(self, initial_slots=8, max_load_factor=0.75):
        self._m = initial_slots
        self._n = 0
        self._max_load = max_load_factor
        self._slots = [None] * self._m
        self._pick_hash_params()

    def _pick_hash_params(self):
        """Draw fresh (a, b) for the universal hash function."""
        self._a = random.randint(1, self._P - 1)
        self._b = random.randint(0, self._P - 1)

    def _key_to_int(self, key):
        """Map any hashable key to a non-negative integer below p."""
        return hash(key) % self._P

    def _hash(self, key):
        k = self._key_to_int(key)
        return ((self._a * k + self._b) % self._P) % self._m

    @property
    def load_factor(self):
        return self._n / self._m

    def __len__(self):
        return self._n

    def insert(self, key, value):
        """Add a key-value pair. If the key exists, update its value."""
        idx = self._hash(key)
        node = self._slots[idx]
        while node is not None:
            if node.key == key:
                node.value = value
                return
            node = node.next
        # Key not present: push a new node onto the front of the chain.
        self._slots[idx] = _Node(key, value, self._slots[idx])
        self._n += 1
        if self.load_factor > self._max_load:
            self._resize(self._m * 2)

    def search(self, key):
        """Return the value for key, or raise KeyError if absent."""
        node = self._slots[self._hash(key)]
        while node is not None:
            if node.key == key:
                return node.value
            node = node.next
        raise KeyError(key)

    def delete(self, key):
        """Remove a key-value pair. Raise KeyError if the key is absent."""
        idx = self._hash(key)
        node = self._slots[idx]
        prev = None
        while node is not None:
            if node.key == key:
                if prev is None:
                    self._slots[idx] = node.next
                else:
                    prev.next = node.next
                self._n -= 1
                return
            prev = node
            node = node.next
        raise KeyError(key)

    def _resize(self, new_m):
        """Grow to new_m slots and rehash everything with fresh (a, b)."""
        old_slots = self._slots
        self._m = new_m
        self._slots = [None] * new_m
        self._n = 0
        self._pick_hash_params()
        for head in old_slots:
            node = head
            while node is not None:
                self.insert(node.key, node.value)
                node = node.next

    def chain_lengths(self):
        """Length of every chain. Useful for checking hash spread."""
        lengths = []
        for head in self._slots:
            count = 0
            node = head
            while node is not None:
                count += 1
                node = node.next
            lengths.append(count)
        return lengths


def _self_test():
    t = HashTable()
    # Insert, search, update.
    for i in range(1000):
        t.insert(f"key{i}", i)
    assert len(t) == 1000
    assert t.search("key537") == 537
    t.insert("key537", -1)
    assert t.search("key537") == -1
    assert len(t) == 1000  # update, not a new entry

    # Delete and confirm absence.
    t.delete("key537")
    assert len(t) == 999
    try:
        t.search("key537")
        raise AssertionError("search should have raised KeyError")
    except KeyError:
        pass

    # Load factor stays bounded after resizing.
    assert t.load_factor <= 0.75, t.load_factor
    print("All correctness tests passed.")
    print(f"Slots: {t._m}, elements: {len(t)}, "
          f"load factor: {t.load_factor:.3f}, "
          f"longest chain: {max(t.chain_lengths())}")


if __name__ == "__main__":
    _self_test()
