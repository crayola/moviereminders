$k.pages.find = new function(){
    this.init = function(){

        var $input = $('#artist-name');
        //init autocomplete input for people name
        mp.artistSearch.initAutocomplete($input);
    }
}