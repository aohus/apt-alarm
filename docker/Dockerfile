# Base image
FROM python:3.8.5

# Set working directory
WORKDIR /app

# Copy requirements.txt file
COPY requirements.txt .

# Install project dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y wget unzip

# google-chrome 설치
RUN wget -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt install /tmp/google-chrome-stable_current_amd64.deb -y \
    && mv /usr/bin/google-chrome-stable /usr/bin/google-chrome

# chromedriver 다운로드 및 설치
RUN wget -O /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/linux64/chromedriver-linux64.zip  \
    && unzip /tmp/chromedriver.zip -d /usr/bin/  \
    && mv /usr/bin/chromedriver-linux64/chromedriver /usr/bin/chromedriver  \
    && chmod +x /usr/bin/chromedriver \
    && apt-get install -y libnss3

# Copy the entire project directory into the container
COPY src .

# Expose the port on which the FastAPI server will run
EXPOSE 8000

# Command to run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
