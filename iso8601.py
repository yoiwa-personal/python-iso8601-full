# -*- python -*-
# Handling ISO 8601:2019 datetime string.
#
# https://github.com/yoiwa-personal/python-iso8601/
#
# Copyright 2019 Yutaka OIWA <yutaka@oiwa.jp>.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This modules handles rarely-used uncommon variations of date
# representation strings defined in ISO 8601:2019.
#
# See also rfc3339.py for simple, commonly-used subset of this format.
# It is licensed with CC0 (dedicated to public domain).

__all__ = ['parse_iso8601_date', 'parse_iso8601_time', 'parse_iso8601_datetime']

import re

try:
    from datetime import timezone
    _timezone_utc = timezone.utc
except ImportError:
    from rfc3339 import timezone, _timezone_utc

import datetime as datetime_
from datetime import datetime, date, time, timedelta
_zerodelta = timedelta(0)
_single_sec = timedelta(seconds=1)
_single_day = timedelta(days=1)

datepart = (r"""(?x)
                (?:(?P<EXT>-?)
                   (?:(?P<M>[01]\d)(?P=EXT)(?P<D>[0-3]\d)
                      |(?P<YD>[0-3]\d\d)
                      |[Ww](?P<W>[0-5]\d)(?:(?P=EXT)(?P<WD>[1-7]))?)
                 |-(?P<MO>[01]\d))""")

yearpart = r"""(?P<CY>\d\d)"""

centurypart_tmpl = r"""(?P<C>(?:[+-]\d{%d,}?)?\d\d)"""

date_regex_num = lambda n: re.compile("\A" + (centurypart_tmpl % n) +
                                      "(?:" + yearpart + "(?:" + datepart + ")?)?\Z")
date_regex = date_regex_num(0)
date_regexs = {}

def parse_date_to_tuple(s, digits_year_ext=4):
    if digits_year_ext <= 4:
        r = date_regex
    elif digits_year_ext in date_regexs:
        r = date_regexs[digits_year_ext]
    else:
        r = date_regexs[digits_year_ext] = date_regex_num(digits_year_ext - 4)
    m = r.match(s)
    if not m:
        raise ValueError("invalid date string")
    m = m.groupdict()
    if m["D"] is not None:
        return ("day", int(m["C"] + m["CY"]), int(m["M"]), int(m["D"]))
    elif m["YD"] is not None:
        return ("day-year", int(m["C"] + m["CY"]), int(m["YD"]))
    elif m["WD"] is not None:
        return ("day-week", int(m["C"] + m["CY"]), int(m["W"]), int(m["WD"]))
    elif m["W"] is not None:
        return ("week", int(m["C"] + m["CY"]), int(m["W"]))
    elif m["MO"] is not None:
        return ("month", int(m["C"] + m["CY"]), int(m["MO"]))
    elif m["CY"] is not None:
        return ("year", int(m["C"] + m["CY"]))
    elif m["C"] is not None:
        return ("century", int(m["C"]))
    else:
        return False

_get = lambda l, i, d: l[i] if len(l) > i else d

def date_tuple_to_start(m, digits_year_ext=4):
    if m[0] in ("day", "month", "year"):
        return date(m[1], _get(m, 2, 1), _get(m, 3, 1))
    elif m[0] == "day-year":
        return date(m[1], 1, 1) + timedelta(days=(m[2] - 1))
    elif m[0] in ("day-week", "week"):
        year = m[1]
        week = m[2]
        wday = _get(m, 3, 1)
        try:
            return datetime.fromisocalendar(year,week,wday)
        except AttributeError:
            day1 = date(m[1], 1, 1)
            wday1 = day1.isoweekday()
            delta = (1 - wday1) if wday1 <= 4 else (8 - wday1)
            delta += (week - 1) * 7 + (wday - 1)
            return day1 + timedelta(days=delta)
    elif m[0] == "century":
        # actually, it's hundred-year, not century (0-start)
        return date(m[1] * 100, 1, 1)
    else:
        raise AssertionError("should not happen: unknown type")

