#!/bin/bash

input_num=$1

if [ $# -lt 1 ]
then
    echo "Supply input number."
    exit 1
fi

str="$(cat modified_outputs/input$input_num.txt)"
python2.7 driver.py $str