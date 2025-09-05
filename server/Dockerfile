# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app
# Set environment variables
# This ensures that print statements are sent straight to the terminal without being buffered.
ENV PYTHONUNBUFFERED=1

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server script into the container at /app
COPY server.py .

EXPOSE 65432

# Command to run the application
CMD ["python", "server.py"]
