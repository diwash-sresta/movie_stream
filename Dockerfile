# Use the official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker caching
COPY requirements.txt /app/

# Install dependencies (including psycopg2 for PostgreSQL)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . /app/

# Expose the port Django runs on
EXPOSE 8000

# Install additional dependencies like "watchdog" for auto-reloading Django
RUN pip install watchdog

# Run migrations and start the Django development server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]