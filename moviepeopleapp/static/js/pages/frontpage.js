$k.pages.frontpage = new function(){

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
        if (currentPeople.profile!=='') {
            $('#people-pic').html('<img width=500 src="http://cf2.imgobject.com/t/p/w342' + currentPeople.profile + '">');
        } else {
            $('#people-pic').html('<img width=500 src="' + staticfolder + 'img/question_mark.png"/>');
        }

        $('#people-pic').show();
        $('#right-pane').show();

        //get all items
        var items=makeItems(movies, asc=false);

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

    function showMovies(currentPeople) {
        if(currentPeople){
            //call server to get stories
            $k.api.GET({
                url:'/api/people/'+currentPeople.id+'/movies',
                success:function(json){
                    //handle dates
                    onMovies(json.movies, currentPeople);
                    $('#people').fadeIn();
                },
                error:function(){
                    $('#hidden-modal').modal('show');
                }
            });
        }
    }

    //acavailhez:temporarily disable all this mess
    return;




























    $('#go').click(showMovies(currentPeople));

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
            ret +=  '<div class="movie-box-title">';
            ret +=  '<h1 class="title">'+item.movie.name+'</h1><hr/>';
            ret += '<div class="date">'+item.date.prettyDate()+'</div>';
            ret +=  '</div>';
            ret +=  '<span class="is">'+describeRole(item.movie, item.movie.people[0])+'</span>';
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




    $('#register-btn').click(function() {
        $('#register').show();
        $('#register-modal').modal('show');
    });




    $('#id_password').keyup(function(e) {
        if(e.keyCode == 13) {
            $("#signin-submit").click();
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



