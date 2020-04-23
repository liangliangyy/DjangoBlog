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

// Get the modal
var modal = $( ".modal" )

$( ".btn-nav-login" ).click(function() {
	modal.css('display', 'block')
	$( "body" ).addClass('modal_open')

});

// When the user clicks anywhere outside of the modal, close it
$(document).click(function(e) {
      if ($(e.target).is('.modal') || $(e.target).is('.close')) {
            modal.css('display', 'none')
		  $( "body" ).removeClass('modal_open')
      }
});


//
// $( ".form-signin a.btn-block" ).click(function( event ) {
//     event.preventDefault();
//     username = document.getElementById("id_username").value;
//     password = document.getElementById("id_password").value;
//     csrfmiddlewaretoken = document.getElementsByName("csrfmiddlewaretoken")[0].value;
//     $("#errorlogin").html("");
//     $.ajax({
//         type:"POST",
//         url:'/login/',
//         data:{
//             'csrfmiddlewaretoken': csrfmiddlewaretoken,
//             'username': username,
//             'password': password,
//         },
//         dataType: 'json',
//         success : function(data){
//             console.log(data);
//             if(data['message'] == "Success"){
//                 location.reload();
//             }
//             else if(data['message'] == "Failure"){
//
//                 var html_data = `
//                 <div class="row">
//                     <div class="col-sm-12 col-sm-offset-0">
//                       <div class="alert alert-danger py-2 mb-3" role="alert">
//                         <p class="text-center mb-0">${data['errors']}</p>
//                       </div>
//                     </div>
//                   </div>`
//                 $(".sign_up_messages").html(html_data);
//             }
//             else{
//                 $("#errorlogin").html("The E-mail and Password do not match.");
//             }
//         }
//     });
//     console.log("LOL");
// });
