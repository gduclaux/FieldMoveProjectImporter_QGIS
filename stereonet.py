# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Stereonet Tool
                                 Uses a QGIS plugin
 Displays a geologic stereonet of selected data imported from FieldMove
                             -------------------
                             Original plugin
        begin               : 2016-11-29
        copyright           : (C) 2016 by Daniel Childs
        email               : daniel@childsgeo.com
                             -------------------
                             New developments
        begin               : 2025-04-29
        copyright           : (C) 2025 by Guillaume Duclaux
        email               : guillaume.duclaux@univ-cotedazur.fr
        
        git sha             : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                          *
 *   This program is free software; you can redistribute it and/or modify   *
 *   it under the terms of the GNU General Public License as published by   *
 *   the Free Software Foundation; either version 2 of the License, or      *
 *   (at your option) any later version.                                    *
 *                                                                          *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from .mplstereonet import *
from qgis.core import *
from qgis.gui import *
import os, csv
from qgis.core import QgsProject
from math import asin,sin,degrees,radians,cos,tan,atan
import json


class StereonetDialog(QDialog):
    
    def __init__(self, plugin_dir, iface, parent=None):
        super().__init__(parent)
        self.iface = iface  # This is the critical addition
        self.settings = QgsSettings()
        self.plugin_dir = plugin_dir
        self.setWindowTitle("FieldMove Importer Stereonet Viewer")
        #self.setWindowIcon(QIcon(os.path.join(plugin_dir, 'stereo.png')))
        self.setMinimumWidth(400)
        
        # Initialize with default values or saved values
        self.stereoConfig = self.load_settings()
        self.output_folder = self.settings.value("stereonet_plugin/output_folder", "")

        self.init_ui()
        self.restore_settings()
        
    
    def init_ui(self):
        # Create main layout
        layout = QVBoxLayout()
        
        # Header
        header = QLabel()
        header.setPixmap(QPixmap(os.path.join(self.plugin_dir, 'stereo.png')).scaled(48, 48, Qt.KeepAspectRatio))
        header.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(header)
        
        # Description
        desc = QLabel("""
        <h3>Stereonet Settings</h3>
        <p>Visualise selected planes and lines from imported FieldMove project:</p>
        <ul>
            <li>Select data (either planes or lines) you want to plot in QGIS Map</li>
            <li>Choose stereonet settings below</li>
            <li>(optional) Select output folder for exporting selection to CSV</li>
        </ul>
        <p>Data are coloured according to the Geologic Unit colour set in the original project. The stereonet is an equal area projection, lower hemisphere. </p>""")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        #boxes for options selection
         # Horizontal line separator
        line0 = QFrame()
        line0.setFrameShape(QFrame.HLine)
        line0.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line0)
        # Create checkboxes with separators

        # Option 1 - planes or lines: contouring
        desc=QLabel("""<h4>Contouring display option</h4>""")
        layout.addWidget(desc)
        self.contours_cb = QCheckBox("Show Contours")
        layout.addWidget(self.contours_cb)
        
        # Add horizontal line after Option 1
        line1 = QFrame()
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line1)
        desc=QLabel("""<h4>Planes display options</h4>""")
        layout.addWidget(desc)

        # Option 2 - Planes: plot great circles
        self.gt_circles_cb = QCheckBox("Show Great Circles")
        layout.addWidget(self.gt_circles_cb)
        
        # Option 3 - Planes: plot poles
        self.lin_planes_cb = QCheckBox("Show Poles")
        layout.addWidget(self.lin_planes_cb)
        
        # Add horizontal line after Option 3
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)
        desc=QLabel("""<h4>Rose diagram option</h4>
                    <p>if selected individual planes or lines, or their contours won't be displayed</p>""")
        layout.addWidget(desc)
        
        # Option 4 - Rose Diagram
        self.rose_diagram_cb = QCheckBox("Rose Diagram")
        layout.addWidget(self.rose_diagram_cb)
        
        # Add horizontal line after Option 3
        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine)
        line3.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line3)
        # Project folder selection
        folder_layout = QVBoxLayout()
        folder_label = QLabel("<h4>Select folder path for export:</h4>")
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Path to export CSV file")
        folder_btn = QPushButton("Browse...")
        folder_btn.clicked.connect(self.select_folder)
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(folder_btn)
        layout.addLayout(folder_layout)
        
        # Button box (using QHBoxLayout)
        btn_box = QHBoxLayout()  # Now properly imported
        plot_btn = QPushButton("Plot")
        plot_btn.clicked.connect(self.accept)
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_data)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_box.addWidget(plot_btn)
        btn_box.addWidget(export_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)
        
        self.setLayout(layout)
    
    def select_folder(self):
        """Handle folder selection and update both the UI and class variable"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select Output Folder", 
            "", 
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.folder_edit.setText(folder)
            self.output_folder = folder  # Update the class variable
    
    def get_configuration(self):
        """Returns the stereoConfig dictionary and output folder path"""
        self.stereoConfig = {
            'showGtCircles': self.gt_circles_cb.isChecked(),
            'showContours': self.contours_cb.isChecked(),
            'linPlanes': self.lin_planes_cb.isChecked(),
            'roseDiagram': self.rose_diagram_cb.isChecked()
        }
        
        return self.stereoConfig, self.output_folder
    
    def save_settings(self):
        """Save current settings to QgsSettings"""
        config, folder = self.get_configuration()
        
        # Save checkbox states
        self.settings.setValue("stereonet_plugin/showGtCircles", config['showGtCircles'])
        self.settings.setValue("stereonet_plugin/showContours", config['showContours'])
        self.settings.setValue("stereonet_plugin/linPlanes", config['linPlanes'])
        self.settings.setValue("stereonet_plugin/roseDiagram", config['roseDiagram'])
        
        # Save output folder
        self.settings.setValue("stereonet_plugin/output_folder", folder)
    
    def load_settings(self):
        """Load settings from QgsSettings"""
        return {
            'showGtCircles': self.settings.value("stereonet_plugin/showGtCircles", True, type=bool),
            'showContours': self.settings.value("stereonet_plugin/showContours", False, type=bool),
            'linPlanes': self.settings.value("stereonet_plugin/linPlanes", False, type=bool),
            'roseDiagram': self.settings.value("stereonet_plugin/roseDiagram", False, type=bool)
        }
    
    def restore_settings(self):
        """Restore checkbox states from saved settings"""
        self.gt_circles_cb.setChecked(self.stereoConfig['showGtCircles'])
        self.contours_cb.setChecked(self.stereoConfig['showContours'])
        self.lin_planes_cb.setChecked(self.stereoConfig['linPlanes'])
        self.rose_diagram_cb.setChecked(self.stereoConfig['roseDiagram'])

    def export_data(self):
        """Handle the export process"""
        # Get configuration first
        self.stereoConfig, _ = self.get_configuration()
        
        # Get the current folder path from the line edit
        self.output_folder = self.folder_edit.text()
        
        # Check if folder is selected
        if not self.output_folder:
            QMessageBox.warning(self, "Warning", "Please select an output folder first!")
            return
            
        # Get active layer
        layer = self.iface.activeLayer()
        if not layer:
            QMessageBox.warning(self, "Warning", "No active layer selected!")
            return
            
        # Check for selected features
        if layer.selectedFeatureCount() == 0:
            QMessageBox.warning(self, "Warning", "No features selected in the active layer!")
            return
            
        # Create output filename based on configuration
        filename = "stereonet_export"
        if layer.name().lower() in ['line', 'plane']:  # Case-insensitive check
            filename += f"_{layer.name().lower()}"
        filename += ".csv"
        
        output_path = os.path.join(self.output_folder, filename)
        
        # Export the data
        success = self.export_selected_to_csv(layer, output_path)
        
        if success:
            self.save_settings()
            # Don't close automatically - let user see success message
            # self.accept()  # Removed this line
    
    def accept(self):
        """Override accept to save settings before closing"""
        # Save settings and close
        self.save_settings()
        super().accept()
        
    def export_selected_to_csv(self, layer, output_path):
        """Export selected features to CSV with advanced controls"""
        try:
            features = layer.selectedFeatures()
            if not features:
                return False

            # Define fields to exclude
            exclude_fields = ['localityId','dataId','x','y','zone','horiz_precision','vert_precision','declination','color']  # Example fields to skip
            
            # Get only the fields we want to keep
            fields_to_export = [
                field.name() for field in layer.fields() 
                if field.name() not in exclude_fields
            ]
            
            # Add our custom geometry fields
            fields_to_export.extend(['latitude', 'longitude'])
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fields_to_export)
                writer.writeheader()
                
                for feature in features:
                    row_data = {}
                    
                    # Process regular fields
                    for field in fields_to_export:
                        if field in ['latitude', 'longitude','elevation']:
                            continue  # Handle separately
                        
                        value = feature[field]
                        
                        # Special formatting for datetime fields
                        if isinstance(value, QDateTime):
                            row_data[field] = value.toString('yyyy-MM-dd HH:mm:ss')
                        else:
                            row_data[field] = value
                    
                    # Add geometry coordinates (for point geometry)
                    geom = feature.geometry()
                    if not geom.isEmpty():
                        point = geom.asPoint()
                        row_data['latitude'] = point.y()  # Latitude
                        row_data['longitude'] = point.x()  # Longitude
                    
                    writer.writerow(row_data)
            
            self.iface.messageBar().pushMessage(
                "Success",
                f"Exported {len(features)} features to {output_path}",
                level=Qgis.Success,
                duration=5
            )
            return True
                            
        except Exception as e:
            self.iface.messageBar().pushMessage(
                "Error",
                f"Export failed: {str(e)}",
                level=Qgis.Critical,
                duration=5
            )
            return False

class StereonetTool:
    def __init__(self, iface, plugin_dir):
        self.iface = iface
        self.plugin_dir = plugin_dir
        self.actions = []

    def initGui(self):
        """Create stereonet menu entries and toolbar icons."""
        # Main stereonet action
        icon_path = os.path.join(self.plugin_dir, 'stereo.png')
        action = QAction(QIcon(icon_path), "Stereonet Viewer", self.iface.mainWindow())
        action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&FieldMove Project Importer", action)
        self.iface.addToolBarIcon(action)
        self.actions.append(action)
        
        return action


    def unload(self):
        """Remove all menu entries and toolbar icons."""
        for action in self.actions:
            self.iface.removePluginMenu("&FieldMove Project Importer", action)
            self.iface.removeToolBarIcon(action)
            action.triggered.disconnect()
        self.actions = []



    def run(self):
        dlg = StereonetDialog(self.plugin_dir, self.iface)
        if not dlg.exec_():  # User cancelled
            return
        else:
            stereoConfig, output_folder = dlg.get_configuration()
                
        self.contourPlot(stereoConfig)

    def rose_diagram(self,strikes,title):
        #modified from: http://geologyandpython.com/structural_geology.html

        bin_edges = np.arange(-5, 366, 10)
        number_of_strikes, bin_edges = np.histogram(strikes, bin_edges)
        number_of_strikes[0] += number_of_strikes[-1]
        half = np.sum(np.split(number_of_strikes[:-1], 2), 0)
        two_halves = np.concatenate([half, half])
        #fig = plt.figure(figsize=(6.5,4.8))
        fig, ax = subplots(projection='polar')

        #ax = fig.add_subplot(111, projection='polar')

        ax.bar(np.deg2rad(np.arange(0, 360, 10)), two_halves, 
            width=np.deg2rad(10), bottom=0.0, color='.8', edgecolor='k', linewidth='0.5')
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.arange(0, 360, 30), labels=[f"{angle:03d}\u00b0" for angle in np.arange(0, 360, 30)])
        ax.set_rgrids(np.arange(1, two_halves.max() * 1.1, max(1,two_halves.max()//3)), angle=180, fontsize=8)
        ax.set_title(title)
        ax.grid(True, linewidth='0.1', linestyle='--')

        #fig.tight_layout()
        plt.show()
        
    def contourPlot(self,stereoConfig):
        sname='strike'
        dname='dip'
        aname='plungeAzimuth'
        pname='plunge'
        color='color'

        strikes = list()
        dips = list()
        plunges=list()
        roseAzimuth = list()
        colors=list()

        self.iface.layerTreeView().selectedLayers()

        layers = list(QgsProject.instance().mapLayers().values())
        layers=self.iface.layerTreeView().selectedLayers()

        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:

                iter = layer.selectedFeatures()
                strikeExists = layer.fields().lookupField(sname)
                dipExists = layer.fields().lookupField(dname)
                azimuthExists = layer.fields().lookupField(aname)
                plungeExists = layer.fields().lookupField(pname)
                colorExists = layer.fields().lookupField(color)

                for feature in iter:
                    if colorExists != -1:
                        colors.append(feature[color])

                    if strikeExists != -1 and dipExists != -1:
                        strikes.append(feature[sname])
                        dips.append(feature[dname])

                    elif azimuthExists != -1 and plungeExists != -1:
                        strikes.append(feature[aname]+90)
                        dips.append(90-feature[pname])

                    if azimuthExists != -1 and stereoConfig['roseDiagram']:
                        roseAzimuth.append(feature[aname])
 
                    if strikeExists != -1 and stereoConfig['roseDiagram']:
                        roseAzimuth.append(feature[sname])
            else:
                continue

        strikes = [i for i in strikes if i != None]
        dips = [i for i in dips if i != None]
        plunges = [i for i in plunges if i != None]
        colors = [i for i in colors if i != None]

        if(len(roseAzimuth) != 0 and stereoConfig['roseDiagram']):
            self.rose_diagram(roseAzimuth,layer.name()+" [# "+str(len(iter))+"]")

        elif (len(strikes) != 0):
            fig, ax = subplots()
            ax.set_azimuth_ticks([0,30,60,90,120,150,180,210,240,270,300,330])
            ax.set_azimuth_ticklabels(['000\u00b0','030\u00b0','060\u00b0','090\u00b0','120\u00b0','150\u00b0','180\u00b0','210\u00b0','240\u00b0','270\u00b0','300\u00b0','330\u00b0'])
            ax.grid(kind='equal_area_stereonet',linewidth='0.2')
            if(stereoConfig['showContours']):
                ax.density_contourf(strikes, dips, measurement='poles',cmap=cm.binary,method='exponential_kamb',sigma=2.,vmin=2)
                ax.density_contour(strikes, dips, measurement='poles',cmap=cm.binary_r,method='exponential_kamb',sigma=2.,linewidths =0.5)

            if(stereoConfig['showGtCircles'] and stereoConfig['linPlanes'] and strikeExists != -1 and colorExists != -1):
                for color in enumerate(colors):
                    ax.plane(strikes[color[0]], dips[color[0]], color=color[1], linewidth=1)
                    ax.pole(strikes[color[0]], dips[color[0]], color=color[1], markersize=3)
            elif(stereoConfig['showGtCircles'] and strikeExists != -1 and colorExists != -1):
                for color in enumerate(colors):
                    ax.plane(strikes[color[0]], dips[color[0]], color=color[1], linewidth=1)
            elif(stereoConfig['showGtCircles'] and strikeExists != -1):
                ax.plane(strikes, dips, 'k',linewidth=1)
            elif(stereoConfig['linPlanes'] and strikeExists != -1 and colorExists != -1):
                for color in enumerate(colors):
                    ax.pole(strikes[color[0]], dips[color[0]], color=color[1], markersize=3)
            else:
                for color in enumerate(colors):
                    ax.pole(strikes[color[0]], dips[color[0]], color=color[1], markersize=3)

            ax.set_title(layer.name()+" [# "+str(len(iter))+"]",pad=24)
            plt.show()

        else:
            self.iface.messageBar().pushMessage("No data selected, or no structural data found: first select a layer with structural info, then select the points that you wish to plot", level=Qgis.Warning, duration=5)