# Assignment 3: Understanding Algorithm Efficiency and Scalability

## Part 1: Randomized Quicksort

### Implementation notes

Both sorts live in `randomized_quicksort.py`. They share the exact same partition routine, so the only difference between them is how the pivot is picked. The randomized version swaps a uniformly random element into the pivot position first. The deterministic version just takes the first element. Keeping everything else identical means the benchmarks measure the effect of pivot choice and nothing else.

The partition is a three-way (Dutch national flag) partition. It splits the subarray into elements less than, equal to, and greater than the pivot. All elements equal to the pivot are done in one pass, which is what keeps arrays full of repeated values from turning quadratic. The recursion always goes into the smaller half and loops on the larger half, so the stack depth stays O(log n) even when the splits are terrible. That let me benchmark the deterministic worst case without hitting Python's recursion limit.

Edge cases are covered by the self-test in the file: empty arrays, one element, sorted, reverse-sorted, and heavy duplicates.

### Average-case analysis: why O(n log n)

The cost of quicksort is dominated by comparisons, so I count expected comparisons using indicator random variables, the same style of argument CLRS uses.

Let z_1 < z_2 < ... < z_n be the elements in sorted order. Define the indicator variable

X_ij = 1 if z_i and z_j are ever compared, 0 otherwise.

Two elements are compared only when one of them is the pivot of a subarray that contains both. The key observation is this. Look at the set Z_ij = {z_i, z_i+1, ..., z_j}. All of these elements travel together until the first time one of them is chosen as a pivot. If that first pivot is z_i or z_j, the two get compared. If it is any of the j - i - 1 elements strictly between them, z_i and z_j land on opposite sides of the pivot and are never compared afterward.

Because the pivot is chosen uniformly at random, each element of Z_ij is equally likely to be the first one picked from that set. So

Pr[X_ij = 1] = 2 / (j - i + 1).

The expected total number of comparisons is

E[X] = sum over i < j of 2 / (j - i + 1).

Substituting k = j - i:

E[X] = sum_{i=1}^{n-1} sum_{k=1}^{n-i} 2 / (k + 1) < sum_{i=1}^{n-1} 2 * H_n = O(n log n),

where H_n is the n-th harmonic number, which is about ln n. So the expected running time of Randomized Quicksort is O(n log n) on every input. The randomness is in the algorithm, not the data, so no adversary can hand it a bad array in advance.

The recurrence view says the same thing. The random pivot lands in the middle half of the subarray with probability 1/2, which gives splits no worse than 1/4 to 3/4. That yields the recurrence T(n) <= T(n/4) + T(3n/4) + O(n) in expectation, and that recursion tree has O(log n) levels with O(n) work per level.

The deterministic first-element pivot has the same O(n log n) behavior on random data but no such guarantee overall. On a sorted array the first element is the minimum, every partition splits n elements into 0 and n - 1, and the recurrence becomes T(n) = T(n - 1) + O(n) = O(n^2).

### Empirical comparison

I timed both sorts on four distributions at five sizes, averaging five trials each, on a MacBook Pro running Python 3.11. Full numbers are in `results.txt`. Times are milliseconds.

| Input | n = 4,000 (rand / det) | n = 16,000 (rand / det) | Ratio at 16,000 |
|---|---|---|---|
| Random | 2.2 / 1.9 | 10.1 / 8.4 | 0.84 |
| Sorted | 2.3 / 7.5 | 10.5 / 56.8 | 5.4 |
| Reverse-sorted | 2.3 / 221.2 | 10.6 / 3,596.1 | 339 |
| Repeated (10 values) | 0.4 / 0.4 | 1.7 / 1.7 | 1.0 |

Three things stand out.

**The randomized sort is flat across all four distributions.** At n = 16,000 it runs in 10 to 11 ms on random, sorted, and reverse-sorted input. Doubling n roughly doubles the time plus a bit, which matches n log n growth. This is the theory showing up directly: expected O(n log n) regardless of input order.

**The deterministic sort collapses on adversarial order.** On reverse-sorted input it shows clean quadratic growth. Going from n = 8,000 to n = 16,000 (2x) multiplied its time by 4.03x, almost exactly the 4x that Θ(n^2) predicts, and it ended up 339 times slower than the randomized version. On sorted input it is also clearly superlinear, though milder than pure n^2. That gap is a real discrepancy between theory and measurement, and it has a concrete cause: the three-way partition swaps greater-than elements toward the back of the subarray, which partially scrambles a sorted array after the first pass. The scrambling breaks the perfect worst case, but the splits are still unbalanced enough to be far worse than O(n log n). Reverse-sorted input does not get that accidental help, so it stays quadratic.

