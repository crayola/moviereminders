$k.log = {
    AJAX_LOG_URL:'/api/log',
    consolelog:function(txt){
        try {
            console&&console.log&&console.log(txt);
        }
        catch(err){
        //could not log
        }
    },
    ajaxLog:function(level,txt,jsonObject){
        try {
            var dataJSON ={
                text:txt,
                time:$k.date.encode(new Date()),
                level:level
            }
            if(jsonObject){
                dataJSON.json = JSON.stringify(jsonObject);
            }
            var data = 'JSON='+escape(JSON.stringify(dataJSON));
            $.ajax({
                type: 'POST',
                dataType:'jsonp',
                url: $k.log.AJAX_LOG_URL+'?apilog=1',
                data: data,
                success:function(){},
                error:function(){}
             
            });
        }
        catch(err){
            var test=0;
        //could not log
        }
    },
    ajaxLogError:function(txt,err){
        try{
            var logObject = {
                browser:$.browser,
                url:location.href
            };
            if(navigator){
                logObject.navigator={
                    appCodeName: navigator.appCodeName,
                    appName: navigator.appName,
                    appVersion: navigator.appVersion,
                    cookieEnabled: navigator.cookieEnabled,
                    language: navigator.language,
                    platform: navigator.platform,
                    product: navigator.product,
                    productSub: navigator.productSub,
                    userAgent: navigator.userAgent,
                    vendor: navigator.vendor,
                    vendorSub: navigator.vendorSub
                };
            }
            if(err){
                logObject.stacktrace = printStackTrace({
                    e:err
                });
                logObject.exception=err;
            }
            $k.log.ajaxLog('error',txt,logObject);
        }
        catch(err){
            //could not log error
        }
    }
}

log = new (function(){
    return{
        debug : function(txt){
            $k.log.consolelog('#DEBUG '+txt);
        },
        info : function(txt,json){
            $k.log.consolelog('#INFO '+txt);
            $k.log.ajaxLog('info',txt,json);
        },
        warn : function(txt,json){
            $k.log.consolelog('#WARN  '+txt);
            $k.log.ajaxLog('warn',txt,json)
        },
        error : function(txt,err){
            $k.log.ajaxLogError(txt,err);
            $k.log.consolelog('#ERROR  '+txt+' '+err.message);
            //throw err;
        }
    }
});