# -*- coding: utf8 -*-

"""
Copyright (C) 2014 Andreas Würl

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

import re

from .base import Base, Event, BuilderError
from .. import data


class Station(Event):
    """
    class for building of station objects
    """

    station_parser = re.compile(r'station;([0-9]+)')
    user_parser = re.compile(r'user;([0-9]+)')
    city_parser = re.compile(r'city;"([^"]+)"')
    country_parser = re.compile(r'country;"([^"]+)"')
    position_parser = re.compile(r'pos;([-0-9\.]+);([-0-9\.]+);([-0-9\.]+)')
    status_parser = re.compile(r'status;"?([^ ]+)"?')
    board_parser = re.compile(r'board;"?([^ ]+)"?')
    last_signal_parser = re.compile(r'last_signal;"([-: 0-9]+)" ?')

    def __init__(self):
        super(Station, self).__init__()
        self.number = -1
        self.user = -1
        self.name = None
        self.country = None
        self.status = None
        self.board = None

    def set_number(self, number):
        self.number = number
        return self

    def set_user(self, user):
        self.user = user
        return self

    def set_name(self, name):
        self.name = name
        return self

    def set_country(self, country):
        self.country = country
        return self

    def set_board(self, board):
        self.board = board

    def set_status(self, status):
        self.status = status

    def from_line(self, line):
        try:
            self.set_number(int(self.station_parser.findall(line)[0]))
            self.set_user(int(self.user_parser.findall(line)[0]))
            self.set_name(self.city_parser.findall(line)[0])
            self.set_country(self.country_parser.findall(line)[0])
            pos = self.position_parser.findall(line)[0]
            self.set_x(float(pos[1]))
            self.set_y(float(pos[0]))
            self.set_board(self.board_parser.findall(line)[0])
            # self.set_status(self.status_parser.findall(line)[0])
            self.set_timestamp(self.last_signal_parser.findall(line)[0])
        except (KeyError, ValueError, IndexError) as e:
            raise BuilderError(e)
        return self

    def build(self):
        return data.Station(self.number, self.user, self.name, self.country,
                            self.x_coord, self.y_coord, self.timestamp, self.status,
                            self.board)


class StationOffline(Base):
    def __init__(self):
        super(StationOffline, self).__init__()
        self.id_value = -1
        self.number = -1
        self.begin = None
        self.end = None

    def set_id(self, id_value):
        self.id_value = id_value
        return self

    def set_number(self, number):
        self.number = number
        return self

    def set_begin(self, begin):
        self.begin = begin
        return self

    def set_end(self, end):
        self.end = end
        return self

    def build(self):
        return data.StationOffline(self.id_value, self.number, self.begin, self.end)


