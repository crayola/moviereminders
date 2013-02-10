mp.guest = new function(){

    this.init = function(){

        $('#login-btn').click(function() {

            if (!mp.currentUser) {
                $('#login-modal').modal('show');
                $('.nav li').removeClass('active');
                $(this).addClass('active');
            } else {

            }
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
                        mp.currentUser = {
                            email: json.username,
                        };
                        $('#signin').hide();
                        $('#signinerror').hide();
                        $('#signedin').show();
                        signinevents(mp.currentUser.email);
                    } else {
                        $('#signinerror').show();
                    }
                },
                error:function(json){
                },
            });
        });

        $('#forgot-password').click(function() {
            $('#forgot-modal').modal('show');
        });

        function logoutevents() {
            $('#username').text('');
            $('#signin-btn > a').text('Sign in');
            $('#register-btn').show();
            $('#yourwhispers-btn').hide();
            $('#yourfollowees-btn').hide();
        }
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
