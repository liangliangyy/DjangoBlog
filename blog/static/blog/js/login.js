function dologin() {
        //公钥加密
        var pwd =$('#id_password').val();
        var pubkey = $('#id_pub_key').val();
        var jsencrypt = new JSEncrypt();
        jsencrypt.setPublicKey(pubkey);
        var en_pwd = jsencrypt.encrypt(pwd);
        $('#id_password').val(en_pwd);
        $('#login_form').submit();
    }