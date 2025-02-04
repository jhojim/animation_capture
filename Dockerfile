FROM python:3.10

# Install necessary libraries.
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    xvfb \
    unzip \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get -y update \
    && apt-get install -y google-chrome-stable

# Install ChromeDriver compatible with Chrome version
RUN CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` \
    && wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P ~/ \
    && unzip ~/chromedriver_linux64.zip -d ~/ \
    && rm ~/chromedriver_linux64.zip \
    && mv -f ~/chromedriver /usr/local/share/ \
    && chmod +x /usr/local/share/chromedriver \
    && ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container
COPY . .

# Define the command that will be used to run the container.
CMD ["bash", "-c", "Xvfb :99 & export DISPLAY=:99 && python3 main.py"]