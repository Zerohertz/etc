POSTGRES_PASSWORD=zerohertz

docker stop postgresql
docker rm postgresql
docker run --name postgresql -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD -d -p 5432:5432 postgres:latest
sleep 3
echo Insert Password: ${POSTGRES_PASSWORD}

psql -h localhost -p 5432 -U postgres
