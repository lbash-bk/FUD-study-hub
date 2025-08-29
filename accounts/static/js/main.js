document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar for mobile
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    // Toggle sidebar
      menuToggle.addEventListener('click', function() {
        this.classList.toggle('active');
        sidebar.classList.toggle('active');
        sidebarOverlay.classList.toggle('active');
        document.body.style.overflow = sidebar.classList.contains('active') ? 'hidden' : '';
    });
    
    // Close sidebar when clicking on overlay or link
    sidebarOverlay.addEventListener('click', closeSidebar);
    
    const navLinks = document.querySelectorAll('.sidebar .nav-links a');
    navLinks.forEach(link => link.addEventListener('click', closeSidebar));
    
    function closeSidebar() {
        menuToggle.classList.remove('active');
        sidebar.classList.remove('active');
        sidebarOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    
    // Highlight active page in sidebar
    const currentPath = window.location.pathname;
    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (currentPath === linkPath) {
            link.classList.add('active');
        }
    });
});

 // Handle desktop dropdowns
    const dropdowns = document.querySelectorAll('.desktop-nav .dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('mouseenter', function() {
            this.querySelector('.dropdown-menu').style.opacity = '1';
            this.querySelector('.dropdown-menu').style.visibility = 'visible';
        });
        
        dropdown.addEventListener('mouseleave', function() {
            this.querySelector('.dropdown-menu').style.opacity = '0';
            this.querySelector('.dropdown-menu').style.visibility = 'hidden';
        });
    });

// Close alert message when clicking the X button
function closeAlert(alertId) {
    const alert = document.getElementById(alertId);
    if (alert) {
        alert.style.opacity = '0';
        setTimeout(() => {
            alert.remove();
        }, 300); // Match this with CSS transition time
    }
}

// Auto-dismiss alerts after 5 seconds
function autoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000); // 5 seconds
    });
}
