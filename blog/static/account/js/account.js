let wait = 60;

function time(o) {
    if (wait == 0) {
        o.removeAttribute("disabled");
        o.value = "获取验证码";
        wait = 60
        return false
    } else {
        o.setAttribute("disabled", true);
        o.value = "重新发送(" + wait + ")";
        wait--;
        setTimeout(function () {
                time(o)
            },
            1000)
    }
}

document.getElementById("btn").onclick = function () {
    let id_email = $("#id_email")
    let token = $("*[name='csrfmiddlewaretoken']").val()
    let ts = this
    let myErr = $("#myErr")
    $.ajax(
        {
            url: "/forget_password_code/",
            type: "POST",
            data: {
                "email": id_email.val(),
                "csrfmiddlewaretoken": token
            },
            success: function (result) {
                if (result != "ok") {
                    myErr.remove()
                    id_email.after("<ul className='errorlist' id='myErr'><li>" + result + "</li></ul>")
                    return
                }
                myErr.remove()
                time(ts)
            },
            error: function (e) {
                alert("发送失败,请重试")
            }
        }
    );
}
