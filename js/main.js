(function ($) {
    "use strict";
    
    // Smooth scrolling on the navbar links
    $(".navbar-nav a").on('click', function (event) {
        if (this.hash !== "") {
            event.preventDefault();
            
            $('html, body').animate({
                scrollTop: $(this.hash).offset().top - 30
            }, 1500, 'easeInOutExpo');
            
            if ($(this).parents('.navbar-nav').length) {
                $('.navbar-nav .active').removeClass('active');
                $(this).closest('a').addClass('active');
            }
        }
    });
    

    // Typed Initiate
    if ($('.header h2').length == 1) {
        var typed_strings = $('.header .typed-text').text();
        var typed = new Typed('.header h2', {
            strings: typed_strings.split('|'),
            typeSpeed: 100,
            backSpeed: 20,
            smartBackspace: false,
            loop: true
        });
    }
    
    
    // Porfolio isotope and filter
    var portfolioIsotope = $('.portfolio-container').isotope({
        itemSelector: '.portfolio-item',
        layoutMode: 'fitRows'
    });

    $('#portfolio-flters li').on('click', function () {
        $("#portfolio-flters li").removeClass('filter-active');
        $(this).addClass('filter-active');

        portfolioIsotope.isotope({filter: $(this).data('filter')});
    });
    
    
    // Review slider
    $('.review-slider').slick({
        autoplay: true,
        dots: false,
        infinite: true,
        slidesToShow: 1,
        slidesToScroll: 1
    });
    
    
    // Hide sidebar footer when contact section is visible. Toggle a class (opacity) rather than
    // fadeIn/fadeOut: fadeIn writes an inline display:block that overrode the CSS hiding the footer
    // on phones, so the unstyled icons showed up in the mobile menu.
    var contactObserver = new IntersectionObserver(function (entries) {
        $('.sidebar-footer').toggleClass('is-hidden', entries[0].isIntersecting);
    }, { threshold: 0.1 });
    var contactButtons = document.querySelector('#contact .social');
    if (contactButtons) {
        contactObserver.observe(contactButtons);
    }

    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({scrollTop: 0}, 1500, 'easeInOutExpo');
        return false;
    });

    // Icon colour on each project card's accent square: white or #222, whichever has the higher
    // WCAG contrast ratio against that card's --accent-rgb. Independent of the page theme.
    function luminance(r, g, b) {
        var c = [r, g, b].map(function (v) {
            v /= 255;
            return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
        });
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
    }

    $('.portfolio-item figure').each(function () {
        var rgb = getComputedStyle(this).getPropertyValue('--accent-rgb').split(',').map(Number);
        if (rgb.length !== 3 || rgb.some(isNaN)) return;
        var L = luminance(rgb[0], rgb[1], rgb[2]);
        var vsWhite = 1.05 / (L + 0.05);
        var vsDark = (L + 0.05) / (luminance(34, 34, 34) + 0.05);
        this.style.setProperty('--on-accent', vsWhite >= vsDark ? '#ffffff' : '#222222');
        // Hover squares are #222/#000: keep the accent icon only if it still reaches 3:1 there.
        this.style.setProperty('--accent-on-dark', vsDark >= 3 ? 'var(--accent)' : '#ffffff');
    });

    // Dark-theme name shine: each part of the heading (name, Apple, Swift) draws the shared band
    // shifted by its own position inside the wrap, so one band sweeps across all of them.
    function placeShine() {
        $('.h1-shine-wrap').children().each(function () {
            this.style.setProperty('--shine-off', this.offsetLeft + 'px');
        });
    }
    placeShine();
    $(window).on('resize', placeShine);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(placeShine);

    // Dark / light theme toggle. The initial theme is set by the inline script in <head>.
    var root = document.documentElement;
    var systemDark = window.matchMedia('(prefers-color-scheme: dark)');

    function savedTheme() {
        try { return localStorage.getItem('theme'); } catch (e) { return null; }
    }

    function applyTheme(theme) {
        root.setAttribute('data-theme', theme);
        var dark = theme === 'dark';
        var label = dark ? 'Switch to light theme' : 'Switch to dark theme';
        $('.theme-toggle').attr({'aria-label': label, title: label});
        $('.theme-toggle i').attr('class', dark ? 'fa fa-sun' : 'fa fa-moon');
    }

    applyTheme(root.getAttribute('data-theme') || 'light');

    $('.theme-toggle').on('click', function () {
        var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem('theme', next); } catch (e) {}
        applyTheme(next);
    });

    // Follow system changes until the visitor picks a theme with the toggle.
    systemDark.addEventListener('change', function (e) {
        if (!savedTheme()) applyTheme(e.matches ? 'dark' : 'light');
    });
})(jQuery);

