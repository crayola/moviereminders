var mp = {};

mp.pages = {};

mp.pages.frontpage = new function(){

    var currentPeople;

    this.init = function(){
        $('#name').autocomplete({
            minLength:2,
            source:function(request, response){
                var name = request.term;
                $.ajax({
                    type:'GET',
                    url:'/api/people/autocomplete',
                    data:'JSON={"term":"'+name+'"}',
                    dataType:'json',
                    success:function(json){
                        response( $.map( json.peoples, function( people ) {
                            return {
                                label: people.name,
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
                        $('#email-modal').modal('show');
                        $('#hidden-modal').modal('show');
                    }
                });
            }
        });

        $('#subscribe').click(function(){
            if(mp.currentUser){
                $.ajax({
                    type:'GET',
                    url:'/api/people/'+currentPeople.id+'/subscribe',
                    data:'JSON={}',
                    dataType:'json',
                    success:function(json){
                        var title = 'you are following '+currentPeople.name+'';
                        if(json.already_follows){
                            title = 'you were already following '+currentPeople.name+''
                        }
                        $('#subscribe').tooltip({
                            title:title,
                            trigger:'manual'
                        }).attr('data-original-title', title)
                          .tooltip('fixTitle')
                          .tooltip('show');
                        setTimeout(function(){ $('#subscribe').tooltip('hide');},2000);
                    },
                    error:function(){
                        $('#email-modal').modal('show');
                        $('#hidden-modal').modal('show');
                    }
                });
            }
            else{
                $('#email-modal').modal('show');
            }
        });

        $('#email-ok').click(function(){
            var email = $('#email').val();
            if(email.indexOf('@') === -1){
                $('#email').tooltip({
                    title:'Please enter your email',
                    trigger:'manual'
                }).tooltip('show');
            }
            else{

                $.ajax({
                    type:'GET',
                    url:'/api/signup',
                    data:'JSON={"email":"'+email+'"}',
                    dataType:'json',
                    success:function(json){
                        if(json.already_exists){
                            //TODO
                            $('#email-modal').modal('show');
                            $('#hidden-modal').modal('show');
                        }
                        else{
                            //logged in
                            $('#email-modal').modal('hide');
                            mp.currentUser = {
                                email:email
                            }
                            $('#subscribe').click();
                        }
                    },
                    error:function(){
                        $('#email-modal').modal('show');
                        $('#hidden-modal').modal('show');
                    }
                });
            }
        });
    }

    function onMovies(movies){
        $('.people-name').html(currentPeople.name);
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
