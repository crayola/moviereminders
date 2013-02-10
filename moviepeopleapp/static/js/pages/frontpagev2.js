$k.pages.frontpagev2 = new function(){

    var artistFrontFolloweds = [];

    this.init = function(){
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
                        response( $.map( json.peoples, function( people ) {
                            return {
                                label: people.name,
                                value: people.name,
                                people: people
                            }
                        }));
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

        $('.artist-box').each(function(){
            activateArtistBox($(this));
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
            var $next = $('<a class="btn btn-primary">Next &raquo;</a>');
            $next.click(function(){
               alert('TODO');
            });
            $menu.html($next);
        }
        artistFrontFolloweds.push(artist);
        var $pic =$('<img src="'+artist.pic_url+'" class="artist-small-pic"/>');
        $menu.prepend($pic);
    }

}