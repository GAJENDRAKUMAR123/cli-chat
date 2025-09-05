# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Set environment variables
# This ensures that print statements are sent straight to the terminal without being buffered.
ENV PYTHONUNBUFFERED=1

# Copy the client script into the container at /app
COPY client.py .

# Command to run the application
CMD ["python", "client.py"]
