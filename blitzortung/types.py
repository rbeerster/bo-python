# -*- coding: utf8 -*-

'''

@author Andreas Würl

'''

import datetime, pytz
import pyproj

class Point(object):
    '''
    Base class for Point like objects
    '''

    __geod = pyproj.Geod(ellps='WGS84', units='m')

    def __init__(self, x_coord, y_coord):
        self.x_coord = x_coord
        self.y_coord = y_coord

    def __invgeod(self, other):
        return Point.__geod.inv(self.x_coord, self.y_coord, other.x_coord, other.y_coord)

    def set_x(self, x_coord):
        self.x_coord = x_coord
        
    def get_x(self):
        ' returns x coordinate of point '
        return self.x_coord

    def set_y(self, y_coord):
        self.y_coord = y_coord
        
    def get_y(self):
        ' returns y coordinate of point '
        return self.y_coord

    def distance_to(self, other):
        return self.__invgeod(other)[2]

    def azimuth_to(self, other):
        return self.__invgeod(other)[0]

    def geodesic_relation_to(self, other):
        result = self.__invgeod(other)
        return result[2], result[0]

    def __str__(self):
        return "(%.4f, %.4f)" %(self.x_coord, self.y_coord)

class Timestamp(object):
    timeformat = '%Y-%m-%d %H:%M:%S'
    timeformat_fractional_seconds = timeformat + '.%f'
    timestamp_string_minimal_fractional_seconds_length = 20
    timestamp_string_microseconds_length = 26

    def __init__(self, timestamp_value):
        self.timestamp = None
        self.init_timestamp(timestamp_value)

    def init_timestamp(self, timestamp_value):
        if isinstance(timestamp_value, datetime.datetime):
            self.timestamp = timestamp_value
        elif isinstance(timestamp_value, str):
            if len(timestamp_value) > Timestamp.timestamp_string_minimal_fractional_seconds_length:
                timestamp_format = Timestamp.timeformat_fractional_seconds
                if len(timestamp_value) > Timestamp.timestamp_string_microseconds_length:
                    timestamp_value = timestamp_value[:self.timestamp_string_microseconds_length]
            else:
                timestamp_format = Timestamp.timeformat

            timestamp = datetime.datetime.strptime(timestamp_value, timestamp_format)
            self.timestamp = timestamp.replace(tzinfo=pytz.UTC)
        else:
            raise ValueError("init_timestamp can only be called with datetime or string")

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    def get_timestamp(self):
        return self.timestamp

    def difference(self, other):
        return self.timestamp - other.timestamp

class NanosecondTimestamp(Timestamp):

    def __init__(self, timestamp_value):
        super(NanosecondTimestamp, self).__init__(timestamp_value)
        self.nanoseconds = 0
        self.init_nanosecond_timestamp(timestamp_value)

    def init_nanosecond_timestamp(self, timestamp_value):
        if isinstance(timestamp_value, str):
            self.init_timestamp(timestamp_value)
            if len(timestamp_value) > Timestamp.timestamp_string_microseconds_length:
                nanoseconds_string = timestamp_value[self.timestamp_string_microseconds_length:self.timestamp_string_microseconds_length + 3]
                self.nanoseconds = int(nanoseconds_string.ljust(3).replace(' ', '0'))
            else:
                self.nanoseconds = 0

    def set_nanoseconds(self, nanoseconds):
        self.nanoseconds = nanoseconds

    def get_nanoseconds(self):
        return self.nanoseconds

    def nanoseconds_difference(self, other):
        return self.nanoseconds - other.nanoseconds  