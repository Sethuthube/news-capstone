# Use the official Python slim image as the base image
FROM python:3.11-slim

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python output is shown immediately in the terminal
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the Docker container
WORKDIR /app

# Copy the requirements file into the container first
COPY requirements.txt /app/

# Install all Python dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the full Django project into the container
COPY . /app/

# Expose port 8000 so the Django app can be accessed in the browser
EXPOSE 8000

# Run migrations and start the Django development server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]