# Stage 1: Build the frontend
FROM node:14-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files and install dependencies
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source code and build assets
COPY frontend/ .
RUN npm run build

# Stage 2: Build the backend and create the final image
FROM python:3.9-slim

WORKDIR /app

# Copy backend requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder /app/frontend/ /app/frontend/

# Expose the application port
EXPOSE 5000

# Set the command to run the application
CMD ["python", "run.py"]
