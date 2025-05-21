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
    return function () {
        clearTimeout(timeout);
        timeout = setTimeout(func, wait);
    };
}

function slideTopSet() {
    var top = $(document).scrollTop();

    if (top > 200) {
        rocket.addClass('show');
    } else {
        rocket.removeClass('show');
    }
}

$(document).on('click', '#rocket', function (event) {
    rocket.addClass('move');
    $('body, html').animate({
        scrollTop: 0
    }, 800);
});
$(document).on('animationEnd', function () {
    setTimeout(function () {
        rocket.removeClass('move');
    }, 400);

});
$(document).on('webkitAnimationEnd', function () {
    setTimeout(function () {
        rocket.removeClass('move');
    }, 400);
});


window.onload = function () {
  var replyLinks = document.querySelectorAll(".comment-reply-link");
  for (var i = 0; i < replyLinks.length; i++) {
    replyLinks[i].onclick = function () {
      var pk = this.getAttribute("data-pk");
      do_reply(pk);
    };
  }
};

// $(document).ready(function () {
//     var form = $('#i18n-form');
//     var selector = $('.i18n-select');
//     selector.on('change', function () {
//         form.submit();
//     });
// });

// 获取CSRF Token的函数
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 文章详情页收藏功能
function initArticleFavorite() {
    const favoriteBtn = document.getElementById('favoriteBtn');
    if (!favoriteBtn) return;

    const favoriteText = document.getElementById('favoriteText');
    const articleId = favoriteBtn.dataset.articleId;

    // 检查是否已收藏
    fetch(`/favorite/check/${articleId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.is_favorite) {
                favoriteBtn.classList.remove('btn-primary');
                favoriteBtn.classList.add('btn-danger');
                favoriteText.textContent = '取消收藏';
            }
        });

    favoriteBtn.addEventListener('click', function() {
        const isFavorite = favoriteBtn.classList.contains('btn-danger');
        const url = isFavorite ? `/favorite/remove/${articleId}/` : `/favorite/add/${articleId}/`;

        fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (isFavorite) {
                    favoriteBtn.classList.remove('btn-danger');
                    favoriteBtn.classList.add('btn-primary');
                    favoriteText.textContent = '收藏文章';
                } else {
                    favoriteBtn.classList.remove('btn-primary');
                    favoriteBtn.classList.add('btn-danger');
                    favoriteText.textContent = '取消收藏';
                }
            }
        });
    });
}

// 收藏列表页功能
function initFavoriteList() {
    document.querySelectorAll('.remove-favorite').forEach(button => {
        button.addEventListener('click', function() {
            const articleId = this.dataset.articleId;
            fetch(`/favorite/remove/${articleId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.closest('.article-item').remove();
                }
            });
        });
    });
}

// 初始化所有功能
document.addEventListener('DOMContentLoaded', function() {
    initArticleFavorite();
    initFavoriteList();
});