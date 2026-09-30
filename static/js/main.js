/**
 * Puranat / Tulunad Homestay — Master main.js
 * Controls Mobile Drawer, Bottom Navigation active indicators, and UI responsiveness.
 */

document.addEventListener('DOMContentLoaded', function () {
    // ── 1. Mobile Drawer Navigation ───────────────────────────
    const drawerToggleBtn = document.getElementById('drawerToggleBtn');
    const drawerCloseBtn = document.getElementById('drawerCloseBtn');
    const drawerOverlay = document.getElementById('mobileDrawerOverlay');
    const bnavMenuBtn = document.getElementById('bnav-menu-btn');

    function openDrawer() {
        if (drawerOverlay) {
            drawerOverlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // prevent background scrolling
        }
    }

    function closeDrawer() {
        if (drawerOverlay) {
            drawerOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    if (drawerToggleBtn) drawerToggleBtn.addEventListener('click', openDrawer);
    if (bnavMenuBtn) bnavMenuBtn.addEventListener('click', openDrawer);
    if (drawerCloseBtn) drawerCloseBtn.addEventListener('click', closeDrawer);

    if (drawerOverlay) {
        drawerOverlay.addEventListener('click', function (e) {
            if (e.target === drawerOverlay) {
                closeDrawer();
            }
        });
    }

    // Close on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && drawerOverlay && drawerOverlay.classList.contains('active')) {
            closeDrawer();
        }
    });

    // ── 2. Highlight Active Bottom Nav Item ───────────────────
    const currentPath = window.location.pathname;
    const bottomNavItems = document.querySelectorAll('.bottom-nav-item');

    bottomNavItems.forEach(function (item) {
        const href = item.getAttribute('href');
        if (href && href !== 'javascript:void(0)') {
            // Check exact or subpath match
            if (currentPath === href || (href !== '/' && currentPath.startsWith(href))) {
                item.classList.add('active');
            }
        }
    });

    // ── 3. Flash Notifications Auto Dismiss ──────────────────
    const flashes = document.querySelectorAll('.flash-message');
    flashes.forEach(function (flash) {
        setTimeout(function () {
            flash.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-10px)';
            setTimeout(function () {
                flash.remove();
            }, 400);
        }, 4500);
    });
});
