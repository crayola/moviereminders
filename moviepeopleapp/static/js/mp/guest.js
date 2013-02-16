mp.guest = new function(){

    this.init = function(){

        $('#login-btn').click(function() {

            $('#login-modal').modal('show');

        });

        $('#register-modal,#email-modal,#forgot-modal').on('hidden', function () {
            $('#forgot-email,#email,#register-email').tooltip('destroy');
        })



        $('#signin-submit').click(function() {
            var username = $('#id_username').val();
            var password = $('#id_password').val();
            $k.api.POST({
                url:'/signin',
                json:{username: username,
                    password: password,
                },
                success:function(json){
                    if (json.auth) {
                        $k.utils.redirect('/');
                    } else {
                        $('#signinerror').show();
                    }
                },
                error:function(json){
                },
            });
        });

        $('#forgot-password-link').click(function(){
            $('#login-modal').modal('hide');
            $('#forgot-password-modal').modal('show');
        });

        $('#forgot-password-submit').async(function(){
            var email = $('#forgot-password-email').val();
            return $k.api.GET({
                url:'api/forgot',
                json:{email:email},
                success:function(){
                    $('#forgot-password-success').fadeIn();
                }
            });
        });
    }

    this.logout = function(){
        return $k.api.POST({
            url:'/logout',
            json:{},
            success:function(json){
                $k.utils.redirect('/');
            }
        });
    }

}
