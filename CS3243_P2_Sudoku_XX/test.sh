#!/bin/bash

input_num=$1

if [ $# -lt 1 ]
then
    echo "Supply an input number."
    exit 1
elif (( $input_num < 1 ||  $input_num > 4 ))
then
    echo "Input number must be between 1-4 (inclusive)."
    exit 1
else
    directory_path="my_outputs/"
    mkdir -p $directory_path

    input_file_path="public_tests_P2_Sudoku/input_$input_num.txt"
    output_file_path="$directory_path/output_$input_num.txt"
fi

# echo $input_file_path
# echo $output_file_path

if [[ -f $output_file_path ]]; then
    rm $output_file_path
    touch $output_file_path
fi

# echo $input_file_path
# echo $output_file_path

python2.7 CS3243_P2_Sudoku_01.py $input_file_path $output_file_path