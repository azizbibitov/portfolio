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
    
    
    // Hide sidebar footer when contact section is visible
    var contactObserver = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) {
            $('.sidebar-footer').fadeOut('fast');
        } else {
            $('.sidebar-footer').fadeIn('slow');
        }
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

