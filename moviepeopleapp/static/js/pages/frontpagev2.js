$k.pages.frontpagev2 = new function(){

    var artistFrontFolloweds = [];

    this.init = function(){


        var $input = $('#artist-name');
        //init autocomplete input for people name
        mp.artistSearch.initAutocomplete($input,addArtistInMenuBox);


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
        $.each(mp.artistSearch.getArtistFolloweds(),function(i,artist){
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

    function addArtistInMenuBox(artist){
        var $menu = $('#menu-box');
        if(artistFrontFolloweds.length<=0){
            var $next = $('<a class="btn btn-primary btn-large">Save your choices &raquo;</a>');
            $next.click(openCreateAccount);
            $menu.html('You follow: <span id="follow-artists"></span>');
            $menu.append($next);
            $menu.animate({opacity:1});
        }
        var $artists = $('#follow-artists');
        artistFrontFolloweds.push(artist);
        var $pic =$('<img src="'+artist.pic_url+'" class="artist-small-pic"/>');
        $pic.tooltip({title:artist.name});
        $artists.prepend($pic);
    }

}