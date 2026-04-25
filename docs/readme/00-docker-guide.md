# Docker Setup Guide

New to Docker? This page explains everything you need — what Docker is, how to install it, and how to use it with this project.

---

## What is Docker?

Docker packages your application and everything it needs (Python, PostgreSQL, dependencies) into isolated containers that run the same way on any machine.

**Without Docker**, setting up this project means: installing Python, installing PostgreSQL, creating a database, activating a virtual environment, installing packages, running migrations, seeding data — all manually.

**With Docker**, the entire setup is one command. Docker handles all of that automatically.

Think of it like this:
- The **Dockerfile** is a recipe for building the app container
- The **docker-compose.yml** is a conductor that starts the app container + the PostgreSQL container together and connects them

---

## Step 1: Install Docker Desktop

Download and install Docker Desktop for your OS:

| OS | Download |
|---|---|
| Windows | https://docs.docker.com/desktop/install/windows-install/ |
| macOS | https://docs.docker.com/desktop/install/mac-install/ |
| Linux | https://docs.docker.com/desktop/install/linux-install/ |

After installing, open Docker Desktop and wait for it to say **"Docker Desktop is running"** in the system tray (Windows) or menu bar (macOS). It must be running before you use any Docker commands.

> **Windows users**: Docker Desktop requires WSL 2 (Windows Subsystem for Linux). The installer will guide you through enabling it if needed.

---

## Step 2: Clone the Repository

```bash
git clone https://github.com/adithyakrishhna/work-orchestration-engine.git
cd work-orchestration-engine
```

---

## Step 3: Start Everything

```bash
docker compose up --build
```

That's it. This single command:
1. Builds the Django app into a container image
2. Pulls the PostgreSQL 17 image
3. Starts PostgreSQL, waits for it to be ready
4. Runs all database migrations automatically
5. Loads sample data (5 test users, a workflow, transition rules)
6. Starts the Django server on port 8000

Wait for this line to appear in the terminal:
```
web-1  | ==> Starting server at http://localhost:8000
```

Then open your browser at `http://localhost:8000`.

**Login with:** `admin_user` / `testpass123`

---

## Daily Usage

Once set up, you don't need `--build` every time.

| Command | What it does |
|---|---|
| `docker compose up` | Start the app (uses existing image) |
| `docker compose up --build` | Start and rebuild the image (use after code changes) |
| `docker compose up -d` | Start in background (detached mode — no log output) |
| `docker compose down` | Stop and remove containers (data is preserved) |
| `docker compose down -v` | Stop containers AND delete all data (clean reset) |
| `docker compose logs -f web` | Stream logs from the Django container |
| `docker compose logs -f db` | Stream logs from the PostgreSQL container |

---

## Running Django Commands Inside the Container

Sometimes you need to run management commands — for example, creating a superuser or checking SLA:

```bash
# Open a shell inside the running web container
docker compose exec web sh

# Then run any Django command inside it:
python manage.py createsuperuser
python manage.py check_sla
python manage.py shell

# Or run a single command without opening a shell:
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py check_sla
```

---

## Resetting Everything (Clean Slate)

If something goes wrong or you want a fresh start:

```bash
# Stop containers and delete all data (PostgreSQL volume is wiped)
docker compose down -v

# Rebuild and start fresh
docker compose up --build
```

This re-runs migrations and seed_data, giving you a clean database with the default test users.

---

## What's Happening Under the Hood

```
docker compose up --build
        │
        ├── Builds the "web" container from Dockerfile
        │     ├── Base: python:3.11-slim (Linux)
        │     ├── Installs system dependencies
        │     ├── pip install -r requirements.txt
        │     └── Copies project files
        │
        ├── Pulls postgres:17-alpine image (if not cached)
        │
        ├── Starts "db" container (PostgreSQL)
        │     └── Waits until pg_isready passes (healthcheck)
        │
        └── Starts "web" container (Django)
              ├── python manage.py migrate --noinput
              ├── python manage.py seed_data
              └── python manage.py runserver 0.0.0.0:8000
```

---

## Access Points

| URL | What You'll See |
|---|---|
| `http://localhost:8000/` | Frontend Dashboard |
| `http://localhost:8000/admin/` | Django Admin Panel |
| `http://localhost:8000/api/v1/` | DRF Browsable API |

---

## Troubleshooting

**Port 8000 is already in use**
```bash
# Find what's using it (Windows)
netstat -ano | findstr :8000

# Kill the process, or change the port in docker-compose.yml:
ports:
  - "8080:8000"   # Then access via localhost:8080
```

**"Cannot connect to Docker daemon"**
Docker Desktop is not running. Open Docker Desktop and wait for it to start.

**Database connection refused / migrations fail**
The PostgreSQL container wasn't ready in time. Just run `docker compose up` again — the healthcheck ensures the db is ready before the web container starts.

**Changes to Python code not reflected**
Rebuild the image: `docker compose up --build`

**Want to see what's inside the container**
```bash
docker compose exec web sh
ls /app          # Project files
pip list         # Installed packages
```
