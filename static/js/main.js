// =============================================
// MAIN JAVASCRIPT - Portfolio Interactions
// Django + Wagtail CMS Version
// =============================================

document.addEventListener('DOMContentLoaded', () => {
  try {
    initNavbar();
    initMobileMenu();
    initTypingEffect();
    initScrollReveal();
    initSmoothScroll();
    initContactForm();
  } catch (error) {
    console.error('Initialization error:', error);
  }
});

// =============================================
// Navbar scroll effect
// =============================================
function initNavbar() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;

  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 50);
  });
}

// =============================================
// Mobile menu toggle
// =============================================
function initMobileMenu() {
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (!toggle || !navLinks) return;

  toggle.addEventListener('click', () => {
    toggle.classList.toggle('active');
    navLinks.classList.toggle('active');
  });

  // Close menu on link click
  document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
      toggle.classList.remove('active');
      navLinks.classList.remove('active');
    });
  });
}

// =============================================
// Typing effect for hero (dynamic from CMS)
// =============================================
function initTypingEffect() {
  const typingElement = document.getElementById('typing');
  if (!typingElement) return;

  // Get typing texts from CMS-injected config or use defaults
  const config = window.PORTFOLIO_CONFIG || {};
  const texts = config.typingTexts && config.typingTexts.length > 0
    ? config.typingTexts
    : [
        'Python Backend Engineer',
        'Generative AI Specialist',
        'LLM & RAG Engineer',
        'FastAPI Developer'
      ];

  let textIndex = 0;
  let charIndex = 0;
  let isDeleting = false;

  function type() {
    try {
      const currentText = texts[textIndex];

      if (isDeleting) {
        typingElement.textContent = currentText.substring(0, charIndex - 1);
        charIndex--;
      } else {
        typingElement.textContent = currentText.substring(0, charIndex + 1);
        charIndex++;
      }

      let typeSpeed = isDeleting ? 50 : 100;

      if (!isDeleting && charIndex === currentText.length) {
        typeSpeed = 2000;
        isDeleting = true;
      } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        textIndex = (textIndex + 1) % texts.length;
        typeSpeed = 500;
      }

      setTimeout(type, typeSpeed);
    } catch (error) {
      console.error('Typing effect error:', error);
    }
  }

  type();
}

// =============================================
// Scroll reveal animations
// =============================================
function initScrollReveal() {
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length === 0) return;

  const observerOptions = {
    threshold: 0.15,
    rootMargin: '0px 0px -50px 0px'
  };

  // Use IntersectionObserver for better performance
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('active');
          observer.unobserve(entry.target); // Stop observing once revealed
        }
      });
    }, observerOptions);

    reveals.forEach(el => observer.observe(el));
  } else {
    // Fallback for older browsers
    function reveal() {
      reveals.forEach(el => {
        const windowHeight = window.innerHeight;
        const revealTop = el.getBoundingClientRect().top;
        const revealPoint = 150;

        if (revealTop < windowHeight - revealPoint) {
          el.classList.add('active');
        }
      });
    }

    window.addEventListener('scroll', reveal);
    reveal();
  }
}

// =============================================
// Smooth scrolling with active link highlighting
// =============================================
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      if (!targetId || targetId === '#') return;

      const target = document.querySelector(targetId);
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // Active link highlighting
  const sections = document.querySelectorAll('section[id]');
  if (sections.length === 0) return;

  window.addEventListener('scroll', () => {
    let current = '';
    sections.forEach(section => {
      const sectionTop = section.offsetTop - 100;
      if (scrollY >= sectionTop) {
        current = section.getAttribute('id');
      }
    });

    document.querySelectorAll('.nav-links a').forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });
  });
}

// =============================================
// Contact form with AJAX submission
// =============================================
function initContactForm() {
  const form = document.getElementById('contactForm');
  if (!form) return;

  const submitBtn = document.getElementById('submitBtn');
  const submitText = document.getElementById('submitText');
  const statusDiv = document.getElementById('form-status');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Clear previous errors
    clearFormErrors();
    hideStatus();

    // Client-side validation
    if (!validateForm()) return;

    // Get config from CMS
    const config = window.PORTFOLIO_CONFIG || {};
    const formUrl = config.contactFormUrl || '/api/contact/submit/';
    const csrfToken = config.csrfToken || getCsrfToken();

    // Show loading state
    setLoading(true);

    try {
      const formData = new FormData(form);

      const response = await fetch(formUrl, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': csrfToken,
        },
        body: formData,
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        showStatus('success', data.message);
        form.reset();
      } else if (response.status === 429) {
        showStatus('error', data.message || 'Too many requests. Please try again later.');
      } else {
        showStatus('error', data.message || 'Something went wrong. Please try again.');
        // Show field-level errors
        if (data.errors) {
          Object.entries(data.errors).forEach(([field, message]) => {
            showFieldError(field, message);
          });
        }
      }
    } catch (error) {
      console.error('Contact form submission error:', error);
      showStatus('error', 'Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  });

  // ---- Helper functions ----

  function validateForm() {
    let isValid = true;
    const name = form.querySelector('#name');
    const email = form.querySelector('#email');
    const message = form.querySelector('#message');

    if (!name.value.trim() || name.value.trim().length < 2) {
      showFieldError('name', 'Name must be at least 2 characters.');
      isValid = false;
    }

    if (!email.value.trim() || !isValidEmail(email.value.trim())) {
      showFieldError('email', 'Please enter a valid email address.');
      isValid = false;
    }

    if (!message.value.trim() || message.value.trim().length < 10) {
      showFieldError('message', 'Message must be at least 10 characters.');
      isValid = false;
    }

    return isValid;
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function showFieldError(field, message) {
    const errorEl = document.getElementById(`error-${field}`);
    const inputEl = document.getElementById(field);
    if (errorEl) errorEl.textContent = message;
    if (inputEl) inputEl.classList.add('error');
  }

  function clearFormErrors() {
    document.querySelectorAll('.form-error').forEach(el => el.textContent = '');
    document.querySelectorAll('.form-group input, .form-group textarea').forEach(el => {
      el.classList.remove('error');
    });
  }

  function showStatus(type, message) {
    if (!statusDiv) return;
    statusDiv.textContent = message;
    statusDiv.className = `form-status ${type}`;
    statusDiv.style.display = 'block';

    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
      setTimeout(hideStatus, 5000);
    }
  }

  function hideStatus() {
    if (statusDiv) {
      statusDiv.style.display = 'none';
    }
  }

  function setLoading(loading) {
    if (!submitBtn) return;
    if (loading) {
      submitBtn.classList.add('btn-loading');
      submitBtn.disabled = true;
      if (submitText) submitText.textContent = 'Sending...';
    } else {
      submitBtn.classList.remove('btn-loading');
      submitBtn.disabled = false;
      if (submitText) submitText.textContent = 'Send Message';
    }
  }

  function getCsrfToken() {
    // Try to get CSRF token from cookie
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrftoken') return value;
    }
    // Try to get from hidden input
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
  }
}
