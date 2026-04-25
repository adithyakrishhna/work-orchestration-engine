# Tech Stack & Architecture

## Tech Stack

| Layer | Technology | Why This Choice |
|---|---|---|
| **Backend Framework** | Django 5.x | Battle-tested, built-in ORM, admin panel, migrations — used by Instagram, Pinterest, Mozilla |
| **API Layer** | Django REST Framework | Industry standard for building RESTful APIs in Python |
| **Database** | PostgreSQL | The most advanced open-source relational database — used by every major product company |
| **Authentication** | SimpleJWT | JWT auth with access/refresh token pattern — the modern standard for API auth |
| **AI/ML** | scikit-learn, NLTK | Lightweight ML libraries — no expensive GPU or paid API needed |
| **API Filtering** | django-filter | Declarative filtering on API endpoints |
| **CORS** | django-cors-headers | Allows frontend to communicate with backend across different origins |
| **Secrets Management** | python-dotenv | Environment variables for sensitive config — never commit passwords to Git |

> **A Note on the Frontend:** This is a backend-focused project. The frontend dashboard was built purely to demonstrate the backend's capabilities visually — it is written entirely in a **single HTML file** (`frontend/dashboard.html`) using vanilla HTML, CSS, and JavaScript with zero build tools, zero frameworks, and zero dependencies. Developers integrating this engine can replace, modify, or completely remove the frontend without affecting any backend functionality.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                 │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐    │
│   │   Frontend   │   │   DRF        │   │   Any External App   │    │
│   │   Dashboard  │   │   Browsable  │   │   (Mobile, CLI,      │    │
│   │   (HTML/JS)  │   │   API        │   │    Postman, curl)    │    │
│   └──────┬───────┘   └──────┬───────┘   └──────────┬───────────┘    │
└──────────┼──────────────────┼──────────────────────┼───────────────-┘
           ▼                  ▼                       ▼
    ┌──────────────────────────────────────────────────────────┐
    │              JWT AUTHENTICATION LAYER                    │
    │     Access Token (1 hour) + Refresh Token (7 days)       │
    │         Token Rotation + Blacklisting on Logout          │
    └────────────────────────┬─────────────────────────────────┘
                             ▼
    ┌──────────────────────────────────────────────────────────┐
    │                    API LAYER (20+ REST Endpoints)        │
    │  /tasks/ /users/ /teams/ /workflows/ /transitions/       │
    │  /comments/ /audit-logs/ /dashboard/ /ai/                │
    └────────────────────────┬─────────────────────────────────┘
                             ▼
    ┌──────────────────────────────────────────────────────────┐
    │               PERMISSION LAYER (Dual RBAC)               │
    │  Layer 1: API Level — "Can this user hit this endpoint?" │
    │  Layer 2: Business — "Can this role do this action?"     │
    └────────────────────────┬─────────────────────────────────┘
                             ▼
    ┌──────────────────────────────────────────────────────────┐
    │                  SERVICE LAYER                           │
    │  StateMachineService │ SLAService │ DashboardService     │
    └────────────────────────┬─────────────────────────────────┘
                             ▼
    ┌──────────────────────────────────────────────────────────┐
    │                   AI ENGINE                              │
    │  PriorityScorer │ TaskRouter │ NLQueryEngine             │
    └────────────────────────┬─────────────────────────────────┘
                             ▼
    ┌──────────────────────────────────────────────────────────┐
    │                   DATA LAYER (8 Models)                  │
    │  Organization │ User │ Team │ WorkflowConfig             │
    │  TransitionRule │ Task │ Comment │ AuditLog              │
    └────────────────────────┬─────────────────────────────────┘
                             ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    └─────────────────┘
```

---

## Database Design (8 Interconnected Models)

All models use **UUIDs** as primary keys instead of auto-incrementing integers — this is a security best practice because sequential IDs leak information.

![Admin Panel Models](../images/admin-models.png)

### Model Relationships

```
Organization (1)
  ├── has many → User (N)
  │               ├── created → Task (N)
  │               ├── assigned to → Task (N)
  │               ├── leads → Team (N)
  │               └── performed → AuditLog (N)
  ├── has many → Team (N)
  │               └── has many → Task (N)
  ├── has many → WorkflowConfig (N)
  │               └── has many → TransitionRule (N)
  └── has many → Task (N)
                  ├── has many → Comment (N)
                  └── has many → AuditLog (N)
```

### Key Model Details

**Organization** — Top-level entity. Every piece of data belongs to an organization (multi-tenancy). Fields: `id` (UUID), `name`, `slug` (used for task key prefix like SUNS-0001).

**User** — Extends Django's built-in user. Fields: `role` (admin/manager/engineer/viewer), `skills` (JSON array like `["python", "django"]`), `max_concurrent_tasks` (workload limit, default 5).

**WorkflowConfig** — Defines the state machine. Fields: `allowed_states` (JSON array), `initial_state`, `final_states` (JSON array).

**TransitionRule** — Controls who can move tasks between states. Fields: `from_state`, `to_state`, `allowed_roles` (JSON array). Example: `from: "review"`, `to: "testing"`, `roles: ["admin", "manager"]`.

**Task** — Core work item. Fields: `task_key` (auto-generated like SUNS-0001), `current_state`, `priority`, `task_type`, `tags` (JSON), `due_date`, `sla_breached`, `ai_priority_score`, `ai_estimated_hours`, `resolved_at`.

**AuditLog** — Immutable record. Fields: `action` (created/state_changed/assigned/commented/sla_breached), `old_value` (JSON), `new_value` (JSON), `reason`. Cannot be edited or deleted via API.
