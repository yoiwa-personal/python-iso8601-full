# -*- python -*-
# Handling ISO 8601:2019 datetime string.
# TESTS

from iso8601 import (parse_date_to_tuple, parse_iso8601_date,
                     parse_iso8601_time, parse_iso8601_datetime)

def test_dates():
    l = ["20191212",
         "2019-12-12",
         "2019-12",
         "2019",
         "20",
         "2019-346",
         "2019346",
         "+02019-12-12",
         "+020191212", # ambiguous: 2019-12-12 or 20191212-xx-xx
         #"-00051212",  # ambiguous: ~5-12-12 or ~51212-xx-xx
         "+02019-11",
         "+00210",
         "+0002", # ambiguous: 0002-xx-xx or 02xx-xx-xx
         "+02019-346",
         "+02010310", # ambiguous: 0201-03-10 or 02010-310

         "2019W504",
         "2019-W50-4",
         "2019W50",
         "2019-W50",

         "2004-W01-1",
         "2004-W01-7",

         "+02019W504",
         "+02019-W50-4",
         "+02019W50",
         "+02019-W50",
    ]

    for s in l:
        print(s, parse_date_to_tuple(s), parse_iso8601_date(s))
    for s in l:
        if s.startswith("+"):
            print(s, parse_iso8601_date(s, digits_year_ext=5))

def test_times():
    l = ["12:34:56",
         "12:34:56.78",
         "12:34:56.78901234",
         "12:34",
         "12:34.56",
         "12:34,5678",
         "12",
         "12.5",
         "24:00:00",
         "23:59:60Z",
    ]

    for s in l:
        print(s, parse_iso8601_time(s, with_delta=True))

def test_datetime1():
    l = [
         "2019-12-12T20:50:53Z",           
         "2019-12-12T20:50:53.1234Z",      
         "2019-12-12T20:50:53.1234567890Z",
         
         "2019-12-12T20:50:53.123456+09:00",
         "2019-12-12T20:50:53.123456+09:30",
         "2019-12-12T20:50:53.123456-09:30",
         "2019-12-12T20:50:53.123456-09:00",
         
         "2019-12-12T09:00:00+09:00",
         "2019-12-11T14:30:00-09:30",
         
         "2019-12-12T23:59:60.5Z",
         "2019-12-12T23:59:60-09:00",
         
         "2019-12-12T23:59:60+09:00",
         "2019-12-12T23:59:60+09:30",
         "2019-12-12T23:59:60-09:30",
         "2019-12-12T23:59:60-09:00",
         "2019-12-12T23:59:60-00:00",
         "2019-12-12T23:59:60Z",     
    ]
    for s in l:
        print(s, [str(s) for s in parse_iso8601_datetime(s)])

test_datetime1()
