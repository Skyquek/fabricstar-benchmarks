# /bin/bash

BENCHMARK="fixed-assets.yaml"

echo "Choose an Option [0: Hyperledger Fabric, 1: Fabric-Star] (default 0)"
read choice

echo "Do you want to enable Prometheus? (y, n, default=n): "
read prometheus 

echo "Creating new Network (name: fabricstar)"
echo

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
    BENCHMARK="fixed-assets-prometheus.yaml"

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