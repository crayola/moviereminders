function KDate(timezone) {
 
    var _values = {
        millisecond: 0,
        second: 0,
        minute: 0,
        hour: 0,
        day: 0,
        month: 0,
        year: 0
    }
    var _offset = 0;
    var _systemOffset = 0;
    var _timezone;
    var _units = [
    {
        key : "millisecond", 
        base : 1000
    },

    {
        key : "second", 
        base : 60
    },

    {
        key : "minute", 
        base : 60
    },

    {
        key : "hour", 
        base : 24
    },

    {
        key : "day", 
        base : 31
    },

    {
        key : "month", 
        base : 12
    },

    {
        key : "year", 
        base : 10000
    }
    ];
            
    //public functions
    this.fromJsDate = function(jsDate) {
        _values.millisecond = jsDate.getMilliseconds();
        _values.second = jsDate.getSeconds();
        _values.minute = jsDate.getMinutes();
        _values.hour = jsDate.getHours();
        _values.day = jsDate.getDate();
        _values.month = jsDate.getMonth();
        _values.year = jsDate.getFullYear();
        _systemOffset = -jsDate.getTimezoneOffset(); //in JS, this is reversed
        _offset = _systemOffset;      
        return this;        
    }
    
    this.toJsDate = function() {
        var utc = this.UTC().getTime();
        return new Date(utc);
    }
    
    this.getValues = function() {
        return _values;
    }
    
    this.getTimeZone = function() {
        return _timezone;
    }
    
    this.getOffset = function() {
        return _offset;
    }
    
    this.add = function(values) {        
        var keep = 0;
        for(var i=0; i<_units.length; i++) {
            var unit = _units[i].key;
            var base = _units[i].base;
            if(keep || values[unit]) {
                var add = keep + (values[unit] || 0);
                if(unit === "day") {                    
                    //specific for days/months
                    keep = 0;
                    if(add > 0) {
                        base = _getNumberOfDaysInMonth(_values.month, _values.year);
                        while(_values[unit] + add > base) {
                            keep++;
                            add -= base;
                            base = _getNumberOfDaysInMonth(_inc("month", _values.month, keep), _values.year);
                        }
                        _values[unit] += add;
                    } else {
                        base = _getNumberOfDaysInMonth(_inc("month", _values.month, -1), _values.year);
                        while(_values[unit] + add < 1) {
                            keep--;
                            add += (base );
                            base = _getNumberOfDaysInMonth(_inc("month", _values.month, keep - 1), _values.year);
                        }
                        _values[unit] += add;
                    }
                } else {
                    //standard case
                    keep = Math.floor((_values[unit] + add) / base);                    
                    _values[unit] = _values[unit] + add - (keep * base);
                }
            }
        }
        return this;
    }
    
    this.set = function(values) {
        if('millisecond' in values) _values.millisecond = values.millisecond;
        if('second' in values) _values.second = values.second;
        if('minute' in values) _values.minute = values.minute;
        if('hour' in values)   _values.hour = values.hour;
        if('day' in values)    _values.day = values.day;
        if('month' in values)  _values.month = values.month;
        if('year' in values)   _values.year = values.year;
        return this;
    }
    
    this.clone = function() {
        var k = new KDate(_timezone);
        k.set(_values);
        return k;
    }
    
    this.setTimeZone = function(timezone) {
        //store values
        _timezone = timezone;
        var newOffset = _getOffsetFromTimeZone(timezone);                
        if(newOffset !== _offset) {
            var delta = newOffset - _offset;
            _offset = newOffset;

            //update current time
            this.add({
                minute : delta
            });
        }
        return this;        
    }
    
    this.getMilliseconds = function() {
        return _values.millisecond;
    }
    
    this.getSeconds = function() {
        return _values.second;
    }
    
    this.getMinutes = function() {
        return _values.minute;
    }
    
    this.getHours = function() {
        return _values.hour;
    } 
    
    this.getDay = function() {
        return _values.day;
    }
    
    this.getMonth = function() {
        return _values.month;
    }   
    
    this.getYear = function() {
        return _values.year;
    }     
    
    this.getDayOfWeek = function() {
        return ((Math.floor(this.getLocalTime() / 86400000) + 4) % 7); //Epoch is a thursday, returning ISO values (Sunday = 7, Monday = 1) 
    }
    
    this.getLocalTime = function() {
        return Date.UTC(_values.year, _values.month, _values.day, _values.hour, _values.minute, _values.second, _values.millisecond);
    }    
    
    this.getTime = function() {
        var time = this.getLocalTime() - _offset * 60000;
        return time;
    }
    
    this.UTC = function() {
        return this.clone().setTimeZone("UTC");
    }
    
    this.isLeap = function() {
        return _isLeapYear(_values.year);
    }
    
    this.clearTime = function() {
        return this.set({
            hour:0, 
            minute:0, 
            second:0, 
            millisecond: 0
        });
    }
    
    //REQUIRES DateJs for CultureInfo
    this.toString = function(format) {
        format = format || "F";
        var x = this;
        var C = Date.CultureInfo;
        // Standard Date and Time Format Strings. Formats pulled from CultureInfo file and
        // may vary by culture. 
        if (format && format.length == 1) {
            var c = C.formatPatterns;
            x.t = x.toString;
            switch (format) {
                case "d":
                    return x.t(c.shortDate);
                case "D":
                    return x.t(c.longDate);
                case "F":
                    return x.t(c.fullDateTime);
                case "m":
                    return x.t(c.monthDay);
                case "r":
                    return x.t(c.rfc1123);
                case "s":
                    return x.t(c.sortableDateTime);
                case "t":
                    return x.t(c.shortTime);
                case "T":
                    return x.t(c.longTime);
                case "u":
                    return x.t(c.universalSortableDateTime);
                case "y":
                    return x.t(c.yearMonth);
                
            }    
        }        
        var ord = function (n) {
            switch (n * 1) {
                case 1: 
                case 21: 
                case 31:
                    return "st";
                case 2: 
                case 22:
                    return "nd";
                case 3: 
                case 23:
                    return "rd";
                default:
                    return "th";
            }
        };
        return format.replace(/(\\)?(dd?d?d?|MM?M?M?|yy?y?y?|hh?|HH?|mm?|ss?|tt?|K|SS?S?)/g, 
            function (m) {
                if (m.charAt(0) === "\\") {
                    return m.replace("\\", "");
                }
                x.h = x.getHours;
                switch (m) {
                    case "hh":
                        return _p(x.h() < 13 ? (x.h() === 0 ? 12 : x.h()) : (x.h() - 12));
                    case "h":
                        return x.h() < 13 ? (x.h() === 0 ? 12 : x.h()) : (x.h() - 12);
                    case "HH":
                        return _p(x.h());
                    case "H":
                        return x.h();
                    case "mm":
                        return _p(x.getMinutes());
                    case "m":
                        return x.getMinutes();
                    case "ss":
                        return _p(x.getSeconds());
                    case "s":
                        return x.getSeconds();
                    case "yyyy":
                        return _p(x.getYear(), 4);
                    case "yy":
                        return _p(x.getYear());
                    case "dddd":
                        return C.dayNames[x.getDayOfWeek()];
                    case "ddd":
                        return C.abbreviatedDayNames[x.getDayOfWeek()];
                    case "dd":
                        return _p(x.getDay());
                    case "d":
                        return x.getDay();
                    case "MMMM":
                        return C.monthNames[x.getMonth()];
                    case "MMM":
                        return C.abbreviatedMonthNames[x.getMonth()];
                    case "MM":
                        return _p((x.getMonth() + 1));
                    case "M":
                        return x.getMonth() + 1;
                    case "t":
                        return x.h() < 12 ? C.amDesignator.substring(0, 1) : C.pmDesignator.substring(0, 1);
                    case "tt":
                        return x.h() < 12 ? C.amDesignator : C.pmDesignator;
                    case "SSS":
                        return _p(x.getMilliseconds());
                    case "S":
                        return ord(x.getDay());
                    case "K"://AM/PM 
                        return x.h()<12?'AM':'PM';
                    default:
                        return m;
                }
            });
    }

    this.prettyDateMP = function(extended) {
        //var diff = Math.floor((this.getTime() - KDate.today(_timezone).getTime()) / (24*60*60*1000));
        var text = "" + this.toString("dddd, MMMM dS yyyy") + "";
        return text;  
    };

    this.prettyDate = function(extended) {
        var diff = Math.floor((this.getTime() - KDate.today(_timezone).getTime()) / (24*60*60*1000));
        var text = "";
        switch(diff) {
            case -1:
                text = "Yesterday";
                if(extended) text += " (" + this.toString("dddd, MMMM dS") + ")";
                break;            
            case 0:
                text = "Today";
                if(extended) text += " (" + this.toString("dddd, MMMM dS") + ")";
                break;
            case 1:
                text = "Tomorrow";
                if(extended) text += " (" + this.toString("dddd, MMMM dS") + ")";
                break;
            case 2:
            case 3:
            case 4:
            case 5:
            case 6:
            case 7:
                text = "" + this.toString("dddd");
                if(extended) text += " (" + this.toString("dS MMMM") + ")"; 
                break;
            default:
                text = "" + this.toString("dddd, MMMM dS yyyy") + "";
                break;
        }
        return text;  
    }

    
    //private functions
    function _getOffsetFromTimeZone(timezone) {
        return KDATE_TIMEZONE_OFFSETS[timezone];
    }
    
    function _getNumberOfDaysInMonth(month, year) {
        if(month === 1) {
            return _isLeapYear(year) ? 29 : 28;
        } else {
            return month <= 6 ? 31 - month % 2 : 30 + month % 2;
        }
    }
    
    function _isLeapYear(year) {
        return year % 400 == 0 || (year % 4 == 0 && year % 100 != 0);
    }
    
    function _p(s, l) {
        if (!l) l = 2;
        return ("000" + s).slice(l * -1); 
    }   
    
    function _inc(unit, original, amount) {
        if(unit === "month") {
            if(amount >= 0) {
                return (original + amount) % 12;
            } else {
                var r = original + amount;
                while(r<0) {
                    r = 12 - r;
                }
                return r;
            }
        }
        return null;
    }
    
 
    //date.floor(5) > round to previous 5 minutes
    this.floor=function(span){
        var min = this.getMinutes();
        var newMin = 5 * (Math.floor(min / 5));
        this.add({
            minute:newMin-min
        });
        this.set({
            second:0,
            millisecond:0
        });
        return this;
    }
    //date.ceil(5) > round to next 5 minutes
    this.ceil=function(span){
        var min = this.getMinutes();
        var newMin = 5 * (Math.ceil(min / 5));
        this.add({
            minute:newMin-min
        });
        this.set({
            second:0,
            millisecond:0
        });
        return this;
    }
    
    this.isToday=function(){
        var today = KDate.today(timezone);
        return (today.getYear() === this.getYear()
            && today.getMonth() === this.getMonth()
            && today.getDay() === this.getDay()) 
    }
    
    this.fromJsDate(new Date());
    this.setTimeZone(timezone || "UTC"); 
}

