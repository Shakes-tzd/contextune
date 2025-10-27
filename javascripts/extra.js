/* ============================================
   Contextune - Enhanced Documentation JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {

  // Add smooth scroll behavior
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // Add copy button animation feedback
  document.addEventListener('clipboard-copy', function(e) {
    const button = e.target.closest('button');
    if (button) {
      const originalText = button.innerHTML;
      button.innerHTML = '✓ Copied!';
      button.style.background = '#2dce89';
      setTimeout(() => {
        button.innerHTML = originalText;
        button.style.background = '';
      }, 2000);
    }
  });

  // Enhance feature sections with intersection observer
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);

  // Observe feature sections
  document.querySelectorAll('.md-typeset h3').forEach(heading => {
    heading.style.opacity = '0';
    heading.style.transform = 'translateY(20px)';
    heading.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(heading);
  });

  // Add stats counter animation
  function animateCounter(element, target, duration = 1000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        element.textContent = Math.round(target);
        clearInterval(timer);
      } else {
        element.textContent = Math.round(current);
      }
    }, 16);
  }

  // Find and animate percentage numbers
  document.querySelectorAll('code').forEach(code => {
    const text = code.textContent;
    const match = text.match(/(\d+)%/);
    if (match) {
      const number = parseInt(match[1]);
      if (number > 10) { // Only animate significant percentages
        const numberSpan = document.createElement('span');
        numberSpan.textContent = '0';
        code.innerHTML = code.innerHTML.replace(match[0], `<span class="animated-stat">${match[0]}</span>`);

        const observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const statElement = entry.target;
              animateCounter(statElement, number);
              statElement.innerHTML = statElement.innerHTML.replace(/\d+/, '<span class="number"></span>');
              const numberElement = statElement.querySelector('.number');
              animateCounter(numberElement, number);
              setTimeout(() => {
                numberElement.textContent = number;
              }, 1000);
              observer.unobserve(entry.target);
            }
          });
        });

        const animatedStat = code.querySelector('.animated-stat');
        if (animatedStat) {
          observer.observe(animatedStat);
        }
      }
    }
  });

  // Add hover effect to navigation items
  document.querySelectorAll('.md-nav__link').forEach(link => {
    link.addEventListener('mouseenter', function() {
      this.style.transform = 'translateX(5px)';
      this.style.transition = 'transform 0.2s ease';
    });

    link.addEventListener('mouseleave', function() {
      this.style.transform = 'translateX(0)';
    });
  });

  // Enhanced table interactions
  document.querySelectorAll('.md-typeset table').forEach(table => {
    table.addEventListener('mouseover', function(e) {
      if (e.target.tagName === 'TD') {
        const row = e.target.parentElement;
        row.style.transition = 'all 0.2s ease';
      }
    });
  });

  // Add "Back to Top" button
  const backToTop = document.createElement('button');
  backToTop.innerHTML = '↑';
  backToTop.className = 'back-to-top';
  backToTop.style.cssText = `
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    font-size: 1.5rem;
    cursor: pointer;
    opacity: 0;
    transform: translateY(100px);
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 1000;
  `;

  document.body.appendChild(backToTop);

  window.addEventListener('scroll', function() {
    if (window.scrollY > 500) {
      backToTop.style.opacity = '1';
      backToTop.style.transform = 'translateY(0)';
    } else {
      backToTop.style.opacity = '0';
      backToTop.style.transform = 'translateY(100px)';
    }
  });

  backToTop.addEventListener('click', function() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  backToTop.addEventListener('mouseenter', function() {
    this.style.transform = 'translateY(-5px) scale(1.1)';
    this.style.boxShadow = '0 8px 24px rgba(0,0,0,0.2), 0 0 20px rgba(94, 114, 228, 0.3)';
  });

  backToTop.addEventListener('mouseleave', function() {
    this.style.transform = 'translateY(0) scale(1)';
    this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
  });

  // Log successful initialization
  console.log('✨ Contextune documentation enhancements loaded');
});
