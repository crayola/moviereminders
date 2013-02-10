$k.pages.frontpagev2 = new function(){

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
                $box.flip({
                    direction:'lr',
                    content:json.artist_box
                })
            }
        });
    }

    function flipBox($box){
        $
    }

}