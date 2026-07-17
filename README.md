# MSCS-532 Assignment 3: Algorithm Efficiency and Scalability

Randomized Quicksort and a Hash Table with Chaining, implemented from scratch in Python, with benchmarks and a written analysis.

## Files

| File | What it is |
|---|---|
| `randomized_quicksort.py` | Randomized and deterministic quicksort sharing one three-way partition |
| `hash_table.py` | Chaining hash table with universal hashing and dynamic resizing |
| `benchmark.py` | Runs all timing experiments for both parts |
| `results.txt` | Raw output from the benchmark run used in the report |
| `results.xlsx` | Benchmark results in Excel, one tab per part |
| `REPORT.md` | Theoretical analysis, empirical results, and discussion |

## How to run

Requires Python 3.10+. No external packages.

```bash
# Correctness self-tests
python3 randomized_quicksort.py
python3 hash_table.py

# Full benchmark suite (takes about a minute; the deterministic
# quicksort on reverse-sorted input is the slow part, on purpose)
python3 benchmark.py
```

## Using the hash table

```python
from hash_table import HashTable

t = HashTable()
t.insert("alice", 42)
t.search("alice")   # 42
t.delete("alice")   # raises KeyError if absent
```

## Summary of findings

- Randomized Quicksort ran in expected O(n log n) on every distribution tested. At n = 16,000 it stayed between 10 and 11 ms on random, sorted, and reverse-sorted input.
- Deterministic (first-element pivot) quicksort matched it on random data but went quadratic on reverse-sorted input: 3.6 seconds at n = 16,000, about 339x slower.
- Three-way partitioning kept arrays with heavy duplicates fast for both sorts, since all copies of the pivot are handled in one pass.
- Hash table insert, search, and delete all cost Θ(1 + α) expected, where α is the load factor. Measured per-op times stayed under half a microsecond from α = 0.25 up to α = 4, while the longest chain grew with α as predicted.
- Doubling the table when α passes 0.75 keeps α bounded, so all operations stay expected O(1) with O(1) amortized resize cost per insert.
