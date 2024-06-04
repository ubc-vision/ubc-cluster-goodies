#!/bin/bash

# Loop through each node that has GPUs
while IFS= read -r node; do
  # Fetch the detailed information for each node
  node_info=$(scontrol show node "$node")

  # Extract relevant information
  node_name=$(echo "$node_info" | grep -oP "(?<=NodeName=)\S+")
  total_cpus=$(echo "$node_info" | grep -oP "(?<=CPUTot=)\S+")
  alloc_cpus=$(echo "$node_info" | grep -oP "(?<=CPUAlloc=)\S+" || echo "0")
  free_memory=$(echo "$node_info" | grep -oP "(?<=FreeMem=)\S+")
  total_gpus=$(echo "$node_info" | grep "Gres=" | grep -oP "gpu:[^:]+:\K[0-9]+")
  alloc_gpus=$(echo "$node_info" | grep "AllocTRES=" | grep -oP "gres/gpu=\K[0-9]+" || echo "0")
  gpu_type=$(echo "$node_info" | grep -oP "(?<=AvailableFeatures=)\S+")
  users=$(squeue --nodes=$node_name --noheader --format="%u" | sort | uniq | paste -sd, -)


  # Calculate available resources
  free_cpus=$((total_cpus - alloc_cpus))
  free_gpus=$((total_gpus - alloc_gpus))

  # Print the information
  echo "$node_name available resources: $free_gpus/$total_gpus GPUs, $free_cpus/$total_cpus CPUs, ${free_memory}M memory, $gpu_type, users:$users"
done < <(sinfo -N -o "%N %G" --noheader | grep "gpu:" | awk '{print $1}')
