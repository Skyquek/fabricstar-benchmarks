# /bin/bash

echo "Make sure you have a ssh-agent running!"
echo

iplist="ip-list.txt"

while IFS= read -r line 
do
    echo "$line"
    dirs=$(ssh "ubuntu@$line" -f "ls" | grep "fabricstar-benchmarks")

    if [ "$dirs" == "" ]; then 
        ssh "ubuntu@$line" -f "rm -rf fabricstar-benchmarks; git clone https://github.com/eggersn/fabricstar-benchmarks"
    else
        ssh "ubuntu@$line" -f "cd fabricstar-benchmarks; git pull origin master"
    fi

done < "$iplist"
