/**
 * Custom JavaScript for the admin page
 */

// Add custom interactivity or enhancements for the admin page here

document.addEventListener('DOMContentLoaded', function() {
    // Example: Add a custom class to the body element
    document.body.classList.add('custom-admin-page');

    // Example: Add a click event listener to a button
    const customButton = document.getElementById('customButton');
    if (customButton) {
        customButton.addEventListener('click', function() {
            alert('Custom button clicked!');
        });
    }

    // Example: Add a custom tooltip to an element
    const tooltipElement = document.getElementById('tooltipElement');
    if (tooltipElement) {
        tooltipElement.setAttribute('title', 'This is a custom tooltip');
    }
});
