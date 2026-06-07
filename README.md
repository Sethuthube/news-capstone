# Capstone Project – News Application

## Project Overview

This project is a Django-based news application developed for the HyperionDev Capstone Project – News Application.

The application allows different types of users to interact with news content based on their role. Readers can view approved articles and subscribe to publishers or journalists. Journalists can create articles and newsletters. Editors can review and approve articles before they are published.

When an editor approves an article, the system notifies subscribed readers by email and logs the approved article internally.

The project includes:

* A custom Django user model
* Role-based permissions
* Publisher and journalist subscriptions
* Article approval workflow
* Newsletter management
* REST API endpoints
* JWT authentication
* MariaDB database support
* Automated unit tests

---

## Table of Contents

1. Project Overview
2. User Roles
3. Main Features
4. Technologies Used
5. Project Structure
6. Installation Instructions
7. MariaDB Database Setup
8. Running the Project
9. Test Users
10. Web Routes
11. API Endpoints
12. JWT Authentication
13. Email Notification System
14. Automated Tests
15. Review Feedback Fixes
16. Final Submission Checklist

---

## User Roles

The application uses three main user roles.

### Reader

Readers can:

* View approved articles
* View newsletters
* Subscribe to publishers
* Subscribe to journalists
* Receive email notifications when subscribed content is approved

Readers cannot:

* Create articles
* Create newsletters
* Create publishers
* Approve articles
* Delete content

### Journalist

Journalists can:

* Create articles
* Create newsletters
* View their submitted articles
* Update their own articles
* Delete their own articles
* See whether their articles are pending or approved

Journalists cannot:

* Approve articles
* Create publishers
* Manage other users’ content unless permitted by the system

### Editor

Editors can:

* Review pending articles
* Approve articles
* Update articles
* Delete articles
* Create newsletters
* Update newsletters
* Delete newsletters
* Create publishers
* Update publishers
* Delete publishers

---

## Main Features

### Custom User Model

The project uses a custom user model called `CustomUser`.

The model includes:

* `username`
* `email`
* `role`
* reader subscriptions to publishers
* reader subscriptions to journalists

Emails are unique to prevent duplicate email registration issues.

```python
email = models.EmailField(unique=True)
```

Reader-only subscription fields are cleared automatically for users who are not readers.

---

### Publishers

Publishers can have:

* Multiple editors
* Multiple journalists
* Multiple articles

Readers can subscribe to publishers and receive notifications when a publisher-linked article is approved.

---

### Articles

Articles include:

* Title
* Content
* Author
* Publisher
* Created date
* Approval status

Articles are created as unapproved by default.

```python
approved = models.BooleanField(default=False)
```

An article only becomes visible to readers after an editor approves it.

---

### Newsletters

Newsletters include:

* Title
* Description
* Author
* Created date
* Many-to-many relationship with articles

Journalists and editors can create newsletters.

Readers can view newsletters.

---

### Article Approval Workflow

The article approval process works like this:

1. A journalist creates an article.
2. The article is saved as pending approval.
3. An editor reviews the article.
4. The editor approves the article.
5. The article becomes visible to readers.
6. Subscribed readers receive an email notification.
7. The approved article is logged internally.

---

### Reader Subscriptions

Readers can subscribe to:

* Publishers
* Journalists

When an article is approved, the system checks:

* readers subscribed to the article’s publisher
* readers subscribed to the article’s journalist

Those readers are then notified by email.

---

## Technologies Used

* Python
* Django
* Django REST Framework
* Django REST Framework Simple JWT
* MariaDB
* XAMPP
* Bootstrap
* HTML
* CSS
* Django Templates
* Django Automated Testing Framework

---

## Project Structure

```text
news_capstone/
│
├── manage.py
├── README.md
├── requirements.txt
│
├── news_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── news/
│   ├── migrations/
│   ├── templates/
│   │   └── news/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── reader_dashboard.html
│   │       ├── journalist_dashboard.html
│   │       ├── editor_dashboard.html
│   │       ├── editor_review.html
│   │       ├── article_list.html
│   │       ├── article_detail.html
│   │       ├── article_form.html
│   │       ├── article_confirm_delete.html
│   │       ├── newsletter_list.html
│   │       ├── newsletter_form.html
│   │       ├── newsletter_confirm_delete.html
│   │       ├── publisher_list.html
│   │       ├── publisher_form.html
│   │       ├── publisher_confirm_delete.html
│   │       ├── journalist_list.html
│   │       └── reader_newsletters.html
│   │
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
```

