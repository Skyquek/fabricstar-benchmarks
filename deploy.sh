# /bin/bash

function deploy {
    BENCHMARK=$1
    docker network create --attachable -d overlay fabricstar

    kafkaImage="hyperledger/fabric-kafka"
    ordererImage="hyperledger/fabric-orderer:1.4.8"
    peerImage="hyperledger/fabric-peer:1.4.8"

    if [ "$choice" == "1" ]; then 
        kafkaImage="fabric_star/kafka"
        ordererImage="fabric_star/fabric-orderer:1.4.8"
        peerImage="fabric_star/fabric-peer:1.4.8"
    fi

    if [ "$prometheus" == "y" ]; then 
        echo
        echo "Deploying Prometheus & other Tools..."
        echo

        docker stack deploy --compose-file="network/docker/docker-compose-prometheus.yaml" fabricstar

        sleep 2s
    fi 

    echo
    echo "Deploying Zookeepers..."
    echo

    docker stack deploy --compose-file="network/docker/swarms/docker-compose-zk.yaml" fabricstar

    sleep 2s

    echo
    echo "Deploying Kafka Brokers..."
    echo

    env KAFKAIMAGE="${kafkaImage}" docker stack deploy --compose-file="network/docker/swarms/docker-compose-kafka.yaml" fabricstar

    sleep 2s

    echo
    echo "Deploying CAs..."
    echo

    docker stack deploy --compose-file="network/docker/swarms/orgs/docker-compose-ca.yaml" fabricstar

    sleep 2s

    echo
    echo "Deploying Orderers..."
    echo

    env ORDERERIMAGE="${ordererImage}" docker stack deploy --compose-file="network/docker/swarms/docker-compose-orderer.yaml" fabricstar

    sleep 2s

    echo
    echo "Deploying Org1..."
    echo

    env PEERIMAGE="${peerImage}" docker stack deploy --compose-file="network/docker/swarms/orgs/docker-compose-org1.yaml" fabricstar

    sleep 2s

    echo
    echo "Deploying Org2..."
    echo

    env PEERIMAGE="${peerImage}" docker stack deploy --compose-file="network/docker/swarms/orgs/docker-compose-org2.yaml" fabricstar

    echo
    echo "Deploying Caliper."
    echo

    env BENCHMARK="${BENCHMARK}" docker stack deploy --compose-file="network/docker/swarms/docker-compose-caliper.yaml" fabricstar
}


echo "Choose an Option [0: Hyperledger Fabric, 1: Fabric-Star] (default 0)"
read choice

echo "Do you want to enable Prometheus? (y, n, default=n): "
read prometheus 

echo "Creating new Network (name: fabricstar)"
echo

echo "Select a Benchmark [default 0]:"
echo "Use , to seperate multiple selections"
echo 

count=0
dir="default"

if [ "$prometheus" == "y" ]; then
    dir="prometheus"
fi

for entry in "benchmarks/${dir}"/*
do
  echo "$count: $entry"
  ((count=count+1))
done

echo

read selection  
selection=$(echo $selection | sed "s/ //")

benchmarks=(`echo $selection | tr ',' ' '`)

for benchmark in "${benchmarks[@]}"
do 
    count=0
    for entry in "benchmarks/${dir}"/*
    do
        if [ "$count" == "$benchmark" ];
        then 
            BENCHMARK="$entry"
        fi
        ((count=count+1))
    done
    
    echo 
    echo "Running $BENCHMARK..."
    deploy $BENCHMARK
    

    echo 
    echo "Sleeping till benchmark is complete..."
    echo 

    replica=""
    while [ "$replica" == "" ]
    do
        sleep 30s 
        replica=$(docker service ls | grep "fabricstar_caliper" | grep "0/1")
    done
    ./shutdown.sh

    reportid=$(ls reports/local | wc -l )
    mv "report.html" "reports/local/$reportid.html"
    rm caliper.log

    sleep 10s
done
