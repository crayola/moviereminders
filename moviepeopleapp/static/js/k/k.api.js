//auhtor: Arnaud CAVAILHEZ
if(!$k) var $k = {};
$k.api = new (function(){

    var call = function(url,method,json,callback,callbackError){
        json = $.extend({},json);
        var data ='json='+encodeURIComponent(JSON.stringify(json))+'&api=true';
        return $.ajax({
            type: method,
            dataType:'json',
            url: url,
            data: data,
            success: function(json){
                if(json.error){
                    var error = json.error;
                    callbackError&&callbackError(json);
                }
                else{
                    //API success
                    try{
                        callback&&callback(json);
                    }
                    catch(ex){
                        callbackError&&callbackError({error:'call to success failed'});
                    }
                }
            },
            error:function(jqXHR, textStatus, errorThrown){
                callbackError&&callbackError({
                    error:'network'
                });
            }
        });
    }

    var callWithMethod= function(method,params){
         return call(params.url,method,params.json,params.success,params.error);
    }

    var that = {
        GET:function(params){
            return callWithMethod('GET',params); //note: we return the ajax wich is a $.Deferred
        },
        POST:function(params){
            return callWithMethod('POST',params);
        },
        DELETE:function(params){
            return callWithMethod('DELETE',params);
        }
    }
    return that;

})();

