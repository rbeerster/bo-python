# -*- coding: utf8 -*-

import unittest
import datetime
import pytz
import numpy as np
import pandas as pd

import blitzortung


class TestBase(unittest.TestCase):
    def get_timestamp(self, time_string):
        return pd.Timestamp(np.datetime64(time_string), tz=pytz.UTC)


class BaseTest(TestBase):
    def setUp(self):
        self.builder = blitzortung.builder.Base()

    def assert_timestamp_base(self, timestamp):
        self.assertEqual(timestamp.day, 10)
        self.assertEqual(timestamp.month, 2)
        self.assertEqual(timestamp.year, 2012)
        self.assertEqual(timestamp.hour, 12)
        self.assertEqual(timestamp.minute, 56)
        self.assertEqual(timestamp.second, 18)

    def test_create_from_string(self):
        timestamp = self.builder.parse_timestamp("2012-02-10 12:56:18.096651423")

        self.assert_timestamp_base(timestamp)
        self.assertEqual(timestamp.microsecond, 96651)
        self.assertEqual(timestamp.nanosecond, 423)

    def test_create_from_millisecond_string(self):
        timestamp = self.builder.parse_timestamp("2012-02-10 12:56:18.096")

        self.assert_timestamp_base(timestamp)
        self.assertEqual(timestamp.microsecond, 96000)
        self.assertEqual(timestamp.nanosecond, 0)

    def test_create_from_string_wihtout_fractional_seconds(self):
        timestamp = self.builder.parse_timestamp("2012-02-10 12:56:18")

        self.assert_timestamp_base(timestamp)
        self.assertEqual(timestamp.microsecond, 0)
        self.assertEqual(timestamp.nanosecond, 0)

    def test_create_from_nanosecond_string(self):
        timestamp = self.builder.parse_timestamp("2012-02-10 12:56:18.123456789")

        self.assert_timestamp_base(timestamp)
        self.assertEqual(timestamp.microsecond, 123456)
        self.assertEqual(timestamp.nanosecond, 789)

        self.builder = blitzortung.builder.Base()
        timestamp = self.builder.parse_timestamp("2012-02-10 12:56:18.12345678")

        self.assert_timestamp_base(timestamp)
        self.assertEqual(timestamp.microsecond, 123456)
        self.assertEqual(timestamp.nanosecond, 780)

        self.builder = blitzortung.builder.Base()
        timestamp = self.builder.parse_timestamp("2012-02-10 12:56:18.1234567")

        self.assert_timestamp_base(timestamp)
        self.assertEqual(timestamp.microsecond, 123456)
        self.assertEqual(timestamp.nanosecond, 700)


class TimestampTest(unittest.TestCase):
    def setUp(self):
        self.builder = blitzortung.builder.Timestamp()

    def assert_correct_timestamp(self):
        self.assertEqual(self.builder.timestamp.day, 10)
        self.assertEqual(self.builder.timestamp.month, 2)
        self.assertEqual(self.builder.timestamp.year, 2012)
        self.assertEqual(self.builder.timestamp.hour, 12)
        self.assertEqual(self.builder.timestamp.minute, 56)
        self.assertEqual(self.builder.timestamp.second, 18)
        self.assertEqual(self.builder.timestamp.microsecond, 96651)

    def test_set_timestamp_from_string(self):
        self.builder.set_timestamp("2012-02-10 12:56:18.096651423")

        self.assert_correct_timestamp()
        self.assertEqual(423, self.builder.timestamp.nanosecond)
        self.assertEqual(pytz.UTC, self.builder.timestamp.tzinfo)

    def test_set_timestamp_from_datetime(self):
        self.builder.set_timestamp(datetime.datetime(2012, 2, 10, 12, 56, 18, 96651))

        self.assert_correct_timestamp()

    def test_set_timestamp_from_pandas_timestamp(self):
        timestamp = pd.Timestamp(datetime.datetime(2012, 2, 10, 12, 56, 18, 96651))
        timestamp = pd.Timestamp(timestamp.value + 423)

        self.builder.set_timestamp(timestamp)

        self.assert_correct_timestamp()
        self.assertEqual(self.builder.timestamp.nanosecond, 423)

    def test_set_timestamp_from_pandas_timestamp_with_ns_offset(self):
        timestamp = pd.Timestamp(datetime.datetime(2012, 2, 10, 12, 56, 18, 96651), tz='CET')

        self.builder.set_timestamp(timestamp, 423)

        self.assert_correct_timestamp()

        self.assertEqual(pytz.timezone('CET'), self.builder.timestamp.tzinfo)
        self.assertEqual(423, self.builder.timestamp.nanosecond)


