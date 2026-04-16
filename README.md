# School Support CRM - Minimalist Helpdesk System

A minimalist CRM system for school support services built with FastAPI, SQLModel, and HTMX.

## Features

- **Ticket Management**: Create, view, edit, and delete support tickets
- **Priority Levels**: Low, Medium, High
- **Status Tracking**: Open, In Progress, Resolved, Closed
- **Categories**: Organize tickets by category
- **Comments**: Add comments to tickets
- **User Roles**: User, Support, Admin
- **Dashboard**: Statistics and overview

## Tech Stack

- **Backend**: Python 3.8+ with FastAPI
- **Database**: SQLite with SQLModel ORM
- **Frontend**: HTML templates + Tailwind CSS + HTMX
- **Template Engine**: Jinja2

## Project Structure

```
school-crm/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main application entry point
│   ├── database.py          # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User model
│   │   ├── ticket.py        # Ticket model
│   │   ├── category.py      # Category model
│   │   └── comment.py       # Comment model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py          # User schemas
│   │   ├── ticket.py        # Ticket schemas
│   │   ├── category.py      # Category schemas
│   │   └── comment.py       # Comment schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── users.py         # User API endpoints
│   │   ├── tickets.py       # Ticket API endpoints
│   │   ├── categories.py    # Category API endpoints
│   │   └── comments.py      # Comment API endpoints
│   └── templates/
│       ├── base.html        # Base template
│       ├── index.html       # Dashboard
│       ├── tickets.html     # Tickets list
│       ├── ticket_detail.html # Ticket detail view
│       ├── ticket_form.html # Ticket form
│       └── categories.html  # Categories page
├── static/                  # Static files (CSS, JS)
├── requirements.txt         # Python dependencies
├── .gitignore
├── README.md
├── DEPLOY.md                # Deployment instructions
├── deploy_hook.py           # GitHub webhook handler
├── school-crm.service       # systemd service file
├── school-crm-hook.service  # Webhook systemd service
└── nginx.conf.example       # Nginx configuration example
```

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/konstantin79771883907-maker/school-crm.git
cd school-crm
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Open in browser:
```
http://localhost:8000
```

## Default Users

The system comes with 3 predefined users:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| support | support123 | Support |
| user | user123 | User |

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

- `GET/POST /api/tickets/` - List/Create tickets
- `GET/PUT/DELETE /api/tickets/{id}` - Ticket operations
- `GET/POST /api/users/` - List/Create users
- `GET/POST /api/categories/` - List/Create categories
- `GET/POST /api/comments/` - List/Create comments

## Deployment

For production deployment with auto-deploy from GitHub, see [DEPLOY.md](DEPLOY.md).

## License

MIT License
