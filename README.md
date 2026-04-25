# ⚡ AI-Powered Work Orchestration Engine

> A production-grade backend engine for managing tasks, enforcing workflows, controlling access, and tracking every state change — built with Django, DRF, and PostgreSQL.

![Dashboard](docs/images/dashboard.png)

---

## Why This Project Stands Out

- **Zero-setup onboarding** — A new organization configures roles, priorities, task types, workflows, and admin account with a single API call. No code changes. No redeployment.
- **Configurable state machine** — Define your own workflow states and transition rules per organization. The engine adapts to your company, not the other way around.
- **Dual-layer RBAC** — Authorization enforced at both API level and business logic level independently.
- **AI intelligence layer** — Fully local: multi-factor priority scoring, intelligent task routing, and natural language queries with no paid APIs.
- **Enterprise audit trail** — Every action logged immutably with old/new values, actor, timestamp, and reason. Even admins cannot edit or delete logs.
- **Multi-tenant isolation** — Users from different organizations can never access each other's data, even with direct UUIDs.
- **Production-ready JWT auth** — Access tokens, refresh tokens, rotation, and blacklisting on logout.

---

## Quick Start

```bash
git clone https://github.com/adithyakrishhna/work-orchestration-engine.git
cd work-orchestration-engine
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
# Create .env from .env.example, then:
psql -U postgres -c "CREATE DATABASE work_orchestration;"
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Then open `http://127.0.0.1:8000/` — log in with `admin_user / testpass123`.

---

## Documentation

| Topic | What You'll Find |
|---|---|
| [Features & Design Goals](docs/readme/01-features.md) | What makes this system strong — state machine, RBAC, audit trail, AI, multi-tenancy |
| [Getting Started](docs/readme/02-getting-started.md) | Prerequisites, full installation steps, access points, test credentials |
| [Organization Setup & Configuration](docs/readme/03-configuration.md) | Zero-code setup API, role ordering, setup examples, env variables |
| [Architecture & Database](docs/readme/04-architecture.md) | Tech stack, system architecture diagram, 8-model database design |
| [Backend Internals](docs/readme/05-backend-internals.md) | State machine engine, RBAC layers, audit trail, SLA detection, error handling |
| [AI Engine](docs/readme/06-ai-engine.md) | Priority scoring, intelligent task routing, natural language queries |
| [JWT Authentication](docs/readme/07-authentication.md) | How tokens work, timeline walkthrough, auth endpoints |
| [API, Admin & Frontend](docs/readme/08-api-and-interfaces.md) | Full API overview, Django admin panel, DRF browsable API, frontend dashboard |
| [Screenshots](docs/readme/09-screenshots.md) | Visual walkthrough of every major feature |
| [Project Structure & Integration](docs/readme/10-project-structure.md) | File structure, integration options |

For the complete API reference with curl commands and lifecycle examples: **[📖 API_REFERENCE.md](API_REFERENCE.md)**

---

## Access Points (after starting the server)

| URL | What You'll See |
|---|---|
| `http://127.0.0.1:8000/` | Frontend Dashboard |
| `http://127.0.0.1:8000/admin/` | Django Admin Panel |
| `http://127.0.0.1:8000/api/v1/` | DRF Browsable API |

---

## Contributing

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push and open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

**Built by [Adithya Krishna](https://github.com/adithyakrishhna)** — *⭐ Star this repo if you find it useful!*
