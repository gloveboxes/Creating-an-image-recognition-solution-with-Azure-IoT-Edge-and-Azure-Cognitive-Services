# FROM microsoft/azureiotedge-seeed-camera-capture:1.0-deps-arm32v7
# https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/
FROM arm32v7/debian:jessie
COPY ./qemu-arm-static /usr/bin/qemu-arm-static

WORKDIR /app

RUN apt update && apt install -y python-dev build-essential python-pip cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev \
    libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran \
    wget unzip && rm -rf /var/lib/apt/lists/*

RUN apt update && apt install -y libboost1.55-all-dev && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY /build/arm32v7-requirements.txt ./
RUN pip install -r arm32v7-requirements.txt

RUN wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.4.1.zip \   
    && unzip opencv.zip \
    && wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.4.1.zip \
    && unzip opencv_contrib.zip \
    && rm opencv.zip && rm opencv_contrib.zip

WORKDIR /app/opencv-3.4.1 

RUN mkdir build 
WORKDIR /app/opencv-3.4.1/build

RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=/app/opencv_contrib-3.4.1/modules \
    -D BUILD_EXAMPLES=OFF ..

RUN make -j4 && make install && ldconfig

RUN apt update && apt install -y git portaudio19-dev
RUN pip install pyaudio wave git+https://github.com/westparkcom/Python-Bing-TTS.git


WORKDIR /app

COPY /app/*.py ./

# disable python buffering to console out (https://docs.python.org/2/using/cmdline.html#envvar-PYTHONUNBUFFERED)
ENV PYTHONUNBUFFERED=1

ENTRYPOINT [ "python", "main.py" ]
