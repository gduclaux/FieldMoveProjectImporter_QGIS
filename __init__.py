# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FieldMoveProjectImporter
                                 A QGIS plugin
 This plugins consolidate FieldMove project files into a QGIS project
 Generated using Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
 with massive help from deepseek. SVG symbols originals after Rob Holcombe: 
 https://www.holcombe.net.au/software/geoqsymbol.html
                              -------------------
        begin                : 2025-03-29
        git sha              : $Format:%H$
        copyright            : (C) 2025 by Guillaume Duclaux, Université Côte d'Azur
        email                : guillaume.duclaux@univ-cotedazur.fr
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
    """Load FieldMoveProjectImporter class from file FieldMoveProjectImporter.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .fieldmove_project_importer import FieldMoveProjectImporter
    return FieldMoveProjectImporter(iface)
