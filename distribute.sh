# /bin/bash

echo "Make sure you have a ssh-agent running!"
echo

iplist="ip-list.txt"

while IFS= read -r line 
do
    echo "$line"
    dirs=$(ssh "ubuntu@$line" -f "ls" | grep "caliper-benchmarks")

    if [ "$dirs" == "" ]; then 
        ssh "ubuntu@$line" -f "rm -rf caliper-benchmarks; git clone https://github.com/eggersn/fabricstar-benchmarks; mv fabricstar-benchmarks caliper-benchmarks"
    else
        ssh "ubuntu@$line" -f "cd caliper-benchmarks; git pull origin master"
    fi

done < "$iplist"
