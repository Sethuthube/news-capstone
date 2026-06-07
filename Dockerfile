# Use a lightweight official Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python output is shown immediately in the terminal
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to install dependencies
COPY requirements.txt /app/

# Upgrade pip and install project dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the full project into the container
COPY . /app/

# Expose port 8000 for the Django development server
EXPOSE 8000

# Start the Django application inside the container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]