def parse_date_to_start(s, digits_year_ext=4):
    m = parse_date_to_tuple(s, digits_year_ext);
    return date_tuple_to_start(m, digits_year_ext=digits_year_ext)

def parse_date_to_start_duration(s, digits_year_ext=4):
    m = parse_date_to_tuple(s, digits_year_ext);
    day = date_tuple_to_start(m, digits_year_ext=digits_year_ext)
    if m[0] in ("day", "day-year", "day-week"):
        return day, _single_day
    elif m[0] == "week":
        return day, timedelta(days=7)
    elif m[0] == "month":
        m2 = day.month + 1
        day2 = (date(day.year, m2, 1) if m2 != 13
                else date(day.year + 1, 1, 1))
        return day, day2 - day
    elif m[0] == "year":
        day2 = date(day.year + 1, 1, 1)
        return day, day2 - day
    elif m[0] == "century":
        day2 = date(day.year + 100, 1, 1)
        return day, day2 - day
    else:
        raise AssertionError("should not happen: unknown type")

class parse_iso8601_date(date):
    """Parse a date string formatted in ISO 8601 syntax.

    An optional argument digits_year_ext specifies how many digits
    are expected for the extended year specification (prefixed by + or -).

    Returned value is an extended `date` object pointing to the start
    day of the input.  An additional property precision is set to a
    `timedelta` object specifying a duration of the specified calendar
    dates..

    """
    def __new__(self, s, digits_year_ext=4):
        d, p = parse_date_to_start_duration(s, digits_year_ext=digits_year_ext)
        o = super().__new__(self, d.year, d.month, d.day)
        o.precision = p
        return o
    def __init__(self, s, digits_year_ext=4):
        pass

time_regexp = re.compile(
           r'''(?x)\A(?P<H>\d\d)
                    (?:(?P<HF>[,.]\d+)
                      |(?P<EXT>:?)(?P<M>\d\d)
                       (?:(?P<MF>[,.]\d+)
                         |(?P=EXT)(?P<S>\d\d)(?P<SF>[,.]\d+)?)?)?
                    (?P<TZ>|[Zz]|(?P<TZSIGN>[-+])(?P<TZH>\d\d)((?::?)(?P<TZM>\d\d))?)?\Z''')

def _frac_to_spec(s):
    if not s:
        return 0, 1
    if s[0:1] not in ('.', ','):
        raise ValueError(s)
    s = s[1:]
    expo = len(s or "")
    return (int(s or "0"), 10 ** expo)

def parse_time_to_tuple(s):
    m = time_regexp.match(s)
    if not m:
        raise ValueError("invalid time spec")
    m = m.groupdict()

    # timezone
    if m['TZ'] == '':
        tz = None
    elif m['TZ'] in ('Z', 'z'):
        tz = _timezone_utc
    else:
        tzhour = m['TZH']
        tzminute = (m['TZM'] or "00")
        tzofs = timedelta(hours=int(tzhour), minutes=int(tzminute))
        if m['TZSIGN'] == '-': tzofs = -tzofs
        tz = timezone(tzofs)

    if m['S'] is not None:
        numer, denom = _frac_to_spec(m['SF'])
        return ("s", int(m['H']), int(m['M']), int(m['S']), numer, denom, 1, tz)
    elif m['M'] is not None:
        numer, denom = _frac_to_spec(m['MF'])
        return ("m", int(m['H']), int(m['M']), 0, numer, denom, 60, tz)
    elif m['H'] is not None:
        numer, denom = _frac_to_spec(m['HF'])
        return ("h", int(m['H']), 0, 0, numer, denom, 3600, tz)

