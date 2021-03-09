// Division with integer truncation.

function idiv (n, d) { return Math.floor(n / d); }

// Get year.
//
// N.B. Old browsers do not support getFullYear method so use
//      plain getYear instead. Also getYear returns a value
//      (year - 1900) on some browsers and a 4-digit year on
//      others.

function GetYear (date) {
    var year = date.getYear();
    if (year < 1900) year += 1900;
    return year;
}

// Get Month where January = 1 (not 0).

function GetMonth (date) {
    return date.getMonth() + 1;
}

// Get leap second count.
//   See http://tycho.usno.navy.mil/leapsec.html
//   See http://www.boulder.nist.gov/timefreq/pubs/bulletin/leapsecond.htm
//   See http://hpiers.obspm.fr/iers/bul/bulc/bulletinc.dat
//   "from 1999 January 1, 0h UTC, until further notice : UTC-TAI = - 32 s"

// 2016-10-12 KWS Added leap seconds from 2012, 2015 and 2017

function LeapSecondCount (date) {
    var year = GetYear(date);
    var month = GetMonth(date);
    if ( (year >= 2017) && (month >= 1) ) return 37;
    if ( (year >= 2015) && (month >= 7) ) return 36;
    if ( (year >= 2012) && (month >= 7) ) return 35;
    if ( (year >= 2009) && (month >= 1) ) return 34;
    if ( (year >= 2006) && (month >= 1) ) return 33;
    if ( (year >= 1999) && (month >= 1) ) return 32;
    if ( (year >= 1997) && (month >= 7) ) return 31;
    if ( (year >= 1996) && (month >= 1) ) return 30;
}

// Get elapsed seconds since midnight.

function GetElapsed (date) {
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();
    var elapsed = (((hours * 60) + minutes) * 60) + seconds;
    return elapsed;
}

// Get Modified Julian Date.

function GetMjd1 (date) {
    var year = GetYear(date);
    var month = GetMonth(date);
    var day = date.getDate();
    return GetMjd3(year, month, day);
}

function GetMjd3 (year, month, day) {
    var mjd =
    367 * year
    - idiv(7 * (idiv(month + 9, 12) + year), 4)
    - idiv(3 * (idiv(idiv(month + 9, 12) + year - 1, 100) + 1), 4)
    + idiv(275 * month, 9)
    + day
    + 1721028
    - 2400000;
    return mjd;
}

// Get day of year.

function GetDayOfYear (date) {
    var year = GetYear(date);
    var Doy = GetMjd1(date) - GetMjd3(year, 1, 1) + 1;
    return Doy;
}

// Format date/time in yyyy-mm-dd format (ISO 8601).

function FormatIso8601 (date) {
    var year = GetYear(date);
    var month = GetMonth(date);
    var day = date.getDate();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();

    var s = "";
    s += Fixed4(year) + "-";
    s += Fixed2(month) + "-";
    s += Fixed2(day) + " ";
    s += Fixed2(hours) + ":";
    s += Fixed2(minutes) + ":";
    s += Fixed2(seconds);
    return s;
}

// Format GPS time.

function FormatGpsTime (date, f) {
    var GpsDayCount = GetMjd1(date) - GetMjd3(1980, 1, 6);
    var GpsWeekCount = Math.floor(GpsDayCount / 7);
    var GpsCycle = Math.floor(GpsWeekCount / 1024);
    var GpsDay = GpsDayCount % 7;
    var GpsWeek = GpsWeekCount % 1024;
    var GpsSecond = (GpsDay * 86400) + GetElapsed(date);

    // N.B. Older browsers do not support switch().
    if (f == 0) {
        return "week " + GpsWeekCount;
    }
    if (f == 1) {
        return GpsSecond + " s";
    }
    if (f == 2) {
        var s = "";
        s += "cycle " + GpsCycle;
        s += " week " + Fixed4(GpsWeek);
        s += " day " + GpsDay;
        return s;
    }
}

// Compute Loran Time-Of-Coincidences for GRI 9940.

function LoranNextToc (date, n) {
    var next = new Date(date.getTime() + (n * 1000));
    var hours = next.getHours();
    var minutes = next.getMinutes();
    var seconds = next.getSeconds();

    var s = "";
    s += Fixed2(hours) + ":";
    s += Fixed2(minutes) + ":";
    s += Fixed2(seconds);
    return s;
}

function LoranUntilToc (date) {
    var days = GetMjd1(date) - GetMjd3(1958, 1, 1);
    var seconds = GetElapsed(date);
    var gri = 994;
    var lcm = 2;
    var toc = gri / lcm;
    var nexttoc = (86400 % toc) * days + seconds;
    nexttoc %= toc;
    return toc - nexttoc;
}

// Get weekday name.

function WeekDayName (date) {
    var DayName = new Array ("Sunday", "Monday", "Tuesday",
        "Wednesday", "Thursday", "Friday", "Saturday");
    return DayName[(3 + GetMjd1(date)) % 7];
}

// Display timezone offset as hours east of UTC.

function ShowTimezone (date) {
    if (date.getTimezoneOffset() > 0) {
        return "UTC-" + date.getTimezoneOffset( ) / 60;

    } else {
        return "UTC+" + date.getTimezoneOffset( ) / -60;
    }
}

// Create fixed width integer strings.

function Fixed2 (n) {
    return (n < 10 ? "0" : "") + n;
}
function Fixed3 (n) {
    n = Fixed2(n);
    return (n < 100 ? "0" : "") + n;
}
function Fixed4 (n) {
    n = Fixed3(n);
    return (n < 1e3 ? "0" : "") + n;
}
function Fixed5 (n) {
    n = Fixed4(n);
    return (n < 1e4 ? "0" : "") + n;
}
function Fixed6 (n) {
    n = Fixed5(n);
    return (n < 1e5 ? "0" : "") + n;
}

var timerID = null;
var timerRunning = false;

// Main 1 Hz timer callback.

function DisplayTime () {

    // N.B. Old browsers do not support getUTC methods.
    var local = new Date();
    utc = new Date(local.getTime() + local.getTimezoneOffset() * 60 * 1000);
    tai = new Date(utc.getTime() + (LeapSecondCount(utc) * 1000));
 
    document.Boxes.row2d.value = GetMjd1(tai) +
       "." + Fixed5(Math.floor(GetElapsed(utc) / 86400 * 1e5));

    //
    // Delay thread until next second trying to align the
    // display to within milliseconds of the PC clock.
    //

    var ms = local.getTime() % 1000;
    if (ms > 500) ms -= 1000;
    timerID = setTimeout("DisplayTime()", 1000 - ms);
    timerRunning = true;
}

function TimerThread () {
    if (timerRunning) {
        clearTimeout(timerID);
        timerRunning = false;
    }
    DisplayTime();
}
