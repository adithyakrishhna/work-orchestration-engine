# API, Admin Panel & Frontend

## Complete API Reference

For the complete API reference with every endpoint, request/response examples, curl commands, error codes, and a full step-by-step lifecycle walkthrough, see:

**[📖 Complete API Reference → API_REFERENCE.md](../../API_REFERENCE.md)**

### Quick Overview of Available Endpoints

| Category | Endpoints | Key Actions |
|---|---|---|
| **Setup** | `POST /setup/` | One-click org creation with custom config |
| **Auth** | `/auth/login/` `/auth/register/` `/auth/refresh/` `/auth/logout/` | JWT token lifecycle |
| **Organizations** | `/organizations/` | CRUD + dynamic config |
| **Users** | `/users/` `/users/me/` | CRUD + profile management |
| **Teams** | `/teams/` | CRUD + member management |
| **Workflows** | `/workflows/` | State machine configuration |
| **Transitions** | `/transitions/` | Who can move tasks between states |
| **Tasks** | `/tasks/` `/tasks/{id}/transition/` `/tasks/{id}/assign/` | CRUD + state changes + assignment |
| **Comments** | `/comments/` | Task discussions |
| **Audit Logs** | `/audit-logs/` | Immutable history (read-only) |
| **Dashboard** | `/dashboard/overview/` `/dashboard/sla-check/` | Analytics + SLA monitoring |
| **AI Engine** | `/ai/score-priority/` `/ai/recommend-assignee/` `/ai/query/` | Scoring, routing, natural language |

---

## Django Admin Panel

![Admin Panel](../images/admin-panel.png)

Django includes a powerful built-in admin panel at `/admin/`. This is a separate interface from the frontend dashboard — it gives you direct database access with full CRUD on all 8 models, search, filters, and inline editing.

Access at: `http://127.0.0.1:8000/admin/` with your superuser credentials.

![Admin Task List](../images/admin-tasks.png)

*Task list view — columns for task key, title, state, priority, assignee, and SLA status with built-in filtering sidebar.*

![Admin Task Detail](../images/admin-task-detail.png)

*Single task edit form — every field is editable, auto-generated task key is read-only, timestamps are tracked automatically.*

---

## DRF Browsable API

![DRF API Root](../images/api-root.png)

Django REST Framework provides a browser-based API interface at `/api/v1/`. You can browse all endpoints, send requests, and see formatted JSON responses — all from your browser.

![Setup API Response](../images/setup-response.png)
![Setup API Response 2](../images/setup-response-2.png)

![DRF Task Endpoint](../images/api-tasks.png)

*Tasks endpoint returning paginated JSON response — includes filtering, search, and ordering capabilities.*

![DRF Task Detail](../images/api-task-detail.png)

*Single task detail via API — full JSON response showing all fields including nested comments, assignee details, AI scores, and timestamps.*

---

## Frontend Dashboard

The frontend is a single HTML file — no React build, no npm, no webpack. It communicates with the backend via the REST API using JWT tokens.

| Page | Features |
|---|---|
| **Dashboard** | Clickable cards, state/priority charts, team workload, SLA health, activity feed |
| **Tasks** | Search, filter (state/priority/team), sort columns, pagination, create/edit/delete, inline AI scoring |
| **Users** | List with roles/skills/capacity bars, create/delete users |
| **Teams** | Cards with lead/members, create/edit/delete |
| **Organizations** | Details with counts, create/edit |
| **Workflows** | State machine visualization, create/edit/delete |
| **Transitions** | Rule table, create/delete |
| **AI Engine** | NL query, priority scoring, smart routing, auto-assign |
| **Audit Logs** | Card layout with old/new values, clickable task links |
| **Comments** | Sorted recent-first, clickable task navigation |

![Dashboard](../images/dashboard.png)
