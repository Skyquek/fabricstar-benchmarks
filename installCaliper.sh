# /bin/bash

echo "Make sure you have a ssh-agent running!"
echo

iplist="ip-list.txt"

while IFS= read -r line 
do
    ssh "ubuntu@$line" -f "cd caliper-benchmarks; docker build -t fabric_star/caliper ."

done < "$iplist"