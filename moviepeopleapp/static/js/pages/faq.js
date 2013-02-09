$k.pages.faq = new function(){
    this.init = function(){
        $('#faq-btn').click(function() {
            $('#bigcont > div').hide();
            $('#faq').show();
            $('.nav li').removeClass('active');
            $(this).addClass('active');
        });

    }
}