---

## Installation Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Sethuthube/news-capstone
cd news_capstone
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Requirements

The project uses the following main dependencies:

```text
Django
djangorestframework
djangorestframework-simplejwt
mysqlclient
requests
```

If `mysqlclient` causes installation issues on Windows, `PyMySQL` may be used as an alternative.

---

## MariaDB Database Setup

This project is configured to use MariaDB through XAMPP.

### 1. Start XAMPP

Open XAMPP Control Panel and start:

```text
Apache
MySQL
```

In this project setup, MySQL/MariaDB uses port:

```text
3307
```

### 2. Open phpMyAdmin

Open:

```text
http://localhost/phpmyadmin/
```

### 3. Create Database

Create a new database called:

```text
news_capstone
```

Recommended collation:

```text
utf8mb4_general_ci
```

### 4. Database Configuration

The database configuration is located in:

```text
news_project/settings.py
```

The project uses this MariaDB configuration:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'news_capstone',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3307',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Running the Project

Start the development server:

```bash
python manage.py runserver
```

Open the project in the browser:

```text
http://127.0.0.1:8000/
```

---

## Test Users

The following users were used during testing.

### Reader

```text
Username: reader_test
Password: Testpass123!
Role: Reader
```

### Journalist

```text
Username: journalist_test
Password: Testpass123!
Role: Journalist
```

### Editor

```text
Username: editor_test
Password: Testpass123!
Role: Editor
```

If these users do not exist in a fresh database, they can be recreated from the registration page:

```text
http://127.0.0.1:8000/register/
```

---

## Web Routes

### Public Routes

```text
Home:
http://127.0.0.1:8000/

Register:
http://127.0.0.1:8000/register/

Login:
http://127.0.0.1:8000/login/

Articles:
http://127.0.0.1:8000/articles/
```

### Dashboard Routes

```text
General Dashboard Redirect:
http://127.0.0.1:8000/dashboard/

Reader Dashboard:
http://127.0.0.1:8000/dashboard/reader/

Journalist Dashboard:
http://127.0.0.1:8000/dashboard/journalist/

Editor Dashboard:
http://127.0.0.1:8000/dashboard/editor/
```

### Editor Routes

```text
Editor Review:
http://127.0.0.1:8000/editor/review/
```

### Article Routes

```text
Article List:
http://127.0.0.1:8000/articles/

Create Article:
http://127.0.0.1:8000/articles/create/

Article Detail:
http://127.0.0.1:8000/articles/<article_id>/

Edit Article:
http://127.0.0.1:8000/articles/<article_id>/edit/

Delete Article:
http://127.0.0.1:8000/articles/<article_id>/delete/

Approve Article:
http://127.0.0.1:8000/articles/<article_id>/approve/
```

### Newsletter Routes

```text
Newsletter List:
http://127.0.0.1:8000/newsletters/

Create Newsletter:
http://127.0.0.1:8000/newsletters/create/

Edit Newsletter:
http://127.0.0.1:8000/newsletters/<newsletter_id>/edit/

Delete Newsletter:
http://127.0.0.1:8000/newsletters/<newsletter_id>/delete/

Reader Newsletters:
http://127.0.0.1:8000/reader/newsletters/
```

### Publisher Routes

```text
Publisher List:
http://127.0.0.1:8000/publishers/

Create Publisher:
http://127.0.0.1:8000/publishers/create/

Edit Publisher:
http://127.0.0.1:8000/publishers/<publisher_id>/edit/

Delete Publisher:
http://127.0.0.1:8000/publishers/<publisher_id>/delete/

Subscribe to Publisher:
http://127.0.0.1:8000/publishers/<publisher_id>/subscribe/
```

### Journalist Routes

```text
Journalist List:
http://127.0.0.1:8000/journalists/

Subscribe to Journalist:
http://127.0.0.1:8000/journalists/<journalist_id>/subscribe/
```

---

## REST API Endpoints

The project includes REST API endpoints using Django REST Framework.

### JWT Authentication

```text
POST /api/token/
POST /api/token/refresh/
```

Example token request:

```json
{
    "username": "editor_test",
    "password": "Testpass123!"
}
```

