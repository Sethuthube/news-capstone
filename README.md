# News Capstone Project

This is a Django-based news application created for the Capstone Project – Consolidation task.

The project demonstrates the use of:

* Git and GitHub version control
* Branching and merging
* Sphinx documentation
* Docker containerisation
* Django project setup and deployment instructions

## Project Features

* User registration and login
* Role-based user access
* Reader dashboard
* Journalist dashboard
* Editor dashboard
* Article creation and management
* Newsletter functionality
* Publisher management
* Sphinx-generated documentation
* Docker support

---

## Manual Step-by-Step Implementation Instructions

These steps explain how to run the project manually using a Python virtual environment.

### 1. Clone the Repository

```bash
git clone https://github.com/Sethuthube/news-capstone.git
```

### 2. Navigate Into the Project Folder

```bash
cd news_capstone
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

For macOS/Linux:

```bash
source venv/bin/activate
```

### 5. Install the Required Packages

```bash
pip install -r requirements.txt
```

### 6. Apply Database Migrations

```bash
python manage.py migrate
```

### 7. Create a Superuser

```bash
python manage.py createsuperuser
```

### 8. Run the Django Development Server

```bash
python manage.py runserver
```

### 9. Open the Application in the Browser

Go to:

```bash
http://127.0.0.1:8000/
```

The Django application should now be running locally.

---

## Docker Implementation Instructions

These steps explain how to build and run the project using Docker.

### 1. Make Sure Docker Is Installed

Docker must be installed and running on your machine before using these commands.

### 2. Build the Docker Image

From the root project folder, run:

```bash
docker build -t news-capstone .
```

### 3. Run the Docker Container

```bash
docker run -p 8000:8000 news-capstone
```

### 4. Open the Dockerised Application

Go to:

```bash
http://127.0.0.1:8000/
```

The Django application should now be running inside a Docker container.

---

## Sphinx Documentation Instructions

This project includes documentation generated with Sphinx.

### 1. Navigate to the Documentation Folder

```bash
cd docs
```

### 2. Build the HTML Documentation

```bash
make html
```

### 3. Open the Generated Documentation

The generated documentation can be found at:

```bash
docs/_build/html/index.html
```

Open this file in a browser to view the project documentation.

---

## Project Structure

```txt
news_capstone/
│
├── docs/
│   ├── _build/
│   ├── conf.py
│   ├── index.rst
│   ├── modules.rst
│   ├── news.rst
│   └── news_project.rst
│
├── news/
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
│
├── news_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── Dockerfile
├── .dockerignore
├── .gitignore
├── manage.py
├── README.md
├── requirements.txt
└── capstone.txt
```

---

## Important Notes

* The `venv/` folder should not be committed to GitHub.
* The `__pycache__/` folders should not be committed to GitHub.
* Sensitive files such as `.env` files should not be committed to GitHub.
* The `.gitignore` file is used to exclude unnecessary or sensitive files from version control.
* The `requirements.txt` file is used to install all required Python packages.
* The `Dockerfile` is used to build and run the project inside a Docker container.
* The `docs/` folder contains the Sphinx documentation for the project.
