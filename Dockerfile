# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the logs
ENV PYTHONUNBUFFERED True

# uncomment this if you use flask drectly
ENV PORT=5000

# Copy local code to the container image.
ENV APP_HOME /app
ENV MYSQL_DB_HOST=
ENV MYSQL_DB_USER=
ENV MYSQL_DB_PASSWORD=
ENV MYSQL_DB_NAME=

WORKDIR $APP_HOME
COPY . .

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# uncomment this if you use flask drectly
EXPOSE $PORT

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.

# if you use this, remember to add --PORT 5000 to gcloud run deploy argument
CMD ["flask", "run", "--host=0.0.0.0"]
# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 'app:main()'
