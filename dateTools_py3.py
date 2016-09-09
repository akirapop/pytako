
#import math
#import time
from time import strftime, gmtime
import datetime

""" A note on dates as used in this module:

    Any time a date tuple is required or returned, the tuple will
    have (will be assumed to have, if the tuple is an input) the
    following fields:

          year,month,day,hour,minutes,seconds 
"""

class DateParseError(Exception):
    pass

#
# takes a date tuple (see above!) and returns a
# string containing the date in odb-style format:
#
# yyyymmddhhmmss
#
# Note that the seconds here are ignored -- The end
# of the date string returned is always "00"
#

# Define acceptable formats for date strings to be parsed by parse_date_string()
#  
# Note that all formats may also inclue a time in the form hh:mm  or hh:mm:ss!
#
#  The formats that are accepted:
#  'month day yyyy [hh:mm:ss]'
#  'mon day yyyy [hh:mm:ss]'
#  'month day yy [hh:mm:ss]'
#  'mon day yy [hh:mm:ss]'
#  '[1-12] day yyyy [hh:mm:ss]' (month given as a number)
#  '[1-12] day yy [hh:mm:ss]'   (month given as a number)
#
date_string_formats= ( "%B %d %Y", "%b %d %Y", "%B %d %y", 
                       "%b %d %y", "%m %d %Y", "%m %d %y")

time_string_formats= ( "%H:%M", "%H:%M:%S")

def dstring_to_datetime(dstr):
    """ Given a date string in one of the above formats, returns a datetime instance accordingly """

    if ":" in dstr:           ## A time is given in the string 

        def _formats():
            dformats=date_string_formats
            tformats=time_string_formats

            for dform in dformats:
                for tform in tformats:
                    yield "%s %s" % (dform, tform)
    else:
        def _formats():
            dformats=date_string_formats
            for fmt in dformats:
                yield fmt

    ## Try to parse the given (date) string using any of the formats listed
    ## above in date_string_formats. If they all fail, return None
    for f in _formats():
        try:
            return datetime.datetime.strptime(dstr, f)
        except ValueError:
            pass
    return None


def dstring_to_datetuple(dstr):
    """ Given a date string in some kind of "month day year [time:time:time]" format, returns a tuple """
    dtime=dstring_to_datetime(dstr)

    if dtime is None:
        raise DateParseError("Couldn't parse '%s'" % dstr)

    return (dtime.year, dtime.month, dtime.day, dtime.hour, dtime.minute, dtime.second)

def dstring_to_mjd(dstr):
    """ Given a date string in some kind of "month day year [time:time:time]" format, returns the mjd """

    dtime=dstring_to_datetuple(dstr)

    return atMJulian(dtime)

def odbStyleDate(dateTuple):
    year=dateTuple[0]

    if year < 999:
       year = year + 2000

    odbDate= "%4d%02d%02d%02d%02d00" % ( \
      int(year), int (dateTuple[1]), int (dateTuple[2]), int(dateTuple[3]), int(dateTuple[4]) )

    return odbDate

def thisYear():
    return gmtime()[0]

def today():
    return gmtime()[0], gmtime()[1], gmtime()[2], 0, 0, 0

def todayMjd():
    return atMJulian(today())

######################################################################################################

#  << atMJulian >>
#   Convert UT to Modified Julian Day.
#   Modified from the atFunctions.
#

# The input time tuple must have: [yr,mo,dy,hr,mn,sc]   <--- no milliseconds!
def atMJulian(time):

  if (time[1] > 2):
    y = float(time[0])
    m = float(time[1])
  else:
    y = float(time[0]-1)
    m = float(time[1]+12)

# d = time[2] + (time[3] + (time[4] + (time[5]+time[6]/1000)/60)/60)/24;
  d = float(time[2]) + (float(time[3]) + (float(time[4]) + float(time[5])/60)/60)/24;

  return ( int(y*365.25) - 678912.0 ) + int(y/400) - int(y/100) + int((m-2.0)*30.59) + d

# return ( int(y*365.25) - 678912.0 ) + int(y/400) - int(y/100) + int((m-2.0)*30.59) + d

########################################################################################

