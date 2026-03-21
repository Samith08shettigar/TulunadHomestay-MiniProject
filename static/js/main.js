/**
 * Tulunad Homestay — main.js
 * Auto-dismiss flash messages after 4 seconds
 */

document.addEventListener('DOMContentLoaded', function () {
    const flashes = document.querySelectorAll('.flash-message');
    flashes.forEach(function (flash) {
        setTimeout(function () {
            flash.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-10px)';
            setTimeout(function () {
                flash.remove();
            }, 400);
        }, 4000);
    });
});
