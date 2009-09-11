from pytz import timezone, common_timezones
from datetime import datetime, timedelta
import MaKaC.common.info as info
import calendar
import time

def nowutc():
    return timezone('UTC').localize(datetime.utcnow())

def server2utc( date ):
    servertz = info.HelperMaKaCInfo.getMaKaCInfoInstance().getTimezone()
    return timezone(servertz).localize(date).astimezone(timezone('UTC'))

def date2utctimestamp( date ):
    """ Note by DavidMC: I believe this implementation is flawed. At least in my PC
        it is not correct. I think the result depends on the local time of the PC
        executing it. Use timezoneUtils.datetimeToUnixTime & timezoneUtils.unixTimeToDatetime instead.
        As a test, try the 13th February 2009 at 23:31:30 UTC, the timestamp should be 1234567890.
        With this function it's 1234564290 .
    """
    return int(time.mktime( date.utctimetuple() ))

def utctimestamp2date( ts ):
    """ Note by DavidMC: This function returns a naive datetime.
        You should use timezoneUtils.unixTimeToDatetime instead.
    """
    return datetime.utcfromtimestamp( ts )

def naive2local( naiveDateTime, localTimezone ):
    """ Extends naive datetimes with the specified timezone info (string),
    using DST or STD according to the date in question

    >>> from datetime import datetime
    >>> naive2local(datetime(2008,12,25,0,0,0), 'Europe/Zurich')
    datetime.datetime(2008, 12, 25, 1, 0, tzinfo=<DstTzInfo 'Europe/Zurich' CET+1:00:00 STD>)
    >>> naive2local(datetime(2008,8,25,0,0,0), 'Europe/Zurich')
    datetime.datetime(2008, 8, 25, 2, 0, tzinfo=<DstTzInfo 'Europe/Zurich' CEST+2:00:00 DST>)
    """
    
    utcDateTime = naiveDateTime.replace(microsecond=0, tzinfo=timezone('UTC'))
    localDateTime = utcDateTime.astimezone(timezone(localTimezone))
    return localDateTime

def setAdjustedDate(date, object = None, tz=None):
    # Localizes a date to the timezone tz
    # If tz is None, the timezone of the object is used
    if not tz:
        tz = object.getTimezone()
    if tz not in common_timezones:
        tz = 'UTC'
    return timezone(tz).localize(date)

def getAdjustedDate(date, object = None, tz=None):
    # Returns a date adjusted to the timezone tz
    # If tz is None, the timezone of the object is used
    if not tz:
        tz = object.getTimezone()
    if tz not in common_timezones:
        tz = 'UTC'
    return date.astimezone(timezone(tz))

def isToday(date, tz):
    """ Returns if a date is inside the current day (given a timezone)
        date: a timezone-aware datetime
    """
    today = getAdjustedDate(nowutc(), None, tz).date()
    day = getAdjustedDate(date, None, tz).date()
    return today == day

def isTomorrow(date, tz):
    """ Returns if a date is inside the day tomorrow (given a timezone)
        date: a timezone-aware datetime
    """
    tomorrow = getAdjustedDate(nowutc(), None, tz).date() + timedelta(days = 1)
    day = getAdjustedDate(date, None, tz)
    return tomorrow == day

def isYesterday(date, tz):
    """ Returns if a date is inside the day yesterday (given a timezone)
        date: a timezone-aware datetime
    """
    yesterday = getAdjustedDate(nowutc(), None, tz).date() - timedelta(days = 1)
    day = getAdjustedDate(date, None, tz)
    return yesterday == day

def isSameDay(date1, date2, tz):
    """ Returns if 2 datetimes occur the same day (given a timezone)
    """
    return getAdjustedDate(date1, None, tz).date() == getAdjustedDate(date2, None, tz).date()

def dayDifference(date1, date2, tz):
    """ Returns the difference in datetimes between 2 dates: date1 - date2 (given a timezone).
        For example the following 2 UTC dates: 25/07 21:00 and 26/07 03:00 may be on a different day in Europe,
        but they wouldn't be in Australia, for example
        date1, date2: timezone-aware datetimes.
    """ 
    day1 = getAdjustedDate(date1, None, tz).date()
    day2 = getAdjustedDate(date2, None, tz).date()
    return (day1 - day2).days
    
def datetimeToUnixTime(t):
    """ Gets a datetime object
        Returns a float with the number of seconds from the UNIX epoch
    """
    return calendar.timegm(t.utctimetuple())+t.microsecond/1000000.0

def datetimeToUnixTimeInt(t):
    """ Gets a datetime object
        Returns an int with the number of seconds from the UNIX epoch
    """
    return calendar.timegm(t.utctimetuple())

def unixTimeToDatetime(seconds, tz = 'UTC'):
    """ Gets a float (or an object able to be turned into a float) representing the seconds from the UNIX epoch,
        and a string representing the timezone (UTC) by default.
        Returns a datetime object
    """
    return datetime.fromtimestamp(float(seconds), timezone(tz))


class DisplayTZ:
    
    def __init__(self,aw,conf=None,useServerTZ=0):
        websession = aw.getSession()
        minfo =  info.HelperMaKaCInfo.getMaKaCInfoInstance()
        try:
            sessTimezone = websession.getVar("ActiveTimezone")
        except:
            #sessTimezone = minfo.getTimezone() 
            sessTimezone = "LOCAL"
        if sessTimezone == None:
            #sessTimezone = minfo.getTimezone() 
            sessTimezone = "LOCAL"
            websession.setVar("ActiveTimezone",sessTimezone)
        if sessTimezone == 'LOCAL':
            if useServerTZ == 0 and conf!=None:
                sessTimezone = conf.getTimezone()
            else:
                minfo =  info.HelperMaKaCInfo.getMaKaCInfoInstance()
                sessTimezone = minfo.getTimezone() 
        self._displayTZ = sessTimezone
        if self._displayTZ in ["",None]:
            self._displayTZ = minfo.getTimezone()
 
    def getDisplayTZ(self):
        return self._displayTZ


class SessionTZ:
    
    def __init__(self,user):
        try:
            displayMode = user.getDisplayTZMode()
        except:
            displayMode = 'MyTimezone'
        if displayMode == 'MyTimezone':
            try:
                tz = user.getTimezone()
            except:
                #tz = info.HelperMaKaCInfo.getMaKaCInfoInstance().getTimezone()
                tz = "LOCAL"
        else: 
            tz = "LOCAL"
        self._displayTZ = tz
    
    def getSessionTZ(self):
        return self._displayTZ