**On random and repeated input the deterministic version is slightly faster.** On random data the first element is as good a pivot as any, and skipping the random number generator call saves a little constant-factor work. That is the price of randomization: about 16 percent on friendly input, in exchange for never being 339x slower on hostile input. The repeated-elements case is fast for both because the three-way partition removes all copies of the pivot at once. With only 10 distinct values, the recursion bottoms out after about 10 partitions no matter how the pivot is chosen. A classic two-way partition would have gone quadratic here, which is why the partition scheme matters as much as the pivot rule for this distribution.

## Part 2: Hashing with Chaining

### Implementation notes

The table in `hash_table.py` resolves collisions by chaining. Each slot holds a singly linked list built from a small node class, so insert pushes onto the head of a chain, and search and delete walk the chain with an explicit predecessor pointer. Insert on an existing key updates the value in place.

The hash function is drawn from the universal family

h(k) = ((a * k + b) mod p) mod m

with p = 2^61 - 1 (a Mersenne prime) and a, b drawn at random when the table is created, with 1 <= a < p. Universality means that for any two distinct keys, the probability they collide is at most 1/m over the random choice of a and b. Like the random pivot in Part 1, this moves the randomness into the algorithm so no fixed set of keys is bad for every run.

### Expected cost of the operations

Let n be the number of stored elements and m the number of slots. The load factor is α = n/m. Under simple uniform hashing, each key is equally likely to land in any slot, so the expected chain length is α.

- **Insert** computes the slot in O(1) and walks the chain to check whether the key already exists, so it costs O(1 + α) expected.
- **Unsuccessful search** walks an entire chain of expected length α: Θ(1 + α) expected.
- **Successful search** examines, in expectation, one plus half the elements inserted into the same chain after the target, which also works out to Θ(1 + α).
- **Delete** is a search plus an O(1) pointer splice: Θ(1 + α) expected.

The takeaway is that everything is O(1 + α). If α is held at or below a constant, all three operations are expected O(1). If the table never grows, α = n/m grows linearly with n and the operations degrade to O(n).

### Load factor and resizing

The way to keep α constant is dynamic resizing. My table doubles its slot count whenever α passes 0.75, rehashing every element with freshly drawn hash parameters. A single resize costs Θ(n), but doubling means a resize happens only after the element count itself has doubled, so the amortized cost per insert stays O(1). Doubling also keeps the total space linear in n.

Other standard tactics for keeping collisions down: pick the hash function from a universal family rather than hand-rolling one, keep the threshold well below the point where chains get long (0.75 is a common choice), and optionally shrink the table when heavy deletion drives α very low so space is not wasted. Prime-sized tables help weak hash functions, but with a universal family the mod-m step is already safe.

### Empirical check

I froze the table at fixed load factors (resizing disabled) and timed 20,000 inserts plus 5,000 random searches and deletes at each. Times are average microseconds per operation.

| Load factor α | Insert | Search | Delete | Longest chain |
|---|---|---|---|---|
| 0.25 | 0.40 | 0.22 | 0.26 | 4 |
| 0.75 | 0.36 | 0.22 | 0.25 | 5 |
| 2.00 | 0.43 | 0.23 | 0.28 | 8 |
| 4.00 | 0.41 | 0.25 | 0.30 | 10 |

Per-operation cost is essentially flat from α = 0.25 to α = 4. That looks surprising against the Θ(1 + α) prediction, but it is consistent with it: at these load factors the "1" dominates the "α". The expected chain walk grows from about 0.25 to about 4 comparisons, and a few extra pointer hops are cheap next to the fixed cost of hashing the key in Python. The longest chain tells the truer story. It grows steadily with α (4 at α = 0.25, 10 at α = 4), and that growth is what eventually hurts. Push α to hundreds and every operation becomes a long list scan, which is the O(n) degradation the analysis predicts. Keeping α bounded by a small constant through resizing is what locks in expected O(1) behavior at every scale, not just the sizes I happened to test.

## Closing observations

Both parts land on the same design idea. Worst cases are triggered by structure in the input, and injecting randomness into the algorithm (a random pivot, a randomly drawn hash function) dissolves that structure. Randomized Quicksort turns a Θ(n^2) worst case into expected O(n log n) on all inputs, and universal hashing turns adversarial key sets into expected O(1) operations. The measurements match: the randomized sort never varied by more than a few percent across distributions, while its deterministic twin swung by a factor of 339.
