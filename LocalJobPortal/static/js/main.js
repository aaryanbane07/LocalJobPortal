// =========================================================
// Local Job Portal - main.js
// Modern UI Interactions & Micro-animations
// =========================================================

document.addEventListener("DOMContentLoaded", () => {

  /* ---------------- FLASH MESSAGE DISMISSAL ---------------- */
  const flashMessages = document.querySelectorAll(".flash");
  flashMessages.forEach((flash) => {
    // Auto dismiss after 4 seconds
    const timer = setTimeout(() => {
      dismissFlash(flash);
    }, 4000);

    // Close button click
    const closeBtn = flash.querySelector(".flash-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        clearTimeout(timer);
        dismissFlash(flash);
      });
    }
  });

  function dismissFlash(flash) {
    flash.style.opacity = "0";
    flash.style.transform = "translateX(50px) scale(0.95)";
    setTimeout(() => {
      if (flash.parentElement) {
        flash.remove();
      }
    }, 300);
  }

  /* ---------------- NAVBAR SCROLL MORPH ---------------- */
  const navbar = document.querySelector(".navbar");
  if (navbar) {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        navbar.classList.add("scrolled");
      } else {
        navbar.classList.remove("scrolled");
      }
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    handleScroll();
  }

  /* ---------------- MOBILE DRAWER NAVIGATION ---------------- */
  const burgerBtn = document.getElementById("mobileBurgerBtn");
  const drawer = document.getElementById("mobileDrawer");
  const drawerOverlay = document.getElementById("mobileDrawerOverlay");
  const drawerCloseBtn = document.getElementById("mobileDrawerClose");

  function openDrawer() {
    if (drawer && drawerOverlay) {
      drawer.classList.add("active");
      drawerOverlay.classList.add("active");
      document.body.style.overflow = "hidden";
    }
  }

  function closeDrawer() {
    if (drawer && drawerOverlay) {
      drawer.classList.remove("active");
      drawerOverlay.classList.remove("active");
      document.body.style.overflow = "";
    }
  }

  if (burgerBtn) burgerBtn.addEventListener("click", openDrawer);
  if (drawerCloseBtn) drawerCloseBtn.addEventListener("click", closeDrawer);
  if (drawerOverlay) drawerOverlay.addEventListener("click", closeDrawer);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && drawer && drawer.classList.contains("active")) {
      closeDrawer();
    }
  });

  /* ---------------- NUMBER COUNTER ANIMATION ---------------- */
  const counters = document.querySelectorAll(".stat-card h2, .dcard h2");
  if (counters.length > 0 && "IntersectionObserver" in window) {
    const counterObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const el = entry.target;
          const text = el.innerText.trim();
          const targetNum = parseInt(text.replace(/[^0-9]/g, ""), 10);

          if (!isNaN(targetNum) && targetNum > 0) {
            const hasPlus = text.includes("+");
            let current = 0;
            const duration = 1200; // ms
            const stepTime = Math.max(Math.floor(duration / targetNum), 20);
            const stepIncrement = Math.max(Math.ceil(targetNum / (duration / stepTime)), 1);

            const timer = setInterval(() => {
              current += stepIncrement;
              if (current >= targetNum) {
                current = targetNum;
                clearInterval(timer);
              }
              el.innerText = current + (hasPlus ? "+" : "");
            }, stepTime);
          }
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.2 });

    counters.forEach((c) => counterObserver.observe(c));
  }

  /* ---------------- INSTANT IMAGE FILE PREVIEW ---------------- */
  const photoInput = document.getElementById("photoInput");
  if (photoInput) {
    photoInput.addEventListener("change", function () {
      if (this.files && this.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
          const preview = document.querySelector(".profile-photo-preview");
          const placeholder = document.querySelector(".profile-photo-placeholder");
          if (preview) {
            preview.src = e.target.result;
          } else if (placeholder) {
            const img = document.createElement("img");
            img.src = e.target.result;
            img.className = "profile-photo-preview";
            placeholder.parentNode.replaceChild(img, placeholder);
          }
        };
        reader.readAsDataURL(this.files[0]);
      }
    });
  }

  /* ---------------- BUTTON RIPPLE EFFECT ---------------- */
  document.querySelectorAll(".btn-gradient, .btn-primary").forEach((btn) => {
    btn.addEventListener("click", function (e) {
      const rect = this.getBoundingClientRect();
      const circle = document.createElement("span");
      const diameter = Math.max(rect.width, rect.height);
      const radius = diameter / 2;

      circle.style.width = circle.style.height = `${diameter}px`;
      circle.style.left = `${e.clientX - rect.left - radius}px`;
      circle.style.top = `${e.clientY - rect.top - radius}px`;
      circle.classList.add("ripple-effect");

      const existingRipple = this.querySelector(".ripple-effect");
      if (existingRipple) existingRipple.remove();

      this.appendChild(circle);
      setTimeout(() => circle.remove(), 600);
    });
  });

});

/* ---------------- FAQ ACCORDION HANDLER ---------------- */
function toggleFaq(element) {
  const item = element.closest(".faq-item");
  if (!item) return;

  const isAlreadyOpen = item.classList.contains("open");

  // Optional: close other open items for cleaner UX
  document.querySelectorAll(".faq-item").forEach((faq) => {
    if (faq !== item) {
      faq.classList.remove("open");
    }
  });

  if (isAlreadyOpen) {
    item.classList.remove("open");
  } else {
    item.classList.add("open");
  }
}