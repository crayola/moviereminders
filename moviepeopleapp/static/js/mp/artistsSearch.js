mp.artistSearch = new function(){

    this.initAutocomplete=function($input){
        var $artists = $('#artist-boxes');

        $input.autocomplete({
            minLength:0,
            source:function(request, response){
                $input.removeClass('error');
                var name = request.term;
                if(name.length==0){
                    //display default set
                    displayArtists(mp_artists);
                    response([]);
                }
                else if(name.length<3){
                    //do nothing
                    response([]);
                }
                else{
                    $k.api.GET({
                        url:'/api/people/autocomplete',
                        json:{term:name},
                        success:function(json){
                            displayArtists(json.artists);
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
                }
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

    }

    function displayArtists(artists){
        var $artists = $('#artist-boxes');
        $artists.html('');
        $.each(artists,function(i,artist){
            var $box = $(artist.box);
            activateArtistBox($box);
            $artists.append($box);
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
            $menu.animate({opacity:1});
        }
        var $artists = $('#follow-artists');
        artistFrontFolloweds.push(artist);
        var $pic =$('<img src="'+artist.pic_url+'" class="artist-small-pic"/>');
        $pic.tooltip({title:artist.name});
        $artists.prepend($pic);
    }


};
