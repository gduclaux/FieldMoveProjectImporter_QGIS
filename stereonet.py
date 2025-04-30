# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Stereonet
                                 A QGIS plugin
 Displays a geologic stereonet of selected data
                             -------------------
        begin               : 2016-11-29
        copyright           : (C) 2016 by Daniel Childs
        email               : daniel@childsgeo.com
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
import os
from qgis.core import QgsProject
from math import asin,sin,degrees,radians,cos,tan,atan
import json


class StereonetDialog(QDialog):
    def __init__(self, plugin_dir, parent=None):
        super().__init__(parent)
        self.plugin_dir = plugin_dir
        self.setWindowTitle("F                                                                             t Importer")
        self.setWindowIcon(QIcon(os.path.join(plugin_dir, 'stereo.png')))
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        # Create main layout
        layout = QVBoxLayout()
        
        # Header
        header = QLabel()
        header.setPixmap(QPixmap(os.path.join(self.plugin_dir, 'stereo.png')).scaled(64, 64, Qt.KeepAspectRatio))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("""
        <h3>Stereonet Settings</h3>
        <p>Visualise selected planes and lines data from FieldMove geological data including:</p>
        <ul>
            <li>Select data you want to plot in QGIS Map</li>
            <li>Choose stereonet settings below</li>
            <li>Data are colored according to the Geologic Unit color</li>
        </ul>
        <p>Press Plot.</p>
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Project folder selection
        folder_layout = QVBoxLayout()
        folder_label = QLabel("<b>Select FieldMove Project Folder:</b>")
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Path to folder containing CSV files")
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
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_box.addWidget(plot_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)
        
        self.setLayout(layout)
    
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, 
            "Select FieldMove Project Folder", 
            "", 
            QFileDialog.ShowDirsOnly
        )
        if folder:
            self.folder_edit.setText(folder)
    
    def get_paths(self):
        return {
            'project_dir': self.folder_edit.text()
        }

class StereonetTool:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.menu = "&FieldMove Project Importer"

    def initGui(self):
        # Add toolbar button and menu item
        dir_path = os.path.dirname(__file__)
        self.action = QAction(QIcon(os.path.join(dir_path, "stereo.png")), u'Stereonet Tool', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.menu, self.action)

    def unload(self):
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu(self.menu, action)
        del self.action


    def run(self):
        dlg = StereonetDialog(self.plugin_dir, self.iface.mainWindow())
        if not dlg.exec_():  # User cancelled
            return
        
        stereoConfig={'showGtCircles':False,'showContours':True,'linPlanes':True,'roseDiagram':False}
        
        self.contourPlot(stereoConfig)

    def rose_diagram(self,strikes,title):
        #modified from: http://geologyandpython.com/structural_geology.html

        bin_edges = np.arange(-5, 366, 10)
        number_of_strikes, bin_edges = np.histogram(strikes, bin_edges)
        number_of_strikes[0] += number_of_strikes[-1]
        half = np.sum(np.split(number_of_strikes[:-1], 2), 0)
        two_halves = np.concatenate([half, half])
        fig = plt.figure(figsize=(8,8))

        ax = fig.add_subplot(111, projection='polar')

        ax.bar(np.deg2rad(np.arange(0, 360, 10)), two_halves, 
            width=np.deg2rad(10), bottom=0.0, color='.8', edgecolor='k')
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.arange(0, 360, 10), labels=np.arange(0, 360, 10))
        ax.set_rgrids(np.arange(1, two_halves.max() * 1.1, 2), angle=0, weight= 'black')
        ax.set_title(title)

        fig.tight_layout()
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

        stereoConfig={'showGtCircles':False,'showContours':True,'linPlanes':True,'roseDiagram':False}
        
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
            ax.grid(kind='equal_area_stereonet')
            if(stereoConfig['showContours']):
                ax.density_contour(strikes, dips, measurement='poles',cmap=cm.viridis,method='exponential_kamb',sigma=2.,linewidths =0.5)
            if(stereoConfig['showGtCircles'] and strikeExists != -1 and colorExists != -1):
                for color in enumerate(colors):
                    ax.plane(strikes[color[0]], dips[color[0]], color=color[1], linewidth=1)
            elif(stereoConfig['showGtCircles'] and strikeExists != -1):
                ax.plane(strikes, dips, 'k',linewidth=1)
            else:
                for color in enumerate(colors):
                    ax.pole(strikes[color[0]], dips[color[0]], color=color[1], markersize=3)

            ax.set_title(layer.name()+" [# "+str(len(iter))+"]",pad=24)
            plt.show()

        else:
            self.iface.messageBar().pushMessage("No data selected, or no structural data found: first select a layer with structural info, then select the points that you wish to plot", level=Qgis.Warning, duration=5)