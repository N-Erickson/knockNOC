FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y sqlite3

# Copy the application files to the container
COPY app.py /app/
COPY templates /app/templates
COPY config.yaml /app/

# Install Python dependencies
RUN pip install flask pyyaml ping3 apscheduler requests

# Expose the application port
EXPOSE 5000
ENV FLASK_APP=app.py

# Run the application
#CMD [ "python", "app.py", "runserver" ]

#ENTRYPOINT [ "flask"]
CMD [ "run", "--host", "0.0.0.0" ]
