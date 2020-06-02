#!/bin/bash

if [ $# -lt 1 ]
then
    n=1
else
    n=$1
fi

directory_path="win_rates"
mkdir -p $directory_path

current_time=$(date "+%Y.%m.%d-%H.%M.%S")
output_file_path="$directory_path/$current_time.txt"
touch $output_file_path

for (( i=0; i<n; i++))
do
    echo "Testing iteration $(($i+1))..."
    output=$(python pacman.py -p PacmanQAgent -x 2000 -n 2010 -l smallGrid)
    echo "$output" | grep "Win Rate" >> $output_file_path
done