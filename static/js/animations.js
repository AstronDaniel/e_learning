/**
 * NeonLearn - Custom Animations and Effects
 * 
 * This file contains custom JavaScript for animations and interactive effects
 * throughout the NeonLearn platform.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Counter animation for statistics
    const counterElements = document.querySelectorAll('.counter-value');
    
    const observerOptions = {
        threshold: 0.5
    };
    
    // Create an intersection observer to trigger counting animation when elements come into view
    const observer = new IntersectionObserver(function(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const targetElement = entry.target;
                const targetValue = parseInt(targetElement.getAttribute('data-count'));
                animateCounter(targetElement, targetValue);
                observer.unobserve(targetElement); // Only animate once
            }
        });
    }, observerOptions);
    
    // Observe all counter elements
    counterElements.forEach(element => {
        observer.observe(element);
    });
    
    // Function to animate counting from 0 to target value
    function animateCounter(element, targetValue) {
        let currentValue = 0;
        const duration = 2000; // 2 seconds
        const stepTime = 30; // update every 30ms
        const totalSteps = duration / stepTime;
        const stepSize = targetValue / totalSteps;
        
        const counter = setInterval(() => {
            currentValue += stepSize;
            if (currentValue >= targetValue) {
                element.textContent = targetValue.toLocaleString();
                clearInterval(counter);
            } else {
                element.textContent = Math.floor(currentValue).toLocaleString();
            }
        }, stepTime);
    }
    
    // Mouse move effect for hero section with parallax
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        const heroContent = heroSection.querySelector('.hero-content');
        const heroGrid = heroSection.querySelector('.hero-grid');
        
        heroSection.addEventListener('mousemove', (e) => {
            const { left, top, width, height } = heroSection.getBoundingClientRect();
            const x = (e.clientX - left) / width;
            const y = (e.clientY - top) / height;
            
            const moveX = (x - 0.5) * 20;
            const moveY = (y - 0.5) * 20;
            
            heroGrid.style.transform = `translate(${moveX * 0.5}px, ${moveY * 0.5}px)`;
            heroContent.style.transform = `translate(${moveX * -0.2}px, ${moveY * -0.2}px)`;
        });
    }
    
    // Initialize tilt effect for cards that have data-tilt attribute
    if (typeof VanillaTilt !== 'undefined') {
        VanillaTilt.init(document.querySelectorAll("[data-tilt]"), {
            max: 10,
            speed: 400,
            glare: true,
            "max-glare": 0.3,
        });
    }
    
    // Add spotlight effect to buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('mousemove', (e) => {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            button.style.setProperty('--spotlight-x', `${x}px`);
            button.style.setProperty('--spotlight-y', `${y}px`);
        });
    });
    
    // Typing animation for elements with .typing-text class
    document.querySelectorAll('.typing-text').forEach(element => {
        const text = element.getAttribute('data-text');
        if (!text) return;
        
        element.textContent = '';
        let index = 0;
        
        function typeText() {
            if (index < text.length) {
                element.textContent += text.charAt(index);
                index++;
                setTimeout(typeText, 100);
            }
        }
        
        typeText();
    });
});
