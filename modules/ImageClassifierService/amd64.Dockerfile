FROM ubuntu:xenial

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 libcurl4-openssl-dev python3-pip libboost-python-dev && \
    rm -rf /var/lib/apt/lists/* 



COPY /build/amd64-requirements.txt amd64-requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install setuptools
RUN pip3 install -r amd64-requirements.txt

# ADD app /app

# Expose the port
EXPOSE 80
EXPOSE 3000

# Set the working directory
# WORKDIR /app
# ADD app /app

WORKDIR /
ADD app /

# Run the flask server for the endpoints
# CMD python app.py

CMD ["python3", "-m", "main"]

# CMD [ "python", "-u", "main.py" ]
