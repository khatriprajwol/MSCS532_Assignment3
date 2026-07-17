"""
Randomized Quicksort vs Deterministic Quicksort
MSCS-532 Assignment 3, Part 1

Both sorts are written from scratch. No built-in sorting helpers are used.
The randomized version picks its pivot uniformly at random from the current
subarray. The deterministic version always uses the first element as the
pivot, which is the classic worst case trigger for sorted input.

Both versions use three-way (Dutch national flag) partitioning so that
arrays full of repeated elements do not degrade to quadratic time.
"""

import random
import sys


def randomized_quicksort(arr):
    """Sort a list in place using quicksort with a uniformly random pivot.

    Handles empty arrays, single-element arrays, sorted arrays,
    reverse-sorted arrays, and arrays with many repeated elements.
    Returns the same list for convenience.
    """
    _rqs(arr, 0, len(arr) - 1)
    return arr


def _rqs(arr, low, high):
    while low < high:
        lt, gt = _partition_three_way(arr, low, high, random_pivot=True)
        # Recurse on the smaller side first, loop on the larger side.
        # This keeps the stack depth at O(log n) even in bad cases.
        if lt - low < high - gt:
            _rqs(arr, low, lt - 1)
            low = gt + 1
        else:
            _rqs(arr, gt + 1, high)
            high = lt - 1


def deterministic_quicksort(arr):
    """Sort a list in place using quicksort with the first element as pivot.

    Kept deliberately simple so its worst-case behavior on sorted and
    reverse-sorted input shows up clearly in the benchmarks.
    """
    _dqs(arr, 0, len(arr) - 1)
    return arr


def _dqs(arr, low, high):
    while low < high:
        lt, gt = _partition_three_way(arr, low, high, random_pivot=False)
        if lt - low < high - gt:
            _dqs(arr, low, lt - 1)
            low = gt + 1
        else:
            _dqs(arr, gt + 1, high)
            high = lt - 1


def _partition_three_way(arr, low, high, random_pivot):
    """Partition arr[low..high] into three regions around a pivot value.

    After the call:
        arr[low..lt-1]  < pivot
        arr[lt..gt]     == pivot
        arr[gt+1..high] > pivot

    Returns (lt, gt). The randomized version swaps a random element into
    position low first, so both versions can share the same code path.
    """
    if random_pivot:
        r = random.randint(low, high)
        arr[low], arr[r] = arr[r], arr[low]

    pivot = arr[low]
    lt = low
    i = low + 1
    gt = high
    while i <= gt:
        if arr[i] < pivot:
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        elif arr[i] > pivot:
            arr[i], arr[gt] = arr[gt], arr[i]
            gt -= 1
        else:
            i += 1
    return lt, gt


def _self_test():
    """Quick correctness checks for the edge cases in the assignment."""
    cases = [
        [],
        [7],
        [3, 1, 2],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [2, 2, 2, 2, 2],
        [4, 1, 4, 2, 4, 3, 4],
        [random.randint(0, 100) for _ in range(1000)],
    ]
    for case in cases:
        expected = sorted(case)
        a = list(case)
        b = list(case)
        randomized_quicksort(a)
        deterministic_quicksort(b)
        assert a == expected, f"randomized failed on {case[:10]}..."
        assert b == expected, f"deterministic failed on {case[:10]}..."
    print("All correctness tests passed.")


if __name__ == "__main__":
    sys.setrecursionlimit(20000)
    _self_test()
