var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl, {
        html: true // Set html option to true to allow HTML content
    });
});



document.addEventListener('DOMContentLoaded', function() {
    var buttons = document.querySelectorAll('.nt-food-text');
    
    buttons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Remove 'selected' class from all buttons
            buttons.forEach(function(btn) {
                btn.classList.remove('nt-food-button-active');
            });

            // Add 'selected' class to the clicked button
            this.classList.add('nt-food-button-active');
        });
    });

    // Add click event listener to the document body
    document.body.addEventListener('click', function(event) {
        // Check if the clicked element is not a button
        if (!event.target.classList.contains('nt-food-text')) {
            // Remove 'selected' class from all buttons
            buttons.forEach(function(btn) {
                btn.classList.remove('nt-food-button-active');
            });
        }
    });
});

