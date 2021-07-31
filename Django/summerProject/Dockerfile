# Docker file largely based on this guide https://www.section.io/engineering-education/django-docker/
# This docker file is a bit more complicated because we need to install system dependencies for sql server as Docker does
# not support it natively. Guide for this was taken from https://www.programmersought.com/article/90931589762/
# and https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15#debian17

# Specify version of python to use as image
FROM python:3
# This is needed for docker to work correctly
ENV PYTHONUNBUFFERED 1
# Make a directory for docker
RUN mkdir /code
# Sets this directory as our working directory
WORKDIR /code
# Copy our requirements file to this directory
COPY ./requirements.txt /code/

# Enable https and dependencies and curl so we can install microsoft server
RUN apt-get update && apt-get -y install apt-transport-https curl
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
# Install sql server for debian 10
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN exit
# Install cron
RUN apt-get install -y cron
RUN apt-get update
RUN ACCEPT_EULA=Y apt-get -y install msodbcsql17
# Install other dependencies
RUN apt-get install unixodbc-dev

# Install python dependencies from requirements file
RUN pip install -r requirements.txt
# Copy the django project into the working directory
COPY . /code/
# Expose port 8000 so the application can be accessed
EXPOSE 8000
# Run the command to start the cron tab tasks
CMD ["python", "manage.py", "crontab", "add"]
# Run the command to start the django project
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]