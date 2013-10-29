import unittest
import datetime
from hamcrest import assert_that, is_, equal_to
from nose.tools import raises

import blitzortung
import blitzortung.db.query


class IdIntervalTest(unittest.TestCase):
    def test_nothing_set(self):
        id_interval = blitzortung.db.query.IdInterval()

        self.assertEqual(id_interval.get_start(), None)
        self.assertEqual(id_interval.get_end(), None)
        self.assertEqual(str(id_interval), "[ : ]")

    def test_start_set(self):
        id_interval = blitzortung.db.query.IdInterval(1234)

        self.assertEqual(id_interval.get_start(), 1234)
        self.assertEqual(id_interval.get_end(), None)
        self.assertEqual(str(id_interval), "[1234 : ]")

    def test_start_and_stop_set(self):
        id_interval = blitzortung.db.query.IdInterval(1234, 5678)

        self.assertEqual(id_interval.get_start(), 1234)
        self.assertEqual(id_interval.get_end(), 5678)
        self.assertEqual(str(id_interval), "[1234 : 5678]")

    @raises(ValueError)
    def test_exception_when_start_is_not_integer(self):
        blitzortung.db.query.IdInterval("asdf")

    @raises(ValueError)
    def test_exception_when_end_is_not_integer(self):
        blitzortung.db.query.IdInterval(1, "asdf")


class TimeIntervalTest(unittest.TestCase):
    def test_nothing_set(self):
        id_interval = blitzortung.db.query.TimeInterval()

        self.assertEqual(id_interval.get_start(), None)
        self.assertEqual(id_interval.get_end(), None)
        self.assertEqual(str(id_interval), "[ : ]")

    def test_start_set(self):
        id_interval = blitzortung.db.query.TimeInterval(datetime.datetime(2010, 11, 20, 11, 30, 15))

        self.assertEqual(id_interval.get_start(), datetime.datetime(2010, 11, 20, 11, 30, 15))
        self.assertEqual(id_interval.get_end(), None)
        self.assertEqual(str(id_interval), "[2010-11-20 11:30:15 : ]")

    def test_start_and_stop_set(self):
        id_interval = blitzortung.db.query.TimeInterval(datetime.datetime(2010, 11, 20, 11, 30, 15),
                                                        datetime.datetime(2010, 12, 5, 23, 15, 59))

        self.assertEqual(id_interval.get_start(), datetime.datetime(2010, 11, 20, 11, 30, 15))
        self.assertEqual(id_interval.get_end(), datetime.datetime(2010, 12, 5, 23, 15, 59))
        self.assertEqual(str(id_interval), "[2010-11-20 11:30:15 : 2010-12-05 23:15:59]")

    @raises(ValueError)
    def test_exception_when_start_is_not_integer(self):
        blitzortung.db.query.TimeInterval("asdf")

    @raises(ValueError)
    def test_exception_when_end_is_not_integer(self):
        blitzortung.db.query.TimeInterval(datetime.datetime.utcnow(), "asdf")


class QueryTest(unittest.TestCase):
    def setUp(self):
        self.query = blitzortung.db.query.Query()
        self.query.set_table_name("foo")

    def test_initialization(self):
        self.assertEqual(str(self.query), "SELECT FROM foo")

    def test_set_table_name(self):
        self.assertEqual(str(self.query), "SELECT FROM foo")

    def test_set_columns(self):
        self.query.set_columns(['bar', 'baz'])
        self.assertEqual(str(self.query), "SELECT bar, baz FROM foo")

    def test_add_column(self):
        self.query.add_column('bar')
        self.assertEqual(str(self.query), "SELECT bar FROM foo")
        self.query.add_column('baz')
        self.assertEqual(str(self.query), "SELECT bar, baz FROM foo")

    def test_add_group_by(self):
        self.query.add_group_by('bar')
        self.assertEqual(str(self.query), "SELECT FROM foo GROUP BY bar")
        self.query.add_group_by('baz')
        self.assertEqual(str(self.query), "SELECT FROM foo GROUP BY bar, baz")

    def test_add_condition(self):
        self.query.add_condition("qux")
        self.assertEqual(str(self.query), "SELECT FROM foo WHERE qux")

        self.query.add_condition("quux")
        self.assertEqual(str(self.query), "SELECT FROM foo WHERE qux AND quux")

    def test_add_condition_with_parameters(self):
        self.query.add_condition("column LIKE '%(name)s'", {'name': '<name>'})
        self.assertEqual(str(self.query), "SELECT FROM foo WHERE column LIKE '<name>'")

        self.query.add_condition("other LIKE '%(type)s'", {'type': '<type>'})
        self.assertEqual(str(self.query), "SELECT FROM foo WHERE column LIKE '<name>' AND other LIKE '<type>'")

        assert_that(self.query.get_parameters(), is_(equal_to({'name': '<name>', 'type': '<type>'})))

    def test_add_order(self):
        self.query.add_order(blitzortung.db.query.Order("bar"))
        self.assertEqual(str(self.query), "SELECT FROM foo ORDER BY bar")

        self.query.add_order(blitzortung.db.query.Order("baz", True))
        self.assertEqual(str(self.query), "SELECT FROM foo ORDER BY bar, baz DESC")

    def test_set_limit(self):
        self.query.set_limit(blitzortung.db.query.Limit(10))
        self.assertEqual(str(self.query), "SELECT FROM foo LIMIT 10")
