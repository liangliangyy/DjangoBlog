(function( $ ){
   $.fn.reset_active_element = function() {
    $(this).addClass("active").closest('li','ul').addClass("active").siblings().each(function() {
        $(this).removeClass("active").closest('li','ul').removeClass("active")
    });

    return this;
  };
})( jQuery );

$(document).ready(function () {
  var loc = window.location.pathname;
  var selector_string = 'ul.find_active > li a'
  $(selector_string).each(function() {
    var a_href = $(this).attr("href").toString()
    if (a_href.length == 1 || loc.length == 1){
      if (!loc.localeCompare(a_href)){
        $(this).reset_active_element();
      }
    }
    else if (loc.indexOf(a_href) != -1) {
      $(this).reset_active_element();
    }
  });
});
