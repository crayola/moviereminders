$k.pages.homepage = new function(){
    this.init = function(){
        $('.artist-nofollow').each(function(i,a){
            var $a = $(a);
            $a.async(function(){
                var artistId = $a.attr('artist-id');
                return $k.api.GET({
                    url:'/api/people/'+artistId+'/subscribe'
                })
            });
        });
    }
}