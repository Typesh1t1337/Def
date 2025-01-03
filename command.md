pip freeze > requirements.txt
chmod +x ./entrypoint.sh
docker exec -it django /bin/sh