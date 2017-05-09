/**
 * Created by liangliang on 2016/11/20.
 */


function do_reply(parentid) {
    console.log(parentid);
    $("#id_parent_comment_id").val(parentid)
    $("#commentform").appendTo($("#div-comment-" + parentid));
    $("#reply-title").hide();
    $("#cancel_comment").show();
}

function cancel_reply() {
    $("#reply-title").show();
    $("#cancel_comment").hide();
    $("#id_parent_comment_id").val('')
    $("#commentform").appendTo($("#respond"));
}

NProgress.start();
NProgress.set(0.4);
//Increment
var interval = setInterval(function () {
    NProgress.inc();
}, 1000);
$(document).ready(function () {
    NProgress.done();
    clearInterval(interval);
});



/** 侧边栏回到顶部 */
var rocket = $('#rocket');

$(window).on('scroll', debounce(slideTopSet, 300));

function debounce(func, wait) {
	var timeout;
	return function() {
		clearTimeout(timeout);
		timeout = setTimeout(func, wait);
	};
};
function slideTopSet() {
	var top = $(document).scrollTop();

	if (top > 200) {
		rocket.addClass('show');
	} else {
		rocket.removeClass('show');
	}
}
$(document).on('click', '#rocket', function(event) {
	rocket.addClass('move');
	$('body, html').animate({
		scrollTop: 0
	}, 800);
});
$(document).on('animationEnd', function() {
	setTimeout(function() {
		rocket.removeClass('move');
	}, 400);

});
$(document).on('webkitAnimationEnd', function() {
	setTimeout(function() {
		rocket.removeClass('move');
	}, 400);
});
