# Getting Started

There are two ways to run this project. **Docker is recommended** — it's one command and requires no manual setup.

---

## Option 1: Docker (Recommended)

### Prerequisites

Install **Docker Desktop** and make sure it's running:
- [Windows](https://docs.docker.com/desktop/install/windows-install/)
- [macOS](https://docs.docker.com/desktop/install/mac-install/)
- [Linux](https://docs.docker.com/desktop/install/linux-install/)

### Setup & Start

```bash
git clone https://github.com/adithyakrishhna/work-orchestration-engine.git
cd work-orchestration-engine
docker compose up --build
```

Wait for this line:
```
web-1  | ==> Starting server at http://localhost:8000
```

Then open `http://localhost:8000` and log in with `admin_user / testpass123`.

Docker handles everything: PostgreSQL, migrations, sample data, and the server — automatically.

**New to Docker?** See the [Docker Guide](00-docker-guide.md) for a full walkthrough including daily commands, troubleshooting, and how to run management commands inside the container.

---

## Option 2: Manual Setup (Local)

Use this if you prefer running the project directly on your machine without Docker.

### Prerequisites

| Software | Version | Download |
|---|---|---|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| PostgreSQL | 17+ | [postgresql.org](https://www.postgresql.org/download/) |
| Git | Any | [git-scm.com](https://git-scm.com/downloads/) |

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/adithyakrishhna/work-orchestration-engine.git
cd work-orchestration-engine

# 2. Create virtual environment
python -m venv venv

# Activate (Windows - CMD)
venv\Scripts\activate

# Activate (Windows - PowerShell)
venv\Scripts\Activate.ps1

# Activate (Mac/Linux)
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (copy from .env.example and fill in your values)
cp .env.example .env

# 5. Create the PostgreSQL database
psql -U postgres -c "CREATE DATABASE work_orchestration;"

# 6. Run migrations
python manage.py migrate

# 7. Create admin account
python manage.py createsuperuser

# 8. Load sample data
python manage.py seed_data

# 9. Start the server
python manage.py runserver
```

---

## Access Points

| URL | What You'll See |
|---|---|
| `http://127.0.0.1:8000/` | Frontend Dashboard (login page) |
| `http://127.0.0.1:8000/admin/` | Django Admin Panel |
| `http://127.0.0.1:8000/api/v1/` | DRF Browsable API |

---

## Test Credentials (available after seed_data runs)

| Username | Password | Role | What They Can Do |
|---|---|---|---|
| `admin_user` | `testpass123` | Admin | Everything — full CRUD, all transitions, manage workflows |
| `manager_user` | `testpass123` | Manager | Assign tasks, create users, approve/reject work |
| `dev_alice` | `testpass123` | Engineer | Work on assigned tasks, transition own tasks |
| `dev_bob` | `testpass123` | Engineer | Work on assigned tasks, transition own tasks |
| `viewer_user` | `testpass123` | Viewer | Read-only access to all data |
