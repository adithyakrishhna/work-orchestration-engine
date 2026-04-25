# Screenshots

A visual walkthrough of every major feature in the system.

---

## Login & Dashboard

![Login](../images/login.png)
*JWT-authenticated login screen — credentials are verified against the backend, access and refresh tokens are issued and stored in sessionStorage.*

---

![Dashboard](../images/dashboard.png)
*Command center showing real-time analytics — clickable stat cards, task distribution by state and priority, team workload bars, SLA health, and recent activity feed.*

---

![SLA Board](../images/sla-board.png)
*SLA health check modal — shows breached tasks with hours overdue in red, at-risk tasks with hours remaining in amber, and clickable task keys for quick navigation.*

---

## Task Management

![Tasks](../images/tasks.png)
*Task list with search bar, state/priority/team filters, sortable column headers, pagination, inline AI scoring, and admin delete buttons.*

---

![Task Detail](../images/task-detail.png)
*Task detail panel — shows all task info, edit section (priority, due date, team, tags), assign dropdown with workload info, state transition buttons, and comments thread.*

---

![Create Task](../images/create-task.png)
*Task creation form — title, description, priority, type, workflow, team, due date, and tags. Priority and type options are dynamically loaded from the organization's configuration.*

---

![Transition Modal](../images/transition-modal.png)
*State transition confirmation — validates 5 business rules before allowing the change. Shows a reason field for audit trail documentation.*

---

## AI Engine

![AI Scoring](../images/ai-scoring.png)
*AI priority scoring breakdown — 5 weighted factors (keywords 35%, type 15%, priority 15%, deadline 20%, age 15%) with visual bars showing each factor's contribution. Once the score is generated, it is automatically reflected on the task.*

---

![AI Routing](../images/ai-routing.png)
*Intelligent task routing — engineers ranked by skill match, workload availability, and past performance with human-readable reasoning for each recommendation.*

---

![AI NL Query](../images/ai-nlquery.png)
*Natural language query engine — plain English input converted to database filters. Shows parsed filters as badges and matching tasks in a results table.*

---

## Management Pages

![Users](../images/users.png)
*User management — lists all users with roles, skill tags, active task count, and capacity utilization bars. Admins and managers can create new users with role validation.*

---

![Teams](../images/teams.png)
*Team management — cards showing team lead, members, and member count. Admins can create, edit (change lead, add/remove members), and delete teams.*

---

![Organizations](../images/organizations.png)
*Organization settings — displays org name, slug, member count, and team count. Admins can edit details and create new organizations.*

---

![Workflows](../images/workflows.png)
*Workflow configuration — visualizes the state machine with initial (▶) and final (■) state markers, and lists all transition rules with their allowed roles.*

---

![Transitions](../images/transitions.png)
*Transition rules table — shows every from→to state pair with color-coded allowed roles. Admins can create new rules and delete existing ones.*

---

## Audit, Comments & Errors

![Audit Logs](../images/audit-logs.png)
*Immutable audit trail — every action recorded with old/new values displayed side by side, performer name, timestamp, and reason. Task keys are clickable for navigation.*

---

![Comments](../images/comments.png)
*Comments feed — all comments across tasks sorted recent-first. Shows author, content, and time ago. Task keys are clickable to navigate directly to the task.*

---

![Error Modal](../images/error-modal.png)
*Error handling — business rule violations shown as modal popups with clear error messages. User must acknowledge by clicking OK — errors never flash and disappear.*

---

## Profile & Responsive Design

![Profile Edit](../images/profile-edit.png)
*Profile editor — users can update their email, skills (used by AI for task routing), and max concurrent tasks (used for workload calculations).*

---

![Responsive](../images/responsive.png)
*Responsive design — sidebar collapses into a hamburger menu on mobile, grids stack to single column, tables get horizontal scroll. Works on desktop, tablet, and phone.*

---

## Backend — Admin Panel

![Admin Panel](../images/admin-panel.png)
*Django's built-in admin panel showing all 8 registered models — direct database access with search, filters, and inline editing.*

---

![Admin Tasks](../images/admin-tasks.png)
*Task list view in the admin panel — columns for task key, title, state, priority, assignee, and SLA status with built-in filtering sidebar.*

---

![Admin Task Detail](../images/admin-task-detail.png)
*Single task edit form in admin — every field is editable, auto-generated task key is read-only, timestamps are tracked automatically.*

---

## Backend — DRF Browsable API

![API Root](../images/api-root.png)
*Django REST Framework's browsable API root — lists all available endpoints. Any developer can explore and test the API directly in the browser.*

---

![API Tasks](../images/api-tasks.png)
*Tasks endpoint returning paginated JSON response — includes filtering, search, and ordering capabilities visible in the URL bar.*

---

![API Task Detail](../images/api-task-detail.png)
*Single task detail via API — full JSON response showing all fields including nested comments, assignee details, AI scores, and timestamps.*
