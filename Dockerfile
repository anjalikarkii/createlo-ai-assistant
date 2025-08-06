# Use an official, lightweight Python image from the official registry
FROM python:3.11-slim

# Set an environment variable to ensure Python outputs logs immediately
ENV PYTHONUNBUFFERED True

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Expose the port that the application will run on
EXPOSE 8080

# The command to run will be provided during the Cloud Run deployment.
# This allows us to use this same Dockerfile for both the FastAPI and Flask apps.