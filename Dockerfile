# Start with Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements file
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy all backend code
COPY backend/ .

# Set environment variables for Cloud Run
ENV FLASK_APP=app.py
ENV SECRET_KEY=cloud-run-production-key-12345
ENV PORT=8080

# Cloud Run requires apps to listen on port 8080
EXPOSE 8080

# Run the Flask app with gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --timeout 0 --access-logfile - --error-logfile - app:app
