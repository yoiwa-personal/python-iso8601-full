# -*- python -*-
# Handling RFC 3339 datetime string.

from rfc3339 import parse_RFC3339_datetime, _timezone_utc

import unittest

class TestRFC3339(unittest.TestCase):

    def do(self, f, v, e):
        with self.subTest(v=v):
            if isinstance(e, str):
                self.assertEqual(f(parse_RFC3339_datetime(v)), e)
            else:
                self.assertIn(f(parse_RFC3339_datetime(v)), e)

    def test_parse(self):
        # basic conversion
        self.do(str, "2019-12-12T20:50:53Z",
                         "2019-12-12 20:50:53+00:00")       # exact second
        self.do(str, "2019-12-12T20:50:53.1234Z",
                         "2019-12-12 20:50:53.123400+00:00") # arbitrary precision
        self.do(str, "2019-12-12T20:50:53.1234567890Z",
                         "2019-12-12 20:50:53.123456+00:00") # over-precise precision

        self.do(str, "2019-12-12T20:50:53.123456+09:00",
                         "2019-12-12 20:50:53.123456+09:00") # time zone
        self.do(str, "2019-12-12T20:50:53.123456+09:30",
                         "2019-12-12 20:50:53.123456+09:30") # fractional timezone
        self.do(str, "2019-12-12T20:50:53.123456-09:30",
                         "2019-12-12 20:50:53.123456-09:30") # negative frac. tz
        self.do(str, "2019-12-12T20:50:53.123456-09:00",
                         "2019-12-12 20:50:53.123456-09:00") # negative tz

    # timezone handling
    def test_timezone(self):
        to_utc = lambda d: str(d.astimezone(_timezone_utc))
        self.do(to_utc, "2019-12-12T09:00:00+09:00",
                         "2019-12-12 00:00:00+00:00")
        self.do(to_utc, "2019-12-11T14:30:00-09:30",
                         "2019-12-12 00:00:00+00:00") # negative fractional timezone

    def test_leap(self):
        # leap second rounding
        self.do(str, "2019-12-12T23:59:60.5Z",
                         "2019-12-13 00:00:00+00:00") # leap second rounded
        self.do(str, "2019-12-12T23:59:60-09:00",
                         "2019-12-13 00:00:00-09:00") # leap with timezone

    def test_tzname(self):
        # time zone names
        tzname = lambda d: str(d.tzname())
        self.do(tzname, "2019-12-12T23:59:60+09:00",
                         "UTC+09:00")
        self.do(tzname, "2019-12-12T23:59:60+09:30",
                         "UTC+09:30")
        self.do(tzname, "2019-12-12T23:59:60-09:30",
                         "UTC-09:30")
        self.do(tzname, "2019-12-12T23:59:60-09:00",
                         "UTC-09:00")
        self.do(tzname, "2019-12-12T23:59:60-00:00",
                         ["UTC", "UTC+00:00"]) # -0 -> +0
        self.do(tzname, "2019-12-12T23:59:60Z",
                         ["UTC", "UTC+00:00"])

if __name__ == '__main__':
    unittest.main()
