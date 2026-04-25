# Backend Internals

## Design Patterns

**State Machine Pattern** — The `StateMachineService` acts as a finite automaton controller. Tasks can only transition between states explicitly defined in `TransitionRule`.

**Service Layer Pattern** — Business logic is separated from views into dedicated service classes. Views only handle HTTP request/response. This makes the code testable, reusable, and maintainable.

**Repository Pattern** (via Django ORM) — Database queries are abstracted through Django's ORM. The code never writes raw SQL.

**Serializer Pattern** (via DRF) — Separate serializers for different use cases: `TaskListSerializer` (lightweight, for list views) vs `TaskDetailSerializer` (full data, for single task views).

---

## State Machine Engine

![Workflows Page](../images/workflows.png)

**How a transition works internally:**

```
User: POST /tasks/{id}/transition/ {"to_state": "in_progress"}
                    │
                    ▼
  Check 1: Same state? → FAIL
  Check 2: Valid state in workflow? → FAIL
  Check 3: Transition rule exists? → FAIL
  Check 4: User role allowed? → FAIL
  Check 5: Task assigned? (if going to in_progress) → FAIL
                    │
              ALL PASSED ✅
                    │
  → Update task.current_state
  → Set resolved_at if final state
  → Create AuditLog entry
  → Return updated task
```

**Default Workflow:**

```
  [OPEN] → [IN_PROGRESS] → [REVIEW] → [TESTING] → [DONE]
    │           │                                      │
    ▼           ▼                                      ▼
 [CANCELLED] [CANCELLED]                     [OPEN] (reopen, admin only)
```

---

## Role-Based Access Control (RBAC)

![Users Page](../images/users.png)

### Layer 1 — API Endpoint Level

| Action | Admin | Manager | Engineer | Viewer |
|---|:---:|:---:|:---:|:---:|
| View tasks/users/teams | ✅ | ✅ | ✅ | ✅ |
| Create tasks | ✅ | ✅ | ✅ | ❌ |
| Update any task in org | ✅ | ✅ | ❌ | ❌ |
| Delete tasks | ✅ | ❌ | ❌ | ❌ |
| Create users | ✅ | ✅ | ❌ | ❌ |
| Manage workflows/transitions | ✅ | ❌ | ❌ | ❌ |

*Managers can create all roles except Admin.*

### Layer 2 — Business Logic Level (State Transitions)

| Transition | Admin | Manager | Engineer |
|---|:---:|:---:|:---:|
| open → in_progress | ✅ | ✅ | ✅ |
| open → cancelled | ✅ | ✅ | ❌ |
| in_progress → review | ✅ | ✅ | ✅ |
| review → testing | ✅ | ✅ | ❌ |
| testing → done | ✅ | ✅ | ❌ |
| done → open (reopen) | ✅ | ❌ | ❌ |

**Why two layers?** An engineer might have API access to "update a task" (Layer 1), but the state machine still prevents them from moving a task from "review" to "done" (Layer 2). This is **defense in depth**.

---

## Immutable Audit Trail

![Audit Logs](../images/audit-logs.png)

Every action creates an `AuditLog` with: what happened, who did it, when, what changed (old → new as JSON), and why. Audit logs are **read-only** — no update or delete operations exist, not even for admins.

---

## SLA Breach Detection

Tasks with a `due_date` are monitored. The `SLAService`:
- Flags overdue tasks as `sla_breached = True`
- Identifies at-risk tasks (< 24 hours remaining)
- Creates audit entries for each breach

Triggerable via API (`POST /dashboard/sla-check/`) or CLI (`python manage.py check_sla`).

---

## Error Handling

All errors return clear, specific messages. In the frontend, errors appear as modal popups requiring user acknowledgment.

![Error Modal](../images/error-modal.png)

### State Machine Errors

| What You Tried | Error Message |
|---|---|
| Transition without assigning first | `"Task must be assigned to someone before moving to 'in_progress'."` |
| Invalid state path | `"Transition from 'open' to 'done' is not allowed in workflow 'Standard Bug Tracking'."` |
| Wrong role for transition | `"Your role 'engineer' cannot transition from 'review' to 'testing'. Allowed roles: ['admin', 'manager']"` |
| Already in target state | `"Task is already in 'open' state."` |
| Non-existent state | `"State 'invalid' is not valid for workflow 'Standard Bug Tracking'. Allowed states: [...]"` |

### Assignment Errors

| What You Tried | Error Message |
|---|---|
| Assign to overloaded user | `"dev_alice already has 5 active tasks (max: 5)."` |
| Assign across organizations | `"Cannot assign task to user from different organization."` |
| Engineer tries auto-assign | `"Only admins and managers can auto-assign tasks."` |
