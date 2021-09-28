# -*- python -*-
# Handling ISO 8601:2019 datetime string.
# TESTS

import iso8601
from iso8601 import (parse_ISO8601_date,
                     parse_ISO8601_time, parse_ISO8601_datetime)

import unittest

def td_us(td):
    if td is None: return None
    s = td.days * 86400 + td.seconds
    return s * 1000000 + td.microseconds
def td_s(td):
    if td is None: return None
    if td.microseconds == 0:
        return td.days * 86400 + td.seconds
    else:
        return (td.days * 86400 + td.seconds, td.microseconds)
def td_d(td):
    if td is None: return None
    if td.microseconds == 0 and td.seconds == 0:
        return td.days
    else:
        return (td.days, td.seconds, td.microseconds)

class Test_ISO8601(unittest.TestCase):
    def t_d(self, s, e=None, ex=None):
        if e: h = {"digits_year_ext": e}
        else: h = {}
        d = parse_ISO8601_datetime(s, **h)
        r = (str(d), td_d(d.precision))
        self.assertEqual(r, ex)

    def test_d001(s): s.t_d('20191212',          ex=('2019-12-12',     1))
    def test_d002(s): s.t_d('2019-12-12',        ex=('2019-12-12',     1))
    def test_d003(s): s.t_d('2019-12',           ex=('2019-12-01',    31))
    def test_d004(s): s.t_d('2019',              ex=('2019-01-01',   365))
    def test_d005(s): s.t_d('20',                ex=('2000-01-01', 36525))
    def test_d006(s): s.t_d('2019-346',          ex=('2019-12-12',     1))
    def test_d007(s): s.t_d('2019346',           ex=('2019-12-12',     1))

    def test_d008(s): s.t_d('+02019-12-12',      ex=('2019-12-12',     1))
    def test_d009(s): s.t_d('+02019-12-12', e=5, ex=('2019-12-12',     1))

    # ambiguous: 2019-12-12 or 20191212-xx-xx
    def test_d010(s): s.t_d('+020191212',        ex=('2019-12-12',     1))
    def test_d011(s): s.t_d('+020191212', e=5,   ex=('2019-12-12',     1))

    #"-00051212",  # ambiguous: ~5-12-12 or ~51212-xx-xx

    def test_d012(s): s.t_d('+02019-11',         ex=('2019-11-01',    30))
    def test_d013(s): s.t_d('+02019-11', e=5,    ex=('2019-11-01',    30))
    def test_d014(s): s.t_d('+00210',            ex=('0210-01-01',   365))
    def test_d015(s): s.t_d('+00210', e=5,       ex=('0210-01-01',   365))

    # ambiguous: 0002-xx-xx or 02xx-xx-xx
    def test_d016(s): s.t_d('+0002',             ex=('0002-01-01',   365))
    def test_d017(s): s.t_d('+0002', e=5,        ex=('0200-01-01', 36524)) ##

    def test_d018(s): s.t_d('+02019-346',        ex=('2019-12-12',     1))
    def test_d019(s): s.t_d('+02019-346', e=5,   ex=('2019-12-12',     1))

    # ambiguous: 0201-03-10 or 02010-310
    def test_d020(s): s.t_d('+02010310',         ex=('0201-03-10',     1))
    def test_d021(s): s.t_d('+02010310', e=5,    ex=('2010-11-06',     1)) ##

    def test_d022(s): s.t_d('2019W504',          ex=('2019-12-12',     1))
    def test_d023(s): s.t_d('2019-W50-4',        ex=('2019-12-12',     1))
    def test_d024(s): s.t_d('2019W50',           ex=('2019-12-09',     7))
    def test_d025(s): s.t_d('2019-W50',          ex=('2019-12-09',     7))
    def test_d026(s): s.t_d('2004-W01-1',        ex=('2003-12-29',     1))
    def test_d027(s): s.t_d('2004-W01-7',        ex=('2004-01-04',     1))
    def test_d028(s): s.t_d('+02019W504',        ex=('2019-12-12',     1))
    def test_d029(s): s.t_d('+02019W504', e=5,   ex=('2019-12-12',     1))
    def test_d030(s): s.t_d('+02019-W50-4',      ex=('2019-12-12',     1))
    def test_d031(s): s.t_d('+02019-W50-4', e=5, ex=('2019-12-12',     1))
    def test_d032(s): s.t_d('+02019W50',         ex=('2019-12-09',     7))
    def test_d033(s): s.t_d('+02019W50', e=5,    ex=('2019-12-09',     7))
    def test_d034(s): s.t_d('+02019-W50',        ex=('2019-12-09',     7))
    def test_d035(s): s.t_d('+02019-W50', e=5,   ex=('2019-12-09',     7))

    def t_t(self, s, dt=True, lp=0, ex=None):
        p = parse_ISO8601_time(s, with_delta=dt, leapsecond=lp)
        l = None if p.leap is None else p.leap.total_seconds()
        r = str(p), td_s(p.delta), td_s(p.leap), td_s(p.precision)
        self.assertEqual(r, ex)

    def test_t001(s): s.t_t('12:34:56',          ex=('12:34:56',        0, None, 1))
    def test_t002(s): s.t_t('12:34:56.78',       ex=('12:34:56.780000', 0, None, (0, 10000)))
    def test_t003(s): s.t_t('12:34:56.78901234', ex=('12:34:56.789012', 0, None, (0, 1)))
    def test_t004(s): s.t_t('12:34',             ex=('12:34:00', 0, None, 60 ))
    def test_t005(s): s.t_t('12:34.56',          ex=('12:34:33.600000', 0, None, (0, 600000)))
    def test_t006(s): s.t_t('12:34,5678',        ex=('12:34:34.068000', 0, None, (0, 6000)))
    def test_t007(s): s.t_t('12',                ex=('12:00:00', 0, None, 3600))
    def test_t008(s): s.t_t('12.5',              ex=('12:30:00', 0, None, 360))
    def test_t009(s): s.t_t('24:00:00',          ex=('23:59:59', 1, None, 1))
    def test_t010(s): s.t_t('23:59:60Z',         ex=('23:59:59+00:00', 1, 0, 1))
    def test_t011(s): s.t_t('08:59:60Z',         ex=('09:00:00+00:00', 0, 0, 1))

    def test_t012(s): s.t_t('23:59:60Z', lp=-1, ex=('23:59:59+00:00', 0, 1, 1))
    def test_t013(s): s.t_t('08:59:60Z', lp=-1, ex=('08:59:59+00:00', 0, 1, 1))

    def t_dt(self, s, ex):
        p = parse_ISO8601_datetime(s)
        self.assertEqual((str(p), td_us(p.leap), td_us(p.precision)), ex)

    def test_dt01(s): s.t_dt('2019-12-12T20:50:53Z',             ('2019-12-12 20:50:53+00:00', None, 1000000))
    def test_dt02(s): s.t_dt('2019-12-12T20:50:53.1234Z',        ('2019-12-12 20:50:53.123400+00:00', None, 100))
    def test_dt03(s): s.t_dt('2019-12-12T20:50:53.1234567890Z',  ('2019-12-12 20:50:53.123456+00:00', None, 1))
    def test_dt04(s): s.t_dt('2019-12-12T20:50:53.123456+09:00', ('2019-12-12 20:50:53.123456+09:00', None, 1))
    def test_dt05(s): s.t_dt('2019-12-12T20:50:53.123456+09:30', ('2019-12-12 20:50:53.123456+09:30', None, 1))
    def test_dt06(s): s.t_dt('2019-12-12T20:50:53.123456-09:30', ('2019-12-12 20:50:53.123456-09:30', None, 1))
    def test_dt07(s): s.t_dt('2019-12-12T20:50:53.123456-09:00', ('2019-12-12 20:50:53.123456-09:00', None, 1))
    def test_dt08(s): s.t_dt('2019-12-12T09:00:00+09:00',        ('2019-12-12 09:00:00+09:00', None, 1000000))
    def test_dt09(s): s.t_dt('2019-12-11T14:30:00-09:30',        ('2019-12-11 14:30:00-09:30', None, 1000000))
    def test_dt10(s): s.t_dt('2019-12-12T23:59:60.5Z',           ('2019-12-13 00:00:00+00:00', 500000, 100000))
    def test_dt11(s): s.t_dt('2019-12-12T23:59:60-09:00',        ('2019-12-13 00:00:00-09:00', 0, 1000000))
    def test_dt12(s): s.t_dt('2019-12-12T23:59:60+09:00',        ('2019-12-13 00:00:00+09:00', 0, 1000000))
    def test_dt13(s): s.t_dt('2019-12-12T23:59:60+09:30',        ('2019-12-13 00:00:00+09:30', 0, 1000000))
    def test_dt14(s): s.t_dt('2019-12-12T23:59:60-09:30',        ('2019-12-13 00:00:00-09:30', 0, 1000000))
    def test_dt15(s): s.t_dt('2019-12-12T23:59:60-09:00',        ('2019-12-13 00:00:00-09:00', 0, 1000000))
    def test_dt16(s): s.t_dt('2019-12-12T23:59:60-00:00',        ('2019-12-13 00:00:00+00:00', 0, 1000000))
    def test_dt17(s): s.t_dt('2019-12-12T23:59:60Z',             ('2019-12-13 00:00:00+00:00', 0, 1000000))

unittest.main()
