$k.pages.frontpage = new function(){

    var currentPeople;

    this.init = function(){


        mp.artistSearch.initAutocomplete($('#artist-name'));

        $('#register-email-ok').click(function() {
            emailok(false, false, '#register-email');
        });

        $('#new-email-ok').click(function(){
            emailok(false, false, '#email');
        });

        $('#old-email-ok').click(function(){
            emailok(true, true, '#forgot-email');
        }); // fix this mess
        function emailok(existOk, forgot, emailid) {
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
                            $('#email-modal-already-exists').show();
                        }
                        else if (!('already_exists' in json) && existOk){
                            $('#email-modal-already-exists').show();
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
                        $('#hidden-modal').modal('show');
                    }
                });
            }
        };
    };


    //acavailhez:temporarily disable all this mess below
    /*




























     $('#go').click(showMovies(currentPeople));







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
     */
};



