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
    
    // 初始化代码块功能
    initCodeBlocks();
    
    // 初始化目录导航
    initTocNavigation();
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

// 初始化代码块功能
function initCodeBlocks() {
    var preElements = document.querySelectorAll('pre');
    
    preElements.forEach(function(pre) {
        // 创建控制按钮容器
        var controls = document.createElement('div');
        controls.className = 'code-controls';
        
        // 创建复制按钮
        var copyBtn = document.createElement('button');
        copyBtn.className = 'code-btn';
        copyBtn.innerHTML = '复制';
        copyBtn.onclick = function() {
            copyCode(pre, copyBtn);
        };
        
        // 创建主题切换按钮
        var themeBtn = document.createElement('button');
        themeBtn.className = 'code-btn';
        themeBtn.innerHTML = '主题';
        themeBtn.onclick = function() {
            toggleCodeTheme(pre);
        };
        
        controls.appendChild(copyBtn);
        controls.appendChild(themeBtn);
        pre.appendChild(controls);
    });
}

// 复制代码功能
function copyCode(preElement, button) {
    var code = preElement.querySelector('code').textContent;
    
    navigator.clipboard.writeText(code).then(function() {
        var originalText = button.innerHTML;
        button.innerHTML = '已复制';
        button.style.background = 'rgba(40, 167, 69, 0.7)';
        
        setTimeout(function() {
            button.innerHTML = originalText;
            button.style.background = '';
        }, 2000);
    }).catch(function(error) {
        console.error('复制失败:', error);
        button.innerHTML = '复制失败';
        
        setTimeout(function() {
            button.innerHTML = '复制';
        }, 2000);
    });
}

// 切换代码块主题
function toggleCodeTheme(preElement) {
    preElement.classList.toggle('dark-theme');
    
    // 如果是暗主题，添加相应样式
    if (preElement.classList.contains('dark-theme')) {
        preElement.style.background = '#1e1e1e';
        preElement.style.color = '#d4d4d4';
    } else {
        preElement.style.background = '';
        preElement.style.color = '';
    }
}

// 初始化目录导航
function initTocNavigation() {
    var tocContainer = document.getElementById('toc-container');
    if (!tocContainer) return;
    
    // 为目录链接添加点击事件
    var tocLinks = tocContainer.querySelectorAll('a');
    tocLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            var targetId = this.getAttribute('href').substring(1);
            var targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                var offsetTop = targetElement.offsetTop - 80; // 减去头部高度
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// $(document).ready(function () {
//     var form = $('#i18n-form');
//     var selector = $('.i18n-select');
//     selector.on('change', function () {
//         form.submit();
//     });
// });