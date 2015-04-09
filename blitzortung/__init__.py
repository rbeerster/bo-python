# -*- coding: utf8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2011, Andreas Wuerl. All rights reserved.
#
# See the LICENSE file for details.
# -----------------------------------------------------------------------------
"""
blitzortung python modules
"""
import logging

__version__ = '1.4.0'

# -----------------------------------------------------------------------------
# Constants.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
#   Custom exceptions.
#-----------------------------------------------------------------------------


class Error(Exception):
    """
    General Blitzortung error class.
    """
    pass


#-----------------------------------------------------------------------------
#   Public interface and exports.
#-----------------------------------------------------------------------------

import injector

from . import config
from . import geom
from . import db


INJECTOR = injector.Injector(
    [config.ConfigModule(), db.DbModule()])

__all__ = [

    'builder.Strike', 'builder.Station',

    'calc.ObjectCache'

    'calc.ThreePointSolution', 'calc.ThreePointSolver',

    'data.TimeIntervals', 'data.Timestamp', 'data.NanosecondTimestamp',  # data items

    'db.strike', 'db.station', 'db.stationOffline', 'db.location',  # database access

    'Error',  # custom exceptions

    'files.Raw', 'files.Data',

    'geom.Point',

    'types.Point',

    'util.Timer',

    'dataimport.StrikesBlitzortungDataProvider', 'dataimport.raw'
]

root_logger = logging.getLogger(__name__)
root_logger.setLevel(logging.WARN)


def set_parent_logger(logger):
    logger.parent = root_logger


def set_log_level(log_level):
    root_logger.setLevel(log_level)


def add_log_handler(log_handler):
    root_logger.addHandler(log_handler)


