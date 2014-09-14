# -*- coding: utf8 -*-

"""
Copyright (C) 2014 Andreas Würl

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

import itertools
import datetime
from injector import inject
import numpy as np

from ..util import next_element
from .base import Event, BuilderError
from .. import data


class ChannelWaveform(object):
    """
    class for building of waveforms within raw signal objects
    """
    fields_per_channel = 11

    def __init__(self):
        self.channel_number = None
        self.amplifier_version = None
        self.antenna = None
        self.gain = None
        self.values = 0
        self.start = None
        self.bits = 0
        self.shift = None
        self.conversion_gap = None
        self.conversion_time = None
        self.waveform = None

    def from_field_iterator(self, field):
        self.channel_number = int(next_element(field))
        self.amplifier_version = next_element(field)
        self.antenna = int(next_element(field))
        self.gain = next_element(field)
        self.values = int(next_element(field))
        self.start = int(next_element(field))
        self.bits = int(next_element(field))
        self.shift = int(next_element(field))
        self.conversion_gap = int(next_element(field))
        self.conversion_time = int(next_element(field))
        self.__extract_waveform_from_hex_string(next_element(field))
        return self

    def __extract_waveform_from_hex_string(self, waveform_hex_string):
        hex_character = iter(waveform_hex_string)
        self.waveform = np.zeros(self.values)
        bits_per_char = 4
        if self.bits == 0:
            self.bits = len(waveform_hex_string) // self.values * bits_per_char
        chars_per_sample = self.bits // bits_per_char
        value_offset = -(1 << (chars_per_sample * 4 - 1))

        for index in range(0, self.values):
            value_text = "".join(itertools.islice(hex_character, chars_per_sample))
            value = int(value_text, 16)
            self.waveform[index] = value + value_offset

    def build(self):
        return data.ChannelWaveform(
            self.channel_number,
            self.amplifier_version,
            self.antenna,
            self.gain,
            self.values,
            self.start,
            self.bits,
            self.shift,
            self.conversion_gap,
            self.conversion_time,
            self.waveform)


class RawWaveformEvent(Event):
    """
    class for building of raw signal objects
    """

    @inject(channel_builder=ChannelWaveform)
    def __init__(self, channel_builder):
        super(RawWaveformEvent, self).__init__()
        self.altitude = 0
        self.channels = []

        self.channel_builder = channel_builder

    def build(self):
        return data.RawWaveformEvent(
            self.timestamp,
            self.x_coord,
            self.y_coord,
            self.altitude,
            self.channels
        )

    def set_altitude(self, altitude):
        self.altitude = altitude
        return self

    def from_json(self, json_object):
        self.set_timestamp(json_object[0])
        self.set_x(json_object[1])
        self.set_y(json_object[2])
        self.set_altitude(json_object[3])
        if len(json_object[9]) > 1:
            self.set_y(json_object[9][1])

        return self

    def from_string(self, string):
        """ Construct strike from blitzortung.org text format data line """
        if string:
            try:
                field = iter(string.split(' '))
                self.set_timestamp(next_element(field) + ' ' + next_element(field))
                self.timestamp += datetime.timedelta(seconds=1)
                self.set_y(float(next_element(field)))
                self.set_x(float(next_element(field)))
                self.set_altitude(int(next_element(field)))

                self.channels = []
                while True:
                    try:
                        self.channel_builder.from_field_iterator(field)
                    except StopIteration:
                        break
                    self.channels.append(self.channel_builder.build())
            except ValueError as e:
                raise BuilderError(e, string)

        return self


