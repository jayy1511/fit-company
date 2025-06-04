# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Copy project files
COPY . .

# Install Python dependencies manually
RUN pip install --no-cache-dir flask pydantic sqlalchemy psycopg2-binary pyjwt requests fastapi uvicorn


# Expose port (if needed for testing)
EXPOSE 5000

# Start the Flask app
CMD ["python", "main.py"]
