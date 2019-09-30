/*global JSEncrypt*/
function dologin() {
        //公钥加密
        var pwd =$("#id_password").val();
        var pubkey = $("#id_pub_key").val();
        var jsencrypt = new JSEncrypt();
        jsencrypt.setPublicKey(pubkey);
        var enPwd = jsencrypt.encrypt(pwd);
        $("#id_password").val(enPwd);
        $("#login_form").submit();
    }