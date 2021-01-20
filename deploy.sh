# /bin/bash

BENCHMARK="fixed-assets.yaml"

echo "Do you want to enable Prometheus? (y, n, default=n): "
read prometheus 

echo "Creating new Network (name: fabricstar)"
echo

docker network create --attachable -d overlay fabricstar

if [ "$prometheus" == "y" ]; then 
    BENCHMARK="fixed-assets-prometheus.yaml"

    echo
    echo "Deploying Prometheus & other Tools..."
    echo

    docker stack deploy --compose-file=network/hyperledger/docker-compose-prometheus.yaml fabricstar

    sleep 2s
fi 

echo
echo "Deploying Zookeepers..."
echo

docker stack deploy --compose-file=network/hyperledger/swarms/docker-compose-zk.yaml fabricstar

sleep 2s

ZK0=$(docker network inspect fabricstar | grep -o "fabricstar_zookeeper0[\.a-z0-9]*")
ZK1=$(docker network inspect fabricstar | grep -o "fabricstar_zookeeper1[\.a-z0-9]*")
ZK2=$(docker network inspect fabricstar | grep -o "fabricstar_zookeeper2[\.a-z0-9]*")

export ZOO0NAME=$ZK0
export ZOO1NAME=$ZK1
export ZOO2NAME=$ZK2

sleep 2s

echo
echo "Deploying Kafka Brokers..."
echo

docker stack deploy --compose-file=network/hyperledger/swarms/docker-compose-kafka.yaml fabricstar

sleep 2s

echo
echo "Deploying CAs..."
echo

docker stack deploy --compose-file=network/hyperledger/swarms/orgs/docker-compose-ca.yaml fabricstar

sleep 2s

echo
echo "Deploying Orderers..."
echo

docker stack deploy --compose-file=network/hyperledger/swarms/docker-compose-orderer.yaml fabricstar

sleep 2s

echo
echo "Deploying Org1..."
echo

docker stack deploy --compose-file=network/hyperledger/swarms/orgs/docker-compose-org1.yaml fabricstar

sleep 2s

echo
echo "Deploying Org2..."
echo

docker stack deploy --compose-file=network/hyperledger/swarms/orgs/docker-compose-org2.yaml fabricstar

echo
echo "Deploying Caliper."
echo

env BENCHMARK="${BENCHMARK}" docker stack deploy --compose-file=network/hyperledger/swarms/docker-compose-caliper.yaml fabricstar