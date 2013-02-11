$k.pages.follows = new function(){
    this.init = function(){
        $('.btn-unfollow').each(function(){
            var $btn = $(this);
            $btn.async('ajax',{
                url:'api/unfollow',
                json:function(){
                    return {artist_id:$btn.attr('artist-id')}
                },
                success:function(){
                    $btn.fadeOut();
                }
            });
        });
    }
}