# 🎯 Local Job Portal

A complete **Local Job Portal** web application built for a College CEP (Course End Project).
It connects local companies with college students for jobs and internships.

Built with **plain HTML5, CSS3, JavaScript** (no frontend frameworks) and a **Python Flask + MySQL** backend.

---

## 📁 Project Structure

```
LocalJobPortal/
│
├── app.py                     # Main Flask application (all routes)
├── config.py                  # Database & app configuration
├── database.sql               # Complete MySQL schema + default admin
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── templates/                  # All Jinja2 HTML templates
│   ├── base.html                (navbar + footer layout)
│   ├── index.html                Home page
│   ├── about.html                About page
│   ├── contact.html              Contact page
│   ├── faq.html                  FAQ page
│   ├── jobs.html                  Job listing + search/filter
│   ├── job_details.html           Job details + Apply
│   ├── student_login.html
│   ├── student_register.html
│   ├── forgot_password.html       (shared by student & company)
│   ├── student_dashboard.html
│   ├── student_profile.html       (photo + resume upload, edit profile)
│   ├── student_applications.html
│   ├── company_login.html
│   ├── company_register.html
│   ├── company_dashboard.html
│   ├── company_profile.html
│   ├── post_job.html
│   ├── edit_job.html
│   ├── view_applicants.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── manage_students.html
│   ├── manage_companies.html
│   ├── manage_jobs.html
│   ├── settings.html               (change password)
│   └── 404.html
│
└── static/
    ├── css/
    │   ├── style.css               Main theme (glassmorphism, blue/white)
    │   └── dashboard.css           Dashboard-specific styles
    ├── js/
    │   ├── main.js                 Navbar, flash messages, FAQ accordion
    │   └── validation.js           All client-side form validation
    ├── images/                     (place any static images here)
    └── uploads/
        ├── resumes/                Uploaded student resumes (PDF)
        ├── photos/                 Uploaded student profile photos
        └── logos/                  Uploaded company logos
```

---

## 🖥️ Software Required

| Software | Version | Download Link |
|---|---|---|
| Python | 3.10 or higher | https://www.python.org/downloads/ |
| MySQL Server | 8.0 or higher | https://dev.mysql.com/downloads/mysql/ |
| MySQL Workbench (optional, GUI) | Latest | https://dev.mysql.com/downloads/workbench/ |
| VS Code (recommended editor) | Latest | https://code.visualstudio.com/ |
| pip | Comes with Python | — |

**Recommended VS Code extensions:** Python (Microsoft), Jinja (for template highlighting).

---

## ⚙️ Step-by-Step Setup Guide

### 1. Extract the Project
Unzip `LocalJobPortal.zip` to any folder, e.g. `D:\Projects\LocalJobPortal`.

### 2. Open in VS Code
```
cd LocalJobPortal
code .
```

### 3. Create a Virtual Environment (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Install & Start MySQL
- Install MySQL Server if not already installed.
- Start the MySQL service.
- Make sure you know your MySQL **root password** (or create a dedicated user).

### 6. Import the Database
**Option A — Command Line:**
```bash
mysql -u root -p < database.sql
```

**Option B — MySQL Workbench:**
1. Open MySQL Workbench and connect to your local server.
2. Go to `File > Open SQL Script` and select `database.sql`.
3. Click the ⚡ (execute) icon to run the whole script.

This creates the `local_job_portal` database with all required tables
(`students`, `companies`, `admins`, `jobs`, `applications`, `resumes`, `contact_messages`)
and inserts the **default admin account**.

### 7. Configure Database Connection
Open `config.py` and update the `DB_CONFIG` dictionary with your MySQL credentials:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",        # <-- change this to your MySQL root password
    "database": "local_job_portal"
}
```

### 8. Run the Application
```bash
python app.py
```

You should see output like:
```
 * Running on http://127.0.0.1:5000
