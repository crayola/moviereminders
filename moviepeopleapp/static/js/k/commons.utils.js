//author Arnaud CAVAILHEZ
$k.utils = new function(){
        
    return {
        track:function(json){
            try {
                if(!json)return;
                var category = json.category;
                if(!category) category = 'MISC_CATEGORY';
                json.category = undefined;
                var event = json.event;
                if(!event) event = 'DEFAULT_EVENT';
                json.event = undefined;
            
                var trackText = JSON.stringify(json);
            
                log.info('TRACKING>> ' + category + ' ' + event +' JSON='+trackText);
            //do not actually track
            }
            catch(err){
                log.error('Could not track event',err);
            }
        },
        redirect:function(url, timeout) {
            if($k.sessionId){
                url = $k.url.addSessionId(url,$k.sessionId);
            }
            log.debug('redirect to url:'+url);
            if(!timeout) {
                //see this http://stackoverflow.com/questions/503093/how-can-i-make-a-redirect-page-in-jquery-javascript F
                //window.location.replace(url);
                window.location.href = url;
            //windows.navigate(url);
            } else {
                setTimeout(function(u) {
                    return function() {
                        //window.location.replace(u);
                        window.location.href = url;
                    //windows.navigate(url);
                    }
                }(url), timeout);
            }
        },
        getParameterByName:function(name) {
            var match = RegExp('[?&]' + name + '=([^&]*)')
            .exec(window.location.search);
            return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
        },
        getRootUrl:function(){
            var root = location.protocol + '//' + location.host;
            return root;
        },
        //convert a duration in ms to a text such as 12ms or 1h30
        preciseDuration:function(durationMS){
            var hour=Math.floor(durationMS/3600000);
            var minutes = Math.floor((durationMS-hour*3600000)/60000);
            var seconds = Math.floor((durationMS-minutes*60000)/1000);
            var ms = Math.floor(durationMS-seconds*1000);
            if(hour){
                return hour+'h'+String.pad(minutes,2);
            }
            else if(minutes){
                return minutes+'m'+String.pad(seconds,2)+'s';
            }
            else if(seconds){
                return seconds+'s'+String.pad(ms,3);
            }
            else return String.pad(ms,3)+'ms'
        },
    
        // round(24.5,5) >> 25
        // round(342,100) >> 300
        round:function(number,round){
            return round*Math.round(number/round);
        }
    }
};

String.pad=function(number,length) {
    var str = '' + number;
    while (str.length < length) {
        str = '0' + str;
    }
    return str;
}

String.pad2=function(number) {
    var str = '' + number;
    while (str.length < 2) {
        str = '0' + str;
    }
    return str;
}

Array.prototype.subArray=function(begin,end){
    var newArray = [];
    for(var i=begin;i<end&&i<this.length;i++){
        newArray.push(this[i]);
    }
    return newArray;
}

Math.log2=function(x){
    return Math.log(x)/Math.log(2);
}

if (typeof String.prototype.startsWith != 'function') {
    String.prototype.startsWith = function (str){
        return this.indexOf(str) == 0;
    };
}

if (typeof String.prototype.endsWith != 'function') {
    String.prototype.endsWith = function (str){
        return this.lastIndexOf(str) == this.length-str.length;
    };
}

// Compute the edit distance between the two given strings
//from https://gist.github.com/982927
String.prototype.editDistanceFrom = function(b){
    var a = this;
    if(a.length == 0) return b.length; 
    if(b.length == 0) return a.length; 

    var matrix = [];

    // increment along the first column of each row
    var i;
    for(i = 0; i <= b.length; i++){
        matrix[i] = [i];
    }

    // increment each column in the first row
    var j;
    for(j = 0; j <= a.length; j++){
        matrix[0][j] = j;
    }

    // Fill in the rest of the matrix
    for(i = 1; i <= b.length; i++){
        for(j = 1; j <= a.length; j++){
            if(b.charAt(i-1) == a.charAt(j-1)){
                matrix[i][j] = matrix[i-1][j-1];
            } else {
                matrix[i][j] = Math.min(matrix[i-1][j-1] + 1, // substitution
                    Math.min(matrix[i][j-1] + 1, // insertion
                        matrix[i-1][j] + 1)); // deletion
            }
        }
    }
 
    return matrix[b.length][a.length];
};

// Decompress an LZW-encoded string
// from http://stackoverflow.com/questions/294297/javascript-implementation-of-gzip
function lzw_decode(s) {
    var dict = {};
    var data = (s + "").split("");
    var currChar = data[0];
    var oldPhrase = currChar;
    var out = [currChar];
    var code = 256;
    var phrase;
    for (var i=1; i<data.length; i++) {
        var currCode = data[i].charCodeAt(0);
        if (currCode < 256) {
            phrase = data[i];
        }
        else {
            phrase = dict[currCode] ? dict[currCode] : (oldPhrase + currChar);
        }
        out.push(phrase);
        currChar = phrase.charAt(0);
        dict[code] = oldPhrase + currChar;
        code++;
        oldPhrase = phrase;
    }
    return out.join("");
}

function _lzw(s){
    try{
        var decoded = lzw_decode(s);
        return JSON.parse(decoded);
    }catch(ex){
        log.error('Could not decode lzw',ex);
    }
}

function _base64(s){
    try{
        var decoded = Base64.decode(s);
        return JSON.parse(decoded);
    }catch(ex){
        log.error('Could not decode base64',ex); 
    }
}

//add support for $().outerHTML()
jQuery.fn.outerHTML = function(s) {
    return s
    ? this.before(s).remove()
    : jQuery("<p>").append(this.eq(0).clone()).html();
};

//override jquery rVal() so it does not return placeholder
//http://stackoverflow.com/questions/3534267/can-i-override-jquery-val-for-only-some-input-elements
jQuery.fn.rVal=function() {
    if(this[0]) {
        var ele=$(this[0]);
        if(ele.attr('placeholder')!=''&&ele.val()==ele.attr('placeholder')) {
            return '';
        } else {
            return ele.val();
        }
    }
    return undefined;
};
