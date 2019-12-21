# -*- python -*-
# Handling RFC 3339 datetime string.

from rfc3339 import parse_RFC3339_datetime, _timezone_utc
if __name__ == '__main__':
    def test(src, ans, f = None):
        d = parse_RFC3339_datetime(src)
        if f: d = f(d)
        s = str(d)
        if s == ans:
            print("  %-33s -> %s" % (src, s))
        else:
            print("! %-33s -> %s" % (src, s))
            print("  %33s -> %s" % ("should be:", ans))

    # basic conversion
    test("2019-12-12T20:50:53Z",             "2019-12-12 20:50:53+00:00")        # exact second
    test("2019-12-12T20:50:53.1234Z",        "2019-12-12 20:50:53.123400+00:00") # arbitrary precision
    test("2019-12-12T20:50:53.1234567890Z",  "2019-12-12 20:50:53.123456+00:00") # over-precise precision

    test("2019-12-12T20:50:53.123456+09:00", "2019-12-12 20:50:53.123456+09:00") # time zone
    test("2019-12-12T20:50:53.123456+09:30", "2019-12-12 20:50:53.123456+09:30") # fractional timezone
    test("2019-12-12T20:50:53.123456-09:30", "2019-12-12 20:50:53.123456-09:30") # negative frac. tz
    test("2019-12-12T20:50:53.123456-09:00", "2019-12-12 20:50:53.123456-09:00") # negative tz

    # timezone handling
    to_utc = lambda d: d.astimezone(_timezone_utc)
    test("2019-12-12T09:00:00+09:00", "2019-12-12 00:00:00+00:00", to_utc)
    test("2019-12-11T14:30:00-09:30", "2019-12-12 00:00:00+00:00", to_utc) # negative fractional timezone

    # leap second rounding
    test("2019-12-12T23:59:60.5Z",    "2019-12-13 00:00:00+00:00") # leap second rounded
    test("2019-12-12T23:59:60-09:00", "2019-12-13 00:00:00-09:00") # leap with timezone

    # time zone names
    tzname = lambda d: d.tzname()
    test("2019-12-12T23:59:60+09:00", "UTC+09:00", tzname)
    test("2019-12-12T23:59:60+09:30", "UTC+09:30", tzname)
    test("2019-12-12T23:59:60-09:30", "UTC-09:30", tzname)
    test("2019-12-12T23:59:60-09:00", "UTC-09:00", tzname)
    test("2019-12-12T23:59:60-00:00", "UTC+00:00", tzname) # -0 -> +0
    test("2019-12-12T23:59:60Z",      "UTC+00:00", tzname)