```

Open your browser and go to: **http://127.0.0.1:5000**

---

## 🔑 Default Admin Login

```
URL:      http://127.0.0.1:5000/admin/login
Username: admin
Password: admin123
```

⚠️ For security, change this password after first login is not built into the admin UI by
default — you can update it directly in the `admins` table if needed, or extend the
`settings` route to support admins too.

---

## 🧭 How to Use the Site

1. **Students** register at `/student/register`, log in, complete their profile, upload a
   resume (PDF only) and profile photo, then browse `/jobs` to search/filter and apply.
2. **Companies** register at `/company/register`, log in, post new jobs from their dashboard,
   view applicants, and download resumes.
3. **Admin** logs in at `/admin/login` to view platform statistics, manage (block/unblock/delete)
   student & company accounts, and manage/delete job postings.

---

## 🗄️ Database Overview

| Table | Purpose |
|---|---|
| `students` | Student accounts, profile info, resume & photo filenames |
| `companies` | Company accounts, profile info, logo filename |
| `admins` | Administrator login credentials |
| `jobs` | Job postings created by companies |
| `applications` | Links students to jobs they applied for, with status |
| `resumes` | History log of every resume a student has uploaded |
| `contact_messages` | Messages submitted via the Contact Us page |

---

## 🔒 Security Features Implemented

- Passwords are hashed using Werkzeug's `generate_password_hash` / `check_password_hash`
  (never stored in plain text).
- Flask `session` is used for authentication state (student / company / admin).
- Route-level `login_required` decorators protect dashboard & CRUD routes.
- File uploads are restricted by extension (`.pdf` for resumes, `.jpg/.jpeg/.png` for images)
  and by size (max 5 MB), and filenames are sanitized with `secure_filename`.
- Server-side validation backs up all client-side JavaScript validation.

---

## ✅ Features Checklist

**Student:** Registration, Login, Forgot Password, Dashboard, Update/Edit Profile, Upload
Resume (PDF), Upload Profile Photo, Search Jobs, Filter Jobs, Apply for Jobs, View Applied
Jobs, Logout.

**Company:** Registration, Login, Dashboard, Edit Company Profile, Post New Job, Edit Job,
Delete Job, View Applicants, Download Student Resume, Logout.

**Admin:** Login, Dashboard, Manage Students (block/unblock/delete), Manage Companies
(block/unblock/delete), Manage Jobs (view/delete), View Statistics, Logout.

**General:** Home, About, Contact (with working message form), FAQ, Job Listing with
search & filters, Job Details, Settings (change password), fully responsive Blue & White
glassmorphism UI with gradient buttons, hover effects, and animations.

---

## 🛠️ Troubleshooting

- **`Access denied for user 'root'@'localhost'`** → Double-check the password in `config.py`.
- **`Unknown database 'local_job_portal'`** → Re-run the `database.sql` import step.
- **`ModuleNotFoundError: No module named 'mysql'`** → Run `pip install -r requirements.txt`
  again inside your activated virtual environment.
- **Uploaded files not showing** → Make sure the `static/uploads/resumes`,
  `static/uploads/photos`, and `static/uploads/logos` folders exist (they are included in
  this ZIP already).
- **Port already in use** → Run `python app.py` with a different port:
  `app.run(debug=True, port=5001)` inside `app.py`.

---

## 📌 Project Explanation (for viva/presentation)

Local Job Portal is a 3-tier web application:

1. **Presentation Layer** — Plain HTML5/CSS3/JavaScript templates rendered server-side via
   Flask's Jinja2 templating engine. No JS frameworks are used; all interactivity (form
   validation, FAQ accordion, mobile nav, flash auto-dismiss) is hand-written vanilla JS.
2. **Application Layer** — Python Flask handles routing, authentication (via sessions),
   password hashing, file uploads, and all business logic (posting jobs, applying,
   managing applicants, admin moderation).
3. **Data Layer** — MySQL stores all persistent data across 7 relational tables with
   foreign key constraints (e.g., a job belongs to a company; an application links a
   student and a job).

This mirrors real-world job portals (like Naukri or LinkedIn Jobs) but scoped down for a
local college ecosystem, making it a strong, demonstrable full-stack CEP project.

---

## 👨‍💻 Author Notes

This project was generated as a complete, ready-to-run CEP submission. All routes, forms,
uploads, and database operations are fully implemented — there are no placeholder pages or
"coming soon" sections. Feel free to extend it further (e.g., email notifications, OTP-based
password reset, pagination, or a REST API layer) for bonus marks.


## GitHub repository notes

- Create a **new public or private repository** for this project and upload these source files.
- Do not upload your local `venv/`, `.git/`, `.env`, database dumps containing real personal data, or real uploaded resumes/photos.
- Configure a strong `SECRET_KEY` environment variable before deploying.
- The default admin credentials documented above are for local setup only. Change them immediately and never use them on a public deployment.
- Set your MySQL credentials locally in `config.py` or move them to environment variables before publishing.