Example response:

```json
{
    "refresh": "refresh_token_here",
    "access": "access_token_here"
}
```

---

## Article API

```text
GET /api/articles/
GET /api/articles/subscribed/
GET /api/articles/<id>/
POST /api/articles/
PUT /api/articles/<id>/
PATCH /api/articles/<id>/
DELETE /api/articles/<id>/
POST /api/articles/<id>/approve/
```

### Article API Permissions

Readers:

```text
Can view approved articles.
Can view subscribed approved articles.
Cannot create articles.
Cannot approve articles.
Cannot delete articles.
```

Journalists:

```text
Can create articles.
Can view their own articles.
Can update/delete their own articles.
Cannot approve articles.
```

Editors:

```text
Can view all articles.
Can update articles.
Can delete articles.
Can approve articles.
```

---

## Publisher API

```text
GET /api/publishers/
POST /api/publishers/
GET /api/publishers/<id>/
PUT /api/publishers/<id>/
PATCH /api/publishers/<id>/
DELETE /api/publishers/<id>/
```

---

## Newsletter API

```text
GET /api/newsletters/
POST /api/newsletters/
GET /api/newsletters/<id>/
PUT /api/newsletters/<id>/
PATCH /api/newsletters/<id>/
DELETE /api/newsletters/<id>/
```

---

## User API

```text
GET /api/users/
GET /api/users/<id>/
```

---

## Approved Article Log API

```text
POST /api/approved/
```

This endpoint logs approved articles internally.

Example payload:

```json
{
    "article_id": 1
}
```

---

## Email Notification System

The project uses Django’s console email backend during local testing.

In `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'newsapp@example.com'
```

This means emails are printed in the terminal instead of being sent through a real email service.

When an editor approves an article:

1. The article is marked as approved.
2. The system finds readers subscribed to the article’s publisher.
3. The system finds readers subscribed to the article’s journalist.
4. The system sends an email notification to those readers.
5. The system creates an approved article log.

Example email subject:

```text
New approved article: Email Test Article
```

---

## Automated Tests

The project includes automated tests in:

```text
news/tests.py
```

Run tests:

```bash
python manage.py test
```

Current result:

```text
Ran 11 tests

OK
```

### Test Coverage

The automated tests cover:

1. Reader can only retrieve approved articles.
2. Reader can retrieve subscribed content only.
3. Journalist can create an article.
4. Reader cannot create an article.
5. Editor can approve an article.
6. Reader cannot approve an article.
7. Editor can delete an article.
8. Reader cannot delete an article.
9. Journalist can create a newsletter.
10. Approval sends email to subscribed reader.
11. Duplicate email is not allowed.

---

## Manual Testing Checklist

Before submission, these manual checks were performed.

### Duplicate Email Check

Attempted to register a second user with an already-used email.

Expected result:

```text
An account with this email address already exists.
```

Status:

```text
Passed
```

### Reader Dashboard Check

Logged in as a reader.

Expected result:

```text
Reader can see articles, newsletters, publishers, and journalists.
Reader cannot see Create Publisher.
```

Status:

```text
Passed
```

### Subscription Feedback Check

Reader subscribed to a journalist/publisher.

Expected result:

```text
You have successfully subscribed to journalist_test.
```

Status:

```text
Passed
```

### Article Approval Email Check

A journalist created an article. An editor approved it.

Expected result:

```text
Email notification printed in the terminal for subscribed reader.
```

Status:

```text
Passed
```

### API Test Check

Automated API tests were run.

Expected result:

```text
Ran 11 tests

OK
```

Status:

```text
Passed
```

---

## Review Feedback Fixes

The following review feedback issues were fixed.

### 1. Duplicate Email Addresses

Problem:

```text
The system allowed duplicate email addresses.
```

Fix:

The `CustomUser` model now uses:

```python
email = models.EmailField(unique=True)
```

The registration form also validates duplicate emails and returns a clear message:

```text
An account with this email address already exists.
```

---

### 2. Reader Subscription Feedback

Problem:

```text
When a reader clicked Subscribe, there was no success feedback.
```

Fix:

The subscription views now use Django messages:

```python
messages.success(
    request,
    f'You have successfully subscribed to {journalist.username}.'
)
```

Readers now see a success message after subscribing.

---

### 3. Reader Could See Create Publisher

