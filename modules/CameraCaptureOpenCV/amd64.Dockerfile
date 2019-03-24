FROM ubuntu:xenial

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends libcurl4-openssl-dev python-pip python-dev build-essential libgtk2.0-dev libboost-python-dev git portaudio19-dev  && \
    rm -rf /var/lib/apt/lists/* 

RUN python -m pip install --upgrade pip setuptools wheel
COPY /build/amd64-requirements.txt ./

RUN pip install -r amd64-requirements.txt

RUN pip install pyaudio wave git+https://github.com/westparkcom/Python-Bing-TTS.git

ADD /app/ .
ADD /build/ .
RUN ls
RUN python --version

ENV PYTHONUNBUFFERED=1

CMD [ "python", "-u", "./main.py" ]