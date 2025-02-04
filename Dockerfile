FROM tensorflow/tensorflow:latest-gpu-jupyter

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /usr/src

RUN apt-get update && apt-get install -y \
    python3-apt \
    build-essential \
    cmake \
    wget \
    curl \
    gnupg \
    software-properties-common \
    python3-pip \
    libopenblas-dev \
    liblapack-dev \
    graphviz \
    libgtk2.0-dev \
    pkg-config \
    xvfb

RUN pip3 install --upgrade pip setuptools

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install \
    cmake==3.27.0 \
    dlib==19.24.2 \
    numpy==1.24.3 \
    opencv-python==4.8.0.74 \
    opencv-python-headless==4.8.0.74 \
    Werkzeug==2.3.6 \
    graphviz \
    pyvirtualdisplay \
    pydotplus

RUN playwright install
RUN playwright install-deps

EXPOSE 8000

CMD ["python3", "main.py", "--host", "0.0.0.0"]