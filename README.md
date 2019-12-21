# Python library for handling ISO 8601 date/time strings

## Overview

RFC 3339 is an Internet Standard defining textual format for dates and times on the Internet.
It uses a very rigid syntax using a 4-digit year, numeral months and 24-hour time,
e.g. "`2019-12-12T13:36:00Z`", intending to obsolete several past ad-hoc, hard-to-parse notions of dates/times
(e.g. RFC 822 Syntax "`Thu, 12 Dec 19 13:36:00 +0000`").

ISO 8601:2019 is an origin of that RFC, and is an international standard
defining various textual computer representation of dates and times.
Unlike the RFC, ISO 8601 allows broader varieties of date/time
representations. For example, all of "`2019-12-12`", "`20191212`",
"`2019-346`" (346th day within year), "`2019346`",
"`2019-W50-4`" (Thursday of the 50th week), or even "`2019W504`"
represent the same 12th of December.  For the time notation,
"`13:36:00`", "`13:36.0`", "`13.6`" and "`13,6`" all mean the same time 1 36 pm (note: 0.6 hours equals to 36 minutes).
Also, it allows to specify low-precision period of days,
e.g. "`2019-W50`" for 1 week, "`2019-12`" for 1 month, "`2019`" for 1 year or even "`20`" for 100 years.

The library provides parsing functions which accept all notions of
date/times defined in the ISO 8601:2019, including the above
examples.  It provides two variants of implementations:

 - `rfc3339.py`: a simple, compact version accepting the subset used in RFC 3339.
   For implementing most of the RFC-based Internet-based protocols, this version
   might be sufficient.  It is dedicated to public domain (CC0 License).

 - `iso8601.py`: a full-featured version accepting all currently-defined variants of
   format defined in the international standard.  It also provides information about
   the "precision" of specified inputs. Licensed with Apache Public License 2.0.

Both of these accept the notion of leap seconds (60th second)
gracefully, which many existing libraries may reject.

## Author and Copyright

Both variants are implemented by Yutaka OIWA <yutaka@oiwa.jp> in 2019.

The RFC 3339 variant is then put in public domain (or CC0 licensed).
The ISO 8601 version is also put under a liberal licensing term (Apache 2.0).

See th file LICENSE for more details.
