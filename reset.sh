# /bin/bash

echo "Make sure you have a ssh-agent running!"
echo

iplist="ip-list.txt"

while IFS= read -r line 
do
    echo "$line"

    ssh "ubuntu@$line" -f "rm -rf caliper-benchmarks; docker container rm \$(docker ps -aq); docker volume rm \$(docker volume ls -q)"

done < "$iplist"