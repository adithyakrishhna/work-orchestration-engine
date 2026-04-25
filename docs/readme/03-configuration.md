# Zero-Code Organization Setup

This is what makes this project **production-ready for any company**. No code changes. No editing Python files. No redeployment. A new organization can set up their entire system — custom roles, priorities, task types, workflows, and admin account — with **a single API call**.

Every piece of configuration that most systems hardcode into their source code is **fully dynamic** in this engine:

| What's Dynamic | Example | How It's Configured |
|---|---|---|
| **Roles** | `admin`, `delivery_manager`, `tech_lead`, `developer`, `qa_engineer` | Defined per organization via API or admin panel |
| **Priority Levels** | `p0_blocker`, `p1_critical`, `p2_major`, `p3_minor` | Defined per organization — not locked to critical/high/medium/low |
| **Task Types** | `user_story`, `defect`, `spike`, `tech_debt`, `change_request` | Defined per organization — not locked to bug/feature/task |
| **Workflow States** | `backlog → sprint_ready → in_dev → code_review → qa → uat → deployed` | Fully configurable per workflow |
| **Transition Rules** | "Only `tech_lead` and above can move tasks from `code_review` to `qa`" | Created via API — no code needed |
| **Teams, Users, Tasks** | Everything else | All managed via API endpoints |

> **Why This Matters:** Most workflow tools force you into their terminology — their states, their roles, their priority names. This engine adapts to your company. Your company doesn't adapt to the engine.

---

## Setup API — `POST /api/v1/setup/`

Creates everything a new organization needs in a single request:
- Organization with custom roles, priorities, and task types
- Admin user with JWT tokens (ready to use immediately)
- Default workflow with the states you define
- Auto-generated transition rules (sequential flow + revert + cancellation + reopen)
- Optional team with the admin as lead

---

## Role Ordering Convention

The order of roles in the `allowed_roles` array determines access levels:

| Position | Access Level | Example |
|---|---|---|
| **First role** (index 0) | Full admin access | `admin`, `super_admin`, `owner` |
| **Second role** (index 1) | Management access — assign tasks, create users, approve transitions | `manager`, `delivery_manager`, `lead` |
| **Middle roles** (index 2 to N-2) | Worker access — create tasks, comment, transition own tasks | `developer`, `engineer`, `qa_analyst` |
| **Last role** (index N-1) | Read-only access — view only, no create/edit/delete | `viewer`, `auditor`, `guest` |

**Always place the read-only/viewer role last in the array.** The system uses array position to determine access level, so ordering matters.

> With organizations that have only 2 roles (e.g., `["admin", "dev"]`), the system uses role name detection instead of position — roles containing words like "viewer", "auditor", "guest", or "observer" are automatically treated as read-only.

---

## Example 1 — Enterprise Engineering Team

```json
POST /api/v1/setup/

{
    "org_name": "NovaSphere Engineering",
    "org_slug": "novasphere",
    "admin_username": "nova_admin",
    "admin_password": "securepass2026",
    "admin_email": "admin@novasphere.io",
    "roles": ["admin", "delivery_manager", "tech_lead", "developer", "qa_engineer", "viewer"],
    "priorities": ["p0_blocker", "p1_critical", "p2_major", "p3_minor"],
    "task_types": ["defect", "user_story", "spike", "tech_debt", "change_request"],
    "workflow_name": "Agile Delivery Pipeline",
    "workflow_states": [
        "backlog", "sprint_ready", "in_development",
        "code_review", "qa_testing", "uat", "deployed", "cancelled"
    ],
    "initial_state": "backlog",
    "final_states": ["deployed", "cancelled"],
    "team_name": "Platform Engineering"
}
```

