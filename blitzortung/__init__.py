# -*- coding: utf8 -*-
#-----------------------------------------------------------------------------
#   Copyright (c) 2011, Andreas Wuerl. All rights reserved.
#
#   See the LICENSE file for details.
#-----------------------------------------------------------------------------
"""
blitzortung python modules
"""
__version__ = '1.3.0'

#-----------------------------------------------------------------------------
#  Constants.
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

import builder
import cache
import calc
import config
import data
import dataimport
import db
import geom
import files
import types
import util


INJECTOR = injector.Injector(
    [builder.BuilderModule(), config.ConfigModule(), calc.CalcModule(), db.DbModule(), dataimport.DataImportModule()])

__all__ = [

    'builder.Stroke', 'builder.Station',

    'calc.ObjectCache'

    'calc.ThreePointSolution', 'calc.ThreePointSolver',

    'data.TimeIntervals', 'data.Timestamp', 'data.NanosecondTimestamp',  # data items

    'db.stroke', 'db.station', 'db.stationOffline', 'db.location',  # database access

    'Error', # custom exceptions

    'files.Raw', 'files.Data',

    'geom.Point',

    'types.Point',

    'util.Timer',

    'dataimport.StrokesBlitzortungDataProvider', 'dataimport.StrokesBlitzortungDataProvider',
]
