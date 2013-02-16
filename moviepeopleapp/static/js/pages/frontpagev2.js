$k.pages.frontpagev2 = new function(){

    var artistFrontFolloweds = [];

    this.init = function(){


        var $input = $('#artist-name');
        //init autocomplete input for people name
        mp.artistSearch.initAutocomplete($input);


        $('#create-account-box .close').click(closeCreateAccount);

        $('#create-account-email-ok').async('ajax',{
            url:'/api/signup',
            json:function(){
                var $email = $('#create-account-email');
                var email = $email.val();
                if(email.indexOf('@') === -1){
                    $email.tooltip({
                        title:'Please enter your email',
                        trigger:'manual'
                    }).show();
                    return false;
                }
                return {email:email}
            },
            success:function(json,deferred){
                if(json.already_exists){
                    var $login = $('<a href="javascript:void(0)">log in instead</a>');
                    $login.click(function(){
                        $('#login-modal').modal('show');
                       $('#id_username').val($('#create-account-email').val());
                    });
                    $('#create-account-email-error').html('This email already exists, please ');
                    $('#create-account-email-error').append($login);
                    deferred.reject();
                }
                else{
                    $k.utils.redirect('/home');
                }
            }
        });
    };


    function openCreateAccount(){
        var artistNames = [];
        $.each(artistFrontFolloweds,function(i,artist){
           artistNames.push(artist.name);
        });
        $('#create-account-actor-names').html(artistNames.join(', '));
        var $create = $('#create-account-box');
        $create.animate({right:0},200);
    }

    function closeCreateAccount(){
        var $create = $('#create-account-box');
        $create.animate({right:-$create.outerWidth()-20},200);
    }

}