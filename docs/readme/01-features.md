# What Makes This System Strong

This project is built with a strong focus on real-world engineering practices, with every layer designed to reflect modern product-driven standards. It emphasizes scalability, maintainability, and extensibility to deliver a robust, production-ready system.

---

## Real System Design, Not Just Endpoints

This project implements a **complete workflow orchestration system** with 8 interconnected database models, **20+ API endpoints** with filtering, pagination, and search capabilities, and a layered architecture that separates HTTP handling from business logic from data access.

The system supports complex queries such as filtering tasks by priority, team, and sorting — all handled efficiently within a single request.

---

## Configurable State Machine with Business Rule Enforcement

At the core of the system is a finite state machine that manages task workflows. Workflows are configurable — organizations can define their own states (e.g., `open → in_progress → review → testing → done`), transition rules (e.g., only managers can approve certain stages), and business constraints (e.g., tasks must be assigned before starting).

Each state change is validated against multiple rules before execution, and every transition is recorded in an immutable audit log for traceability.

---

## Dual-Layer Role-Based Access Control (RBAC)

Authorization is enforced at **two independent levels**:

- **Layer 1 — API level**: Controls which endpoints each role can access (e.g., only admins can delete tasks).
- **Layer 2 — Business logic level**: Ensures users can only perform actions permitted by workflow rules.

Even if a user can access an endpoint, specific operations (like certain state transitions) are validated separately — ensuring consistent and secure access control throughout the system.

---

## AI-Powered Intelligence Layer (Zero Cost, Fully Local)

The AI engine runs entirely on the local machine — no external APIs, no cloud services, no subscriptions:

- **Multi-factor priority scoring** — evaluates urgency keywords, task type, manual priority, deadline proximity, and task age to generate a score between 0.0 and 1.0 with a human-readable explanation.
- **Intelligent task routing** — ranks engineers based on skill match, current workload, and historical performance.
- **Natural language query engine** — converts plain English queries into precise database filters using pattern matching.

---

## Enterprise-Grade Audit Trail

Every action in the system — task creation, state transitions, assignments, comments, and SLA breaches — is recorded in an immutable audit log with the exact old value, new value, actor, timestamp, and context.

These logs cannot be modified or deleted through the API, including by administrators, ensuring a complete and tamper-proof history of all changes.

---

## Multi-Tenant Data Isolation

Every database query in the system is automatically filtered by organization. A user from Organization A can never see, modify, or even discover the existence of data belonging to Organization B — even if they know the exact UUID of a resource.

This is the same multi-tenancy pattern used by SaaS platforms like Slack, Jira, and Salesforce.

---

## Production-Ready Authentication

The system uses JWT (JSON Web Token) authentication with a complete token lifecycle:
- **Access token** (short-lived) for API requests.
- **Refresh token** (long-lived) to renew sessions without re-entering credentials.
- Refresh tokens are **rotated on each use**, and logout **blacklists tokens permanently**.

This is the exact same authentication pattern used by every modern API — from GitHub to Stripe to Google.

---

## SLA Monitoring and Breach Detection

Tasks with a `due_date` are actively monitored. The `SLAService` flags overdue tasks as `sla_breached = True`, identifies at-risk tasks (< 24 hours remaining), calculates breach rates per organization, and logs each breach as an audit event.

These checks can be triggered via API, CLI, or scheduled as a background job, enabling continuous and automated monitoring.

---

## What This Project Does

This project is the backend engine of a work management system — responsible for managing tasks, enforcing rules, controlling access, and tracking state changes.

Every task operates within a state machine, ensuring that actions follow defined workflows. The system enforces rules such as requiring assignment before starting work or restricting approvals based on roles.

On top of this, an AI layer enhances decision-making: it evaluates task details to calculate priority scores, suggests optimal assignees based on skills and workload, and supports natural language queries to fetch tasks using simple English.

All actions are recorded in an immutable audit log with complete traceability.

**In short**: Tasks are created, validated, assigned, processed through workflows, monitored for deadlines, intelligently prioritized, and fully tracked — ensuring consistency and reliability across the system.
