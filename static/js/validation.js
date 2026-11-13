// =========================================================
// Local Job Portal - validation.js
// Client-side JavaScript validation for all forms
// =========================================================

const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
const PHONE_REGEX = /^[6-9]\d{9}$/; // 10 digit Indian mobile number

function showError(inputId, message) {
  const input = document.getElementById(inputId);
  const errorSpan = document.getElementById(inputId + "Error");
  if (input) input.classList.add("invalid");
  if (errorSpan) {
    errorSpan.textContent = message;
    errorSpan.style.display = "block";
  }
}

function clearError(inputId) {
  const input = document.getElementById(inputId);
  const errorSpan = document.getElementById(inputId + "Error");
  if (input) input.classList.remove("invalid");
  if (errorSpan) {
    errorSpan.textContent = "";
    errorSpan.style.display = "none";
  }
}

function isEmpty(value) {
  return !value || value.trim().length === 0;
}

// ---------------------------------------------------------
// Generic field validators (return true if VALID)
// ---------------------------------------------------------
function validateRequired(id, label) {
  const el = document.getElementById(id);
  if (!el || isEmpty(el.value)) {
    showError(id, (label || "This field") + " is required.");
    return false;
  }
  clearError(id);
  return true;
}

function validateEmailField(id) {
  const el = document.getElementById(id);
  if (!el || isEmpty(el.value)) {
    showError(id, "Email address is required.");
    return false;
  }
  if (!EMAIL_REGEX.test(el.value.trim())) {
    showError(id, "Please enter a valid email address (e.g. name@domain.com).");
    return false;
  }
  clearError(id);
  return true;
}

function validatePasswordField(id, minLen = 6) {
  const el = document.getElementById(id);
  if (!el || isEmpty(el.value)) {
    showError(id, "Password is required.");
    return false;
  }
  if (el.value.length < minLen) {
    showError(id, `Password must be at least ${minLen} characters long.`);
    return false;
  }
  clearError(id);
  return true;
}

function validatePhoneField(id) {
  const el = document.getElementById(id);
  if (!el || isEmpty(el.value)) {
    showError(id, "Phone number is required.");
    return false;
  }
  const cleanPhone = el.value.trim().replace(/\D/g, "");
  if (!PHONE_REGEX.test(cleanPhone)) {
    showError(id, "Please enter a valid 10-digit Indian phone number.");
    return false;
  }
  clearError(id);
  return true;
}

function validateDateField(id) {
  const el = document.getElementById(id);
  if (!el || isEmpty(el.value)) {
    showError(id, "Last date to apply is required.");
    return false;
  }
  const selectedDate = new Date(el.value);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  if (selectedDate < today) {
    showError(id, "Last date cannot be in the past.");
    return false;
  }
  clearError(id);
  return true;
}

// ---------------------------------------------------------
// FORM-SPECIFIC VALIDATORS
// ---------------------------------------------------------

function validateLoginForm() {
  const emailValid = validateEmailField("email");
  const passwordValid = validateRequired("password", "Password");
  return emailValid && passwordValid;
}

function validateAdminLoginForm() {
  const userValid = validateRequired("username", "Username");
  const passValid = validateRequired("password", "Password");
  return userValid && passValid;
}

function validateForgotForm() {
  const emailValid = validateEmailField("email");
  const passValid = validatePasswordField("new_password");
  return emailValid && passValid;
}

function validateStudentRegisterForm() {
  const nameValid = validateRequired("full_name", "Full name");
  const emailValid = validateEmailField("email");
  const passValid = validatePasswordField("password");
  const phoneValid = validatePhoneField("phone");
  return nameValid && emailValid && passValid && phoneValid;
}

function validateCompanyRegisterForm() {
  const nameValid = validateRequired("company_name", "Company name");
  const emailValid = validateEmailField("email");
  const passValid = validatePasswordField("password");
  const phoneValid = validatePhoneField("phone");
  return nameValid && emailValid && passValid && phoneValid;
}

function validateProfileForm() {
  const nameValid = validateRequired("full_name", "Full name");
  const phoneValid = validatePhoneField("phone");
  return nameValid && phoneValid;
}

function validateCompanyProfileForm() {
  const nameValid = validateRequired("company_name", "Company name");
  const phoneValid = validatePhoneField("phone");
  return nameValid && phoneValid;
}

function validateJobForm() {
  const titleValid = validateRequired("title", "Job title");
  const locationValid = validateRequired("location", "Location");
  const dateValid = validateDateField("last_date");
  return titleValid && locationValid && dateValid;
}

function validateSettingsForm() {
  const currentValid = validateRequired("current_password", "Current password");
  const newValid = validatePasswordField("new_password");
  return currentValid && newValid;
}

function validateContactForm() {
  const nameValid = validateRequired("name", "Full name");
  const emailValid = validateEmailField("email");
  const messageValid = validateRequired("message", "Message");
  return nameValid && emailValid && messageValid;
}

// ---------------------------------------------------------
// FILE VALIDATORS
// ---------------------------------------------------------
function validateResumeFile() {
  const input = document.getElementById("resumeInput");
  if (!input || !input.files || input.files.length === 0) {
    showError("resume", "Please select a resume file.");
    return false;
  }
  const file = input.files[0];
  const ext = file.name.split(".").pop().toLowerCase();
  if (ext !== "pdf") {
    showError("resume", "Only PDF files are allowed for resumes.");
    return false;
  }
  if (file.size > 5 * 1024 * 1024) {
    showError("resume", "File size must be under 5 MB.");
    return false;
  }
  clearError("resume");
  return true;
}

// ---------------------------------------------------------
// LIVE VALIDATION (on blur/input)
// ---------------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {
  const emailEl = document.getElementById("email");
  if (emailEl) {
    emailEl.addEventListener("blur", () => validateEmailField("email"));
    emailEl.addEventListener("input", () => {
      if (emailEl.classList.contains("invalid")) validateEmailField("email");
    });
  }

  const phoneEl = document.getElementById("phone");
  if (phoneEl) {
    phoneEl.addEventListener("input", function () {
      this.value = this.value.replace(/\D/g, "").slice(0, 10);
      if (phoneEl.classList.contains("invalid")) validatePhoneField("phone");
    });
    phoneEl.addEventListener("blur", () => validatePhoneField("phone"));
  }

  const passwordEl = document.getElementById("password");
  if (passwordEl) {
    passwordEl.addEventListener("blur", () => validatePasswordField("password"));
    passwordEl.addEventListener("input", () => {
      if (passwordEl.classList.contains("invalid")) validatePasswordField("password");
    });
  }

  const newPasswordEl = document.getElementById("new_password");
  if (newPasswordEl) {
    newPasswordEl.addEventListener("blur", () => validatePasswordField("new_password"));
    newPasswordEl.addEventListener("input", () => {
      if (newPasswordEl.classList.contains("invalid")) validatePasswordField("new_password");
    });
  }
});
