// SMOOTH SCROLL
$('a[href^="#"]').on('click', function (event) {
  var target = $(this.getAttribute('href'));
  if (target.length) {
    event.preventDefault();
    $('html, body').stop().animate({
      scrollTop: target.offset().top - 100
    }, 900);
  }
});

$(document).ready(function () {
  $('.owl-carousel').owlCarousel({
    autoPlay: 3000,
    loop: true,
    margin: 10,
    responsiveClass: true,
    dots: true,
    responsive: {
      0: {
        items: 1,
        nav: true
      },
      600: {
        items: 3,
        nav: false
      },
      1000: {
        items: 3,
        nav: true,
      }
    }
  })
});

$('.popup-vimeo').magnificPopup({
  src: 'https://vimeo.com/398972182',
  type: 'iframe'
});