#!/bin/bash
echo "Available reports:"
echo 

count="0"
for entry in "reports/zipped"/*
do
  if [ -d "$entry" ]; then
    echo "$count: $entry"
    ((count=count+1))
  fi
done

echo
echo "Select 0-$count to combine files [default: 0]"
echo -n "Selection: "
read selection
echo

count=0
for entry in "reports/zipped"/*
do
    if [ -d "$entry" ]; then
        if [ "$count" == "$selection" ];
        then 
            report="$entry"
        fi
        ((count=count+1))
    fi
done

count=0
touch "Evaluation.csv"
echo "Name, Succ, Fail, Send Rate (TPS), Max Latency (s), Min Latency (s), Avg Latency (s), Throughput (TPS)" > Evaluation.csv
for entry in "$report"/*
do
    echo >> Evaluation.csv 
    echo "Benchmark $count" >> Evaluation.csv
    awk '/Summary of performance metrics/,/\/table/' $entry | grep "<td>.*<\/td>" | while read -r line ; do
        newline=$(echo $line | sed 's/<td>//g' | sed 's/<\/td>/,/g' | sed 's/.$//g')
        echo $newline >> Evaluation.csv
    done 
    ((count=count+1))
done