
    const burgerMenu = document.querySelector('.burger-menu');
    const menuOverlay = document.getElementById('menuOverlay');
    let isMenuOpen = false;

    burgerMenu.addEventListener('click', toggleMenu);
    document.addEventListener('click', handleClickOutside);

    function toggleMenu() {
        isMenuOpen = !isMenuOpen;
        menuOverlay.classList.toggle('active');
        animateBurger();
    }

    function animateBurger() {
        const spans = burgerMenu.querySelectorAll('span');
        if (isMenuOpen) {
            spans[0].style.transform = 'rotate(45deg) translate(6px, 6px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translate(6px, -6px)';
        } else {
            spans[0].style.transform = 'none';
            spans[1].style.opacity = '1';
            spans[2].style.transform = 'none';
        }
    }

    function handleClickOutside(e) {
        if (isMenuOpen && !menuOverlay.contains(e.target) && !burgerMenu.contains(e.target)) {
            isMenuOpen = false;
            menuOverlay.classList.remove('active');
            animateBurger();
        }
    }
