# Base image
FROM python:3.8.5

# Set working directory
WORKDIR /app

# Copy requirements.txt file
COPY requirements.txt .

# Install project dependencies
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the entire project directory into the container
COPY src .

# Expose the port on which the FastAPI server will run
EXPOSE 8000

# Command to run the FastAPI server
CMD ["uvicorn", "main:app", "--workers","3", "--host", "0.0.0.0", "--port", "8000"]
