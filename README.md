<div align="center">

# CyberGuard SOC

Professional Security Operations Center dashboard with premium glassmorphism UI, real-time monitoring, threat visualization, and endpoint management.

</div>

---

# Overview

Login Report System is a lightweight monitoring platform designed to process login and logout events, manage local JSON-based user authentication, and display active sessions in real time with dynamic charts.

The application reads chronological event data, validates internal users, analyzes machine activity, and generates a clean dashboard with real graphics powered by Chart.js.

---

# Dashboard Features

- Secure JSON-based user authentication with werkzeug password hashes
- Active session tracking per machine with chronological event processing
- Real Chart.js visualizations (doughnut, bar, line) derived from real events
- Anti-duplicate login guard per machine without logout precedence
- Login/logout event processing with IP and method
- Recent activity table with status badges
- Responsive dark-mode dashboard UI
- Modular backend architecture (blueprints + services)
- External JSON data sources (events + users)

---

# Tech Stack

| Backend | Frontend | Tools |
|---|---|---|
| Python | HTML5 | Git |
| Flask | CSS3 | GitHub |
| Jinja2 | Chart.js | Virtual Environment |
| Werkzeug | Responsive Layout | python-dotenv |

---

# Project Architecture

```bash
login-report-system/
│
├── app/
│   ├── __init__.py          # Application factory
│   ├── auth.py              # Login, logout, dashboard blueprint
│   ├── common.py            # Shared routes blueprint
│   │
│   ├── services/
│   │   └── report_service.py  # Business logic + chart data
│   │
│   ├── templates/
│   │   ├── base.html        # Layout shell with sidebar and user menu
│   │   ├── login.html       # Login form page
│   │   └── dashboard.html   # Main dashboard with charts
│   │
│   └── static/
│       └── css/
│           └── style.css    # Dark theme styles
│
├── data/
│   ├── events.json          # Login/logout event records
│   └── users.json           # User accounts with password hashes
│
├── docs/
│   └── dashboard-preview.png
│
├── tests/                   # Unit tests
├── run.py                   # Entrypoint
├── requirements.txt
└── README.md
```

---

# Authentication

The app uses a local JSON file (`data/users.json`) with werkzeug password hashes. No public web auth—users are internal and validated server-side.

Default users:

- `admin` / `admin123`
- `analyst` / `analyst123`
- `viewer` / `viewer123`

Session cookie is HTTP-only and secured via Flask secret key.

---

# Installation

Clone repository:

```bash
git clone https://github.com/YOUR_USERNAME/login-report-system.git
```

Move into project:

```bash
cd login-report-system
```

Create virtual environment:

```bash
python -m venv venv
```

Activate virtual environment:

### Windows

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set environment variable for production:

```bash
$env:FLASK_SECRET_KEY = "your-secret-key"
```

Load local environment variables with `python-dotenv`:

```bash
pip install -r requirements.txt
```

Create a `.env` file from `.env.example`.

---

# Run Application

```bash
python run.py
```

Open browser:

```text
http://127.0.0.1:5000
```

Root path `/` redirects to `/login`.

---

# Event Processing Logic

The system processes events chronologically to ensure accurate active session tracking.

Supported event types:

- login
- logout

The backend updates machine session states dynamically and renders results to Chart.js datasets.

User fields stored per event:

- `date`, `user`, `machine`, `ip`, `method`, `type`

---

# Future Roadmap

- SQLite integration
- SQLAlchemy ORM
- REST API
- User management panel
- Search and filtering
- Docker support
- Automated testing
- CI/CD workflows

---

# Development Notes

This project was built as part of a professional Python and Flask backend development learning process, with emphasis on:

- clean architecture
- modular backend organization
- scalable Flask structure
- professional Git workflow
- secure local authentication
- real data-driven charts

---

# Commit Workflow

This project maintains a strict commit policy:

- Conventional Commits (`feat:`, `fix:`, `refactor:`, etc.)
- Detailed body explaining motivation, scope, and impact
- References to affected modules when relevant

---

<div align="center">

Developed by Camilo Melo

</div>