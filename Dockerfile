FROM tensorflow/tensorflow:latest-gpu-jupyter

ENV DEBIAN_FRONTEND=noninteractive
ENV TF_ENABLE_ONEDNN_OPTS=0

WORKDIR /usr/src

RUN apt-get update && apt-get install -y \
    python3-apt \
    python3-pip \
    build-essential \
    xvfb

RUN pip3 install --upgrade pip setuptools

COPY requirements.txt ./

RUN pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install \
    numpy==1.24.3 \
    opencv-python==4.8.0.74 \
    opencv-python-headless==4.8.0.74 \
    pyvirtualdisplay

RUN playwright install
RUN playwright install-deps

EXPOSE 8000

CMD ["python3", "main.py", "--host", "0.0.0.0"]