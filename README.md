# 🚀 **DevFocus - Developer Context Intelligence Engine**

### *A full–scale, production‑grade backend architecture made public — because my real projects are private.* 🔒🔥

---

## 🧩 **Problem**

As developers, we constantly:

- Jump between tasks ➡️ lose flow  
- Forget *why* we context‑switched  
- Scatter links (PRs, Issues, Docs, Research) everywhere  
- Have no metrics on real focus time  
- Work inside private repos where our best architecture never sees daylight  
- Have no unified view of productivity, behavior, or workflow patterns  

👉 **DevFocus was created to break this invisible wall.**  
To show the level of engineering I apply daily in my private projects — but in a fully open, clean, well‑architected system anyone can inspect.

---

## 🌟 **Solution**

DevFocus is a **Context Intelligence Engine** that blends:

### 🧠 Developer workflow tracking

- ⏱️ Session tracking  
- 🔀 Context switching  
- 🧱 Task management (Bug / Feature / Refactor)  
- 🔗 Resource linking  

### 👥 Team collaboration + RBAC

- Teams (Owner / Admin / Member / Viewer)  
- Scoped sessions + scoped tasks  
- Permission‑safe domain logic

### 📊 Reporting Engine

- Daily / Weekly reports  
- Programmatic summaries  
- Insight generation  

### 🧬 Insight Engine

Automatic analytics detecting:

- 🚨 High context switching  
- 💤 Low focus time  
- 📉 Fragile workflow patterns  
- 🔍 Room for deep‑work improvements  

### 🚛 Background Jobs (Celery)

- Non‑blocking report generation  
- Insight analysis  
- Scalable async architecture  

### 🐙 GitHub Issue Importer (async httpx)

- Fetch GitHub issues  
- Auto‑create Tasks  
- Detect + ignore PRs  
- Store external URLs + IDs  

### 📡 Observability Layer

- API Request Logging Middleware  
- Duration, status, user‑agent, IP  
- Full traceability of API usage  

### 🔥 Realtime Event Stream (SSE)

- Live reports  
- Live insights  
- Zero WebSocket overhead  

### 📤 Export System

- CSV  
- JSON  
- For tasks, sessions, reports, insights  

### 🧪 Full Test Suite

- Unit tests  
- Integration tests  
- Signals tests  
- Celery task pipeline tests  
- GitHub importer tests (mocked async)  
- SSE + middleware tests  

---

# 🧱 **Architecture Overview**

```
devfocus/
 ├── core/
 │    ├── models.py          # Domain entities
 │    ├── services.py        # SOLID service layer
 │    ├── signals.py         # Reactive event handling
 │    ├── tasks.py           # Celery jobs
 │    ├── integrations.py    # GitHub importer
 │    └── ...
 │
 ├── api/
 │    ├── serializers.py
 │    ├── views.py
 │    ├── urls.py
 │    └── ...
 │
 ├── devfocus/
 │    ├── settings.py
 │    ├── celery.py
 │    ├── middleware.py
 │    └── ...
 │
 ├── tests/
 └── README.md
```

---

# 🛠 **Tech Stack (Full Breakdown)**

### **Backend Core**

- 🐍 Python 3.11+
- 🦄 Django 5
- 🌐 Django REST Framework
- 🧱 Clean Architecture  
- 🧩 SOLID Principles  
- 🧬 Domain‑Driven Components  
- 🧲 Signals for reactive updates  

### **Async & Integrations**

- ⚡ httpx (async)
- 🐙 GitHub API integration
- 🔌 SSE event‑streaming  

### **Workers & Scalability**

- 🐳 Celery 5  
- 🔴 Redis (Broker + Result backend)
- 🧵 Background report generation  
- ⚙️ Long-running async workflows  

### **Database / ORM**

- 💾 SQLite (dev)  
- ➕ Ready for PostgreSQL  
- 🔍 ORM optimization (annotate, select_related, prefetch)

### **Observability**

- 📘 Structured API logs  
- 🕵️ Request duration tracking  
- 🔍 Per‑user analytics  

### **Testing**

- 🧪 pytest / Django TestCase  
- ⚡ async test support  
- 🧱 full coverage on:
  - core domain  
  - services  
  - insights  
  - Celery tasks  
  - GitHub importer  
  - SSE  
  - permissions + teams  

---

#  Run Guide & API Reference

This document contains **only** the two requested sections:

1.  **How to Run the Project**\
2.  **Full API Endpoint Reference**

------------------------------------------------------------------------

# 🟩 1) How to Run DevFocus

## 1️⃣ Create & Activate Virtual Environment

### macOS / Linux

``` bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (PowerShell)

``` bash
python -m venv venv
.\venv\Scripts\activate
```

------------------------------------------------------------------------

## 2️⃣ Install Dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## 3️⃣ Run Database Migrations

``` bash
python manage.py makemigrations
python manage.py migrate
```

------------------------------------------------------------------------

## 4️⃣ Create Superuser (Optional)

``` bash
python manage.py createsuperuser
```

------------------------------------------------------------------------

## 5️⃣ Start Development Server

``` bash
python manage.py runserver
```

Your API will be served at:

    http://127.0.0.1:8000/api/

------------------------------------------------------------------------

## 6️⃣ Start Celery Worker (Background Jobs)

In a second terminal:

``` bash
celery -A devfocus worker -l info
```

Ensure Redis is running:

``` bash
redis-server
```

------------------------------------------------------------------------

## 7️⃣ Optional: Update Requirements

``` bash
pip freeze > requirements.txt
```

------------------------------------------------------------------------

# 🟦 2) API Endpoints (Full Reference)

## 🔹 Authentication

*(Using default Django session authentication or token if enabled)*

------------------------------------------------------------------------

# 📁 TASKS

### ➤ List Tasks

`GET /api/tasks/`

### ➤ Filter / Search / Order

    GET /api/tasks/?type=BUG
    GET /api/tasks/?priority=HIGH
    GET /api/tasks/?search=login
    GET /api/tasks/?ordering=-created_at

### ➤ Create Task

`POST /api/tasks/`

### ➤ Retrieve Task

`GET /api/tasks/{id}/`

### ➤ Update Task

`PATCH /api/tasks/{id}/`

### ➤ Delete Task

`DELETE /api/tasks/{id}/`

### ➤ Export Tasks

    GET /api/tasks/export/?format=csv
    GET /api/tasks/export/?format=json

### ➤ Import GitHub Issues (async)

`POST /api/tasks/import_github/`

Body:

``` json
{
  "owner": "django",
  "repo": "django",
  "team_id": 1
}
```

------------------------------------------------------------------------

# 🧩 DEV SESSIONS

### ➤ List Sessions

`GET /api/sessions/`

### ➤ Filter / Order

    GET /api/sessions/?status=OPEN
    GET /api/sessions/?date_from=2025-01-01
    GET /api/sessions/?ordering=-switch_count

### ➤ Create Session

`POST /api/sessions/`

### ➤ Retrieve Session

`GET /api/sessions/{id}/`

### ➤ Close Session

`POST /api/sessions/{id}/close/`

### ➤ Attach Task to Session

`POST /api/sessions/{id}/attach_task/`

Body:

``` json
{
  "task_id": 5,
  "role": "MAIN"
}
```

### ➤ Export Sessions

    GET /api/sessions/export/?format=csv
    GET /api/sessions/export/?format=json

------------------------------------------------------------------------

# 🔄 CONTEXT SWITCHES

### ➤ List

`GET /api/context-switches/`

### ➤ Create

`POST /api/context-switches/`

Body:

``` json
{
  "dev_session": 1,
  "from_task": 2,
  "to_task": 3,
  "reason": "INTERRUPT"
}
```

------------------------------------------------------------------------

# 🔗 RESOURCE LINKS

### ➤ List

`GET /api/resources/`

### ➤ Create

`POST /api/resources/`

------------------------------------------------------------------------

# 📊 REPORTS

### ➤ List Reports

`GET /api/reports/`

### ➤ Generate Daily Report (Sync)

`POST /api/reports/daily/`

Body (optional):

``` json
{
  "date": "2025-01-30"
}
```

### ➤ Generate Daily Report (Async)

`POST /api/reports/daily-async/`

------------------------------------------------------------------------

# 🎛️ REPORT REQUESTS (Celery Jobs)

### ➤ Create Report Request

`POST /api/report-requests/`

Body:

``` json
{
  "type": "DAILY",
  "day": "2025-01-30"
}
```

### ➤ List Requests

`GET /api/report-requests/`

------------------------------------------------------------------------

# 🧠 INSIGHTS

### ➤ List

`GET /api/insights/`

------------------------------------------------------------------------

# 👥 TEAMS

### ➤ List Teams

`GET /api/teams/`

### ➤ Create Team

`POST /api/teams/`

### ➤ Team Members

`GET /api/teams/{id}/members/`

------------------------------------------------------------------------

# 📡 SSE Event Stream

### ➤ Live Stream

`GET /api/events/stream/`

Returns: - latest reports\

- latest insights\
  as `text/event-stream`.

------------------------------------------------------------------------

# 📘 LOGGING (internal middleware)

All API calls generate an ApiRequestLog entry locally.

------------------------------------------------------------------------

# 🚀 **Why I Built This (The Real Reason)**

Most of my engineering work happens inside **private, enterprise‑grade repositories**  
— where I build:

- structured clean architectures  
- high‑scale backends  
- domain‑driven systems  
- async microservices  
- data pipelines  
- CI/CD workflows  

…but none of that can be shown publicly.  
So I created **DevFocus** to expose the quality, architecture, principles, and engineering depth  
I actually use daily.

This project is not a toy 
it is a **public representation of how I design real systems**.  

---

# 🐺 **Author’s Note**

> 🖤 *I build systems that keep developers sharp, teams aligned, and architectures clean.  
> DevFocus is just a glimpse - the real power lives in private repos.*  
>
> -- **Soroosh Morshedi** (https://sorooshmorshedi.ir)

🔥🚬💻🖤  

---

