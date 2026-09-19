#!/bin/bash
#SBATCH --job-name=$name
#SBATCH --account=$account
#SBATCH --time=$time
#SBATCH --dependency=singleton
#SBATCH --mail-type=begin
#SBATCH --mail-type=end
#SBATCH --mail-user=$email

#SBATCH --partition=$partition
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=$gpu_cpus
#SBATCH --gres=gpu:1
#SBATCH --mem=$gpu_mem

#SBATCH hetjob

#SBATCH --partition=$cpu_partition
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=$cpus
#SBATCH --mem=$mem

set -euo pipefail

test -f "$partition_file" || { echo "Missing routing partition: $partition_file" >&2; exit 1; }
srun --mpi=pmi2 --label --het-group=0,1 bash "$wrapper" "$yaml" > "$out" 2>&1

$remove_runoff_cmd
