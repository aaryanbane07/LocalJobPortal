-- =========================================================
-- Local Job Portal - Database Schema
-- CEP (Course End Project)
-- =========================================================

CREATE DATABASE IF NOT EXISTS local_job_portal;
USE local_job_portal;

-- ---------------------------------------------------------
-- Table: students
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    college VARCHAR(150) DEFAULT '',
    branch VARCHAR(100) DEFAULT '',
    year VARCHAR(20) DEFAULT '',
    skills VARCHAR(255) DEFAULT '',
    profile_photo VARCHAR(255) DEFAULT NULL,
    resume VARCHAR(255) DEFAULT NULL,
    status ENUM('active','blocked') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------
-- Table: companies
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS companies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    website VARCHAR(150) DEFAULT '',
    address VARCHAR(255) DEFAULT '',
    description TEXT,
    logo VARCHAR(255) DEFAULT NULL,
    status ENUM('active','blocked') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------
-- Table: admins
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ---------------------------------------------------------
-- Table: jobs
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    location VARCHAR(120) NOT NULL,
    salary VARCHAR(60) DEFAULT 'Not Disclosed',
    job_type ENUM('Full-Time','Part-Time','Internship','Contract') DEFAULT 'Internship',
    experience VARCHAR(60) DEFAULT 'Fresher',
    skills VARCHAR(255) DEFAULT '',
    description TEXT,
    last_date DATE NOT NULL,
    status ENUM('open','closed') DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- Table: applications
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    student_id INT NOT NULL,
    status ENUM('Applied','Shortlisted','Rejected','Selected') DEFAULT 'Applied',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_application (job_id, student_id)
);

-- ---------------------------------------------------------
-- Table: resumes  (history of resumes uploaded by students)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

-- ---------------------------------------------------------
-- Table: contact_messages (from Contact Us page)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================================================
-- DEFAULT ADMIN LOGIN
-- Username: admin
-- Password: admin123
-- (password below is a werkzeug pbkdf2:sha256 hash of "admin123")
-- =========================================================
INSERT INTO admins (username, password)
VALUES ('admin', 'pbkdf2:sha256:1000000$9Ty8EhxEbY8NUGmT$d2a36f8f35db32560d88143dd19f33cea8ac888c5bab1d3f02623334be4f4ce3')
ON DUPLICATE KEY UPDATE username = username;
