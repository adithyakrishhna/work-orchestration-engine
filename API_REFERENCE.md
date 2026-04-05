# 📡 Complete API Reference — Work Orchestration Engine

> Every endpoint, every parameter, every response — explained with ready-to-use examples.

**Base URL:** `http://127.0.0.1:8000/api/v1`

**Authentication:** All endpoints except Setup, Login, and Register require a JWT token:
```
Authorization: Bearer <your-access-token>
```

---

## Table of Contents

1. [Quick Start — Setup Your Organization](#1-quick-start--setup-your-organization)
2. [Authentication](#2-authentication)
3. [Organizations](#3-organizations)
4. [Users](#4-users)
5. [Teams](#5-teams)
6. [Workflows](#6-workflows)
7. [Transition Rules](#7-transition-rules)
8. [Tasks](#8-tasks)
9. [Task Actions (Transition, Assign)](#9-task-actions)
10. [Comments](#10-comments)
11. [Audit Logs](#11-audit-logs)
12. [Dashboard & Analytics](#12-dashboard--analytics)
13. [AI Engine](#13-ai-engine)
14. [Error Reference](#14-error-reference)

---

## How to Read This Document

- **`{id}`** = A UUID. You get UUIDs from list endpoints (e.g., `GET /tasks/` returns each task's `id`).
- **Permission: Manager+** = Requires the first or second role in your org's `allowed_roles` (typically admin + manager/lead).
- **Permission: Admin** = Only the first role in `allowed_roles` (typically admin).
- **Permission: Authenticated** = Any logged-in user.
- **Permission: Public** = No token needed.
- Replace `<token>` with your actual JWT access token in all examples.

---

## 1. Quick Start — Setup Your Organization

**This is the first API call any new user makes.** It creates everything needed to start using the system.

### `POST /setup/`

**Permission:** Public (no authentication required)

**What it creates automatically:**
- Organization with your custom roles, priorities, and task types
- Admin user with JWT tokens (ready to use immediately)
- Default workflow with your custom states
- Auto-generated transition rules (sequential flow + revert + cancellation + reopen)
- Optional team with the admin as lead

### Role Ordering Convention

The order of roles in the `allowed_roles` array determines access levels:

| Position | Access Level | Example |
|---|---|---|
| **First role** (index 0) | Full admin access — can manage everything | `admin`, `super_admin`, `owner` |
| **Second role** (index 1) | Management access — can assign tasks, create users, approve transitions | `manager`, `delivery_manager`, `lead` |
| **Middle roles** (index 2 to N-2) | Worker access — can create tasks, comment, transition own tasks | `developer`, `engineer`, `qa_analyst` |
| **Last role** (index N-1) | Read-only access — can only view data, no create/edit/delete | `viewer`, `auditor`, `guest` |

**Example with 6 roles:**
```json
"roles": ["admin", "delivery_manager", "tech_lead", "developer", "qa_engineer", "viewer"]
```
- `admin` → full access
- `delivery_manager` → management level
- `tech_lead`, `developer`, `qa_engineer` → workers
- `viewer` → read-only

**Important:** Always place the read-only/viewer role **last** in the array. The system uses array position to determine access level, so the ordering matters. With organizations that have only 2 roles (e.g., `["admin", "dev"]`), the system uses role name detection instead of position — roles containing words like "viewer", "auditor", "guest", or "observer" are automatically treated as read-only.

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/setup/ \
  -H "Content-Type: application/json" \
  -d '{
    "org_name": "NovaSphere Engineering",
    "org_slug": "novasphere",
    "admin_username": "nova_admin",
    "admin_password": "securepass2026",
    "admin_email": "admin@novasphere.io",
    "roles": ["admin", "delivery_manager", "tech_lead", "developer", "qa_engineer", "viewer"],
    "priorities": ["p0_blocker", "p1_critical", "p2_major", "p3_minor"],
    "task_types": ["defect", "user_story", "spike", "tech_debt", "change_request"],
    "workflow_name": "Agile Delivery Pipeline",
    "workflow_states": ["backlog", "sprint_ready", "in_development", "code_review", "qa_testing", "uat", "deployed", "cancelled"],
    "initial_state": "backlog",
    "final_states": ["deployed", "cancelled"],
    "team_name": "Platform Engineering"
  }'
```

**Required fields:** `org_name`, `org_slug`, `admin_username`, `admin_password`

**Optional fields (with defaults):**
| Field | Default if not provided |
|---|---|
| `roles` | `["admin", "manager", "engineer", "viewer"]` |
| `priorities` | `["critical", "high", "medium", "low"]` |
| `task_types` | `["bug", "feature", "task", "improvement"]` |
| `workflow_states` | `["open", "in_progress", "review", "testing", "done", "cancelled"]` |
| `initial_state` | First state in the list |
| `final_states` | Last two states |
| `team_name` | No team created |

**Response (201 Created):**
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
    "admin_user": {
        "id": "e5f6g7h8-...",
        "username": "nova_admin",
        "role": "admin"
    },
    "workflow": {
        "id": "i9j0k1l2-...",
        "name": "Agile Delivery Pipeline",
        "states": ["backlog", "sprint_ready", "in_development", "code_review", "qa_testing", "uat", "deployed", "cancelled"],
        "transitions_created": 15
    },
    "team": {
        "id": "m3n4o5p6-...",
        "name": "Platform Engineering"
    },
    "tokens": {
        "access": "eyJhbGciOiJIUzI1NiIs...",
        "refresh": "eyJhbGciOiJIUzI1NiIs..."
    }
}
```

**What to do next:** Copy the `access` token from the response and use it in all subsequent API calls.

---

## 2. Authentication

### `POST /auth/login/`

**Permission:** Public

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "nova_admin", "password": "securepass2026"}'
```

**Response:**
```json
{
    "access": "eyJhbG...",
    "refresh": "eyJhbG..."
}
```

Save both tokens. Use `access` for all API calls. Use `refresh` to get a new access token when it expires.

---

### `POST /auth/register/`

**Permission:** Public

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "new_user",
    "password": "securepass123",
    "email": "user@example.com"
  }'
```

**Response:** Returns access and refresh tokens (same as login).

---

### `POST /auth/refresh/`

**Permission:** Public (requires valid refresh token)

Use this when your access token expires (after 1 hour). You don't need to login again.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your-refresh-token"}'
```

**Response:**
```json
{
    "access": "new-access-token"
}
```

---

### `POST /auth/logout/`

**Permission:** Authenticated

Permanently destroys the refresh token so it can never be used again.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh": "your-refresh-token"}'
```

**Response:**
```json
{"message": "Logged out successfully"}
```

---

## 3. Organizations

### List Organizations — `GET /organizations/`

**Permission:** Authenticated (admins see all orgs, others see only their own)

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/organizations/
```

**Response:**
```json
{
    "results": [
        {
            "id": "a1b2c3d4-...",
            "name": "NovaSphere Engineering",
            "slug": "novasphere",
            "allowed_roles": ["admin", "delivery_manager", "tech_lead", "developer", "qa_engineer", "viewer"],
            "allowed_priorities": ["p0_blocker", "p1_critical", "p2_major", "p3_minor"],
            "allowed_task_types": ["defect", "user_story", "spike", "tech_debt", "change_request"],
            "member_count": 5,
            "team_count": 2,
            "created_at": "2026-04-01T09:00:00Z"
        }
    ]
}
```

### Create Organization — `POST /organizations/`

**Permission:** Admin

```bash
curl -X POST http://127.0.0.1:8000/api/v1/organizations/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Corp", "slug": "newcorp"}'
```

### Update Organization — `PATCH /organizations/{id}/`

**Permission:** Admin

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/organizations/{id}/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'
```

### Delete Organization — `DELETE /organizations/{id}/`

**Permission:** Admin

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/organizations/{id}/ \
  -H "Authorization: Bearer <token>"
```

---

## 4. Users

### List Users — `GET /users/`

**Permission:** Authenticated (shows users in your organization only)

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/users/
```

**Response:**
```json
{
    "results": [
        {
            "id": "u1u2u3u4-...",
            "username": "nova_admin",
            "email": "admin@novasphere.io",
            "role": "admin",
            "organization": "a1b2c3d4-...",
            "skills": ["python", "django", "aws"],
            "max_concurrent_tasks": 5,
            "active_task_count": 2
        }
    ]
}
```

### Get My Profile — `GET /users/me/`

**Permission:** Authenticated

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/users/me/
```

Returns the currently logged-in user's full profile.

### Create User — `POST /users/`

**Permission:** Manager+ (first two roles in your org)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/users/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice_dev",
    "password": "securepass123",
    "email": "alice@novasphere.io",
    "role": "developer",
    "skills": ["python", "react", "docker"]
  }'
```

**Important:** The `role` must be one of the values in your organization's `allowed_roles`. If you try `"role": "engineer"` but your org only has `["admin", "developer", "viewer"]`, you'll get a validation error.

### Update User — `PATCH /users/{id}/`

**Permission:** Authenticated (users can update their own profile)

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/users/{id}/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "skills": ["python", "django", "kubernetes"],
    "max_concurrent_tasks": 8
  }'
```

### Delete User — `DELETE /users/{id}/`

**Permission:** Admin

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/users/{id}/ \
  -H "Authorization: Bearer <token>"
```

---

## 5. Teams

### List Teams — `GET /teams/`

**Permission:** Authenticated

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/teams/
```

### Create Team — `POST /teams/`

**Permission:** Manager+

```bash
curl -X POST http://127.0.0.1:8000/api/v1/teams/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Backend Team",
    "lead": "<user-uuid-from-GET-/users/>",
    "members": ["<user-uuid-1>", "<user-uuid-2>"]
  }'
```

**Where to get user UUIDs:** Call `GET /users/` first — each user has an `"id"` field.

### Update Team — `PATCH /teams/{id}/`

**Permission:** Manager+

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/teams/{id}/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Platform Team",
    "lead": "<new-lead-uuid>",
    "members": ["<uuid-1>", "<uuid-2>", "<uuid-3>"]
  }'
```

### Delete Team — `DELETE /teams/{id}/`

**Permission:** Manager+

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/teams/{id}/ \
  -H "Authorization: Bearer <token>"
```

---

## 6. Workflows

A workflow defines the state machine — what states exist, which is the starting state, and which states mark completion.

### List Workflows — `GET /workflows/`

**Permission:** Authenticated

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/workflows/
```

**Response:**
```json
{
    "results": [
        {
            "id": "w1w2w3w4-...",
            "name": "Agile Delivery Pipeline",
            "organization": "a1b2c3d4-...",
            "is_default": true,
            "allowed_states": ["backlog", "sprint_ready", "in_development", "code_review", "qa_testing", "uat", "deployed", "cancelled"],
            "initial_state": "backlog",
            "final_states": ["deployed", "cancelled"],
            "transitions": [
                {
                    "id": "t1t2t3t4-...",
                    "from_state": "backlog",
                    "to_state": "sprint_ready",
                    "allowed_roles": ["admin", "delivery_manager", "tech_lead", "developer", "qa_engineer"]
                }
            ]
        }
    ]
}
```

### Create Workflow — `POST /workflows/`

**Permission:** Admin

```bash
curl -X POST http://127.0.0.1:8000/api/v1/workflows/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hotfix Workflow",
    "allowed_states": ["reported", "fixing", "testing", "deployed", "closed"],
    "initial_state": "reported",
    "final_states": ["deployed", "closed"],
    "is_default": false
  }'
```

### Update Workflow — `PATCH /workflows/{id}/`

**Permission:** Admin

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/workflows/{id}/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Workflow Name",
    "allowed_states": ["open", "doing", "review", "done"],
    "initial_state": "open",
    "final_states": ["done"]
  }'
```

### Delete Workflow — `DELETE /workflows/{id}/`

**Permission:** Admin

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/workflows/{id}/ \
  -H "Authorization: Bearer <token>"
```

---

## 7. Transition Rules

Transition rules define who can move tasks between specific states. Without a rule, the transition is blocked.

### List Transitions — `GET /transitions/`

**Permission:** Authenticated

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/transitions/
```

### Create Transition — `POST /transitions/`

**Permission:** Admin

```bash
curl -X POST http://127.0.0.1:8000/api/v1/transitions/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow": "<workflow-uuid-from-GET-/workflows/>",
    "from_state": "code_review",
    "to_state": "qa_testing",
    "allowed_roles": ["admin", "delivery_manager", "tech_lead"]
  }'
```

**Validation:** Both `from_state` and `to_state` must exist in the workflow's `allowed_states`. The API will reject invalid states with a clear error message.

### Delete Transition — `DELETE /transitions/{id}/`

**Permission:** Admin

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/transitions/{id}/ \
  -H "Authorization: Bearer <token>"
```

---

## 8. Tasks

### List Tasks — `GET /tasks/`

**Permission:** Authenticated (shows only your organization's tasks)

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/tasks/
```

**Filtering, searching, and sorting (all combinable):**

```bash
# Filter by state
GET /tasks/?current_state=backlog

# Filter by priority
GET /tasks/?priority=p0_blocker

# Filter by team
GET /tasks/?team=<team-uuid>

# Filter by assignee
GET /tasks/?assigned_to=<user-uuid>

# Filter SLA breached tasks only
GET /tasks/?sla_breached=true

# Search by title or task key
GET /tasks/?search=login+crash

# Sort by field (prefix with - for descending)
GET /tasks/?ordering=-ai_priority_score
GET /tasks/?ordering=created_at

# Combine everything
GET /tasks/?current_state=backlog&priority=p0_blocker&ordering=-created_at&search=api
```

### Get Single Task — `GET /tasks/{id}/`

**Permission:** Authenticated

Returns full task details including nested comments.

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/tasks/{id}/
```

### Create Task — `POST /tasks/`

**Permission:** Engineer+ (all roles except the last/viewer role)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tasks/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix authentication timeout on Safari",
    "description": "Users report session expires after 5 minutes on Safari 17",
    "priority": "p1_critical",
    "task_type": "defect",
    "workflow": "<workflow-uuid-from-GET-/workflows/>",
    "tags": ["frontend", "auth", "safari"],
    "team": "<team-uuid-from-GET-/teams/>",
    "due_date": "2026-04-10T17:00:00Z"
  }'
```

**Required:** `title`, `workflow`

**Optional:** `description`, `priority`, `task_type`, `tags`, `team`, `due_date`

**Validation:** `priority` must be in your org's `allowed_priorities`. `task_type` must be in your org's `allowed_task_types`. The API will tell you the allowed values if you send an invalid one.

**Response (201 Created):**
```json
{
    "id": "task-uuid-here",
    "task_key": "NOVA-0001",
    "title": "Fix authentication timeout on Safari",
    "current_state": "backlog",
    "priority": "p1_critical",
    "task_type": "defect",
    "created_by": "nova_admin",
    "assigned_to": null,
    "sla_breached": false,
    "ai_priority_score": null,
    "created_at": "2026-04-03T10:00:00Z"
}
```

The `task_key` (e.g., NOVA-0001) is auto-generated from your org slug.

### Update Task — `PATCH /tasks/{id}/`

**Permission:** Task owner or Manager+

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/tasks/{id}/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "priority": "p0_blocker",
    "due_date": "2026-04-05T12:00:00Z",
    "tags": ["frontend", "auth", "safari", "urgent"],
    "team": "<team-uuid>"
  }'
```

### Delete Task — `DELETE /tasks/{id}/`

**Permission:** Admin only

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/tasks/{id}/ \
  -H "Authorization: Bearer <token>"
```

---

## 9. Task Actions

### Check Available Transitions — `GET /tasks/{id}/available-transitions/`

**Permission:** Authenticated

**Always call this before attempting a transition** — it tells you what states are available for your role.

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/tasks/{id}/available-transitions/
```

**Response:**
```json
{
    "current_state": "backlog",
    "available_transitions": [
        {"to_state": "sprint_ready", "allowed_roles": ["admin", "delivery_manager", "tech_lead", "developer"]},
        {"to_state": "cancelled", "allowed_roles": ["admin", "delivery_manager"]}
    ]
}
```

### Transition a Task — `POST /tasks/{id}/transition/`

**Permission:** Role-dependent (checked against TransitionRule)

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tasks/{id}/transition/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "to_state": "sprint_ready",
    "reason": "Groomed and estimated in sprint planning"
  }'
```

**What the state machine validates (5 checks):**
1. Target state is not the current state
2. Target state exists in the workflow
3. A transition rule exists for this from→to path
4. Your role is in the rule's allowed_roles
5. Task must be assigned before moving past the initial state

If any check fails, you get a specific error message telling you exactly what went wrong.

### Assign a Task — `POST /tasks/{id}/assign/`

**Permission:** Manager+

```bash
# Step 1: Get the user's UUID
curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/v1/users/
# Find the user you want → copy their "id"

# Step 2: Assign
curl -X POST http://127.0.0.1:8000/api/v1/tasks/{id}/assign/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<user-uuid-from-step-1>",
    "reason": "Best skill match for Safari debugging"
  }'
```

**Validation:** The system checks that the assignee hasn't exceeded their `max_concurrent_tasks` limit and belongs to the same organization.

---

## 10. Comments

### List Comments — `GET /comments/`

**Permission:** Authenticated (shows only comments on your org's tasks)

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/comments/
```

### Add Comment — `POST /comments/`

**Permission:** Authenticated

```bash
curl -X POST http://127.0.0.1:8000/api/v1/comments/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "<task-uuid-from-GET-/tasks/>",
    "content": "Found the root cause — its a WebKit rendering issue in Safari 17.2"
  }'
```

---

## 11. Audit Logs

Audit logs are **read-only**. They cannot be created, updated, or deleted through the API. The system creates them automatically.

### List Audit Logs — `GET /audit-logs/`

**Permission:** Authenticated (shows only your org's logs)

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/audit-logs/
```

**Filter by action type:**
```bash
GET /audit-logs/?action=state_changed
GET /audit-logs/?action=assigned
GET /audit-logs/?action=sla_breached
GET /audit-logs/?action=created
```

**Filter by task:**
```bash
GET /audit-logs/?task=<task-uuid>
```

**Response:**
```json
{
    "results": [
        {
            "id": "log-uuid",
            "task": "task-uuid",
            "task_key": "NOVA-0001",
            "action": "state_changed",
            "performed_by": "user-uuid",
            "performed_by_name": "nova_admin",
            "old_value": {"state": "backlog"},
            "new_value": {"state": "sprint_ready"},
            "reason": "Groomed and estimated in sprint planning",
            "timestamp": "2026-04-03T10:30:00Z"
        }
    ]
}
```

---

## 12. Dashboard & Analytics

### Overview — `GET /dashboard/overview/`

**Permission:** Authenticated

Returns task counts grouped by state, priority, and type for your organization.

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/dashboard/overview/
```

**Response:**
```json
{
    "overview": {
        "total_tasks": 25,
        "by_state": {"backlog": 5, "sprint_ready": 3, "in_development": 8, "code_review": 4, "deployed": 5},
        "by_priority": {"p0_blocker": 2, "p1_critical": 6, "p2_major": 10, "p3_minor": 7},
        "by_type": {"defect": 8, "user_story": 12, "spike": 3, "tech_debt": 2},
        "unassigned": 4,
        "last_7_days": {"created": 8, "completed": 3}
    },
    "sla": {
        "healthy": 18,
        "at_risk": 3,
        "breached": 4,
        "breach_rate": "16.0"
    }
}
```

### Team Performance — `GET /dashboard/team-performance/`

**Permission:** Authenticated

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/dashboard/team-performance/
```

**Response:**
```json
{
    "team_performance": [
        {
            "username": "alice_dev",
            "active_tasks": 3,
            "completed_tasks": 12,
            "sla_breaches": 1,
            "avg_resolution_hours": 18.5,
            "workload_percentage": 60,
            "max_concurrent_tasks": 5
        }
    ]
}
```

### Recent Activity — `GET /dashboard/activity/`

**Permission:** Authenticated

```bash
curl -H "Authorization: Bearer <token>" \
  http://127.0.0.1:8000/api/v1/dashboard/activity/
```

Returns the last 20 actions (state changes, assignments, comments, etc.).

### SLA Check — `POST /dashboard/sla-check/`

**Permission:** Authenticated

Scans all active tasks in your organization, flags overdue tasks, identifies at-risk tasks (< 24 hours remaining).

```bash
curl -X POST http://127.0.0.1:8000/api/v1/dashboard/sla-check/ \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
    "results": {
        "checked": 15,
        "breached": 2,
        "breached_tasks": [
            {
                "id": "task-uuid",
                "task_key": "NOVA-0003",
                "title": "Fix payment gateway timeout",
                "priority": "p0_blocker",
                "assigned_to": "alice_dev",
                "due_date": "2026-04-02T12:00:00Z",
                "hours_overdue": 22.5
            }
        ],
        "at_risk_tasks": [
            {
                "id": "task-uuid",
                "task_key": "NOVA-0007",
                "title": "Update API documentation",
                "priority": "p3_minor",
                "assigned_to": "bob_dev",
                "due_date": "2026-04-04T09:00:00Z",
                "hours_remaining": 18.3
            }
        ]
    }
}
```

---

## 13. AI Engine

### Score a Task's Priority — `POST /ai/score-priority/`

**Permission:** Authenticated

Analyzes a task using 5 weighted factors and returns a priority score between 0.0 and 1.0 with an explanation.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/score-priority/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"task_id": "<task-uuid>"}'
```

**Response:**
```json
{
    "task_key": "NOVA-0001",
    "priority_analysis": {
        "score": 0.78,
        "explanation": "AI Priority: HIGH — Primary driver: urgency keywords detected",
        "factors": {
            "keyword_score": 0.85,
            "type_score": 0.80,
            "priority_score": 0.75,
            "deadline_score": 0.90,
            "age_score": 0.40
        }
    },
    "estimated_hours": 6.5
}
```

### Score All Tasks — `POST /ai/score-all/`

**Permission:** Authenticated

Scores every active (non-completed) task in your organization at once.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/score-all/ \
  -H "Authorization: Bearer <token>"
```

**Response:**
```json
{
    "scored_count": 15,
    "results": [
        {"task_key": "NOVA-0001", "score": 0.78},
        {"task_key": "NOVA-0002", "score": 0.45},
        {"task_key": "NOVA-0003", "score": 0.92}
    ]
}
```

### Recommend Assignee — `POST /ai/recommend-assignee/`

**Permission:** Authenticated

Ranks all eligible engineers by skill match, workload, and past performance.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/recommend-assignee/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"task_id": "<task-uuid>"}'
```

**Response:**
```json
{
    "task_key": "NOVA-0001",
    "recommendations": [
        {
            "username": "alice_dev",
            "total_score": 0.82,
            "reasoning": "alice_dev: strong skill match, high availability, excellent track record",
            "factors": {
                "skill_match": 1.0,
                "workload": 0.80,
                "performance": 0.70
            }
        },
        {
            "username": "bob_dev",
            "total_score": 0.45,
            "reasoning": "bob_dev: no matching skills, high availability, solid track record",
            "factors": {
                "skill_match": 0.0,
                "workload": 1.0,
                "performance": 0.50
            }
        }
    ]
}
```

### Auto-Assign — `POST /ai/auto-assign/`

**Permission:** Manager+ (first two roles only)

Automatically assigns the task to the highest-ranked candidate from the recommendation engine.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/auto-assign/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"task_id": "<task-uuid>"}'
```

**Response:**
```json
{
    "message": "Task NOVA-0001 auto-assigned to alice_dev (score: 82%)",
    "assigned_to": "alice_dev",
    "score": 0.82
}
```

### Natural Language Query — `POST /ai/query/`

**Permission:** Authenticated

Convert plain English questions into database queries.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/ai/query/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"question": "show me all critical defects assigned to alice"}'
```

**Example queries you can try:**
| What You Type | What It Finds |
|---|---|
| `"critical defects"` | priority = p0/p1 AND type = defect |
| `"unassigned tasks"` | assigned_to IS NULL |
| `"tasks assigned to alice_dev"` | assigned_to = alice_dev |
| `"overdue tasks"` | sla_breached = true |
| `"my tasks"` | assigned_to = current user |
| `"high priority user stories in review"` | priority = high AND type = user_story AND state = review |

**Response:**
```json
{
    "question": "show me all critical defects assigned to alice",
    "explanation": "Showing tasks matching: priority=critical, type=defect, assigned to alice_dev",
    "parsed_filters": {
        "priority": "critical",
        "task_type": "defect",
        "assigned_to": "alice_dev"
    },
    "results": [
        {
            "task_key": "NOVA-0003",
            "title": "Fix payment gateway timeout",
            "state": "in_development",
            "priority": "p1_critical",
            "assigned_to": "alice_dev"
        }
    ]
}
```

---

## 14. Error Reference

### Authentication Errors

| HTTP Status | Error | Cause |
|---|---|---|
| 401 | `Authentication credentials were not provided.` | No `Authorization` header sent |
| 401 | `Given token not valid for any token type` | Access token expired — use refresh endpoint |
| 401 | `Token is blacklisted` | Refresh token was used after logout |
| 403 | `You do not have permission to perform this action.` | Your role cannot access this endpoint |

### Validation Errors

| Error | Cause |
|---|---|
| `Invalid priority 'xyz'. Allowed: [...]` | Priority not in org's allowed_priorities |
| `Invalid task type 'xyz'. Allowed: [...]` | Task type not in org's allowed_task_types |
| `Invalid role 'xyz'. Allowed roles for this organization: [...]` | Role not in org's allowed_roles |
| `State 'xyz' does not exist in workflow '...'` | Transition state not in workflow's allowed_states |

### State Machine Errors

| Error | Cause |
|---|---|
| `Task is already in 'xyz' state.` | Trying to transition to current state |
| `Transition from 'a' to 'b' is not allowed in workflow '...'` | No TransitionRule for this path |
| `Your role 'x' cannot transition from 'a' to 'b'. Allowed roles: [...]` | Role not permitted for this transition |
| `Task must be assigned to someone before moving to 'xyz'.` | Task needs an assignee before progressing |

### Assignment Errors

| Error | Cause |
|---|---|
| `alice_dev already has 5 active tasks (max: 5).` | User at capacity — increase max_concurrent_tasks or complete existing tasks |
| `Cannot assign task to user from different organization.` | Cross-org assignment blocked |
| `Only admins and managers can auto-assign tasks.` | Role not in first two org roles |

---

## Complete Workflow Example (Step by Step)

Here is a full lifecycle from zero to a completed task:

```bash
# 1. Setup organization
POST /setup/ → Get tokens

# 2. Create users
POST /users/ {username: "alice", role: "developer", skills: ["python"]}
POST /users/ {username: "bob", role: "developer", skills: ["react"]}

# 3. Create a team
POST /teams/ {name: "Backend", lead: "<alice-uuid>", members: ["<alice-uuid>", "<bob-uuid>"]}

# 4. Create a task
POST /tasks/ {title: "Fix login bug", priority: "p1_critical", task_type: "defect", workflow: "<wf-uuid>", tags: ["python", "auth"]}
# Response: task_key = "NOVA-0001", current_state = "backlog"

# 5. AI scores the task
POST /ai/score-priority/ {task_id: "<task-uuid>"}
# Response: score = 0.85 (HIGH)

# 6. AI recommends assignee
POST /ai/recommend-assignee/ {task_id: "<task-uuid>"}
# Response: alice (82%) > bob (45%) — alice has python skills

# 7. Assign to alice
POST /tasks/<id>/assign/ {user_id: "<alice-uuid>", reason: "Best skill match"}

# 8. Check available transitions
GET /tasks/<id>/available-transitions/
# Response: can go to "sprint_ready" or "cancelled"

# 9. Move to sprint_ready
POST /tasks/<id>/transition/ {to_state: "sprint_ready", reason: "Added to Sprint 12"}

# 10. Move through workflow
POST /tasks/<id>/transition/ {to_state: "in_development", reason: "Starting work"}
POST /tasks/<id>/transition/ {to_state: "code_review", reason: "PR submitted"}

# 11. Add a comment
POST /comments/ {task: "<task-uuid>", content: "Fixed in PR #234"}

# 12. Complete the review
POST /tasks/<id>/transition/ {to_state: "qa_testing", reason: "Code approved"}
POST /tasks/<id>/transition/ {to_state: "uat", reason: "QA passed"}
POST /tasks/<id>/transition/ {to_state: "deployed", reason: "Deployed to production"}

# 13. Check audit trail
GET /audit-logs/?task=<task-uuid>
# Shows complete history of every action

# 14. Check SLA health
POST /dashboard/sla-check/
# Shows breached and at-risk tasks

# 15. View dashboard
GET /dashboard/overview/
# Shows org-wide statistics
```

---

Explore and interact with the system directly through the Django admin panel at `http://127.0.0.1:8000/admin/` for full visibility and control over the database.