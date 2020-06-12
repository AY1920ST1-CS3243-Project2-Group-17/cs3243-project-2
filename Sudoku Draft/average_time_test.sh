#!/bin/bash
TIMEFORMAT=%R

if [ $# -lt 1 ]
then
    n=20
else
    n=$1
fi

echo "Average Timings for $n iterations."
printf "\n"

for (( i = 1 ; i <= 4; i++ ))
do
    sum_time=0
    for (( j = 1; j <= $n; j++))
    do
        mytime="$(time (./test.sh $i) 2>&1 1>/dev/null )"
        # echo "Input $i: ${mytime}s."
        time_as_float=$(echo $mytime | bc)
        sum_time=$(echo $sum_time + $time_as_float | bc)
    done
    echo "Total for Input$i: ${sum_time}s."
    out=""
    average=$(printf $(echo $sum_time / $n | bc -l))
    out+=$average
    out=$(echo $out | cut -c -5)
    echo "Average for Input$i: ${out}s" 
    printf "\n"
    # echo "Average Input $i: $((sum/3)) s."
done

unset TIMEFORMAT
