#!/bin/bash
# Basic script to run the commands to delete our old docker image/container and then create new ones after changes are made
# This may not be necessary if we use a docker compose file, but I haven't figured that out yet and this should save time
# in the mean-time

# First stop the container in case it's running
echo "Stopping and deleting docker container 'django_project'"
docker stop django_project
# Then delete the container
docker rm django_project
# re-build docker image
echo "re-building docker image 'django_project:latest'"
docker build --tag django_project:latest .
# Create and run new container based on the updated image
echo "create and run new docker container (also called 'django_project')"
docker run --name django_project -d -it -p 8000:8000 django_project:latest
echo "Finished!, django project should now be running in docker container, you can stop it any time with 'docker stop django_project'"