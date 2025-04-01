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
"""

import os

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'fieldmove_project_importer_dialog_base.ui'))


class FieldMoveProjectImporterDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(FieldMoveProjectImporterDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
