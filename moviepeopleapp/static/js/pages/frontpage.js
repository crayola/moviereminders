var mp = {};

mp.pages = {};

mp.pages.frontpage = new function(){

    var currentPeople;


    showMovies = function(currentPeople) {
        $('#home-btn').click();
        if(currentPeople){
            //call server to get stories
            $k.api.GET({
                url:'/api/people/'+currentPeople.id+'/movies',
                success:function(json){
                    //handle dates
                    onMovies(json.movies, currentPeople);
                },
                error:function(){
                    console.log('hi');
                    $('#email-modal').modal('show');
                    $('#hidden-modal').modal('show');
                }
            });
        }
    }

    $('#go').click(showMovies(currentPeople));


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
                                people: people
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
                    currentPeople = ui.item.people;
                    showMovies(currentPeople);
                    //showMovies(ui.item.people);
                }
            }
        });
    };




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
                    $('#email-modal').modal('show');
                    $('#hidden-modal').modal('show');
                }
            });
        }
        else{
            $('#email-modal').modal('show');
        }
    });

    var emailok = function(existOk, forgot, emailid) {
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
                        $('#email-modal').modal('show');
                        $('#hidden-modal').modal('show');
                    }
                    else if (!('already_exists' in json) && existOk){
                        //TODO
                        $('#email-modal').modal('show');
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
                    $('#email-modal').modal('show');
                    $('#hidden-modal').modal('show');
                }
            });
        }
    };

    $('#register-email-ok').click(function() {
        emailok(false, false, '#register-email');
    });

    $('#new-email-ok').click(function(){
        emailok(false, false, '#email');
    });

    $('#old-email-ok').click(function(){
      emailok(true, true, '#forgot-email');
    }); // fix this mess

    function describeRole(movie, people) {
      console.log('hi2');
      console.log(people);
      director = (people.roles.filter(function(x) {return x.role==='Director'})).length > 0;
      console.log('hi3');
        // for now very simple but in future would be nice to have more.
      actor_role=(people.roles.filter(function(x) {return x.role==='Actor'}));
      if (actor_role.length > 0) {
        actor_role = actor_role.sort(function(a,b) {return b.order - a.order})[0];
      } else {
        actor_role = undefined;
      }
      if (typeof(actor_role) !== "undefined") {
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
            if (actor_role.character === '') {
                comma = '';
            } else {
                comma = ', ';
            }
            return (people.name + isdir + ' stars as ' + actor_role.character + comma + roleimp + '.')
        } else if (director) {
            return (people.name + ' is the director.')
        }
    }

    //display
    function makeTimeline(items) {
      var ret = '';
      $.each(items,function(i,item){
        ret += '<div class="movie-box">';

        if (item.movie.poster!=='') { 
          ret +=  '<img src="http://cf2.imgobject.com/t/p/w185'+item.movie.poster+'"/>';
        } else { 
          ret += '<img src="' + staticfolder + 'img/question_mark.png"/>';
        }
        ret +=  '<h1 class="title">'+item.movie.name+'</h1><hr/>';
        ret += '<div class="date">'+item.date.prettyDate()+'</div>';
        console.log(item);
        ret +=  '<span class="is">'+describeRole(item.movie, item.movie.people[0])+'</span>';
        console.log(item.movie.RT_audience_score)
        if (item.movie.RT_critics_score!==null || item.movie.RT_audience_score!==null) {
          ret += '<div class="RT-box"><a class="RT-link" href="http://rottentomatoes"></a>';
          if (item.movie.RT_critics_score!==null) {
            if (item.movie.RT_critics_score >= 60) {
              var tomato = staticfolder + 'img/fresh.png';
            } else {
              var tomato = staticfolder + 'img/rotten.png';
            }
            ret +=   '<div class="RT-score RT-critic-score">Critics: <img width=12px src="' + tomato + '"> ' + item.movie.RT_critics_score +'%</div>';
          }
          if (item.movie.RT_audience_score!==null) {
            if (item.movie.RT_audience_score >= 60) {
              var tomato = staticfolder + 'img/fresh.png';
            } else {
              var tomato = staticfolder + 'img/rotten.png';
            }
            ret +=   '<div class="RT-score RT-audience-score">Audience: <img width=12px src="' + tomato + '"> ' + item.movie.RT_audience_score +'%</div>';
          }
          ret +=  '</div>';
        }
        ret +=  '<div style="position:absolute;right:6px;bottom:6px;">';
        if (item.trailer && item.trailer.date) {
          ret +=   '<a href="http://www.youtu.be/'+item.trailer.url+'" class="dark-link" target="_new"><i class="icon-film"></i> Watch trailer</a>';
        }
        ret +=  '</div>';
        ret += '</div>';

        //            ret += '<div class="row">';
        //            if(item.type === 'release'){
        //                if (item.movie.poster) {
        //                    ret += '<div class="span2"><img src="http://cf2.imgobject.com/t/p/w185' + item.movie.poster + '" class="poster"></div>';
        //                }
        //                var trailertext = ''
        //                if (item.trailer && item.trailer.date) {
        //                    //$div.append('<br> <br> <div class="date">'+item.trailer.date.prettyDate()+'</div>' + 'Watch the trailer! <br> <iframe height="200" src="http://www.youtube.com/embed/'+item.trailer.url+'" frameborder="0"></iframe>');
        //                    //trailertext = '<br> <br> <a href=> Watch the trailer! <br> <iframe height="200" src="http://www.youtube.com/embed/'+item.trailer.url+'" frameborder="0"></iframe>';
        //                    trailertext = '<br> <br> <a target="_blank" href="http://www.youtu.be/'+item.trailer.url+'"> Watch the trailer on YouTube!</a>';
        //                }
        //                //console.log(ret);
        //                if (currentPeople) {
        //                    ret += '<div class="span" style="width:360px;"><h3>' + item.movie.name+' </h3><div>' + describeRole(item.moviepeople_actor, item.moviepeople_director, item.movie, currentPeople) + trailertext + '</div></div></div></div>';
        //                } else {
        //                    ret += '<div class="span" style="width:360px;"><h3>' + item.movie.name+' </h3><div>' + trailertext + '</div></div></div></div>';
        //                }
        //            }
      });
      return ret;
    }

    function makeItems(movies, asc) {
        var items = [];
        $.each(movies,function(i,movie){
            if(movie.release){
                var release = {};
                release.movie=movie;
                release.date = new KDate().fromJsDate(Date.parse(movie.release));
                console.log(release);
                //release.date = new KDate()
                release.type='release';
                release.movie = movie;
                if (movie.trailers.length>0) {
                    release.trailer = movie.trailers[0];
                    if (!release.trailer.date) {
                        release.trailer.date = "1970-01-01"
                    }
                    release.trailer.date = new KDate().fromJsDate(Date.parse(release.trailer.date));
                }
                //release.trailer.date = new KDate().fromJsDate(Date.parse(release.trailer.date));
                //release.moviepeople_actor = movie.moviepeople_actor;
                //release.moviepeople_director = movie.moviepeople_director;
                items.push(release);
            }
        });

        //sort
        if (!asc) {
          items.sort(function(a,b){return b.date.getTime() - a.date.getTime();});
        } else {
          items.sort(function(a,b){return a.date.getTime() - b.date.getTime();});
        }


        return items;
    }



    function showyourWhispers() {
      $('#yourwhispers').html('');
      $('#yourwhispers').show();
        //call server to get stories
        $k.api.GET({
            url:'/api/yourwhispers',
            success:function(json){
                //console.log(json);
                items=makeItems(json.movies, asc=true);
                //console.log(items);
                $('#yourwhispers').html(makeTimeline(items));
            },
            error:function(){
                $('#hidden-modal').modal('show');
            }
        });
    }



    function makeFollowees(people) {
      console.log(people);

      $('#followees').html('');
      $.each(people,function(i,item){
        console.log(item.name);
        $('#followees').append('<div class="followee-box" id="unsub_' + item.id + '">');
        $('#unsub_' + item.id).append('<h1 class="title">'+item.name+'</h1>');
        if (item.profile!=='') { 
          $('#unsub_' + item.id).append('<img src="http://cf2.imgobject.com/t/p/w185' + item.profile + '">');
        } else { 
          $('#unsub_' + item.id).append('<img src="' + staticfolder + 'img/question_mark.png"/>');
        }
        //$('#unsub_' + item.id).append('<img src="http://cf2.imgobject.com/t/p/w185'+item.profile+'"/>');
        $('#unsub_' + item.id).append('<a class="btn followee-unsubscribe" id="unsub_btn_' + item.id + '"> unsubscribe </a>');
        $('#unsub_' + item.id).append(
          $('#unsub_btn_' + item.id).click(function() {
              $k.api.GET({
                url:'/api/unfollow',
                json:{followee:item.id},
                success:function(json){
                },
                error:function(){
                  response('boo');
                }
          })
          //console.log('asjh');
          console.log(item.id);
          $('#unsub_' + item.id).fadeOut()
          }));
      });
      //return ret;
    }


    function showFollowees() {
        //call server to get stories
        $k.api.GET({
            url:'/api/followees',
            success:function(json){
                //console.log(json);
                makeFollowees(json.people, '');
                $('#followees').show();
            },
            error:function(){
                $('#hidden-modal').modal('show');
            }
        });
    }



    function onMovies(movies, currentPeople) {
      $('.people-name').html(currentPeople.name)
      if (currentPeople['follow']===true) {
        $('#subscribe').addClass('disabled');
        $('#subscribe').removeClass('btn-primary');
        $('.subscribe-text').html('You are already following ' + currentPeople.name + "'s movie updates.");
      } else {
        $('#subscribe').removeClass('disabled');
        $('#subscribe').addClass('btn-primary');
        $('.subscribe-text').html('Subscribe to the latest ' + currentPeople.name + ' movie updates!');
      }

      //class="subscribe-text"></span>Subscribe to the latest <br> <span class="people-name"></span> movie updates</a>

//$('#people-pic').html('<img width=500 src="http://cf2.imgobject.com/t/p/w342' + currentPeople.profile + '">');
            if (currentPeople.profile!=='') { 
              $('#people-pic').html('<img width=500 src="http://cf2.imgobject.com/t/p/w342' + currentPeople.profile + '">');
            } else { 
              $('#people-pic').html('<img width=500 src="' + staticfolder + 'img/question_mark.png"/>');
            }

        $('#people-pic').show();
        $('#right-pane').show();

        //get all items
        items=makeItems(movies, asc=false);
        
        for (var i = 0; i < items.length; i++) {
          items[i]['people'] = currentPeople;
        }

        //make timeline
        $('#timeline').html(makeTimeline(items));

        if($('#people').outerHeight()<$(window).height()){
            $('#people').css('height',$(window).height());
        }

        var el=$('#right-pane');
        var elpos=el.offset().top;
        var $inliner = $('#inliner');
        $inliner.css('height',el.outerHeight());
        $(window).scroll(function () {
            var y=$(this).scrollTop();
            if (y>elpos) {
                $inliner.show();
                el.addClass('fixed');
            } else {
                $inliner.hide();
                el.removeClass('fixed');
            }

            //el.stop().css({'margin-top':Math.max(0, y-elpos)});
        });

        //$('body').animate({
        //        scrollTop: elpos
        //    },
        //    200);

        $('#name').blur()
    }


    $('#go').hide();

    $('#people').fadeIn(100);
    $('#faq').hide();
    $('#people-pic').hide();
    $('#yourwhispers-btn').hide();
    $('#yourfollowees-btn').hide();

    $('#name').click(function() {
        $(this).val('')
    })



    $('#name').keypress(function(ev) {
            if (ev.which == 13) {
                //console.log(currentPeople)
                //  if (currentPeople) {
                //    showMovies(currentPeople);
                //  } else {
                $k.api.GET({
                    url:'/api/people/manualsearch',
                    json:{term:$(this).val()},
                    success:function(json){
                        //console.log(json);
                        currentPeople=json;
                        showMovies(json);
                    },
                    error:function(){
                        response('boo');
                    }
                    //  });
                })
                return false
            }
        }
    );

    $('#home-btn').click(function() {
        $('#bigcont > div').hide();
        $('#people-input').show();
        $('#people').show();
        $('.nav li').removeClass('active');
        $(this).addClass('active');
    });

