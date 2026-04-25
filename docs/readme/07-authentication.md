# JWT Authentication

JWT (JSON Web Token) is the industry-standard way to authenticate API requests.

---

## The Problem

APIs are **stateless** — the server does not remember anything between requests. Every API call is independent. So how does the server know who you are?

## The Solution: Tokens

When you log in, the server gives you two tokens:

**Access Token** — Your main ID card. Sent with every request. Expires in **1 hour** for security. If stolen, usable for 1 hour maximum.

**Refresh Token** — A backup to get a new access token without logging in again. Lasts **7 days**.

---

## How It Works Step-by-Step

```
Step 1: LOGIN
   You send: POST /auth/login/ {"username": "admin_user", "password": "testpass123"}
   Server returns: {"access": "eyJhbG...", "refresh": "eyJhbG..."}

Step 2: USE THE ACCESS TOKEN
   You send: GET /tasks/
   Header: Authorization: Bearer eyJhbG...
   Server decodes the token → finds your user ID → returns your tasks

Step 3: TOKEN EXPIRES (after 1 hour)
   You send: POST /auth/refresh/ {"refresh": "eyJhbG..."}
   Server returns: {"access": "NEW_TOKEN_HERE"}

Step 4: LOGOUT
   You send: POST /auth/logout/ {"refresh": "eyJhbG..."}
   Server blacklists the refresh token → it can never be used again
```

---

## Example Timeline

| Time | Action | What Happens |
|---|---|---|
| **0:00 — LOGIN** | Send username + password | Receive access token (1h) + refresh token (7d) |
| **0:01 — CREATE TASK** | Send access token + task data | Server decodes token → identifies user → checks role → creates task ✅ |
| **0:05 — ASSIGN TASK** | Send access token + user_id | Server decodes token → verifies permissions → assigns task ✅ |
| **0:30 — TRANSITION** | Send access token + target state | Server validates role → enforces workflow → transitions task ✅ |
| **1:00 — TOKEN EXPIRES** | Send expired access token | Server rejects → `401 Unauthorized` ❌ |
| **1:01 — REFRESH** | Send refresh token | Receive new access token (valid 1 more hour) |
| **1:02 — BACK TO WORK** | Send new access token | Requests succeed again ✅ |
| **Logout** | Send refresh token | Token blacklisted → cannot be reused ❌ |

![Outstanding Tokens](../images/outstanding-tokens.png)

- **Outstanding Tokens** — All refresh tokens that have been issued and are still recognized. They represent active user sessions.
- **Blacklisted Tokens** — Refresh tokens explicitly invalidated on logout or rotation. Permanently blocked and cannot be reused.

---

## Why JWT Matters in This Project

- Runs completely **in the background** — no manual session handling
- **Stateless** — no server-side session storage needed
- **High performance** — avoids database lookups on every request
- **Secure** — short-lived access tokens + rotation on refresh
- **Scalable** — ideal for API-first and distributed systems

JWT is used across the system to secure all endpoints, enforce RBAC, validate workflow transitions, and enable fast request processing.

---

## Authentication Endpoints

| Endpoint | Method | Who Can Access | What It Does |
|---|---|---|---|
| `/auth/login/` | POST | Anyone | Send username + password, get tokens |
| `/auth/register/` | POST | Anyone | Create account + get tokens |
| `/auth/refresh/` | POST | Anyone with valid refresh token | Get new access token |
| `/auth/logout/` | POST | Logged-in users | Blacklist refresh token permanently |
