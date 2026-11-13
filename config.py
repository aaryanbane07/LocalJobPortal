"""
config.py
Central configuration for Local Job Portal
Change the DB_CONFIG values below to match your MySQL installation.
"""

import os

# ---------------- MySQL DATABASE CONFIG ----------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",        # <-- change this to your MySQL root password
    "database": "local_job_portal"
}

# ---------------- FLASK APP CONFIG ----------------
SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-development-secret-key")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
RESUME_FOLDER = os.path.join(UPLOAD_FOLDER, "resumes")
PHOTO_FOLDER = os.path.join(UPLOAD_FOLDER, "photos")
LOGO_FOLDER = os.path.join(UPLOAD_FOLDER, "logos")

ALLOWED_RESUME_EXT = {"pdf"}
ALLOWED_IMAGE_EXT = {"jpg", "jpeg", "png"}

MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload size