KDate.prototype.isBefore=function(other){
    return this.getTime()< other.getTime();
}

KDate.prototype.isAfter=function(other){
    return this.getTime() > other.getTime(); 
}

KDate.prototype.isEqual=function(other){
    return this.getTime() === other.getTime();
}

//static properties and methods
KDate.today = function(timezone) {
    return new KDate(timezone).clearTime();
}
KDate.now = function(timezone) {  
    return new KDate(timezone);
}

var KDATE_TIMEZONE_OFFSETS = {
    "Etc/GMT+12":-720, 
    "Etc/GMT+11":-660, 
    "Pacific/Apia":-660, 
    "Pacific/Midway":-660, 
    "Pacific/Niue":-660, 
    "Pacific/Pago_Pago":-660, 
    "America/Adak":-600, 
    "Etc/GMT+10":-600, 
    "HST":-600, 
    "Pacific/Fakaofo":-600, 
    "Pacific/Honolulu":-600, 
    "Pacific/Johnston":-600, 
    "Pacific/Rarotonga":-600, 
    "Pacific/Tahiti":-600, 
    "Pacific/Marquesas":-510, 
    "America/Anchorage":-540, 
    "America/Juneau":-540, 
    "America/Nome":-540, 
    "America/Yakutat":-540, 
    "Etc/GMT+9":-540, 
    "Pacific/Gambier":-540, 
    "America/Dawson":-480, 
    "America/Los_Angeles":-420,//tmp hack daylight saving time 
    "America/Santa_Isabel":-480, 
    "America/Tijuana":-480, 
    "America/Vancouver":-480, 
    "America/Whitehorse":-480, 
    "Etc/GMT+8":-480, 
    "PST":-480, 
    "PST8PDT":-480, 
    "Pacific/Pitcairn":-480, 
    "America/Boise":-420, 
    "America/Cambridge_Bay":-420, 
    "America/Chihuahua":-420, 
    "America/Dawson_Creek":-420, 
    "America/Denver":-420, 
    "America/Edmonton":-420, 
    "America/Hermosillo":-420, 
    "America/Inuvik":-420, 
    "America/Mazatlan":-420, 
    "America/Ojinaga":-420, 
    "America/Phoenix":-420, 
    "America/Yellowknife":-420, 
    "Etc/GMT+7":-420, 
    "MST":-420, 
    "MST7MDT":-420, 
    "America/Bahia_Banderas":-360, 
    "America/Belize":-360, 
    "America/Cancun":-360, 
    "America/Chicago":-360, 
    "America/Costa_Rica":-360, 
    "America/El_Salvador":-360, 
    "America/Guatemala":-360, 
    "America/Indiana/Knox":-360, 
    "America/Indiana/Tell_City":-360, 
    "America/Managua":-360, 
    "America/Matamoros":-360, 
    "America/Menominee":-360, 
    "America/Merida":-360, 
    "America/Mexico_City":-360, 
    "America/Monterrey":-360, 
    "America/North_Dakota/Center":-360, 
    "America/North_Dakota/New_Salem":-360, 
    "America/Rainy_River":-360, 
    "America/Rankin_Inlet":-360, 
    "America/Regina":-360, 
    "America/Swift_Current":-360, 
    "America/Tegucigalpa":-360, 
    "America/Winnipeg":-360, 
    "CST6CDT":-360, 
    "Etc/GMT+6":-360, 
    "Pacific/Easter":-360, 
    "Pacific/Galapagos":-360, 
    "America/Atikokan":-300, 
    "America/Bogota":-300, 
    "America/Cayman":-300, 
    "America/Detroit":-300, 
    "America/Grand_Turk":-300, 
    "America/Guayaquil":-300, 
    "America/Havana":-300, 
    "America/Indiana/Indianapolis":-300, 
    "America/Indiana/Marengo":-300, 
    "America/Indiana/Petersburg":-300, 
    "America/Indiana/Vevay":-300, 
    "America/Indiana/Vincennes":-300, 
    "America/Indiana/Winamac":-300, 
    "America/Iqaluit":-300, 
    "America/Jamaica":-300, 
    "America/Kentucky/Louisville":-300, 
    "America/Kentucky/Monticello":-300, 
    "America/Lima":-300, 
    "America/Montreal":-300, 
    "America/Nassau":-300, 
    "America/New_York":-300, 
    "America/Nipigon":-300, 
    "America/Panama":-300, 
    "America/Pangnirtung":-300, 
    "America/Port-au-Prince":-300, 
    "America/Resolute":-300, 
    "America/Thunder_Bay":-300, 
    "America/Toronto":-300, 
    "EST":-300, 
    "EST5EDT":-300, 
    "Etc/GMT+5":-300, 
    "America/Caracas":-210, 
    "America/Anguilla":-240, 
    "America/Antigua":-240, 
    "America/Argentina/San_Luis":-180, 
    "America/Aruba":-240, 
    "America/Asuncion":-240, 
    "America/Barbados":-240, 
    "America/Blanc-Sablon":-240, 
    "America/Boa_Vista":-240, 
    "America/Campo_Grande":-240, 
    "America/Cuiaba":-240, 
    "America/Curacao":-240, 
    "America/Dominica":-240, 
    "America/Eirunepe":-240, 
    "America/Glace_Bay":-240, 
    "America/Goose_Bay":-240, 
    "America/Grenada":-240, 
    "America/Guadeloupe":-240, 
    "America/Guyana":-240, 
    "America/Halifax":-240, 
    "America/La_Paz":-240, 
    "America/Manaus":-240, 
    "America/Martinique":-240, 
    "America/Moncton":-240, 
    "America/Montserrat":-240, 
    "America/Port_of_Spain":-240, 
    "America/Porto_Velho":-240, 
    "America/Puerto_Rico":-240, 
    "America/Rio_Branco":-240, 
    "America/Santiago":-240, 
    "America/Santo_Domingo":-240, 
    "America/St_Kitts":-240, 
    "America/St_Lucia":-240, 
    "America/St_Thomas":-240, 
    "America/St_Vincent":-240, 
    "America/Thule":-240, 
    "America/Tortola":-240, 
    "Antarctica/Palmer":-240, 
    "Atlantic/Bermuda":-240, 
    "Atlantic/Stanley":-240, 
    "Etc/GMT+4":-240, 
    "America/St_Johns":-150, 
    "America/Araguaina":-180, 
    "America/Argentina/Buenos_Aires":-180, 
    "America/Argentina/Catamarca":-180, 
    "America/Argentina/Cordoba":-180, 
    "America/Argentina/Jujuy":-180, 
    "America/Argentina/La_Rioja":-180, 
    "America/Argentina/Mendoza":-180, 
    "America/Argentina/Rio_Gallegos":-180, 
    "America/Argentina/Salta":-180, 
    "America/Argentina/San_Juan":-180, 
    "America/Argentina/Tucuman":-180, 
    "America/Argentina/Ushuaia":-180, 
    "America/Bahia":-180, 
    "America/Belem":-180, 
    "America/Cayenne":-180, 
    "America/Fortaleza":-180, 
    "America/Godthab":-180, 
    "America/Maceio":-180, 
    "America/Miquelon":-180, 
    "America/Montevideo":-180, 
    "America/Paramaribo":-180, 
    "America/Recife":-180, 
    "America/Santarem":-180, 
    "America/Sao_Paulo":-180, 
    "Antarctica/Rothera":-180, 
    "Etc/GMT+3":-180, 
    "America/Noronha":-120, 
    "Atlantic/South_Georgia":-120, 
    "Etc/GMT+2":-120, 
    "America/Scoresbysund":-60, 
    "Atlantic/Azores":-60, 
    "Atlantic/Cape_Verde":-60, 
    "Etc/GMT+1":-60, 
    "Africa/Abidjan":0, 
    "Africa/Accra":0, 
    "Africa/Bamako":0, 
    "Africa/Banjul":0, 
    "Africa/Bissau":0, 
    "Africa/Casablanca":0, 
    "Africa/Conakry":0, 
    "Africa/Dakar":0, 
    "Africa/El_Aaiun":0, 
    "Africa/Freetown":0, 
    "Africa/Lome":0, 
    "Africa/Monrovia":0, 
    "Africa/Nouakchott":0, 
    "Africa/Ouagadougou":0, 
    "Africa/Sao_Tome":0, 
    "America/Danmarkshavn":0, 
    "Atlantic/Canary":0, 
    "Atlantic/Faroe":0, 
    "Atlantic/Madeira":0, 
    "Atlantic/Reykjavik":0, 
    "Atlantic/St_Helena":0, 
    "Etc/GMT":0, 
    "Etc/UCT":0, 
    "Etc/UTC":0, 
    "Europe/Dublin":0, 
    "Europe/Lisbon":0, 
    "Europe/London":0, 
    "UTC":0, 
    "WET":0, 
    "Africa/Algiers":60, 
    "Africa/Bangui":60, 
    "Africa/Brazzaville":60, 
    "Africa/Ceuta":60, 
    "Africa/Douala":60, 
    "Africa/Kinshasa":60, 
    "Africa/Lagos":60, 
    "Africa/Libreville":60, 
    "Africa/Luanda":60, 
    "Africa/Malabo":60, 
    "Africa/Ndjamena":60, 
    "Africa/Niamey":60, 
    "Africa/Porto-Novo":60, 
    "Africa/Tunis":60, 
    "Africa/Windhoek":60, 
    "CET":60, 
    "Etc/GMT-1":60, 
    "Europe/Amsterdam":60, 
    "Europe/Andorra":60, 
    "Europe/Belgrade":60, 
    "Europe/Berlin":60, 
    "Europe/Brussels":60, 
    "Europe/Budapest":60, 
    "Europe/Copenhagen":60, 
    "Europe/Gibraltar":60, 
    "Europe/Luxembourg":60, 
    "Europe/Madrid":60, 
    "Europe/Malta":60, 
    "Europe/Monaco":60, 
    "Europe/Oslo":60, 
    "Europe/Paris":60, 
    "Europe/Prague":60, 
    "Europe/Rome":60, 
    "Europe/Stockholm":60, 
    "Europe/Tirane":60, 
    "Europe/Vaduz":60, 
    "Europe/Vienna":60, 
    "Europe/Warsaw":60, 
    "Europe/Zurich":60, 
    "MET":60, 
    "Africa/Blantyre":120, 
    "Africa/Bujumbura":120, 
    "Africa/Cairo":120, 
    "Africa/Gaborone":120, 
    "Africa/Harare":120, 
    "Africa/Johannesburg":120, 
    "Africa/Kigali":120, 
    "Africa/Lubumbashi":120, 
    "Africa/Lusaka":120, 
    "Africa/Maputo":120, 
    "Africa/Maseru":120, 
    "Africa/Mbabane":120, 
    "Africa/Tripoli":120, 
    "Asia/Amman":120, 
    "Asia/Beirut":120, 
    "Asia/Damascus":120, 
    "Asia/Gaza":120, 
    "Asia/Jerusalem":120, 
    "Asia/Nicosia":120, 
    "EET":120, 
    "Etc/GMT-2":120, 
    "Europe/Athens":120, 
    "Europe/Bucharest":120, 
    "Europe/Chisinau":120, 
    "Europe/Helsinki":120, 
    "Europe/Istanbul":120, 
    "Europe/Kaliningrad":120, 
    "Europe/Kiev":120, 
    "Europe/Minsk":120, 
    "Europe/Riga":120, 
    "Europe/Simferopol":120, 
    "Europe/Sofia":120, 
    "Europe/Tallinn":120, 
    "Europe/Uzhgorod":120, 
    "Europe/Vilnius":120, 
    "Europe/Zaporozhye":120, 
    "Africa/Addis_Ababa":180, 
    "Africa/Asmara":180, 
    "Africa/Dar_es_Salaam":180, 
    "Africa/Djibouti":180, 
    "Africa/Kampala":180, 
    "Africa/Khartoum":180, 
    "Africa/Mogadishu":180, 
    "Africa/Nairobi":180, 
    "Antarctica/Syowa":180, 
    "Asia/Aden":180, 
    "Asia/Baghdad":180, 
    "Asia/Bahrain":180, 
    "Asia/Kuwait":180, 
    "Asia/Qatar":180, 
    "Asia/Riyadh":180, 
    "Etc/GMT-3":180, 
    "Europe/Moscow":180, 
    "Europe/Samara":180, 
    "Europe/Volgograd":180, 
    "Indian/Antananarivo":180, 
    "Indian/Comoro":180, 
    "Indian/Mayotte":180, 
    "Asia/Tehran":210, 
    "Asia/Baku":240, 
    "Asia/Dubai":240, 
    "Asia/Muscat":240, 
    "Asia/Tbilisi":240, 
    "Asia/Yerevan":240, 
    "Etc/GMT-4":240, 
    "Indian/Mahe":240, 
    "Indian/Mauritius":240, 
    "Indian/Reunion":240, 
    "Asia/Kabul":270, 
    "Antarctica/Mawson":300, 
    "Asia/Aqtau":300, 
    "Asia/Aqtobe":300, 
    "Asia/Ashgabat":300, 
    "Asia/Dushanbe":300, 
    "Asia/Karachi":300, 
    "Asia/Oral":300, 
    "Asia/Samarkand":300, 
    "Asia/Tashkent":300, 
    "Asia/Yekaterinburg":300, 
    "Etc/GMT-5":300, 
    "Indian/Kerguelen":300, 
    "Indian/Maldives":300, 
    "Asia/Colombo":330, 
    "Asia/Kolkata":330, 
    "Asia/Kathmandu":345, 
    "Antarctica/Vostok":360, 
    "Asia/Almaty":360, 
    "Asia/Bishkek":360, 
    "Asia/Dhaka":360, 
    "Asia/Novokuznetsk":360, 
    "Asia/Novosibirsk":360, 
    "Asia/Omsk":360, 
    "Asia/Qyzylorda":360, 
    "Asia/Thimphu":360, 
    "Etc/GMT-6":360, 
    "Indian/Chagos":360, 
    "Asia/Rangoon":390, 
    "Indian/Cocos":390, 
    "Antarctica/Davis":420, 
    "Asia/Bangkok":420, 
    "Asia/Ho_Chi_Minh":420, 
    "Asia/Hovd":420, 
    "Asia/Jakarta":420, 
    "Asia/Krasnoyarsk":420, 
    "Asia/Phnom_Penh":420, 
    "Asia/Pontianak":420, 
    "Asia/Vientiane":420, 
    "Etc/GMT-7":420, 
    "Indian/Christmas":420, 
    "Antarctica/Casey":480, 
    "Asia/Brunei":480, 
    "Asia/Choibalsan":480, 
    "Asia/Chongqing":480, 
    "Asia/Harbin":480, 
    "Asia/Hong_Kong":480, 
    "Asia/Irkutsk":480, 
    "Asia/Kashgar":480, 
    "Asia/Kuala_Lumpur":480, 
    "Asia/Kuching":480, 
    "Asia/Macau":480, 
    "Asia/Makassar":480, 
    "Asia/Manila":480, 
    "Asia/Shanghai":480, 
    "Asia/Singapore":480, 
    "Asia/Taipei":480, 
    "Asia/Ulaanbaatar":480, 
    "Asia/Urumqi":480, 
    "Australia/Perth":480, 
    "Etc/GMT-8":480, 
    "Australia/Eucla":525, 
    "Asia/Dili":540, 
    "Asia/Jayapura":540, 
    "Asia/Pyongyang":540, 
    "Asia/Seoul":540, 
    "Asia/Tokyo":540, 
    "Asia/Yakutsk":540, 
    "Etc/GMT-9":540, 
    "Pacific/Palau":540, 
    "Australia/Adelaide":570, 
    "Australia/Broken_Hill":570, 
    "Australia/Darwin":570, 
    "Antarctica/DumontDUrville":600, 
    "Asia/Sakhalin":600, 
    "Asia/Vladivostok":600, 
    "Australia/Brisbane":600, 
    "Australia/Currie":600, 
    "Australia/Hobart":600, 
    "Australia/Lindeman":600, 
    "Australia/Melbourne":600, 
    "Australia/Sydney":600, 
    "Etc/GMT-10":600, 
    "Pacific/Chuuk":600, 
    "Pacific/Guam":600, 
    "Pacific/Port_Moresby":600, 
    "Pacific/Saipan":600, 
    "Australia/Lord_Howe":630, 
    "Antarctica/Macquarie":660, 
    "Asia/Anadyr":660, 
    "Asia/Kamchatka":660, 
    "Asia/Magadan":660, 
    "Etc/GMT-11":660, 
    "Pacific/Efate":660, 
    "Pacific/Guadalcanal":660, 
    "Pacific/Kosrae":660, 
    "Pacific/Noumea":660, 
    "Pacific/Pohnpei":660, 
    "Pacific/Norfolk":690, 
    "Antarctica/McMurdo":720, 
    "Etc/GMT-12":720, 
    "Pacific/Auckland":720, 
    "Pacific/Fiji":720, 
    "Pacific/Funafuti":720, 
    "Pacific/Kwajalein":720, 
    "Pacific/Majuro":720, 
    "Pacific/Nauru":720, 
    "Pacific/Tarawa":720, 
    "Pacific/Wake":720, 
    "Pacific/Wallis":720, 
    "Pacific/Chatham":765, 
    "Etc/GMT-13":780, 
    "Pacific/Enderbury":780, 
    "Pacific/Tongatapu":780, 
    "Etc/GMT-14":840, 
    "Pacific/Kiritimati":840
};  
