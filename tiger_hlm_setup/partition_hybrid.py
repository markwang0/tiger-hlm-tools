#!/usr/bin/env python3
"""
Hybrid GPU+CPU partition:
  rank 0      = all level-0 links (GPU node)
  ranks 1..N  = levels 1+ split evenly (CPU nodes)

Usage:
  python partition_hybrid.py <routing_table.csv> <n_cpu_ranks> <output.part>
"""
import struct, sys
import numpy as np
import pandas as pd

if len(sys.argv) < 4:
    print(f"Usage: {sys.argv[0]} <routing_table.csv> <n_cpu_ranks> <output.part>")
    sys.exit(1)

routing_table = sys.argv[1]
n_cpu_ranks   = int(sys.argv[2])
output_file   = sys.argv[3]

df = pd.read_csv(routing_table)
n_links = len(df)
levels  = df['level'].values
n_ranks = 1 + n_cpu_ranks

# rank 0 = level 0, ranks 1..N = levels 1+ split evenly
ranks = np.zeros(n_links, dtype=np.int32)

l1_indices = np.where(levels > 0)[0]
n_l1 = len(l1_indices)

if n_cpu_ranks == 1:
    ranks[l1_indices] = 1
else:
    chunk = max(1, (n_l1 + n_cpu_ranks - 1) // n_cpu_ranks)
    for i, idx in enumerate(l1_indices):
        ranks[idx] = 1 + min(i // chunk, n_cpu_ranks - 1)

# Write HLMPART1 binary
with open(output_file, 'wb') as f:
    f.write(b'HLMPART1')
    f.write(struct.pack('<Q', n_links))
    f.write(struct.pack('<Q', n_ranks))
    f.write(ranks.tobytes())

# Summary
counts = {r: int((ranks == r).sum()) for r in range(n_ranks)}
with open(output_file + '.txt', 'w') as f:
    f.write(f"Hybrid GPU+CPU partition\n")
    f.write(f"  total: {n_links:,} links, {n_ranks} ranks (1 GPU + {n_cpu_ranks} CPU)\n")
    for r in range(n_ranks):
        label = "GPU level-0" if r == 0 else f"CPU {r}"
        f.write(f"  rank {r}: {counts[r]:>10,} links ({label})\n")

print(f"Written: {output_file}")
n0 = counts[0]
print(f"  rank 0 (GPU):  {n0:>10,} links (level 0, {100*n0/n_links:.1f}%)")
for r in range(1, n_ranks):
    print(f"  rank {r} (CPU):  {counts[r]:>10,} links ({100*counts[r]/n_links:.1f}%)")
print(f"  total:         {n_links:>10,}")
