$k.pages.frontpagev2 = new function(){

    var artistFrontFolloweds = [];

    this.init = function(){

        var $artists = $('#artist-boxes');
        var $input = $('#artist-name');
        //init autocomplete input for people name
        $input.autocomplete({
            minLength:3,
            source:function(request, response){
                $input.removeClass('error');
                var name = request.term;
                $k.api.GET({
                    url:'/api/people/autocomplete',
                    json:{term:name},
                    success:function(json){
                        $artists.html('');
                        $.each(json.artists,function(i,artist){
                            var $box = $(artist.box);
                            activateArtistBox($box);
                            $artists.append($box);
                        });
                        if(json.artists.length<=0){
                            $artists.html('<div>No result</div>');
                        }
                        response([]);
                    },
                    error:function(){
                        $input.addClass('error');
                        response([]);
                    }
                });
            },
            select: function( event, ui ) {
                if(ui.item) {
                    //TODO when artist selected in dropdwon
                }
            }
        });

        $('.artist-box-front').each(function(){
            activateArtistBox($(this));
        });

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
    }

    function activateArtistBox($box){
        var $btn = $('.btn-follow',$box)
        $btn.async('ajax',{
            url:'/api/people/frontFollow',
            data:function(){
                return {JSON:{artist_id:$btn.attr('artist-id')}};
            },
            success:function(json){
                log.info('followed artist');
                var newBoxContent = $(json.artist_box).html();
                $box.flip({
                    direction:'lr',
                    content:newBoxContent,
                    onEnd: function(){
                        $box.css('background','transparent');
                        activateArtistBox($box);
                    }
                });
                //add artist in menubox
                addArtistInMenuBox(json.artist);
            }
        });
    }

    function addArtistInMenuBox(artist){
        var $menu = $('#menu-box');
        if(artistFrontFolloweds.length<=0){
            var $next = $('<a class="btn btn-primary btn-large">Save your choices &raquo;</a>');
            $next.click(openCreateAccount);
            $menu.html('You follow: <span id="follow-artists"></span>');
            $menu.append($next);
        }
        var $artists = $('#follow-artists');
        artistFrontFolloweds.push(artist);
        var $pic =$('<img src="'+artist.pic_url+'" class="artist-small-pic"/>');
        $pic.tooltip({title:artist.name});
        $artists.prepend($pic);
    }

    function openCreateAccount(){
        var artistNames = [];
        $.each(artistFrontFolloweds,function(i,artist){
           artistNames.push(artist.name);
        });
        $('#create-account-actor-names').html(artistNames.join(', '));
        var $create = $('#create-account-box');
        $create.animate({right:0},200);
    }

}