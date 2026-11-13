"""
app.py
Local Job Portal - Main Flask Application
CEP (Course End Project)

Run with:  python app.py
"""

import os
from datetime import date, datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, send_from_directory, abort, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import mysql.connector
from mysql.connector import Error

import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

# Make sure upload folders exist
for folder in (config.RESUME_FOLDER, config.PHOTO_FOLDER, config.LOGO_FOLDER):
    os.makedirs(folder, exist_ok=True)


# =========================================================
# DATABASE HELPERS
# =========================================================
def get_db():
    """Create and return a new MySQL connection."""
    return mysql.connector.connect(**config.DB_CONFIG)


def query_db(query, args=(), fetchone=False, fetchall=False, commit=False):
    """Generic helper to run a query and clean up the connection."""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    result = None
    last_id = None
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
            last_id = cursor.lastrowid
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
    if commit:
        return last_id
    return result


# =========================================================
# FILE UPLOAD HELPERS
# =========================================================
def allowed_file(filename, allowed_ext):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_ext


def save_upload(file_storage, folder, prefix):
    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit(".", 1)[1].lower()
    unique_name = f"{prefix}_{int(datetime.utcnow().timestamp())}.{ext}"
    path = os.path.join(folder, unique_name)
    file_storage.save(path)
    return unique_name