class StrokeTest(TestBase):
    def setUp(self):
        self.builder = blitzortung.builder.Stroke()

    def test_default_values(self):
        self.assertEqual(self.builder.id_value, -1)
        self.assertEqual(self.builder.altitude, None)
        self.assertEqual(self.builder.participants, [])

    def test_set_id(self):
        self.builder.set_id(1234)
        self.assertEqual(self.builder.id_value, 1234)

        self.builder.set_x(0.0)
        self.builder.set_y(0.0)
        self.builder.set_timestamp(datetime.datetime.utcnow())
        self.builder.set_amplitude(1.0)
        self.builder.set_lateral_error(5.0)
        self.builder.set_type(-1)
        self.builder.set_station_count(10)

        self.assertEqual(self.builder.build().get_id(), 1234)

    def test_set_timestamp(self):
        timestamp = datetime.datetime.utcnow()
        self.builder.set_timestamp(timestamp)
        self.assertEqual(self.builder.timestamp, timestamp)

        self.builder.set_x(0.0)
        self.builder.set_y(0.0)
        self.builder.set_amplitude(1.0)
        self.builder.set_lateral_error(5.0)
        self.builder.set_type(-1)
        self.builder.set_station_count(10)

        self.assertEqual(self.builder.build().get_timestamp(), pd.Timestamp(timestamp))

    def test_build_stroke_from_data(self):
        stroke_data = {u'sta': [u'10', u'24',
                                u'226,529,391,233,145,398,425,533,701,336,336,515,434,392,439,283,674,573,559,364,111,43,582,594'],
                       u'pos': [u'44.162701', u'8.931001', u'0'], u'dev': u'20146', u'str': u'4.75',
                       'time': u'10:30:03.644038642', 'date': u'2013-08-08', u'typ': u'0'}

        stroke = self.builder.from_data(stroke_data).build()

        self.assertEqual(stroke.get_timestamp(), self.get_timestamp("2013-08-08 10:30:03.644038642Z"))
        self.assertEqual(stroke.get_x(), 8.931001)
        self.assertEqual(stroke.get_y(), 44.162701)
        self.assertEqual(stroke.get_amplitude(), 4.75)
        self.assertEqual(stroke.get_type(), 0)
        self.assertEqual(stroke.get_lateral_error(), 20146)
        self.assertEqual(stroke.get_station_count(), 24)