#  << atMJDate >>
#  Convert Modified Julian Day to UT.
#  Modified from atFunctions / dateTools.pl
#

def atMJDate(mjd):

  month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
  time2 = [0, 1, 1, 0, 0, 0, 0.0 ]
  time  = [0, 1, 1, 0, 0, 0 ]         # to be the final result -- BUT, it 
                                      # will be returned as a _tuple_

  time[0] = int(mjd*0.0027379093 + 1858.877)

  flag=1

  while flag == 1:
    time2[0] = time[0] + 1
    mjd0 = atMJulian( time )
    mjd2 = atMJulian( time2 )

    if mjd < mjd0: 
       time[0] -= 1
    elif mjd >= mjd2:
       time[0] += 1
    else:
       flag = 0


  month[2] = 28

  if  (0 == time[0]%4) and (0 == time[0]%400 or 0 != time[0]%100):
    month[2] = 29

  day = mjd - mjd0

# for($j=1; $day >= $month[$j]; $j++) { $day -= $month[$j]; }

  j=1
##
  while j<13:
     if day < month[j]:
         break
     day -= month[j]
     j = j + 1
##

  day += 1.0
  time[1] = j

  if day < 33.0:
    time[2] = int (day)
    day -= time[2];  day *= 24;  time[3] = int (day);
    day -= time[3];  day *= 60;  time[4] = int (day);
    day -= time[4];  day *= 60;  time[5] = int (day);
#   time[6] = (day - time[5])*1000   ## milli-seconds -- not needed

  return tuple(time)

######################################################################################################

#
# Given a date tuple ( year, month, day, hour, min, seconds ), 
# returns a string in the form: 'month dd, hh:mm'

def dateString(dateTuple):
  retVal=None
  try:
#    retVal=strftime( '%B %d, %H:%M', dateTuple + [0, 0, -1 ] )
     retVal=strftime( '%B %d, %H:%M', dateTuple + (0, 0, -1 ) )
  except ValueError:
     pass              ## yes, the doy number (the -1 above) is out-of-range. I don't care

  return retVal

######################################################################################################

def mjdToOdbstyleDate(mjd):
    return odbStyleDate(atMJDate(mjd))

def odbStyleDateStringToMjd(odbDate):
    dateTuple= [ int(odbDate[0:4]), int(odbDate[4:6]), int(odbDate[6:8]), int(odbDate[8:10]), int(odbDate[10:12]), 0 ]

    return atMJulian(dateTuple)

######################################################################################################

def mjdToDateString(mjd):
    return dateString(atMJDate(mjd))


######################################################################################################

def odbStyleToDateString(odbDate):
    dateTuple= ( int(odbDate[0:4]), int(odbDate[4:6]), int(odbDate[6:8]), int(odbDate[8:10]), int(odbDate[10:12]), 0 )

    return dateString(dateTuple)

######################################################################################################

#
# Given an mjd, returns a string in the form: 'dd month, hh:mm'

def mjdToDateString__deprecated(mjd):
  retVal=None
  try:
     retVal=strftime( '%B %d, %H:%M', atMJDate(mjd) + [0, 0, -1] )
  except ValueError:
     pass              ## yes, the doy number (the -1 above) is out-of-range. I don't care

  return retVal


mname_to_num= {   "1":1, "01":1, "jan":1, "january":1, 
                  "2":2, "02":2, "feb":2, "february":2, 
                  "3":3, "03":3, "mar":3, "march":3,
                  "4":4, "04":4, "apr":4, "april":4, 
                  "5":5, "05":5, "may":5, 
                  "6":6, "06":6, "jun":6, "june":6, 
                  "7":7, "07":7, "jul":7, "july":7,
                  "8":8, "08":8, "aug":8, "august":8, 
                  "9":9, "09":9, "sep":9, "september":9, 
                  "10":10, "oct":10, "october":10,
                  "11":11, "nov":11, "november":11, 
                  "12":12, "dec":12, "december":12 }

def monthName_to_number(mname):
    try:
        return mname_to_num[mname.lower()]
    except KeyError:
        print("** Unrecognized month name (%s)." % (mname))
        return -1


######################################################################################################