# =========================================================
# AUTH DECORATORS
# =========================================================
def login_required(role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if session.get("user_type") != role:
                flash(f"Please log in as {role} to continue.", "error")
                return redirect(url_for(f"{role}_login"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


student_required = login_required("student")
company_required = login_required("company")
admin_required = login_required("admin")


# =========================================================
# CONTEXT PROCESSOR (available in every template)
# =========================================================
@app.context_processor
def inject_globals():
    return {
        "current_year": datetime.now().year,
        "session": session
    }


# =========================================================
# PUBLIC PAGES
# =========================================================
@app.route("/")
def index():
    jobs = query_db(
        """SELECT jobs.*, companies.company_name FROM jobs
           JOIN companies ON jobs.company_id = companies.id
           WHERE jobs.status='open' ORDER BY jobs.created_at DESC LIMIT 6""",
        fetchall=True
    )
    stats = {
        "students": query_db("SELECT COUNT(*) AS c FROM students", fetchone=True)["c"],
        "companies": query_db("SELECT COUNT(*) AS c FROM companies", fetchone=True)["c"],
        "jobs": query_db("SELECT COUNT(*) AS c FROM jobs", fetchone=True)["c"],
    }
    return render_template("index.html", jobs=jobs, stats=stats)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if name and email and message:
            query_db(
                "INSERT INTO contact_messages (name, email, message) VALUES (%s,%s,%s)",
                (name, email, message), commit=True
            )
            flash("Your message has been sent. We will get back to you soon!", "success")
            return redirect(url_for("contact"))
        flash("Please fill all fields.", "error")
    return render_template("contact.html")


@app.route("/jobs")
def jobs():
    search = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()
    job_type = request.args.get("job_type", "").strip()

    query = """SELECT jobs.*, companies.company_name FROM jobs
               JOIN companies ON jobs.company_id = companies.id
               WHERE jobs.status='open'"""
    args = []
    if search:
        query += " AND (jobs.title LIKE %s OR jobs.skills LIKE %s OR companies.company_name LIKE %s)"
        like = f"%{search}%"
        args += [like, like, like]
    if location:
        query += " AND jobs.location LIKE %s"
        args.append(f"%{location}%")
    if job_type:
        query += " AND jobs.job_type = %s"
        args.append(job_type)
    query += " ORDER BY jobs.created_at DESC"

    job_list = query_db(query, tuple(args), fetchall=True)
    locations = query_db("SELECT DISTINCT location FROM jobs", fetchall=True)
    return render_template("jobs.html", jobs=job_list, locations=locations,
                            search=search, sel_location=location, sel_type=job_type)


@app.route("/jobs/<int:job_id>")
def job_details(job_id):
    job = query_db(
        """SELECT jobs.*, companies.company_name, companies.address, companies.website,
                  companies.description AS company_description, companies.logo
           FROM jobs JOIN companies ON jobs.company_id = companies.id
           WHERE jobs.id = %s""", (job_id,), fetchone=True
    )
    if not job:
        abort(404)
    already_applied = False
    if session.get("user_type") == "student":
        app_row = query_db(
            "SELECT id FROM applications WHERE job_id=%s AND student_id=%s",
            (job_id, session["user_id"]), fetchone=True
        )
        already_applied = bool(app_row)
    return render_template("job_details.html", job=job, already_applied=already_applied)


# =========================================================
# STUDENT AUTH
# =========================================================
@app.route("/student/register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        college = request.form.get("college", "").strip()
        branch = request.form.get("branch", "").strip()
        year = request.form.get("year", "").strip()

        if not all([full_name, email, password, phone]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for("student_register"))

        existing = query_db("SELECT id FROM students WHERE email=%s", (email,), fetchone=True)
        if existing:
            flash("An account with this email already exists.", "error")
            return redirect(url_for("student_register"))

        hashed = generate_password_hash(password)
        query_db(
            """INSERT INTO students (full_name, email, password, phone, college, branch, year)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (full_name, email, hashed, phone, college, branch, year), commit=True
        )
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("student_login"))

    return render_template("student_register.html")


@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        student = query_db("SELECT * FROM students WHERE email=%s", (email,), fetchone=True)
        if student and check_password_hash(student["password"], password):
            if student["status"] == "blocked":
                flash("Your account has been blocked by admin. Contact support.", "error")
                return redirect(url_for("student_login"))
            session["user_type"] = "student"
            session["user_id"] = student["id"]
            session["user_name"] = student["full_name"]
            flash(f"Welcome back, {student['full_name']}!", "success")
            return redirect(url_for("student_dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("student_login.html")


@app.route("/student/forgot-password", methods=["GET", "POST"])
def student_forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        new_password = request.form.get("new_password", "")
        student = query_db("SELECT id FROM students WHERE email=%s", (email,), fetchone=True)
        if not student:
            flash("No account found with this email.", "error")
            return redirect(url_for("student_forgot_password"))
        hashed = generate_password_hash(new_password)
        query_db("UPDATE students SET password=%s WHERE email=%s", (hashed, email), commit=True)
        flash("Password reset successful! Please log in with your new password.", "success")
        return redirect(url_for("student_login"))
    return render_template("forgot_password.html", user_type="student")


@app.route("/student/logout")
def student_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# =========================================================
# STUDENT DASHBOARD / PROFILE / JOBS
# =========================================================
@app.route("/student/dashboard")
@student_required
def student_dashboard():
    sid = session["user_id"]
    total_applied = query_db(
        "SELECT COUNT(*) AS c FROM applications WHERE student_id=%s", (sid,), fetchone=True
    )["c"]
    shortlisted = query_db(
        "SELECT COUNT(*) AS c FROM applications WHERE student_id=%s AND status='Shortlisted'",
        (sid,), fetchone=True
    )["c"]
    selected = query_db(
        "SELECT COUNT(*) AS c FROM applications WHERE student_id=%s AND status='Selected'",
        (sid,), fetchone=True
    )["c"]
    open_jobs = query_db("SELECT COUNT(*) AS c FROM jobs WHERE status='open'", fetchone=True)["c"]
    recent_jobs = query_db(
        """SELECT jobs.*, companies.company_name FROM jobs
           JOIN companies ON jobs.company_id=companies.id
           WHERE jobs.status='open' ORDER BY jobs.created_at DESC LIMIT 5""",
        fetchall=True
    )
    student = query_db("SELECT * FROM students WHERE id=%s", (sid,), fetchone=True)
    return render_template("student_dashboard.html", student=student, total_applied=total_applied,
                            shortlisted=shortlisted, selected=selected, open_jobs=open_jobs,
                            recent_jobs=recent_jobs)


@app.route("/student/profile", methods=["GET", "POST"])
@student_required
def student_profile():
    sid = session["user_id"]
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        college = request.form.get("college", "").strip()
        branch = request.form.get("branch", "").strip()
        year = request.form.get("year", "").strip()
        skills = request.form.get("skills", "").strip()

        query_db(
            """UPDATE students SET full_name=%s, phone=%s, college=%s, branch=%s,
               year=%s, skills=%s WHERE id=%s""",
            (full_name, phone, college, branch, year, skills, sid), commit=True
        )
        session["user_name"] = full_name
        flash("Profile updated successfully!", "success")
        return redirect(url_for("student_profile"))

    student = query_db("SELECT * FROM students WHERE id=%s", (sid,), fetchone=True)
    return render_template("student_profile.html", student=student)


@app.route("/student/upload-photo", methods=["POST"])
@student_required
def upload_photo():
    sid = session["user_id"]
    file = request.files.get("photo")
    if file and allowed_file(file.filename, config.ALLOWED_IMAGE_EXT):
        filename = save_upload(file, config.PHOTO_FOLDER, f"photo_{sid}")
        query_db("UPDATE students SET profile_photo=%s WHERE id=%s", (filename, sid), commit=True)
        flash("Profile photo updated!", "success")
    else:
        flash("Please upload a valid image file (jpg, jpeg, png).", "error")
    return redirect(url_for("student_profile"))


@app.route("/student/upload-resume", methods=["POST"])
@student_required
def upload_resume():
    sid = session["user_id"]
    file = request.files.get("resume")
    if file and allowed_file(file.filename, config.ALLOWED_RESUME_EXT):
        filename = save_upload(file, config.RESUME_FOLDER, f"resume_{sid}")
        query_db("UPDATE students SET resume=%s WHERE id=%s", (filename, sid), commit=True)
        query_db("INSERT INTO resumes (student_id, filename) VALUES (%s,%s)", (sid, filename), commit=True)
        flash("Resume uploaded successfully!", "success")
    else:
        flash("Please upload a valid PDF file.", "error")
    return redirect(url_for("student_profile"))


@app.route("/student/apply/<int:job_id>", methods=["POST"])
@student_required
def apply_job(job_id):
    sid = session["user_id"]
    student = query_db("SELECT resume FROM students WHERE id=%s", (sid,), fetchone=True)
    if not student or not student["resume"]:
        flash("Please upload your resume before applying to jobs.", "error")
        return redirect(url_for("student_profile"))

    job = query_db("SELECT * FROM jobs WHERE id=%s", (job_id,), fetchone=True)
    if not job or job["status"] != "open":
        flash("This job is no longer accepting applications.", "error")
        return redirect(url_for("jobs"))

    existing = query_db(
        "SELECT id FROM applications WHERE job_id=%s AND student_id=%s", (job_id, sid), fetchone=True
    )
    if existing:
        flash("You have already applied for this job.", "error")
        return redirect(url_for("job_details", job_id=job_id))

    query_db(
        "INSERT INTO applications (job_id, student_id) VALUES (%s,%s)", (job_id, sid), commit=True
    )
    flash("Application submitted successfully!", "success")
    return redirect(url_for("student_applications"))


@app.route("/student/applications")
@student_required
def student_applications():
    sid = session["user_id"]
    applications = query_db(
        """SELECT applications.*, jobs.title, jobs.location, jobs.job_type, jobs.last_date,
                  companies.company_name
           FROM applications
           JOIN jobs ON applications.job_id = jobs.id
           JOIN companies ON jobs.company_id = companies.id
           WHERE applications.student_id=%s
           ORDER BY applications.applied_at DESC""",
        (sid,), fetchall=True
    )
    return render_template("student_applications.html", applications=applications)


# =========================================================
# COMPANY AUTH
# =========================================================
@app.route("/company/register", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()
        website = request.form.get("website", "").strip()
        address = request.form.get("address", "").strip()
        description = request.form.get("description", "").strip()

        if not all([company_name, email, password, phone]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for("company_register"))

        existing = query_db("SELECT id FROM companies WHERE email=%s", (email,), fetchone=True)
        if existing:
            flash("An account with this email already exists.", "error")
            return redirect(url_for("company_register"))

        hashed = generate_password_hash(password)
        query_db(
            """INSERT INTO companies (company_name, email, password, phone, website, address, description)
               VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (company_name, email, hashed, phone, website, address, description), commit=True
        )
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("company_login"))

    return render_template("company_register.html")


@app.route("/company/login", methods=["GET", "POST"])
def company_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        company = query_db("SELECT * FROM companies WHERE email=%s", (email,), fetchone=True)
        if company and check_password_hash(company["password"], password):
            if company["status"] == "blocked":
                flash("Your account has been blocked by admin. Contact support.", "error")
                return redirect(url_for("company_login"))
            session["user_type"] = "company"
            session["user_id"] = company["id"]
            session["user_name"] = company["company_name"]
            flash(f"Welcome back, {company['company_name']}!", "success")
            return redirect(url_for("company_dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("company_login.html")


@app.route("/company/logout")
def company_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# =========================================================
# COMPANY DASHBOARD / PROFILE / JOBS
# =========================================================
@app.route("/company/dashboard")
@company_required
def company_dashboard():
    cid = session["user_id"]
    total_jobs = query_db(
        "SELECT COUNT(*) AS c FROM jobs WHERE company_id=%s", (cid,), fetchone=True
    )["c"]
    open_jobs = query_db(
        "SELECT COUNT(*) AS c FROM jobs WHERE company_id=%s AND status='open'", (cid,), fetchone=True
    )["c"]
    total_applicants = query_db(
        """SELECT COUNT(*) AS c FROM applications
           JOIN jobs ON applications.job_id = jobs.id
           WHERE jobs.company_id=%s""", (cid,), fetchone=True
    )["c"]
    job_list = query_db(
        "SELECT * FROM jobs WHERE company_id=%s ORDER BY created_at DESC", (cid,), fetchall=True
    )
    company = query_db("SELECT * FROM companies WHERE id=%s", (cid,), fetchone=True)
    return render_template("company_dashboard.html", company=company, total_jobs=total_jobs,
                            open_jobs=open_jobs, total_applicants=total_applicants, jobs=job_list)


@app.route("/company/profile", methods=["GET", "POST"])
@company_required
def company_profile():
    cid = session["user_id"]
    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        phone = request.form.get("phone", "").strip()
        website = request.form.get("website", "").strip()
        address = request.form.get("address", "").strip()
        description = request.form.get("description", "").strip()

        query_db(
            """UPDATE companies SET company_name=%s, phone=%s, website=%s,
               address=%s, description=%s WHERE id=%s""",
            (company_name, phone, website, address, description, cid), commit=True
        )
        session["user_name"] = company_name

        logo_file = request.files.get("logo")
        if logo_file and logo_file.filename and allowed_file(logo_file.filename, config.ALLOWED_IMAGE_EXT):
            filename = save_upload(logo_file, config.LOGO_FOLDER, f"logo_{cid}")
            query_db("UPDATE companies SET logo=%s WHERE id=%s", (filename, cid), commit=True)

        flash("Company profile updated successfully!", "success")
        return redirect(url_for("company_profile"))

    company = query_db("SELECT * FROM companies WHERE id=%s", (cid,), fetchone=True)
    return render_template("company_profile.html", company=company)


@app.route("/company/post-job", methods=["GET", "POST"])
@company_required
def post_job():
    if request.method == "POST":
        cid = session["user_id"]
        title = request.form.get("title", "").strip()
        location = request.form.get("location", "").strip()
        salary = request.form.get("salary", "").strip() or "Not Disclosed"
        job_type = request.form.get("job_type", "Internship")
        experience = request.form.get("experience", "").strip() or "Fresher"
        skills = request.form.get("skills", "").strip()
        description = request.form.get("description", "").strip()
        last_date = request.form.get("last_date", "")

        if not all([title, location, last_date]):
            flash("Please fill all required fields.", "error")
            return redirect(url_for("post_job"))

        query_db(
            """INSERT INTO jobs (company_id, title, location, salary, job_type, experience,
               skills, description, last_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (cid, title, location, salary, job_type, experience, skills, description, last_date),
            commit=True
        )
        flash("Job posted successfully!", "success")
        return redirect(url_for("company_dashboard"))

    return render_template("post_job.html")


@app.route("/company/edit-job/<int:job_id>", methods=["GET", "POST"])
@company_required
def edit_job(job_id):
    cid = session["user_id"]
    job = query_db("SELECT * FROM jobs WHERE id=%s AND company_id=%s", (job_id, cid), fetchone=True)
    if not job:
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        location = request.form.get("location", "").strip()
        salary = request.form.get("salary", "").strip() or "Not Disclosed"
        job_type = request.form.get("job_type", "Internship")
        experience = request.form.get("experience", "").strip() or "Fresher"
        skills = request.form.get("skills", "").strip()
        description = request.form.get("description", "").strip()
        last_date = request.form.get("last_date", "")
        status = request.form.get("status", "open")

        query_db(
            """UPDATE jobs SET title=%s, location=%s, salary=%s, job_type=%s, experience=%s,
               skills=%s, description=%s, last_date=%s, status=%s WHERE id=%s AND company_id=%s""",
            (title, location, salary, job_type, experience, skills, description, last_date,
             status, job_id, cid), commit=True
        )
        flash("Job updated successfully!", "success")
        return redirect(url_for("company_dashboard"))

    return render_template("edit_job.html", job=job)


@app.route("/company/delete-job/<int:job_id>", methods=["POST"])
@company_required
def delete_job(job_id):
    cid = session["user_id"]
    query_db("DELETE FROM jobs WHERE id=%s AND company_id=%s", (job_id, cid), commit=True)
    flash("Job deleted successfully.", "success")
    return redirect(url_for("company_dashboard"))


@app.route("/company/applicants/<int:job_id>")
@company_required
def view_applicants(job_id):
    cid = session["user_id"]
    job = query_db("SELECT * FROM jobs WHERE id=%s AND company_id=%s", (job_id, cid), fetchone=True)
    if not job:
        abort(404)
    applicants = query_db(
        """SELECT applications.*, students.full_name, students.email, students.phone,
                  students.college, students.branch, students.skills, students.resume,
                  students.profile_photo
           FROM applications
           JOIN students ON applications.student_id = students.id
           WHERE applications.job_id=%s
           ORDER BY applications.applied_at DESC""",
        (job_id,), fetchall=True
    )
    return render_template("view_applicants.html", job=job, applicants=applicants)


@app.route("/company/update-application-status/<int:app_id>", methods=["POST"])
@company_required
def update_application_status(app_id):
    new_status = request.form.get("status")
    application = query_db(
        """SELECT applications.id, jobs.company_id, jobs.id AS job_id FROM applications
           JOIN jobs ON applications.job_id = jobs.id WHERE applications.id=%s""",
        (app_id,), fetchone=True
    )
    if not application or application["company_id"] != session["user_id"]:
        abort(403)
    query_db("UPDATE applications SET status=%s WHERE id=%s", (new_status, app_id), commit=True)
    flash("Applicant status updated.", "success")
    return redirect(url_for("view_applicants", job_id=application["job_id"]))


@app.route("/download-resume/<int:student_id>")
def download_resume(student_id):
    # Company users can download any applicant's resume; students can download their own.
    if session.get("user_type") not in ("company", "admin", "student"):
        abort(403)
    student = query_db("SELECT resume, full_name FROM students WHERE id=%s", (student_id,), fetchone=True)
    if not student or not student["resume"]:
        abort(404)
    return send_from_directory(config.RESUME_FOLDER, student["resume"], as_attachment=True)


# =========================================================
# ADMIN AUTH
# =========================================================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = query_db("SELECT * FROM admins WHERE username=%s", (username,), fetchone=True)
        if admin and check_password_hash(admin["password"], password):
            session["user_type"] = "admin"
            session["user_id"] = admin["id"]
            session["user_name"] = admin["username"]
            flash("Welcome back, Admin!", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# =========================================================
# ADMIN DASHBOARD / MANAGEMENT
# =========================================================
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    stats = {
        "students": query_db("SELECT COUNT(*) AS c FROM students", fetchone=True)["c"],
        "companies": query_db("SELECT COUNT(*) AS c FROM companies", fetchone=True)["c"],
        "jobs": query_db("SELECT COUNT(*) AS c FROM jobs", fetchone=True)["c"],
        "applications": query_db("SELECT COUNT(*) AS c FROM applications", fetchone=True)["c"],
        "open_jobs": query_db("SELECT COUNT(*) AS c FROM jobs WHERE status='open'", fetchone=True)["c"],
        "blocked_students": query_db(
            "SELECT COUNT(*) AS c FROM students WHERE status='blocked'", fetchone=True)["c"],
        "blocked_companies": query_db(
            "SELECT COUNT(*) AS c FROM companies WHERE status='blocked'", fetchone=True)["c"],
    }
    recent_students = query_db(
        "SELECT * FROM students ORDER BY created_at DESC LIMIT 5", fetchall=True
    )
    recent_companies = query_db(
        "SELECT * FROM companies ORDER BY created_at DESC LIMIT 5", fetchall=True
    )
    return render_template("admin_dashboard.html", stats=stats, recent_students=recent_students,
                            recent_companies=recent_companies)


@app.route("/admin/students")
@admin_required
def manage_students():
    students = query_db("SELECT * FROM students ORDER BY created_at DESC", fetchall=True)
    return render_template("manage_students.html", students=students)


@app.route("/admin/companies")
@admin_required
def manage_companies():
    companies = query_db("SELECT * FROM companies ORDER BY created_at DESC", fetchall=True)
    return render_template("manage_companies.html", companies=companies)


@app.route("/admin/jobs")
@admin_required
def manage_jobs():
    job_list = query_db(
        """SELECT jobs.*, companies.company_name FROM jobs
           JOIN companies ON jobs.company_id = companies.id
           ORDER BY jobs.created_at DESC""", fetchall=True
    )
    return render_template("manage_jobs.html", jobs=job_list)


@app.route("/admin/toggle-student/<int:student_id>", methods=["POST"])
@admin_required
def toggle_student(student_id):
    student = query_db("SELECT status FROM students WHERE id=%s", (student_id,), fetchone=True)
    if not student:
        abort(404)
    new_status = "blocked" if student["status"] == "active" else "active"
    query_db("UPDATE students SET status=%s WHERE id=%s", (new_status, student_id), commit=True)
    flash(f"Student account {new_status}.", "success")
    return redirect(url_for("manage_students"))


@app.route("/admin/delete-student/<int:student_id>", methods=["POST"])
@admin_required
def delete_student(student_id):
    query_db("DELETE FROM students WHERE id=%s", (student_id,), commit=True)
    flash("Student account deleted.", "success")
    return redirect(url_for("manage_students"))


@app.route("/admin/toggle-company/<int:company_id>", methods=["POST"])
@admin_required
def toggle_company(company_id):
    company = query_db("SELECT status FROM companies WHERE id=%s", (company_id,), fetchone=True)
    if not company:
        abort(404)
    new_status = "blocked" if company["status"] == "active" else "active"
    query_db("UPDATE companies SET status=%s WHERE id=%s", (new_status, company_id), commit=True)
    flash(f"Company account {new_status}.", "success")
    return redirect(url_for("manage_companies"))


@app.route("/admin/delete-company/<int:company_id>", methods=["POST"])
@admin_required
def delete_company(company_id):
    query_db("DELETE FROM companies WHERE id=%s", (company_id,), commit=True)
    flash("Company account deleted.", "success")
    return redirect(url_for("manage_companies"))


@app.route("/admin/delete-job/<int:job_id>", methods=["POST"])
@admin_required
def admin_delete_job(job_id):
    query_db("DELETE FROM jobs WHERE id=%s", (job_id,), commit=True)
    flash("Job deleted.", "success")
    return redirect(url_for("manage_jobs"))


# =========================================================
# SETTINGS (shared page for student/company - change password)
# =========================================================
@app.route("/settings", methods=["GET", "POST"])
def settings():
    user_type = session.get("user_type")
    if user_type not in ("student", "company"):
        flash("Please log in to access settings.", "error")
        return redirect(url_for("index"))

    table = "students" if user_type == "student" else "companies"
    uid = session["user_id"]

    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        row = query_db(f"SELECT password FROM {table} WHERE id=%s", (uid,), fetchone=True)
        if row and check_password_hash(row["password"], current_password):
            hashed = generate_password_hash(new_password)
            query_db(f"UPDATE {table} SET password=%s WHERE id=%s", (hashed, uid), commit=True)
            flash("Password changed successfully!", "success")
        else:
            flash("Current password is incorrect.", "error")
        return redirect(url_for("settings"))

    return render_template("settings.html", user_type=user_type)


# =========================================================
# ERROR HANDLERS
# =========================================================
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(413)
def too_large(e):
    flash("File is too large. Maximum upload size is 5 MB.", "error")
    return redirect(request.referrer or url_for("index"))


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)
