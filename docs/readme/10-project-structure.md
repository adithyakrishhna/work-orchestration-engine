# Project Structure & Integration

## Project Structure

```
work-orchestration-engine/
├── config/                          # Project configuration
│   ├── settings.py                  # Database, auth, REST, CORS, JWT settings
│   ├── urls.py                      # Root URL routing
│   ├── wsgi.py                      # WSGI server entry point
│   └── asgi.py                      # ASGI server entry point
│
├── core/                            # Main application (backend brain)
│   ├── models.py                    # 8 database models
│   ├── admin.py                     # Django admin panel configuration
│   ├── urls.py                      # Core API URL routing
│   ├── auth_urls.py                 # Auth endpoint routing
│   │
│   ├── serializers/                 # JSON ↔ Python conversion layer
│   │   ├── organization.py          # Org serializer with dynamic config fields
│   │   ├── user.py                  # User + UserCreate with role validation
│   │   ├── team.py                  # Team with nested lead details
│   │   ├── workflow.py              # Workflow with nested transition rules
│   │   ├── task.py                  # TaskList (light) + TaskDetail (full)
│   │   └── audit.py                 # Read-only, immutable audit serializer
│   │
│   ├── views/                       # API endpoint handlers
│   │   ├── organization.py          # Organization CRUD
│   │   ├── user.py                  # User CRUD + /me endpoint
│   │   ├── team.py                  # Team CRUD
│   │   ├── workflow.py              # Workflow + Transition CRUD
│   │   ├── task.py                  # Task CRUD + transition + assign endpoints
│   │   ├── audit.py                 # Read-only audit log listing
│   │   ├── dashboard.py             # Analytics, SLA check, team performance
│   │   ├── auth.py                  # Register + Logout views
│   │   └── setup.py                 # One-click organization setup endpoint
│   │
│   ├── permissions/
│   │   └── rbac.py                  # IsAdmin, IsManagerOrAbove, IsSameOrganization, TaskPermission
│   │
│   ├── services/                    # Business logic (separated from views)
│   │   ├── state_machine.py         # transition(), assign_task(), get_available_transitions()
│   │   ├── sla_service.py           # check_all_sla(), get_sla_summary()
│   │   └── dashboard_service.py     # get_overview(), get_team_performance(), get_recent_activity()
│   │
│   └── management/commands/
│       ├── seed_data.py             # Populate sample data for testing
│       └── check_sla.py             # Run SLA breach check from terminal
│
├── ai_engine/                       # AI/ML intelligence module
│   ├── priority_scorer.py           # 5-factor weighted priority scoring engine
│   ├── task_router.py               # Skill + workload + performance matching
│   ├── nl_query.py                  # Natural language → database query parser
│   ├── views.py                     # AI API endpoints (score, route, query)
│   └── urls.py                      # AI URL routing
│
├── frontend/
│   └── dashboard.html               # Complete SPA dashboard (single file, no build tools)
│
├── docs/
│   ├── images/                      # Screenshots for documentation
│   └── readme/                      # Documentation split by topic
│
├── .env                             # Your secrets — gitignored, never pushed
├── .env.example                     # Template showing required env variables
├── manage.py                        # Django CLI entry point
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```

---

## How to Integrate This Into Your Own Project

### Option 1: Use the REST API from any frontend
Any application that can make HTTP requests can use this backend — React, Vue, Angular, mobile apps, CLI tools, or Postman scripts.

### Option 2: Use as a Django app
Copy `core/` and `ai_engine/` into your Django project, add to `INSTALLED_APPS`, include URLs, run migrations.

### Option 3: Customize workflows
Create your own workflows through the API or admin panel. Define custom states, transitions, and role permissions for your specific use case — support tickets, manufacturing orders, patient tracking, HR approvals, and so on.
