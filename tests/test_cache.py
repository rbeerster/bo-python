# -*- coding: utf8 -*-

"""

   Copyright 2014-2016 Andreas Würl

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

from unittest import TestCase
from hamcrest import assert_that, is_, instance_of, is_not, same_instance, contains
import time
from mock import Mock

from blitzortung.cache import CacheEntry, ObjectCache


class TestCacheEntry(TestCase):
    def setUp(self):
        self.payload = Mock()
        self.cache_entry = CacheEntry(self.payload, time.time() + 10)

    def test_is_valid(self):
        assert_that(self.cache_entry.is_valid(time.time()))

        self.cache_entry = CacheEntry(self.payload, time.time() - 10)
        assert_that(not self.cache_entry.is_valid(time.time()))

    def test_get_payload(self):
        assert_that(self.cache_entry.get_payload(), is_(self.payload))

    def test_get_payload_increases_hit_count(self):
        self.cache_entry.get_payload()

        assert_that(self.cache_entry.get_hit_count(), is_(1))

    def test_get_hit_count(self):
        assert_that(self.cache_entry.get_hit_count(), is_(0))


class TestObject(object):
    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs

    def get_args(self):
        return self.__args

    def get_kwargs(self):
        return self.__kwargs


class TestObjectCache(TestCase):
    def setUp(self):
        self.cache = ObjectCache()

    def test_get_time_to_live_default_value(self):
        assert_that(self.cache.get_time_to_live(), is_(30))

    def test_get_time_to_live(self):
        self.cache = ObjectCache(ttl_seconds=60)
        assert_that(self.cache.get_time_to_live(), is_(60))

    def test_get(self):
        cached_object = self.cache.get(TestObject)
        assert_that(cached_object, instance_of(TestObject))

    def test_get_caches_objects(self):
        cached_object = self.cache.get(TestObject)
        assert_that(self.cache.get(TestObject), is_(same_instance(cached_object)))

    def test_clear_clears_cache(self):
        cached_object = self.cache.get(TestObject)

        self.cache.clear()
        assert_that(self.cache.get(TestObject), is_not(same_instance(cached_object)))

    def test_clear_resets_counters(self):
        self.cache.get(TestObject)
        self.cache.get(TestObject)

        self.cache.clear()

        assert_that(self.cache.get_ratio(), is_(0.0))

    def test_get_creates_new_object_if_original_object_is_expired(self):
        self.cache = ObjectCache(ttl_seconds=-10)
        cached_object = self.cache.get(TestObject)
        assert_that(self.cache.get(TestObject), is_not(same_instance(cached_object)))

    def test_get_different_objects_for_different_create_objects(self):
        class OtherTestObject(TestObject):
            pass

        cached_object = self.cache.get(TestObject)
        other_cached_object = self.cache.get(OtherTestObject)

        assert_that(cached_object, is_not(other_cached_object))

    def test_get_with_arg_is_called_with_same_arg(self):
        argument1 = object()
        argument2 = object()

        cached_object = self.cache.get(TestObject, argument1, argument2)

        assert_that(cached_object.get_args(), contains(argument1, argument2))
        assert_that(not cached_object.get_kwargs())

    def test_get_with_arg_is_cached(self):
        argument = object()

        cached_object = self.cache.get(TestObject, argument)
        assert_that(self.cache.get(TestObject, argument), is_(same_instance(cached_object)))

    def test_get_with_kwargs_is_called_with_same_kwargs(self):
        argument1 = object()
        argument2 = object()

        cached_object = self.cache.get(TestObject, foo=argument1, bar=argument2)

        assert_that(not cached_object.get_args())
        assert_that(cached_object.get_kwargs(), is_({'foo': argument1, 'bar': argument2}))

    def test_get_with_kwargs_is_cached(self):
        argument1 = object()
        argument2 = object()

        cached_object = self.cache.get(TestObject, foo=argument1, bar=argument2)
        assert_that(self.cache.get(TestObject, bar=argument2, foo=argument1), is_(same_instance(cached_object)))

    def test_get_ratio(self):
        assert_that(self.cache.get_ratio(), is_(0.0))

        self.cache.get(TestObject)
        assert_that(self.cache.get_ratio(), is_(0.0))

        self.cache.get(TestObject)
        assert_that(self.cache.get_ratio(), is_(0.5))