//
//    $('#about-btn').click(function() {
//        $('#bigcont > div').hide();
//        $('#about').show();
//        $('.nav li').removeClass('active');
//        $(this).addClass('active');
//    });
//

    $('#faq-btn').click(function() {
        $('#bigcont > div').hide();
        $('#faq').show();
        $('.nav li').removeClass('active');
        $(this).addClass('active');
    });


    $('#yourwhispers-btn').click(function() {
        $('#bigcont > div').hide();
        showyourWhispers();
        //$('#yourwhispers').show();
        $('.nav li').removeClass('active');
        $(this).addClass('active');
    });


    $('#yourfollowees-btn').click(function() {
        $('#bigcont > div').hide();
        showFollowees();
        //$('#yourwhispers').show();
        $('.nav li').removeClass('active');
        $(this).addClass('active');

    });


    $('#signin-btn').click(function() {
        $('#bigcont > div').hide();
        if (!mp.currentUser) {
            $('#signin').show();
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


    $('#register-btn').click(function() {
        $('#register').show();
        $('#register-modal').modal('show');
    });



    $('#register-modal,#email-modal,#forgot-modal').on('hidden', function () {
      $('#forgot-email,#email,#register-email').tooltip('destroy');
    })


    $('#id_password').keyup(function(e) {
      if(e.keyCode == 13) {       
        $("#signin-submit").click();
      }
    });

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

    signinevents = function(email) {
        $('#username').text(email);
        $('#signin-btn > a').text('Log out');
        $('#register-btn').hide();
        $('#yourwhispers-btn').show();
        $('#yourfollowees-btn').show();
    }

    logoutevents = function() {
        $('#username').text('');
        $('#signin-btn > a').text('Sign in');
        $('#register-btn').show();
        $('#yourwhispers-btn').hide();
        $('#yourfollowees-btn').hide();
    }


    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            function getCookie(name) {
                var cookieValue = null;
                if (document.cookie && document.cookie != '') {
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                        var cookie = jQuery.trim(cookies[i]);
                        // Does this cookie string begin with the name we want?
                        if (cookie.substring(0, name.length + 1) == (name + '=')) {
                            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                            break;
                        }
                    }
                }
                return cookieValue;
            }
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                // Only send the token to relative URLs i.e. locally.
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });


    $(document).keyup(function(ev) {
      if (ev.which === 191) {
        $('#name').val('');
        //$('html,body').animate({
        //  scrollTop: $("#name").offset().top
        //}, 2000);
        $('#name').focus();
      }
    }
    );

};

$(document).ready(mp.pages.frontpage.init);


