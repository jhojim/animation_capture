FROM nvidia/cuda:12.8.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /usr/src

RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-apt \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    gnupg \
    software-properties-common \
    libopenblas-dev \
    liblapack-dev \
    libgtk2.0-dev \
    pkg-config \
    python3-numpy \
    libtbb2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libavformat-dev \
    libswscale-dev \
    xvfb \
    libavcodec-dev \
    libavutil-dev \
    libeigen3-dev \
    libglew-dev \
    libgtk-3-dev \
    libpostproc-dev \
    libxvidcore-dev \
    libx264-dev \
    zlib1g-dev \
    libgl1 \
    libglvnd-dev \
    pkg-config

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install \
    cmake==3.21.3 \
    librosa==0.8.0 \
    numpy==1.24.3 \
    Werkzeug==2.3.6 \
    pyvirtualdisplay \
    pydotplus

RUN git clone https://github.com/opencv/opencv.git && \
    git clone https://github.com/opencv/opencv_contrib.git && \
    cd opencv && mkdir build && cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=/usr/src/opencv_contrib/modules \
    -D WITH_CUDA=ON \
    -D CUDA_ARCH_BIN=7.0 \
    -D CUDA_ARCH_PTX="" \
    -D WITH_CUBLAS=1 \
    -D WITH_LIBV4L=ON \
    -D WITH_V4L=ON \
    -D BUILD_opencv_python3=ON \
    -D BUILD_opencv_python2=OFF \
    -D BUILD_opencv_java=OFF \
    -D WITH_GSTREAMER=ON \
    -D WITH_GTK=ON \
    -D BUILD_TESTS=OFF \
    -D BUILD_PERF_TESTS=OFF \
    -D BUILD_EXAMPLES=OFF \
    -D OPENCV_ENABLE_NONFREE=ON .. && \
    make -j$(nproc) && make install && ldconfig

ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/usr/local/cuda/lib64

RUN playwright install
RUN playwright install-deps

EXPOSE 8000

CMD ["sh", "-c", "cd /usr/src/app && python3 main.py --host 0.0.0.0"]