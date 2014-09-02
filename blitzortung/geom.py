# -*- coding: utf8 -*-

"""
Copyright (C) 2010-2014 Andreas Würl

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

import math
from abc import ABCMeta, abstractmethod
import pyproj

import shapely.geometry

import numpy


class Geometry(object):
    """
    abstract base class for geometries
    """

    __metaclass__ = ABCMeta

    DefaultSrid = 4326

    def __init__(self, srid=DefaultSrid):
        self.srid = srid

    def get_srid(self):
        return self.srid

    def set_srid(self, srid):
        self.srid = srid

    @abstractmethod
    def get_env(self):
        pass


class Envelope(Geometry):
    """
    definition of a coordinate envelope
    """

    def __init__(self, x_min, x_max, y_min, y_max, srid=Geometry.DefaultSrid):
        super(Envelope, self).__init__(srid)
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def get_x_min(self):
        return self.x_min

    def get_x_max(self):
        return self.x_max

    def get_y_min(self):
        return self.y_min

    def get_y_max(self):
        return self.y_max

    def get_y_delta(self):
        return abs(self.y_max - self.y_min)

    def get_x_delta(self):
        return abs(self.x_max - self.x_min)

    def contains(self, point):
        return (point.get_x() >= self.x_min) and \
               (point.get_x() <= self.x_max) and \
               (point.get_y() >= self.y_min) and \
               (point.get_y() <= self.y_max)

    def get_env(self):
        return shapely.geometry.LinearRing(
            [(self.x_min, self.y_min), (self.x_min, self.y_max), (self.x_max, self.y_max), (self.x_max, self.y_min)])

    def __repr__(self):
        return 'Envelope(x: %.4f..%.4f, y: %.4f..%.4f)' % (
            self.x_min, self.x_max, self.y_min, self.y_max)


class Grid(Envelope):
    """ grid characteristics"""

    def __init__(self, x_min, x_max, y_min, y_max, x_div, y_div, srid=Geometry.DefaultSrid):
        super(Grid, self).__init__(x_min, x_max, y_min, y_max, srid)
        self.x_div = x_div
        self.y_div = y_div
        self.x_bin_count = None
        self.y_bin_count = None

    def get_x_div(self):
        return self.x_div

    def get_y_div(self):
        return self.y_div

    def get_x_bin(self, x_pos):
        return int(math.ceil(float(x_pos - self.x_min) / self.x_div)) - 1

    def get_y_bin(self, y_pos):
        return int(math.ceil(float(y_pos - self.y_min) / self.y_div)) - 1

    def get_x_bin_count(self):
        if not self.x_bin_count:
            self.x_bin_count = self.get_x_bin(self.x_max) + 1
        return self.x_bin_count

    def get_y_bin_count(self):
        if not self.y_bin_count:
            self.y_bin_count = self.get_y_bin(self.y_max) + 1
        return self.y_bin_count

    def get_x_center(self, cell_index):
        return self.x_min + (cell_index + 0.5) * self.x_div

    def get_y_center(self, row_index):
        return self.y_min + (row_index + 0.5) * self.y_div

    def __repr__(self):
        return 'Grid(x: %.4f..%.4f (%.4f), y: %.4f..%.4f (%.4f))' % (
            self.get_x_min(), self.get_x_max(), self.get_x_div(),
            self.get_y_min(), self.get_y_max(), self.get_y_div())


class GridFactory(object):
    WGS84 = pyproj.Proj(init='epsg:4326')

    def __init__(self, min_lon, max_lon, min_lat, max_lat, coord_sys):
        self.min_lon = min_lon
        self.max_lon = max_lon
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.coord_sys = coord_sys

        self.grid_data = {}

    @staticmethod
    def fix_max(minimum, maximum, delta):
        return minimum + math.floor((maximum - minimum) / delta) * delta

    def get_for(self, base_length):
        if base_length not in self.grid_data:
            ref_lon = (self.min_lon + self.max_lon) / 2.0
            ref_lat = (self.min_lat + self.max_lat) / 2.0

            utm_x, utm_y = pyproj.transform(self.WGS84, self.coord_sys, ref_lon, ref_lat)
            lon_d, lat_d = pyproj.transform(self.coord_sys, self.WGS84, utm_x + base_length, utm_y + base_length)

            delta_lon = lon_d - ref_lon
            delta_lat = lat_d - ref_lat

            max_lon = self.fix_max(self.min_lon, self.max_lon, delta_lon)
            max_lat = self.fix_max(self.min_lat, self.max_lat, delta_lat)

            self.grid_data[base_length] = Grid(self.min_lon, max_lon, self.min_lat, max_lat,
                                               delta_lon, delta_lat,
                                               Geometry.DefaultSrid)

        return self.grid_data[base_length]


class GridElement(object):
    """
    raster data entry
    """

    def __init__(self, count, timestamp):
        self.count = count
        self.timestamp = timestamp

    def __gt__(self, other):
        return self.count > other.count

    def get_count(self):
        return self.count

    def get_timestamp(self):
        return self.timestamp

    def __str__(self):
        if self.timestamp is None:
            return str(self.count)

    def __repr__(self):
        return "RasterElement(%d, %s)" % (self.count, str(self.timestamp))
