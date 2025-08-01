#!/bin/bash

# Define the arrays
references=("Allen08")
abundances=("Solar")
densities=("1")
mag_fields=("1" "2" "4")

# Loop over the combinations
for r in "${references[@]}"; do
    for a in "${abundances[@]}"; do
        for d in "${densities[@]}"; do
            for m in "${mag_fields[@]}"; do
                filename="${r}_${a}_${d}_${m}_original.txt"
                echo "$filename"
                python 3mdbs_data_processing.py "$filename"
            done
        done
    done
done