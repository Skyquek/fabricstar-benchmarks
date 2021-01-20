# /bin/bash

echo "Make sure you have a ssh-agent running!"
echo

iplist="ip-list.txt"
count=0
token=""

while IFS= read -r line 
do
    echo 
    echo "$line"
    echo

    if [ "$count" == "0" ]; then
        # Assuming as Caliper Node
        ssh "ubuntu@$line" -f "docker swarm leave --force; docker swarm init"
        sleep 5s
        token=$(ssh "ubuntu@$line" -f "docker swarm join-token manager | grep docker")
        echo $token
    else 
        ssh "ubuntu@$line" -f "docker swarm leave --force; $token"
    fi

    ((count=count+1))

    sleep 5s

done < "$iplist"