Problem:

```text
Reader users could see the Create Publisher button.
```

Fix:

The reader dashboard and navigation were updated so that only editors and superusers can see publisher creation links.

---

### 4. Reader Email Notifications

Problem:

```text
Subscribed readers did not receive emails when subscribed content was approved.
```

Fix:

The approval logic now checks:

* readers subscribed to the article publisher
* readers subscribed to the article journalist

Those readers receive email notifications when the article is approved.

---

### 5. User Model Role Technicality

Problem:

```text
Reader-specific subscription fields needed to be handled correctly for journalist users.
```

Fix:

Reader-only subscription fields are cleared for users who are not readers.

This means journalist and editor accounts do not keep reader subscription values.

---

## Important Commands

### Run Django System Check

```bash
python manage.py check
```

### Make Migrations

```bash
python manage.py makemigrations
```

### Apply Migrations

```bash
python manage.py migrate
```

### Run Server

```bash
python manage.py runserver
```

### Run Automated Tests

```bash
python manage.py test
```

### Create Superuser

```bash
python manage.py createsuperuser
```
---

## Sphinx Documentation Setup

This project includes Sphinx documentation inside the `docs` folder.

The documentation was generated to provide user-friendly technical documentation for the Django project.

### 1. Install Sphinx

If Sphinx is not already installed, install it with:

```bash
pip install sphinx                

### 2. Move into the docs folder

```bash
cd docs
### 3. Generate the HTML documentation

On Windows, run:

```bash
.\make.bat html
```

On macOS/Linux, run:

```bash
make html
```

### 4. Open the documentation

After building the documentation, open:

```text
docs/_build/html/index.html
```

### 5. Important Sphinx Configuration

For Django projects, the Sphinx `conf.py` file must include the Django project setup.

Example:

```python
import os
import sys
import django

sys.path.insert(0, os.path.abspath('..'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'news_project.settings'
django.setup()
```

This allows Sphinx to import the Django modules correctly when generating documentation.

---

## Docker Setup Instructions

This project includes a Dockerfile so that the application can be built and run inside a Docker container.

### 1. Make sure Docker is installed

Confirm Docker is working:

```bash
docker --version
```

### 2. Build the Docker image

Run this command from the root folder of the project, where the `Dockerfile` is located:

```bash
docker build -t news-capstone .
```

### 3. Run the Docker container

```bash
docker run -p 8000:8000 news-capstone
```

### 4. Open the application

Once the container is running, open the app in your browser:

```text
http://127.0.0.1:8000/
```

### 5. Stop the container

To stop the running container, press:

```text
CTRL + C
```

If the container is running in the background, list running containers:

```bash
docker ps
```

Then stop the container:

```bash
docker stop <container_id>
```

### Docker Notes

- The Dockerfile installs the project dependencies from `requirements.txt`.
- The container exposes port `8000`.
- The application runs using Django’s development server.
- Local database settings may need to be adjusted depending on the user’s environment.
- Do not commit database passwords, secret keys, or access tokens to GitHub.

---
---

## Final Pre-Submission Checklist

Before requesting review:

* [ ] XAMPP Apache is running.
* [ ] XAMPP MySQL is running.
* [ ] phpMyAdmin opens correctly.
* [ ] MariaDB database `news_capstone` exists.
* [ ] `settings.py` is using MariaDB.
* [ ] `python manage.py check` passes.
* [ ] `python manage.py makemigrations` runs successfully.
* [ ] `python manage.py migrate` runs successfully.
* [ ] `python manage.py test` passes.
* [ ] README is updated.
* [ ] requirements.txt is updated.
* [ ] Duplicate email registration has been tested.
* [ ] Reader dashboard has been tested.
* [ ] Subscribe feedback has been tested.
* [ ] Editor approval has been tested.
* [ ] Email notification has been tested.
* [ ] API token endpoint has been checked.
* [ ] Code has been pushed to GitHub.

---

## Submission Notes

This project has been tested with MariaDB using XAMPP on port `3307`.

The automated test suite currently passes with:

```text
Ran 11 tests

OK
```

The application satisfies the core project requirements:

* custom user model
* role-based access
* reader subscriptions
* publisher and journalist relationships
* article approval workflow
* email notification system
* REST API
* JWT authentication
* automated tests
* MariaDB database configuration
