# Manufacturing Manual Assistant
### Round 1 Hackathon Challenge — Python Full Stack + RAG

An AI-powered web application that indexes manufacturing machine PDF manuals, performs strict machine-filtered retrieval, and answers technical engineering questions with exact PDF page references, grounded answers, role-based access control, and **PostgreSQL** persistent storage.

---

## 1. Project Architecture & Tech Stack

- **Backend Web Framework:** Django 6.1 + Django REST Framework (DRF)
- **Database:** PostgreSQL (`manufacturing_db` on `localhost:5432`) driven by `.env` environment variables
- **PostgreSQL Driver:** `psycopg` 3.3.6 (with pre-compiled C binaries `psycopg-binary`)
- **PDF Extraction:** PyMuPDF (`pymupdf` / `fitz`) preserving exact 1-based page numbers
- **RAG & Retrieval:** Custom lexical + semantic hybrid retrieval with **Strict Machine-Based Filtering**
- **Frontend:** Responsive Bootstrap 5 + Bootstrap Icons + In-Browser PDF Page Viewer modal

---

## 2. Environment Variables (.env)

The database is configured via `.env`:

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=manufacturing_db
DB_USER=postgres
DB_PASSWORD=shiva
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=django-insecure-manufacturing-assistant-round1-student-pack-key
DEBUG=True
ALLOWED_HOSTS=*
```

An SQLite backup remains available in `db.sqlite3.backup`.

---

## 3. Default User Accounts & Roles

| Role | Username | Password | Permissions |
|---|---|---|---|
| **Administrator** | `admin` | `adminpassword123` | Upload manuals, register machines, full access |
| **Engineer** | `engineer` | `engineerpassword123` | Select machine, ask questions, inspect citations & PDF pages |
| **Supervisor** | `supervisor` | `supervisorpassword123` | Read-only audit log dashboard, question tracking |

---

## 4. Verification & Testing

### Verification Suite (against PostgreSQL):
```powershell
python test_full_suite_postgresql.py
```
**Test Results:**
- **Database Engine Check:** Verified `vendor == 'postgresql'`, connected to `manufacturing_db`.
- **Authentication & Roles:** Admin, Engineer, and Supervisor authenticated successfully.
- **Machine Selection & Data:** HP-200 and AC-90 verified with all attached manuals.
- **Mandatory Check 1:** Engineer manual upload rejected with `HTTP 403 Forbidden`.
- **Mandatory Check 2:** Machine-based retrieval isolation strictly enforced (0 cross-contamination).
- **RAG Demonstrations:** Demo 1, Demo 2 (multi-manual), Demo 3 (isolation), and Demo 4 (missing info) all passed.
- **Audit Logging:** Interaction saved and verified in PostgreSQL `history_questionhistory`.

### Django Test Suite:
```powershell
python manage.py test assistant
```

---

## 5. How to Run the Application

```powershell
# 1. Run migrations on PostgreSQL
python manage.py migrate

# 2. Run automated test suite
python test_full_suite_postgresql.py

# 3. Start development server
python manage.py runserver 127.0.0.1:8000
```
Open your browser at **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**.
