echo "Removing Services..."
echo 

docker stack rm fabricstar

sleep 5s 

echo 
echo "Removing Network..."
echo 

docker network rm fabricstar