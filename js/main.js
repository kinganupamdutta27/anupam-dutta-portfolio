// =============================================
// MAIN JAVASCRIPT - Portfolio Interactions
// =============================================

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initMobileMenu();
  initTypingEffect();
  initScrollReveal();
  initSmoothScroll();
  initContactForm();
});

// Navbar scroll effect
function initNavbar() {
  const navbar = document.querySelector('.navbar');
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 50);
  });
}

// Mobile menu toggle
function initMobileMenu() {
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  
  toggle?.addEventListener('click', () => {
    toggle.classList.toggle('active');
    navLinks.classList.toggle('active');
  });
  
  // Close menu on link click
  document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
      toggle?.classList.remove('active');
      navLinks?.classList.remove('active');
    });
  });
}

// Typing effect for hero
function initTypingEffect() {
  const typingElement = document.getElementById('typing');
  if (!typingElement) return;
  
  const texts = [
    'Python Backend Engineer',
    'Generative AI Specialist',
    'LLM & RAG Engineer',
    'FastAPI Developer'
  ];
  
  let textIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  
  function type() {
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
  }
  
  type();
}

// Scroll reveal animations
function initScrollReveal() {
  const reveals = document.querySelectorAll('.reveal');
  
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
  reveal(); // Initial check
}

// Smooth scrolling
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
  
  // Active link highlighting
  const sections = document.querySelectorAll('section[id]');
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

// Contact form handling
function initContactForm() {
  const form = document.getElementById('contactForm');
  form?.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const name = form.querySelector('#name').value;
    const email = form.querySelector('#email').value;
    const message = form.querySelector('#message').value;
    
    // Create mailto link
    const mailtoLink = `mailto:anupamdutta27121998.in@gmail.com?subject=Portfolio Contact from ${name}&body=${encodeURIComponent(message)}%0A%0AFrom: ${name}%0AEmail: ${email}`;
    window.location.href = mailtoLink;
    
    // Reset form
    form.reset();
  });
}
