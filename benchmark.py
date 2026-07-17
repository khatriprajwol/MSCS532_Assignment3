"""
Empirical benchmarks for Assignment 3.

Part 1: Randomized vs Deterministic Quicksort on four input distributions
        (random, sorted, reverse-sorted, repeated elements) at several sizes.
Part 2: Average insert/search/delete time in the hash table at different
        load factors, with resizing turned off so the load factor holds still.

Times are wall-clock, averaged over several trials, reported in ms.
"""

import random
import sys
import time

from randomized_quicksort import randomized_quicksort, deterministic_quicksort
from hash_table import HashTable

TRIALS = 5
SIZES = [1000, 2000, 4000, 8000, 16000]


def make_input(kind, n):
    if kind == "random":
        return [random.randint(0, n) for _ in range(n)]
    if kind == "sorted":
        return list(range(n))
    if kind == "reverse":
        return list(range(n, 0, -1))
    if kind == "repeated":
        return [random.randint(0, 9) for _ in range(n)]
    raise ValueError(kind)


def time_sort(sort_fn, data):
    arr = list(data)
    start = time.perf_counter()
    sort_fn(arr)
    return (time.perf_counter() - start) * 1000.0


def run_quicksort_benchmarks():
    print("=" * 72)
    print("Part 1: Randomized vs Deterministic Quicksort (times in ms)")
    print("=" * 72)
    results = {}
    for kind in ["random", "sorted", "reverse", "repeated"]:
        print(f"\nInput distribution: {kind}")
        print(f"{'n':>8} {'randomized':>12} {'deterministic':>14} {'ratio':>8}")
        for n in SIZES:
            r_total = d_total = 0.0
            for _ in range(TRIALS):
                data = make_input(kind, n)
                r_total += time_sort(randomized_quicksort, data)
                d_total += time_sort(deterministic_quicksort, data)
            r_avg = r_total / TRIALS
            d_avg = d_total / TRIALS
            ratio = d_avg / r_avg if r_avg > 0 else float("inf")
            results[(kind, n)] = (r_avg, d_avg)
            print(f"{n:>8} {r_avg:>12.3f} {d_avg:>14.3f} {ratio:>8.2f}")
    return results


def run_hash_benchmarks():
    print()
    print("=" * 72)
    print("Part 2: Hash table ops vs load factor (avg microseconds per op)")
    print("=" * 72)
    n_ops = 20000
    print(f"\n{'load':>6} {'slots':>8} {'insert':>10} {'search':>10} "
          f"{'delete':>10} {'max chain':>10}")
    for load in [0.25, 0.5, 0.75, 1.0, 2.0, 4.0]:
        slots = int(n_ops / load)
        # Huge max_load_factor disables resizing so the target load holds.
        t = HashTable(initial_slots=slots, max_load_factor=10 ** 9)

        keys = [f"key{i}" for i in range(n_ops)]

        start = time.perf_counter()
        for i, k in enumerate(keys):
            t.insert(k, i)
        insert_us = (time.perf_counter() - start) / n_ops * 1e6

        probe = random.sample(keys, 5000)
        start = time.perf_counter()
        for k in probe:
            t.search(k)
        search_us = (time.perf_counter() - start) / len(probe) * 1e6

        start = time.perf_counter()
        for k in probe:
            t.delete(k)
        delete_us = (time.perf_counter() - start) / len(probe) * 1e6

        print(f"{load:>6.2f} {slots:>8} {insert_us:>10.3f} {search_us:>10.3f} "
              f"{delete_us:>10.3f} {max(t.chain_lengths()):>10}")


if __name__ == "__main__":
    sys.setrecursionlimit(50000)
    random.seed(42)
    run_quicksort_benchmarks()
    run_hash_benchmarks()
