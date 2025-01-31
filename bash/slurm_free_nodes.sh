#!/bin/bash

# Loop through each unique node that has GPUs
while IFS= read -r node; do
  # Fetch the detailed information for each node
  node_info=$(scontrol show node "$node")

  # Extract relevant information
  node_name=$(echo "$node_info" | grep -oP "(?<=NodeName=)\S+")
  total_cpus=$(echo "$node_info" | grep -oP "(?<=CPUTot=)\S+")
  alloc_cpus=$(echo "$node_info" | grep -oP "(?<=CPUAlloc=)\S+" || echo "0")
  total_memory=$(echo "$node_info" | grep -oP "(?<=RealMemory=)\S+")
  alloc_memory=$(echo "$node_info" | grep -oP "(?<=AllocMem=)\S+" || echo "0")

  # Calculate free memory and convert memory from MB to GB
  free_memory=$((total_memory - alloc_memory))
  free_memory_gb=$(echo "scale=2; $free_memory/1024" | bc)
  total_memory_gb=$(echo "scale=2; $total_memory/1024" | bc)

  total_gpus=$(echo "$node_info" | grep "Gres=" | grep -oP "gpu:[^:]+:\K[0-9]+")
  alloc_gpus=$(echo "$node_info" | grep "AllocTRES=" | grep -oP "gres/gpu=\K[0-9]+" || echo "0")
  gpu_type=$(echo "$node_info" | grep -oP "(?<=AvailableFeatures=)\S+")
  users=$(squeue --nodes=$node_name --noheader --format="%u" | sort | uniq | paste -sd, -)

  # Calculate available resources
  free_cpus=$((total_cpus - alloc_cpus))
  free_gpus=$((total_gpus - alloc_gpus))

  # Print the information with memory in GB
  echo "$node_name available resources: $free_gpus/$total_gpus GPUs, $free_cpus/$total_cpus CPUs, ${free_memory_gb}GB/${total_memory_gb}GB memory, $gpu_type, users:$users"
done < <(sinfo -N -o "%N %G" --noheader | grep "gpu:" | awk '{print $1}' | sort -u)
