#!/bin/bash

# Run the qstat command and store the output in a variable
output=$(qstat -f gpu | grep "Job Id" | awk '{print $3}')

# Initialize the total number of GPUs
total_gpus=0

# Read the output line by line and extract the number of GPUs
while read -r line; do
    # Extract the job state for the current line
    state=$(qstat -f $line | grep "job_state" | awk '{print $3}')

    echo "Job $line is in state $state"

    # If state is R or B, then the job is running or begun, so add the number of GPUs to the total
    if [ "$state" == "R" ] || [ "$state" == "B" ]; then
        gpus=$(qstat -f $line | grep "Resource_List.ngpus" | awk '{print $3}')

        if [ "$state" == "B" ]; then
            # Get the number of active runs from the "array_state_count" field
            active_runs=$(qstat -f $line | grep "array_state_count" | awk '{print $4}' | awk -F: '{print $2}')

            # Multiply the number of GPUs by the number of active runs
            gpus=$((gpus * active_runs))
        fi

        echo "Job $line is using $gpus GPUs"
        total_gpus=$((total_gpus + gpus))
    fi

    echo "Total number of GPUs: $total_gpus"
done <<< "$output"

# Print the total number of GPUs
echo "Total number of GPUs: $total_gpus"