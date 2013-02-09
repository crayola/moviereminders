$k.pages = {};
$k.load = function(page) {
    try{
        log.info('Loading url '+document.URL);
        $(document).trigger('onBeforeInit');
        if(page && page !== ''){
            if(!($k.pages)){
                log.error('Loading page '+page+' but no pages defined');
            }
            if(!($k.pages[page])){
                log.error('Loading page '+page+' (no specific javascript)')
            }
            else{
                log.info('Loading page '+page+'')
                $k.page = $k.pages[page];
                $k.page.init();
            }
        }
        $(document).trigger('onAfterInit');

    }catch(ex){
        log.error('error while loading page:'+page,ex);
    }
}