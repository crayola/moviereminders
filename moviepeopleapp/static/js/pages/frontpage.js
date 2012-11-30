var mp = {};

mp.pages = {};

mp.pages.frontpage = new function(){

    var currentPeople;

    this.init = function(){
        $('#name').autocomplete({
            minLength:3,
            source:function(request, response){
                var name = request.term;
                $k.api.GET({
                    url:'/api/people/autocomplete',
                   json:{term:name},
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
                $k.api.GET({
                    url:'/api/people/'+currentPeople.id+'/movies',
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
                $k.api.GET({
                    url:'/api/people/'+currentPeople.id+'/subscribe',
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

               $k.api.GET({
                    url:'/api/signup',
                    json:{email:email},
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

    describeRole = function(actor_role, director, movie, people) {
      // for now very simple but in future would be nice to have more.
      if (actor_role) {
        roleimp='a supporting role';
        switch (actor_role.order) {
          case 0: 
            roleimp='the main character';
            break;
          case 1: case 2: case 3: case 4:
            roleimp='one of the main characters';
            break;
        }
        if (director) {
          isdir = ' is the director and ';
        } 
        else {
          isdir = '';
        }
        return (people.name + isdir + ' stars as ' + actor_role.character + ', ' + roleimp + '.')
      }
      else if (director) {
        return (people.name + ' is the director.')
      }
    }

    function onMovies(movies){
        $('.people-name').html(currentPeople.name);
        //get all items
        var items = [];
        $.each(movies,function(i,movie){
            //$.each(movie.trailers,function(j,trailer){
            //    //trailer.date = new KDate().fromJsDate(Date.parse(trailer.date));
            //    trailer.date = new KDate()
            //    trailer.type='trailer';
            //    trailer.movie = movie;
            //    items.push(trailer);
            //});
            if(movie.release){
                var release = movie.release;
                release.date = new KDate().fromJsDate(Date.parse(release.date));
                //release.date = new KDate()
                release.type='release';
                release.movie = movie;
                console.log(movie.trailers)
                if (movie.trailers.length>0) {
                  release.trailer = movie.trailers[0];
                  if (!release.trailer.date) {
                    release.trailer.date = "1970-01-01"
                  }
                  release.trailer.date = new KDate().fromJsDate(Date.parse(release.trailer.date));
                }
                //release.trailer.date = new KDate().fromJsDate(Date.parse(release.trailer.date));
                release.moviepeople_actor = movie.moviepeople_actor
                release.moviepeople_director = movie.moviepeople_director
                items.push(release);
            }
        });
        //sort
        items.sort(function(a,b){return b.date.getTime() - a.date.getTime();});

        //display
        $('#timeline').html('');
        $.each(items,function(i,item){
            $div = $('<div class="timeline-item"><div class="date">'+item.date.prettyDate()+'</div></div>');
            if(item.type === 'release'){
                $div.append(
                  item.movie.name+' release! <br>' + describeRole(item.moviepeople_actor, item.moviepeople_director, item.movie, currentPeople)
                  );
                if (item.trailer && item.trailer.date) {
                  $div.append('<br> <br> <div class="date">'+item.trailer.date.prettyDate()+'</div>' + 'Watch the trailer! <br> <iframe height="200" src="http://www.youtube.com/embed/'+item.trailer.url+'" frameborder="0"></iframe>');
                }
            }
            else if(item.type === 'trailer'){
//$div.append('Watch the trailer: <a href="'+item.url+'">'+item.url+'</a>');
              $div.append('Watch the trailer for ' + item.movie.name + '! <br> <iframe height="200" src="http://www.youtube.com/embed/'+item.url+'" frameborder="0"></iframe>')
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

$('#go').hide()

$('#name').keypress(function(ev) {
  if (ev.which == 13) {
    $('#go').click();
    return false
  }});
