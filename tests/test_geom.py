# -*- coding: utf8 -*-

"""
Copyright (C) 2011-2014 Andreas Würl

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

from unittest import TestCase
import datetime

from hamcrest import assert_that, is_, equal_to, close_to
import pyproj
import shapely.geometry

import blitzortung.geom
import blitzortung.types


class GeometryForTest(blitzortung.geom.Geometry):
    def __init__(self, srid=None):
        if srid:
            super(GeometryForTest, self).__init__(srid)
        else:
            super(GeometryForTest, self).__init__()

    def get_env(self):
        return None


class TestGeometry(TestCase):
    def setUp(self):
        self.geometry = GeometryForTest()

    def test_default_values(self):
        assert_that(self.geometry.get_srid(), is_(equal_to(blitzortung.geom.Geometry.DefaultSrid)))

    def test_set_srid(self):
        self.geometry.set_srid(1234)

        assert_that(self.geometry.get_srid(), is_(equal_to(1234)))

    def test_create_with_different_srid(self):
        self.geometry = GeometryForTest(1234)

        assert_that(self.geometry.get_srid(), is_(equal_to(1234)))


class TestEnvelope(TestCase):
    def setUp(self):
        self.envelope = blitzortung.geom.Envelope(-5, 4, -3, 2)

    def test_default_values(self):
        assert_that(self.envelope.get_srid(), is_(equal_to(blitzortung.geom.Geometry.DefaultSrid)))

    def test_custom_srid_value(self):
        self.envelope = blitzortung.geom.Envelope(-5, 4, -3, 2, 1234)
        assert_that(self.envelope.get_srid(), is_(equal_to(1234)))

    def test_get_envelope_coordinate_components(self):
        assert_that(self.envelope.get_x_min(), is_(equal_to(-5)))
        assert_that(self.envelope.get_x_max(), is_(equal_to(4)))
        assert_that(self.envelope.get_y_min(), is_(equal_to(-3)))
        assert_that(self.envelope.get_y_max(), is_(equal_to(2)))

    def test_get_envelope_parameters(self):
        assert_that(self.envelope.get_x_delta(), is_(equal_to(9)))
        assert_that(self.envelope.get_y_delta(), is_(equal_to(5)))

    def test_contains_point_inside_envelope(self):
        self.assertTrue(self.envelope.contains(blitzortung.types.Point(0, 0)))
        self.assertTrue(self.envelope.contains(blitzortung.types.Point(1, 1.5)))
        self.assertTrue(self.envelope.contains(blitzortung.types.Point(-1, -1.5)))

    def test_contains_point_on_border(self):
        self.assertTrue(self.envelope.contains(blitzortung.types.Point(0, -3)))
        self.assertTrue(self.envelope.contains(blitzortung.types.Point(0, 2)))
        self.assertTrue(self.envelope.contains(blitzortung.types.Point(-5, 0)))
        self.assertTrue(self.envelope.contains(blitzortung.types.Point(4, 0)))

    def test_does_not_contain_point_outside_border(self):
        self.assertFalse(self.envelope.contains(blitzortung.types.Point(0, -3.0001)))
        self.assertFalse(self.envelope.contains(blitzortung.types.Point(0, 2.0001)))
        self.assertFalse(self.envelope.contains(blitzortung.types.Point(-5.0001, 0)))
        self.assertFalse(self.envelope.contains(blitzortung.types.Point(4.0001, 0)))

    def test_get_env(self):
        expected_env = shapely.geometry.LinearRing([(-5, -3), (-5, 2), (4, 2), (4, -3)])
        self.assertTrue(expected_env.almost_equals(self.envelope.get_env()))

    def test_str(self):
        assert_that(repr(self.envelope), is_(equal_to('Envelope(x: -5.0000..4.0000, y: -3.0000..2.0000)')))


class TestGrid(TestCase):
    def setUp(self):
        self.grid = blitzortung.geom.Grid(-5, 4, -3, 2, 0.5, 1.25)

    def test_get_x_div(self):
        assert_that(self.grid.get_x_div(), is_(equal_to(0.5)))

    def test_get_y_div(self):
        assert_that(self.grid.get_y_div(), is_(equal_to(1.25)))

    def test_get_x_bin_count(self):
        assert_that(self.grid.get_x_bin_count(), is_(equal_to(18)))

    def test_get_y_bin_count(self):
        assert_that(self.grid.get_y_bin_count(), is_(equal_to(4)))

    def test_get_x_bin(self):
        assert_that(self.grid.get_x_bin(-5), is_(equal_to(-1)))
        assert_that(self.grid.get_x_bin(-4.9999), is_(equal_to(0)))
        assert_that(self.grid.get_x_bin(-4.5), is_(equal_to(0)))
        assert_that(self.grid.get_x_bin(-4.4999), is_(equal_to(1)))
        assert_that(self.grid.get_x_bin(4), is_(equal_to(17)))
        assert_that(self.grid.get_x_bin(4.0001), is_(equal_to(18)))

    def test_get_y_bin(self):
        assert_that(self.grid.get_y_bin(-3), is_(equal_to(-1)))
        assert_that(self.grid.get_y_bin(-2.9999), is_(equal_to(0)))
        assert_that(self.grid.get_y_bin(-1.7500), is_(equal_to(0)))
        assert_that(self.grid.get_y_bin(-1.7499), is_(equal_to(1)))
        assert_that(self.grid.get_y_bin(2), is_(equal_to(3)))
        assert_that(self.grid.get_y_bin(2.0001), is_(equal_to(4)))

    def test_get_x_center(self):
        assert_that(self.grid.get_x_center(0), is_(equal_to(-4.75)))
        assert_that(self.grid.get_x_center(17), is_(equal_to(3.75)))

    def test_get_y_center(self):
        assert_that(self.grid.get_y_center(0), is_(equal_to(-2.375)))
        assert_that(self.grid.get_y_center(3), is_(equal_to(1.375)))

    def test_repr(self):
        assert_that(repr(self.grid), is_(equal_to("Grid(x: -5.0000..4.0000 (0.5000), y: -3.0000..2.0000 (1.2500))")))


class TestGridFactory(TestCase):
    def setUp(self):
        self.base_proj = pyproj.Proj(init='epsg:4326')
        self.proj = pyproj.Proj(init='epsg:32633')
        self.grid_factory = blitzortung.geom.GridFactory(10, 11, 52, 53, self.proj)
        self.base_length = 5000

    def test_get_for_srid(self):
        grid = self.grid_factory.get_for(self.base_length)

        assert_that(grid.get_srid(), is_(4326))

    def test_grid_boundaries(self):
        grid = self.grid_factory.get_for(self.base_length)

        x_div = grid.get_x_div()
        y_div = grid.get_y_div()

        assert_that(grid.get_x_min(), is_(10))
        assert_that(grid.get_y_min(), is_(52))
        assert_that(grid.get_x_max(), is_(close_to(10.964855970781894, 1e-10)))
        assert_that(grid.get_y_max(), is_(close_to(52.99942586979069, 1e-10)))
        assert_that(x_div, is_(close_to(0.06891828362727814, 1e-10)))
        assert_that(y_div, is_(close_to(0.04759170808527102, 1e-10)))

        x_0, y_0 = pyproj.transform(self.base_proj, self.proj, 10.5, 52.5)
        x_1, y_1 = pyproj.transform(self.base_proj, self.proj, 10.5 + x_div, 52.5 + y_div)

        assert_that(x_1 - x_0, is_(close_to(self.base_length, 1e-4)))
        assert_that(y_1 - y_0, is_(close_to(self.base_length, 1e-4)))

    def test_get_for_cache(self):
        grid_1 = self.grid_factory.get_for(self.base_length)
        grid_2 = self.grid_factory.get_for(self.base_length)

        assert_that(grid_1, is_(grid_2))





class TestRasterElement(TestCase):
    def setUp(self):
        self.timestamp = datetime.datetime(2013, 9, 6, 21, 36, 0, 123456)
        self.raster_element = blitzortung.geom.GridElement(1234, self.timestamp)

    def test_get_count(self):
        assert_that(self.raster_element.get_count(), is_(equal_to(1234)))

    def test_get_timestamp(self):
        assert_that(self.raster_element.get_timestamp(), is_(equal_to(self.timestamp)))

    def test_comparison(self):
        other_raster_element = blitzortung.geom.GridElement(10, self.timestamp)

        assert_that(other_raster_element < self.raster_element)
        assert_that(self.raster_element > other_raster_element)

    def test_string_representation(self):
        assert_that(repr(self.raster_element), is_(equal_to("RasterElement(1234, 2013-09-06 21:36:00.123456)")))