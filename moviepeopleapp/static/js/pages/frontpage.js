var mp = {};

mp.pages = {};

mp.pages.frontpage = new function(){

    var currentPeople;

    this.init = function(){
        $('#name').autocomplete({
            source:function(request, response){
                var name = request.term;
                $.ajax({
                    type:'GET',
                    url:'/api/people/autocomplete',
                    data:'JSON={"name":"'+name+'"}',
                    dataType:'json',
                    success:function(json){
                        response( $.map( json.peoples, function( people ) {
                            return {
                                label: people.first_name+''+people.last_name,
                                value: people.name,
                                people:people
                            }
                        }));
                    },
                    error:function(){
                        response();
                    }
                });
            },
            select: function( event, ui ) {

                if(ui.item) {
                    currentPeople = ui.item.people
                }
            }
        });

        $('#go').click(function(){
            if(currentPeople){
                //call server to get stories
                $.ajax({
                    type:'GET',
                    url:'/api/people/'+currentPeople.id+'/movies',
                    data:'JSON={}',
                    dataType:'json',
                    success:function(json){
                        //handle dates
                        onMovies(json.movies);
                    },
                    error:function(){
                    }
                });
            }
        });

        $('#subscribe').click(function(){
            $.ajax({
                type:'GET',
                url:'/api/people/'+currentPeople.id+'/subscribe',
                data:'JSON={}',
                dataType:'json',
                success:function(json){

                },
                error:function(){

                }
            });
        });
    }

    function onMovies(movies){
        $('#people-name').html(currentPeople.first_name+' '+currentPeople.last_name);
        //get all items
        var items = [];
        $.each(movies,function(i,movie){
            $.each(movie.trailers,function(j,trailer){
                trailer.date = new KDate(trailer.date);
                trailer.type='trailer';
                trailer.movie = movie;
                items.push(trailer);
            });
            if(movie.release){
                var release = movie.release;
                release.date = new KDate(release.date);
                release.type='release';
                release.movie = movie;
                items.push(release);
            }
        });
        //sort
        items.sort(function(a,b){return a.date.getTime() - b.date.getTime();});

        //display
        $('#timeline').html('');
        $.each(items,function(i,item){
            $div = $('<div class="timeline-item"><div class="date">'+item.date.prettyDate()+'</div></div>');
            if(item.type === 'release'){
                $div.append(item.movie.name+' Relased!');
            }
            else if(item.type === 'trailer'){
                $div.append('Watch the trailer: <a href="'+item.url+'">'+item.url+'</a>');
            }
            $('#timeline').append($div);
        });
        if($('#people').outerHeight()<$(window).height()){
            $('#people').css('height',$(window).height());
        }
        setTimeout(function(){
            var top = $('#people-input').offset().top;
            $('html, body').animate({scrollTop:top},100);
        },100);


        $('#people').fadeIn(100);
    }
};

$(document).ready(mp.pages.frontpage.init);
