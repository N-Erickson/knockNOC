# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Node.js and npm
RUN apt-get update && apt-get install -y nodejs npm

# Copy the rest of the application code
COPY . .

# Create a script to touch the file if it doesn't exist
RUN sh -c 'if [ ! -f /app/pings.db ]; then touch /app/pings.db; fi'

# Set permissions
RUN chown -R root:root /app && chmod -R 755 /app

# Change to the frontend directory and install npm dependencies
WORKDIR /app/frontend
RUN npm cache clean --force
RUN npm install -g npm@latest
RUN npm install

# Build the Vue.js application
RUN npm run build

# Change back to the main app directory
WORKDIR /app

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "run.py"]