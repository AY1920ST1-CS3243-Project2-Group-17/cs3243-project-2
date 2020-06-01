#!/bin/bash
TIMEFORMAT=%R


for (( i = 1 ; i <= 4; i++ ))
do
    mytime="$(time (./test.sh $i) 2>&1 1>/dev/null )"
    echo "Input $i: $mytime s."
done

unset TIMEFORMAT
