#!/bin/bash
set -eo pipefail

CONFIG="$${1:?Expected a routing YAML file}"
[[ -r "$$CONFIG" ]]
: "$${SLURM_PROCID:?Must run through srun}"
module --force purge
module load intel/2024.2
module load intel-oneapi/2024.2
module load hdf5/oneapi-2024.2/1.14.4
module load netcdf/oneapi-2024.2/hdf5-1.14.4/4.9.2
module load intel-mpi/oneapi/2021.13
export OMP_STACKSIZE=512M

# The combined module loads CUDA unconditionally, which fails on CPU nodes.
ROUTING_BIN=/home/GVILLARI/software/Tiger_HLM_Routing_CPU/$routing_version/bin
if [ "$$SLURM_PROCID" -eq 0 ]; then
    module load cudatoolkit/12.9
    export OMP_NUM_THREADS=$gpu_cpus
    binary=$$ROUTING_BIN/routing_gpu
else
    export OMP_NUM_THREADS=$cpus
    binary=$$ROUTING_BIN/routing_cpu
fi
[[ -x "$$binary" ]]
echo "rank $$SLURM_PROCID: $$(hostname), threads=$$OMP_NUM_THREADS, binary=$$binary"
exec "$$binary" "$$CONFIG"
