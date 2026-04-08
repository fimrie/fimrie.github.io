$(document).ready(function() {
  var $nav = $('.navbar');
  var $body = $('body');
  var $window = $(window);
  var navOffsetTop = $nav.length ? $nav.offset().top : 0;

  function onScroll() {
    if (!$nav.length) {
      return;
    }

    if (navOffsetTop < $window.scrollTop() && !$body.hasClass('has-docked-nav')) {
      $body.addClass('has-docked-nav');
    }

    if (navOffsetTop >= $window.scrollTop() && $body.hasClass('has-docked-nav')) {
      $body.removeClass('has-docked-nav');
    }
  }

  function resize() {
    if (!$nav.length) {
      return;
    }

    $body.removeClass('has-docked-nav');
    navOffsetTop = $nav.offset().top;
    onScroll();
  }

  function smoothScroll(e) {
    var target = this.hash ? $(this.hash) : $();

    if (!target.length) {
      return;
    }

    e.preventDefault();
    $('html, body').stop().animate(
      { scrollTop: target.offset().top - 40 },
      200
    );
  }

  $window.on('scroll', onScroll);
  $window.on('resize', resize);
  $('a[href^="#"]').on('click', smoothScroll);

  onScroll();
});
