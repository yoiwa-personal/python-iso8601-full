# -*- python -*-
# Handling RFC 3339 datetime string.
#
# A part of https://github.com/yoiwa-personal/python-iso8601-full/
#
# Written in 2019 by Yutaka OIWA <yutaka@oiwa.jp>.
#
# Dedicated under the Creative Commons Zero (CC0):
#
# To the extent possible under law, the author have dedicated all
# copyright and related and neghboring rights to the public domain
# worldwide. This software is provided WITHOUT ANY WARRANTY.
#
# You may obtain a copy of the legal code of the dedication at
#
#     http://creativecommons.org/publicdomain/zero/1.0/

"""Handling RFC 3339 datetime string.

The module parses date/time representation strings formatted according
to RFC 3339, which is a compact subset of ISO 8601:2019.

It provides the function 'parse_RFC3339_datetime'.
"""

__author__ = 'Yutaka OIWA <yutaka@oiwa.jp>'
__all__ = ['parse_RFC3339_datetime']

RFC3339_datetime_regexp=r'\A(\d\d\d\d)-(\d\d)-(\d\d)(?:[Tt](\d\d):(\d\d):(\d\d)(?:\.(\d+))?(|[Zz]|([-+])(\d\d):(\d\d)))?\Z'

import re, datetime
from datetime import timedelta

_zerodelta = timedelta(0)
_single_sec = timedelta(seconds=1)

try:
    from datetime import timezone
    _timezone_utc = timezone.utc
except ImportError:
    class timezone(datetime.tzinfo):
        def __init__(self, ofs):
            self.__offset = ofs
            self.__name = self._compute_name(ofs)
        def utcoffset(self, dt): return self.__offset
        def tzname(self, dt): return self.__name
        def dst(self, dt): return _zerodelta
        @classmethod
        def _compute_name(self, ofs):
            # minimal implementation!
            sg, s = 1, ofs.seconds + ofs.days * 86400
            if s < 0: (sg, s) = (-1, -s) # needed for -03:30 timezone
            s //= 60
            h, m = (s // 60, s % 60)
            return "UTC%+03d:%02d" % (h * sg, m)
    _timezone_utc = timezone(_zerodelta)

from datetime import date, datetime

class LeapSecondValueError(ValueError):
    pass

def parse_RFC3339_datetime(s, leapsecond=0):
    """Parse RFC3339 date-time string.

    Returns either a datetime.date or a datetime.datetime instance,
    depending on the input string (whether it contains a time part).

    Optional argument "leapsecond" specifies how the "60th second" 
    will be treated (example: "11:59:60.5" will be converted to):

      - -1: duplicates the 59th second twice (11:59:59:5).
      -  0: freezes at the next exact 0th second (12:00:00.0) (default).
      -  1: duplicates the next 0th second (12:00:00.5).
      - "raise": raises a ValueError.
    """

    match = re.match(RFC3339_datetime_regexp, s)
    if not match:
        raise ValueError("invalid RFC3339 datestring")
    (year, month, day, hour, minute, second, fraction, tz, tzsign, tzhour, tzminute) = match.groups()
    if hour == None:
        return date(int(year), int(month), int(day))
    if tz == '':
        tz = None
    elif tz == 'Z' or tz == 'z':
        tz = _timezone_utc
    else:
        tzofs = timedelta(hours=int(tzhour), minutes=int(tzminute))
        if tzsign == '-': tzofs = -tzofs
        tz = timezone(tzofs)
    fraction = (fraction or "") + "0000000"
    fraction = fraction[0:6] # + "." + fraction[6:]
    microsecond = int(float(fraction))
    adjust = False
    if (second == '60'):
        # 23:59:60Z allowed for leap sec.
        second = '59'
        if leapsecond == -1:
            pass # duplicates 59th sec.
        elif leapsecond == 0:
            adjust = _single_sec
            microsecond = 0 # holds at exact 0th sec.
        elif leapsecond == 1:
            adjust = _single_sec # duplicates 0th sec.
        else:
            raise LeapSecondValueError("leap second is given")

    r = datetime(int(year), int(month), int(day),
                 int(hour), int(minute), int(second),
                 microsecond, tz)
    if adjust: r += adjust
    return r

# Python 3.7's datetime.datetime.fromisoformat() almost works for
# RFC 3339's datestring.  Differences are:

#   - RFC 3339 allows arbitrary precision of second fractions.
#     Python's fromisoformat() only accepts either 3 or 6 digits.
#     Over-specified nanoseconds will be rounded down.

#   - RFC 3339 allows to specify the 60th second.
#     Python (and POSIX) assumes no leap seconds (it's OK, but)
#     and rejects the 60th second from being specified.
#     When a leap second is actually specified, we need to hide it
#     in some way.  The default choice satisfies two important
#     properties:

#      (1) The conversion is (non-strictly) monotonically
#          increasing.

#      (2) The duration from 00:00 to 23:59:60 has exactly 86400
#          seconds, which is another way of exploiting the "60th
#          second" notation.

#     However, it looses local "strictly increasing" behavior of
#     fractional seconds.

# It does not check whether the leap second is actually existing
# on the earth or not.
