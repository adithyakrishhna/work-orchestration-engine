# AI Engine — The Intelligence Layer

Runs entirely locally — no paid APIs, no cloud services, no subscriptions.

---

## 1. Priority Scoring (5 Weighted Factors)

![AI Scoring](../images/ai-scoring.png)

The AI evaluates the task and assigns a priority score (0.0 to 1.0), which is then reflected on the task for better decision-making.

| Factor | Weight | Example |
|---|---|---|
| **Keyword analysis** | 35% | "crash", "security", "blocker" → high score |
| **Task type** | 15% | Bugs score 0.8, features score 0.5 |
| **Manual priority** | 15% | Aligns with human-set priority |
| **Deadline proximity** | 20% | Overdue → 1.0, 24h left → 0.8, 1 week → 0.3 |
| **Task age** | 15% | Older unresolved tasks score higher |

**Score interpretation:** 🔴 70–100% = CRITICAL &nbsp; 🟡 40–70% = MEDIUM/HIGH &nbsp; 🟢 0–40% = LOW

---

## 2. Intelligent Task Routing

![AI Routing](../images/ai-routing.png)

Engineers are ranked and the best match is auto-assigned based on:

| Factor | Weight | How It's Measured |
|---|---|---|
| **Skill match** | 40% | Task tags vs user skills array |
| **Workload** | 30% | Fewer active tasks = higher score |
| **Past performance** | 30% | SLA compliance + resolution speed on similar tasks |

---

## 3. Natural Language Queries

![AI NL Query](../images/ai-nlquery.png)

Type plain English → get database results:

| Query | What It Returns |
|---|---|
| `"critical bugs"` | Tasks with high priority and bug type |
| `"unassigned tasks"` | Tasks with no assignee |
| `"tasks assigned to dev_alice"` | All tasks assigned to dev_alice |
| `"overdue tasks"` | Tasks past their due_date |
| `"my tasks"` | Tasks assigned to the current user |

Parsed filters are shown as badges alongside the results table.

---

## AI API Endpoints

| Endpoint | Method | What It Does |
|---|---|---|
| `/api/v1/ai/score-priority/` | POST | Calculate priority score for a task |
| `/api/v1/ai/recommend-assignee/` | POST | Get ranked engineer recommendations |
| `/api/v1/ai/query/` | POST | Natural language task search |
