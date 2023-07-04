# Base image
FROM python:3.8.5

# Set working directory
WORKDIR /app

# Copy requirements.txt file
COPY requirements.txt .

# Install project dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

#install chrome
RUN apt-get update && apt-get install -y wget
RUN wget -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt install /tmp/google-chrome-stable_current_amd64.deb -y
RUN mv /usr/bin/google-chrome-stable /usr/bin/google-chrome

# ChromeDriver 다운로드 및 설치
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/114.0.5735.16/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip -d /usr/bin/
RUN chmod +x /usr/bin/chromedriver

# Copy the entire project directory into the container
COPY app .

# Expose the port on which the FastAPI server will run
EXPOSE 8000

# Command to run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
