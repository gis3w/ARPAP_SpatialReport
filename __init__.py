# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ARPAP_SpatialReport
                                 A QGIS plugin
 ARPAP Spatial Report
                             -------------------
        begin                : 2014-11-20
        copyright            : (C) 2014 by Walter Lorenzetti GIS3W
        email                : lorenzetti@gis3w.it
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ARPAP_SpatialReport class from file ARPAP_SpatialReport.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .arpap_spatialreport import ARPAP_SpatialReport
    return ARPAP_SpatialReport(iface)