**Response — everything ready to use:**
```json
{
    "message": "Organization 'NovaSphere Engineering' created successfully!",
    "organization": {
        "id": "a1b2c3d4-...",
        "name": "NovaSphere Engineering",
        "slug": "novasphere",
        "allowed_roles": ["admin", "delivery_manager", "tech_lead", "developer", "qa_engineer", "viewer"],
        "allowed_priorities": ["p0_blocker", "p1_critical", "p2_major", "p3_minor"],
        "allowed_task_types": ["defect", "user_story", "spike", "tech_debt", "change_request"]
    },
    "admin_user": { "id": "e5f6g7h8-...", "username": "nova_admin", "role": "admin" },
    "workflow": {
        "id": "i9j0k1l2-...",
        "name": "Agile Delivery Pipeline",
        "states": ["backlog", "sprint_ready", "in_development", "code_review", "qa_testing", "uat", "deployed", "cancelled"],
        "initial_state": "backlog",
        "final_states": ["deployed", "cancelled"],
        "transitions_created": 15
    },
    "team": { "id": "m3n4o5p6-...", "name": "Platform Engineering" },
    "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIs...",
        "refresh": "eyJhbGciOiJIUzI1NiIs..."
    }
}
```

The admin can immediately use the `access` token to start creating users, assigning roles, and managing tasks — zero additional setup.

![Setup API Response](../images/setup-response.png)
![Setup API Response 2](../images/setup-response-2.png)
![Setup API Response 3](../images/setup-response-3.png)
![Setup API Response 4](../images/setup-response-4.png)

---

## Example 2 — Small Startup (Minimal Setup)

```json
POST /api/v1/setup/

{
    "org_name": "CloudPeak Labs",
    "org_slug": "cloudpeak",
    "admin_username": "ceo_sarah",
    "admin_password": "launchday2026",
    "roles": ["admin", "lead", "dev", "intern"],
    "priorities": ["urgent", "normal", "someday"],
    "task_types": ["feature", "bugfix", "chore"],
    "workflow_states": ["todo", "building", "review", "shipped", "dropped"],
    "initial_state": "todo",
    "final_states": ["shipped", "dropped"]
}
```

---

## Example 3 — IT Support Desk

```json
POST /api/v1/setup/

{
    "org_name": "Meridian Corp IT",
    "org_slug": "meridian-it",
    "admin_username": "it_head",
    "admin_password": "support2026secure",
    "roles": ["admin", "supervisor", "l2_support", "l1_support", "requester"],
    "priorities": ["sev1_outage", "sev2_degraded", "sev3_minor", "sev4_cosmetic"],
    "task_types": ["incident", "service_request", "change", "problem"],
    "workflow_name": "ITIL Incident Flow",
    "workflow_states": ["reported", "triaged", "investigating", "pending_vendor", "resolved", "closed"],
    "initial_state": "reported",
    "final_states": ["resolved", "closed"],
    "team_name": "L2 Support Team"
}
```

---

## After Setup — What Comes Next

1. **Create users** → `POST /api/v1/users/` with any role from the org's `allowed_roles`
2. **Create teams** → `POST /api/v1/teams/` and assign members
3. **Create tasks** → `POST /api/v1/tasks/` with priorities and types from the org's config
4. **Manage workflows** → Add transition rules via `POST /api/v1/transitions/`
5. **Use the dashboard** → Login at `http://your-server/` to see everything visually

All validation is automatic — if a user tries to create a task with a priority not in their org's config, the API returns:
```json
{
    "priority": "Invalid priority 'critical'. Allowed: ['p0_blocker', 'p1_critical', 'p2_major', 'p3_minor']"
}
```

The system guides users toward correct values without anyone reading documentation.

---

## Configuration via Admin Panel

Organizations can also be configured through Django's admin panel at `/admin/`. The Organization edit page shows three editable JSON fields — `allowed_roles`, `allowed_priorities`, and `allowed_task_types` — that can be modified at any time.

![Org Config Admin](../images/org-config-admin.png)

---

## Environment Variables (.env)

| Variable | Description |
|---|---|
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | Database username |
| `DB_PASSWORD` | Database password (**never commit this**) |
| `DB_HOST` | Database host (usually `localhost`) |
| `DB_PORT` | Database port (usually `5432`) |
| `SECRET_KEY` | Django secret key for cryptographic signing |

## Key Django Settings

| Setting | Value | Purpose |
|---|---|---|
| `ACCESS_TOKEN_LIFETIME` | 1 hour | JWT access token duration |
| `REFRESH_TOKEN_LIFETIME` | 7 days | JWT refresh token duration |
| `ROTATE_REFRESH_TOKENS` | True | New refresh token on each use |
| `BLACKLIST_AFTER_ROTATION` | True | Old refresh tokens invalidated |
| `PAGE_SIZE` | 20 | Default pagination size |
