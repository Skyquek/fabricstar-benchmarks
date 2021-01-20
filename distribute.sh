# /bin/bash

echo "Make sure you have a ssh-agent running!"
echo

iplist="ip-list.txt"

while IFS= read -r line 
do
    echo "$line"
    ssh "ubuntu@$line" -f "rm -rf caliper-benchmarks; git clone https://github.com/eggersn/fabricstar-benchmarks"
done < "$iplist"
