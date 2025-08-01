#!/bin/bash

# Define the arrays
references=("Allen08")
abundances=("Allen2008_Dopita2005" "Allen2008_Solar" "Allen2008_TwiceSolar" "Allen2008_LMC" "Allen2008_SMC")

# Create the master directory
mkdir -p 3mdbs_data
cd 3mdbs_data

# Loop over all references/abundances
for r in "${references[@]}"; do
    mkdir -p "$r"
    cd "$r"  # Go into references directory
    for a in "${abundances[@]}"; do
        mkdir -p "$a"
    done
done
cd ../..  # Nagivate back to PTERO directory

# Execute data scraping
python 3mdbs_data_scraping.py