class StationTest(TestBase):
    def setUp(self):
        self.builder = blitzortung.builder.Station()

    def test_default_values(self):
        self.assertEqual(self.builder.number, -1)
        self.assertEqual(self.builder.user, -1)
        self.assertEqual(self.builder.name, None)
        self.assertEqual(self.builder.status, None)
        self.assertEqual(self.builder.board, None)

    def test_build_station_from_data(self):
        data = {u'status': u'0', u'city': u'Musterdörfl', u'last_signal': u'2012-02-10 14:39:47.410492569',
                u'last_stroke': u'0000-00-00',
                u'input_firmware': [u'1.9_/_May_13_201', u'1.9_/_May_13_201', u'', u'', u'', u''],
                u'distance': u'71.474273030335',
                u'strokes': [u'0', u'0', u'0', u'0', u'0', u'0', u'0', u'5879', u'0'], u'country': u'Germany',
                u'firmware': u'STM32F4', u'myblitz': u'N', u'pos': [u'49.5435', u'9.7314', u'130'],
                u'input_board': [u'5.7', u'5.7', u'', u'', u'', u''], u'signals': u'100', u'station': u'364',
                u'input_gain': [u'7.7', u'7.7', u'7.7', u'7.7', u'7.7', u'7.7'], u'board': [u'6.8'],
                u'input_antenna': [u'', u'', u'', u'', u'', u''], u'user': u'1'}

        station = self.builder.from_data(data).build()

        self.assertEqual(station.get_number(), 364)
        self.assertEqual(station.get_user(), 1)
        self.assertEqual(station.get_name(), u'Musterdörfl')
        self.assertEqual(station.get_country(), 'Germany')
        self.assertEqual(station.get_x(), 9.7314)
        self.assertEqual(station.get_y(), 49.5435)
        self.assertEqual(station.get_timestamp(), self.get_timestamp("2012-02-10T14:39:47.410492569Z"))


    def test_build_station_offline(self):
        self.builder.set_number(364)
        self.builder.set_user(10)
        self.builder.set_name('Musterdörfl')
        self.builder.set_country('Germany')
        self.builder.set_x(9.7314)
        self.builder.set_y(49.5435)
        self.builder.set_timestamp("2012-02-10 14:39:47.410492123")
        self.builder.set_status('A')
        self.builder.set_board('WT 5.20.3')

        station = self.builder.build()

        self.assertEqual(station.get_number(), 364)
        self.assertEqual(station.get_name(), 'Musterdörfl')
        self.assertEqual(station.get_country(), 'Germany')
        self.assertEqual(station.get_x(), 9.7314)
        self.assertEqual(station.get_y(), 49.5435)
        self.assertEqual(station.get_timestamp(), self.get_timestamp("2012-02-10T14:39:47.410492123Z"))
        self.assertEqual(station.get_status(), 'A')
        self.assertEqual(station.get_board(), 'WT 5.20.3')


class StationOffline(unittest.TestCase):
    def setUp(self):
        self.builder = blitzortung.builder.StationOffline()

    def test_default_values(self):
        self.assertEqual(self.builder.id_value, -1)
        self.assertEqual(self.builder.number, -1)
        self.assertEqual(self.builder.begin, None)
        self.assertEqual(self.builder.end, None)

    def test_build_station_offline(self):
        self.builder.set_id(364)
        self.builder.set_number(123)

        end = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        begin = end - datetime.timedelta(hours=1)
        self.builder.set_begin(begin)
        self.builder.set_end(end)

        station_offline = self.builder.build()

        self.assertEqual(station_offline.get_id(), 364)
        self.assertEqual(station_offline.get_number(), 123)
        self.assertEqual(station_offline.get_begin(), begin)
        self.assertEqual(station_offline.get_end(), end)


class RawEvent(unittest.TestCase):
    def setUp(self):
        self.builder = blitzortung.builder.RawEvent()

    def test_default_values(self):
        self.assertEqual(self.builder.x_coord, 0)
        self.assertEqual(self.builder.y_coord, 0)
        self.assertEqual(self.builder.timestamp, None)
        self.assertEqual(self.builder.altitude, 0)
        self.assertEqual(self.builder.amplitude, 0.0)
        self.assertEqual(self.builder.angle, 0.0)


    def test_build_raw_event(self):
        self.builder.set_x(11.0)
        self.builder.set_y(49.0)
        self.builder.set_altitude(530)

        raw_event = self.builder.build()

        self.assertEqual(raw_event.get_x(), 11.0)
        self.assertEqual(raw_event.get_y(), 49.0)
        self.assertEqual(raw_event.get_altitude(), 530)


class ExtEvent(unittest.TestCase):
    def setUp(self):
        self.builder = blitzortung.builder.ExtEvent()

    def test_default_values(self):
        self.assertEqual(self.builder.x_coord, 0)
        self.assertEqual(self.builder.y_coord, 0)
        self.assertEqual(self.builder.timestamp, None)
        self.assertEqual(self.builder.altitude, 0)
        self.assertEqual(self.builder.amplitude, 0.0)
        self.assertEqual(self.builder.angle, 0.0)
        self.assertEqual(self.builder.station_number, 0)

    def test_build_ext_event(self):
        self.builder.set_x(11.0)
        self.builder.set_y(49.0)
        self.builder.set_altitude(530)
        self.builder.set_station_number(39)

        ext_event = self.builder.build()

        self.assertEqual(ext_event.get_x(), 11.0)
        self.assertEqual(ext_event.get_y(), 49.0)
        self.assertEqual(ext_event.get_altitude(), 530)
        self.assertEqual(ext_event.get_station_number(), 39)

