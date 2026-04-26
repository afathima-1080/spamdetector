# Email Spam Detector — Project Documentation (2026)

---

## Student Details

| Field               | Details                                      |
|---------------------|----------------------------------------------|
| **Name**            | Fathima R                                    |
| **Role / Title**    | Email Spam Detector / Student                |
| **Department**      | Bachelor of Computer Applications (BCA)      |
| **College**         | SRM Institute of Science and Technology      |
| **Register No.**    | DA2231006010004                              |
| **Email**           | fr0379@srmist.edu.in                         |
| **GitHub**          | [afathima-1080](https://github.com/afathima-1080) |
| **Academic Year**   | 2025 – 2026                                  |
| **Guide / Supervisor** | As per department records               |

---

## Abstract

Email spam remains one of the most prevalent threats to digital communication, flooding inboxes with unsolicited, often malicious content. This project presents an **Email Spam Detector** — a full-stack web application that leverages a large language model (LLM) to classify incoming emails as **spam** or **ham** (legitimate) in real time.

The system is built with a **Flask** back-end, a **PostgreSQL** database for persistent storage of emails and user accounts, and integrates the **OpenAI API** for intelligent spam classification. Each classification returns a label, confidence score, human-readable reasons, risk flags (e.g. `credential_theft`, `urgent_payment`), and a neutral safe summary of the email content.

---

## 1. Introduction

### 1.1 Background

Spam emails constitute more than 45 % of all email traffic worldwide. Traditional rule-based and statistical filters (e.g., Bayesian classifiers) have difficulty keeping pace with modern, contextually complex spam campaigns. Large language models offer a promising alternative: they can evaluate nuanced intent, idiomatic phrasing, and social-engineering patterns that simpler models miss.

### 1.2 Objectives

- Provide a secure, multi-user web application for composing and receiving emails.
- Automatically classify each outgoing email body as spam or ham before delivery.
- Present classification results — label, confidence, reasons, risk flags, and a safe summary — to the sender before they confirm sending.
- Persist all emails and their classification metadata in a relational database.

### 1.3 Scope

This project covers:

- User registration and authentication (hashed passwords via Werkzeug).
- Email composition with pre-send spam checking.
- Inbox view with per-email spam metadata.
- RESTful Flask routes with CSRF-safe redirect guards.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User's Browser                        │
│  (Login / Register / Compose / Inbox / Email Detail)     │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTP (Flask routes)
┌───────────────────────▼─────────────────────────────────┐
│               Flask Web Application (app.py)             │
│  Routes: /, /login, /register, /logout,                  │
│          /inbox, /compose, /email/<id>                   │
└────────┬──────────────────────────────┬─────────────────┘
         │ SQLAlchemy ORM               │ OpenAI SDK
┌────────▼──────────┐        ┌──────────▼─────────────────┐
│  PostgreSQL DB    │        │   OpenAI API (gpt-4.1-mini) │
│  Tables:          │        │   JSON Schema output        │
│  • users          │        │   (label, confidence,       │
│  • emails         │        │    reasons, risk_flags,     │
└───────────────────┘        │    safe_summary)            │
                             └────────────────────────────┘
```

### 2.1 Component Breakdown

| Component          | Technology                        | Purpose                                      |
|--------------------|-----------------------------------|----------------------------------------------|
| Web Framework      | Flask 3.1                         | HTTP routing, session management             |
| Authentication     | Flask-Login 0.6                   | Session-based login / logout                 |
| ORM & Database     | SQLAlchemy 2.0 + PostgreSQL       | Persistent storage of users and emails       |
| Password Hashing   | Werkzeug 3.1                      | Secure `pbkdf2:sha256` password hashing      |
| Spam Classification| OpenAI API (`gpt-4.1-mini`)       | LLM-powered spam/ham classification          |
| Environment Config | python-dotenv                     | Loads secrets from `.env`                    |
| Templating         | Jinja2 (bundled with Flask)       | HTML template rendering                      |

---

## 3. Technology Stack

### 3.1 Back-End

- **Python 3.11+**
- **Flask 3.1.0** — lightweight WSGI web framework
- **Flask-SQLAlchemy 3.1.1** — ORM integration
- **Flask-Login 0.6.3** — user session management
- **psycopg2-binary 2.9.10** — PostgreSQL adapter
- **openai 1.77.0** — OpenAI Python SDK
- **python-dotenv 1.1.0** — `.env` file loader
- **Werkzeug 3.1.3** — WSGI utilities and security helpers

### 3.2 Database

- **PostgreSQL** (production)
- **SQLite** (testing / CI via `DATABASE_URL=sqlite:///:memory:`)

### 3.3 Front-End

- HTML5 / CSS3 (Jinja2 templates in `templates/`)
- Static assets in `static/`

### 3.4 AI / ML

- **OpenAI `gpt-4.1-mini`** via the Responses API with a strict JSON Schema for deterministic output.

---

## 4. Database Design

### 4.1 Entity Relationship Diagram (simplified)

```
users
 ├── id          (PK, Integer)
 ├── username    (String, unique)
 ├── email       (String, unique)
 └── password_hash (String)

emails
 ├── id               (PK, Integer)
 ├── sender_id        (FK → users.id)
 ├── recipient_id     (FK → users.id)
 ├── subject          (String)
 ├── body             (Text)
 ├── sent_at          (DateTime, default=now)
 ├── spam_label       (String: "spam" | "ham" | NULL)
 ├── spam_confidence  (Float 0–1 | NULL)
 ├── spam_reasons     (JSON string | NULL)
 ├── spam_risk_flags  (JSON string | NULL)
 └── spam_safe_summary (Text | NULL)
```

### 4.2 Key Constraints

- Usernames and email addresses are unique.
- `sender_id` and `recipient_id` use foreign keys with cascade behavior managed by SQLAlchemy.
- Spam fields are nullable — if the OpenAI service is unavailable, the email is still delivered without classification.

---

## 5. Module Descriptions

### 5.1 `app.py` — Flask Application

| Route         | Method(s)  | Description                                                                 |
|---------------|------------|-----------------------------------------------------------------------------|
| `/`           | GET        | Redirects authenticated users to inbox; others to login.                    |
| `/login`      | GET, POST  | User login form. Validates credentials, starts session.                     |
| `/register`   | GET, POST  | New user registration. Hashes password and persists user.                   |
| `/logout`     | GET        | Ends the current session and redirects to login.                            |
| `/inbox`      | GET        | Lists all emails received by the current user, newest first.                |
| `/compose`    | GET, POST  | Email composition form. Supports `check` (preview spam result) and `send`. |
| `/email/<id>` | GET        | Shows full email detail with spam classification metadata.                  |

**Open-Redirect Protection:** The `_is_safe_redirect_url()` helper validates that `next` query parameters resolve to the same host before redirecting, preventing open-redirect attacks.

### 5.2 `spam_detector.py` — Spam Classification Engine

```python
classify_email(email_text: str, *, model: str = "gpt-4.1-mini") -> SpamResult
```

- Builds a structured prompt that instructs the model **not** to follow instructions inside the email (prompt-injection defence).
- Calls the OpenAI Responses API with a strict JSON Schema (`additionalProperties: False`) to guarantee a well-formed response.
- Returns a `SpamResult` dataclass:

```python
@dataclass
class SpamResult:
    label: Literal["spam", "ham"]
    confidence: float          # 0.0 – 1.0
    reasons: List[str]         # ≤ 5 reasons
    risk_flags: List[str]      # e.g. "credential_theft", "urgent_payment"
    safe_summary: str          # 1–2 sentence neutral summary
```

### 5.3 `models.py` — Database Models

Defines `User` and `Email` SQLAlchemy models, along with `db = SQLAlchemy()` initialised in `app.py`.

---

## 6. Security Considerations

| Threat                  | Mitigation                                                                    |
|-------------------------|-------------------------------------------------------------------------------|
| Password storage        | `werkzeug.security.generate_password_hash` (PBKDF2-SHA256 with salt)         |
| Session fixation        | Flask-Login regenerates session on login                                      |
| Open redirect           | `_is_safe_redirect_url()` enforces same-host validation                       |
| Prompt injection        | Classifier prompt explicitly forbids following instructions inside email text |
| Insecure secret key     | Warning logged; must set `SECRET_KEY` env var in production                  |
| SQL injection           | SQLAlchemy ORM with parameterised queries                                     |

---

## 7. Setup and Installation

### 7.1 Prerequisites

- Python 3.11 or later
- PostgreSQL 14 or later
- An [OpenAI API key](https://platform.openai.com/api-keys)

### 7.2 Clone and Install

```bash
git clone https://github.com/afathima-1080/spamdetector.git
cd spamdetector
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 7.3 Environment Variables

Create a `.env` file (see `.env.example`):

```dotenv
SECRET_KEY=your-very-secret-key
DATABASE_URL=postgresql://user:password@localhost/spamdetector
OPENAI_API_KEY=sk-...
```

### 7.4 Database Initialisation

```bash
# Start PostgreSQL and create the database
createdb spamdetector

# Tables are created automatically on first run
python app.py
```

### 7.5 Running the Application

```bash
python app.py
```

Navigate to `http://127.0.0.1:5000` in your browser.

---

## 8. Usage Guide

1. **Register** — create an account at `/register`.
2. **Login** — sign in at `/login`.
3. **Compose** — go to `/compose`, enter a recipient username, subject, and body.
4. Click **Check for Spam** to preview the classification result before sending.
5. Review the label (spam / ham), confidence score, risk flags, and safe summary.
6. Click **Send** to deliver the email (classification metadata is saved alongside it).
7. **Inbox** — view received emails and their spam classification at `/inbox`.

---

## 9. Testing

Run the test suite (SQLite in-memory, OpenAI mocked):

```bash
DATABASE_URL=sqlite:///test.db pytest
```

The test configuration mocks the `openai` module so no API key is required for testing.

---

## 10. Project Structure

```
spamdetector/
├── app.py                  # Flask application and routes
├── models.py               # SQLAlchemy models (User, Email)
├── spam_detector.py        # OpenAI-powered spam classification
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── static/                 # CSS, JS, images
├── templates/              # Jinja2 HTML templates
│   ├── login.html
│   ├── register.html
│   ├── inbox.html
│   ├── compose.html
│   └── email_detail.html
└── docs/
    ├── Email-Spam-Detector-Documentation-2026.md   # This file
    ├── Email-Spam-Detector-Documentation-2026.pdf  # Auto-generated PDF
    ├── spam-detector.md                             # API usage reference
    └── old/
        └── Probe Attack Prediction Using ML(...).pdf  # Archived original PDF
```

---

## 11. GitHub Actions — Automated PDF Build

A workflow at `.github/workflows/build-docs-pdf.yml` automatically converts this Markdown file to a PDF using Pandoc and XeLaTeX.

**Trigger options:**

- **Manual** — go to *Actions → Build Documentation PDF → Run workflow*.
- **Automatic** — triggers on every push to the branch when any `docs/*.md` file changes.

**What it does:**

1. Checks out the repository.
2. Installs Pandoc and XeLaTeX (via `apt-get`).
3. Moves the old PDF to `docs/old/` (preserving it).
4. Generates `docs/Email-Spam-Detector-Documentation-2026.pdf` from this Markdown.
5. Commits and pushes the PDF back to the same branch.

See [`.github/workflows/build-docs-pdf.yml`](../.github/workflows/build-docs-pdf.yml) for the full workflow source.

---

## 12. References

1. OpenAI Platform Documentation — <https://platform.openai.com/docs>
2. Flask Documentation — <https://flask.palletsprojects.com/>
3. Flask-Login Documentation — <https://flask-login.readthedocs.io/>
4. SQLAlchemy Documentation — <https://docs.sqlalchemy.org/>
5. PostgreSQL Documentation — <https://www.postgresql.org/docs/>
6. Pandoc User's Guide — <https://pandoc.org/MANUAL.html>
7. Python Dataclasses — PEP 557 — <https://peps.python.org/pep-0557/>

---

## 13. Acknowledgements

The author thanks the faculty of the Department of Computer Applications at SRM Institute of Science and Technology for their guidance and support throughout this project.

---

*Document generated: 2026 | SRM Institute of Science and Technology*
