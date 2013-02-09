mp.guest = new function(){

    this.init = function(){


        $('#subscribe').click(function(){
            $(this).addClass('disabled');
            $(this).removeClass('btn-primary');
            if (currentPeople['follow']===true) {
                $('.subscribe-text').html('You are already following ' + currentPeople.name + "'s movie updates.");
            } else {
                $('.subscribe-text').html('You are now following ' + currentPeople.name + "'s movie updates!");
                currentPeople['follow']=true
            }
            if(mp.currentUser){
                $k.api.GET({

                    url:'/api/people/'+currentPeople.id+'/subscribe',
                    success:function(json){
                        //var title = 'you are following '+currentPeople.name+'';
                        //if(json.already_follows){
                        //    title = 'you were already following '+currentPeople.name+''
                        //}
                        //$('#subscribe').tooltip({
                        //    title:title,
                        //    trigger:'manual'
                        //}).attr('data-original-title', title)
                        //    .tooltip('fixTitle')
                        //    .tooltip('show');
                        //setTimeout(function(){ $('#subscribe').tooltip('hide');},2000);
                    },
                    error:function(){
                        $('#hidden-modal').modal('show');
                    }
                });
            }
            else{
                $('#email-modal').modal('show');
            }
        });



        $('#register-email-ok').click(function() {
            emailok(false, false, '#register-email');
        });

        $('#new-email-ok').click(function(){
            emailok(false, false, '#email');
        });

        $('#old-email-ok').click(function(){
            emailok(true, true, '#forgot-email');
        }); // fix this mess


        function emailok(existOk, forgot, emailid) {
            var email = $(emailid).val();
            var url = '/api/signup';
            if (forgot) {
                url = '/api/forgot';
            }
            if(email.indexOf('@') === -1){
                $(emailid).tooltip({
                    title:'Please enter your email',
                    trigger:'manual'
                })
                $(emailid).tooltip('show');
            }
            else{
                $(emailid).tooltip('destroy');
                $k.api.GET({
                    url:url,
                    json:{email:email},
                    success:function(json){
                        if(json.already_exists && !(existOk)){
                            //TODO
                            $('#hidden-modal').modal('show');
                        }
                        else if (!('already_exists' in json) && existOk){
                            //TODO
                            $('#hidden-modal').modal('show');
                        }
                        else{
                            //logged in
                            $('#register-modal').modal('hide');
                            $('#forgot-modal').modal('hide');
                            $('#email-modal').modal('hide');
                            mp.currentUser = {
                                email:email
                            }
                            $('#username').html(mp.currentUser.email)
                            if (currentPeople && emailid==='#email') {
                                $('#subscribe').click();
                            }
                            if (emailid !=='#forgot-email') {
                                signinevents(mp.currentUser.email);
                            }
                        }
                    },
                    error:function(){
                        $('#hidden-modal').modal('show');
                    }
                });
            }
        };


        $('#login-btn').click(function() {

            if (!mp.currentUser) {
                $('#login-modal').modal('show');
                $('.nav li').removeClass('active');
                $(this).addClass('active');
            } else {
                $k.api.POST({
                    url:'/logout',
                    json:{},
                    success:function(json){
                        mp.currentUser = '';
                        $('#logout').show();
                        $('.nav li').removeClass('active');
                        $('#home-btn').addClass('active');
                        logoutevents();
                    },
                });
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

}
