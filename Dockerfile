FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y sqlite3

# Copy the application files to the container
COPY app.py /app/

# Install Python dependencies
RUN pip install flask pyyaml ping3 apscheduler requests

# Expose the application port
EXPOSE 5000

# Run the application
CMD [ "python", "app.py", "runserver" ]
