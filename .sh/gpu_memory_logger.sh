#!/bin/bash

'''
chmod +x gpu_memory_logger.sh
./gpu_memory_logger.sh
'''

gpu_indexes=(0 1 2 3)

function record_gpu_memory_usage() {
    gpu_index=$1
    output_file=$2

    echo "Timestamp,Memory Usage (MiB)" > "$output_file"

    while true; do
        memory_usage=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits --id="$gpu_index")
        timestamp=$(date +"%Y-%m-%d %H:%M:%S")
        echo "$timestamp,$memory_usage" >> "$output_file"
        sleep 1
    done
}

for index in ${!gpu_indexes[@]}; do
    gpu_index=${gpu_indexes[$index]}
    output_file=gpu_memory_usage_${gpu_indexes[$index]}.txt
    echo $output_file

    record_gpu_memory_usage "$gpu_index" "$output_file" &
done

wait