def time_tuple_to_start_prec(t, leapsecond=0):
    (type, hour, minute, second, numer, denom, scale, tz) = t
    duration = timedelta(microseconds = 1000000.0 / denom * scale);
    if duration == _zerodelta: duration = timedelta.resolution
    if (hour == 24):
        if minute == second == numer == 0:
            return(time(23, 59, 59), _single_sec, duration)
    if (hour < 0 or minute < 0 or second < 0
        or hour >= 24 or minute >= 60 or second > 60 or
        numer < 0 or numer >= denom or denom < 0 or scale <= 0):
        raise ValueError
    delta = _zerodelta
    if second == 60: # leap second
        if leapsecond == -1:
            second = 59
        elif leapsecond == 0:
            numer = 0
        elif leapsecond == 1:
            pass
        else:
            raise LeapSecondValueError

    # adjust for fraction
    microsecond = 1000000 * numer * scale // denom
    if microsecond >= 1000000:
        second += microsecond // 1000000
        microsecond = microsecond % 1000000
    if second >= 60:
        minute += second // 60
        second = second % 60

    # adjust for overflow by 24:00 or --:--:60
    if (hour >= 24):
        minute += 60 * (hour - 23)
        hour = 23
    if (minute >= 60):
        second += 60 * (minute - 59)
        minute = 59
    if (second >= 60):
        delta = _single_sec * (second - 59)
        second = 59

    t = time(hour, minute, second, microsecond, tzinfo=tz)
    return (t, delta, duration)

def parse_time_to_start_prec(s, leapsecond=0):
    t = parse_time_to_tuple(s)
    return time_tuple_to_start_prec(t, leapsecond=leapsecond)

class parse_iso8601_time(time):
    """Parse a time-in-day string formatted in ISO 8601 syntax.

    An optional argument leapsecond specifies how the 60th second is
    treated:
      -1: the preceeding 59th second is repeated.
       0: the clock holds at the top of the next 0th second.
      +1: the next 0th second is repeated.
      "raise": raise a Value Error.

    Returned value is an `time` object by default with the following
    properties.

      delta: If with_delta is set to True, it is a `timedelta` object
             representing an extra duration overflown from the allowed
             time range.  

             It might happen when either "24:00:00" or "23:59:60.xxx"
             is specified.

             If with_delta is False (default), a ValueError is raised
             for such cases.

      precision: a `timedelta` object representing a width of thte
                 timerange specified in the input.
    """
    def __new__(self, s, leapsecond=0, with_delta=False):
        t, delta, duration = parse_time_to_start_prec(s, leapsecond=leapsecond)
        o = super().__new__(self, t.hour, t.minute, t.second, t.microsecond, tzinfo=t.tzinfo)
        o.delta = delta
        o.precision = duration
        return o

    def __init__(self, s, leapsecond=0, with_delta=False):
        if not with_delta:
            if self.delta != _zerodelta:
                raise ValueError("time overflow (24:00:00)")

datetime_sep_regexp = re.compile(r'\A(.+?)([Tt](.+))?\Z')

# TODO: consistency of extended/normal notations between components are not checked
def parse_iso8601_datetime(s, digits_year_ext=4, leapsecond=0):
    """Parse a date string formatted in ISO 8601 syntax.

    An optional argument digits_year_ext specifies how many digits
    are expected for the extended year specification (prefixed by + or -).

    An optional argument leapsecond specifies how the 60th second is
    treated:
      -1: the preceeding 59th second is repeated.
       0: the clock holds at the top of the next 0th second.
      +1: the next 0th second is repeated.
      "raise": raise a Value Error.

    Returned value is a pair of:

       * Either an `date` or `datetime` object representing the
         starting point of the specified time.

       * A `timedelta` object representing how long or how precise the
         specified time is.

    """
    match = datetime_sep_regexp.match(s)
    if match:
        d = parse_date_to_start_duration(match.group(1), digits_year_ext=digits_year_ext)
        date, duration = d
        if duration > _single_day:
            raise ValueError("not-a-single-day date with a specific time")
        t = parse_time_to_start_prec(match.group(3), leapsecond=leapsecond)
        if not t: return t
        time, delta, duration = t
        date_time = datetime.combine(date, time)
        date_time += delta
        return date_time, duration
    else:
        return parse_date_to_start_duration(s, digits_year_ext=digits_year_ext)
