# Django News Application

## Project Overview

This is a Django-based news application developed as part of the HyperionDev Capstone Project. The application allows journalists to create articles and newsletters, editors to review and approve submitted articles, and readers to view approved articles based on their subscriptions.

The project includes a role-based user system, article approval workflow, email notification logic, REST API endpoints, JWT authentication, automated unit tests, and MariaDB database integration.

---

## Main Features

- Custom user model with role-based access
- Reader, Editor, and Journalist roles
- Django groups and permissions
- Publishers with assigned editors and journalists
- Articles created by journalists
- Newsletters linked to articles
- Editor article review and approval workflow
- Approved articles visible to readers
- Email notification logic for subscribers
- Internal API logging for approved articles
- REST API built with Django REST Framework
- JWT authentication
- Subscribed articles endpoint
- Automated API unit tests
- MariaDB database connection

---

## User Roles

### Reader

Readers can:

- View approved articles
- View newsletters
- Subscribe to publishers
- Subscribe to journalists
- Retrieve subscribed articles through the API

### Journalist

Journalists can:

- Create articles
- View their articles
- Update their articles
- Delete their articles
- Create newsletters
- Link newsletters to articles

### Editor

Editors can:

- View articles and newsletters
- Review unapproved articles
- Approve articles
- Update articles and newsletters
- Delete articles and newsletters

---

## Models

### CustomUser

The custom user model extends Django's `AbstractUser` and includes:

- Role field
- Subscribed publishers
- Subscribed journalists

### Publisher

Represents a news publication. A publisher can have:

- Multiple editors
- Multiple journalists
- Multiple subscribers

### Article

Represents a news article. Each article includes:

- Title
- Content
- Author
- Publisher
- Created date
- Approval status

### Newsletter

Represents a curated collection of articles. Each newsletter includes:

- Title
- Description
- Author
- Created date
- Related articles

### ApprovedArticleLog

Stores a log whenever an article is approved.

---

## Application Pages

| Page | Description |
|---|---|
| `/` | Shows approved articles |
| `/articles/<id>/` | Shows a single approved article |
| `/editor/review/` | Allows editors to review unapproved articles |
| `/editor/articles/<id>/approve/` | Allows editors to approve articles |
| `/admin/` | Django admin panel |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/articles/` | Returns articles based on user role |
| GET | `/api/articles/subscribed/` | Returns articles from subscribed publishers/journalists |
| GET | `/api/articles/<id>/` | Returns a single article |
| POST | `/api/articles/` | Allows journalists to create articles |
| PUT | `/api/articles/<id>/` | Allows editors/journalists to update articles |
| DELETE | `/api/articles/<id>/` | Allows editors/journalists to delete articles |
| POST | `/api/articles/<id>/approve/` | Allows editors to approve articles |
| POST | `/api/approved/` | Logs approved articles internally |
| POST | `/api/token/` | Returns JWT access and refresh tokens |
| POST | `/api/token/refresh/` | Refreshes JWT access token |
| GET | `/api/newsletters/` | Returns newsletters |
| GET | `/api/publishers/` | Returns publishers |
| GET | `/api/users/` | Returns users |

---

## Authentication

The project uses JWT authentication through Django REST Framework Simple JWT.

To obtain a token, send a POST request to:

```text
/api/token/

## Role-Based Functionality

This Django news application supports four user roles:

- Reader: Can view approved articles and newsletters.
- Journalist: Can create and manage their own articles and newsletters.
- Editor: Can review and approve submitted articles.
- Publisher: Can view publishing structure, articles, editors, and journalists.

Articles created by journalists are submitted as pending. Editors approve articles before they become visible to readers.

## API Functionality

The application includes REST API endpoints for articles, publishers, newsletters, users, and approved article logging.

## Styling

The application uses Bootstrap and shared template inheritance through `base.html` to provide a consistent dashboard layout.