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
import csv
from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                                QPushButton, QFileDialog, QMessageBox,
                                QAction, QFileDialog, QMessageBox)
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtCore import QVariant, Qt
from qgis.PyQt.QtGui import QColor  
from qgis.core import (
    QgsApplication,
    QgsVectorLayer,
    QgsField,
    QgsFields,
    QgsFeature,
    QgsGeometry,
    QgsPoint,
    QgsPointXY,
    QgsMarkerSymbol,
    QgsMessageLog,
    QgsSingleSymbolRenderer,
    QgsVectorFileWriter,
    QgsProject,
    QgsRasterLayer,
    QgsContrastEnhancement,
    QgsRuleBasedRenderer,
    QgsSettings,
    QgsSymbolLayer,
    QgsProperty,
    QgsSvgMarkerSymbolLayer
)


class FieldMoveImportDialog(QDialog):
    def __init__(self, plugin_dir, parent=None):
        super().__init__(parent)
        self.plugin_dir = plugin_dir
        self.setWindowTitle("FieldMove Project Importer")
        self.setWindowIcon(QIcon(os.path.join(plugin_dir, 'icon.png')))
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        # Create main layout
        layout = QVBoxLayout()
        
        # Header
        header = QLabel()
        header.setPixmap(QPixmap(os.path.join(self.plugin_dir, 'icon.png')).scaled(64, 64, Qt.KeepAspectRatio))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Description
        desc = QLabel("""
        <h3>FieldMove Project Importer</h3>
        <p>Import FieldMove geological data including:</p>
        <ul>
            <li>CSV files (localities, lines, planes, notes, and images)</li>
            <li>Basemaps (geotifs) you might have used for mapping</li>
            <li>KML file storing lines and polygons</li>
        </ul>
        <p>Select the .fm project folder containing your CSV files (and basemaps)
        and optionally a KML file for line drawing reference.</p>
        """)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Project folder selection
        folder_layout = QVBoxLayout()
        folder_label = QLabel("<b>1. Select FieldMove Project Folder:</b>")
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Path to folder containing CSV files")
        folder_btn = QPushButton("Browse...")
        folder_btn.clicked.connect(self.select_folder)
        
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(folder_btn)
        layout.addLayout(folder_layout)
        
        # KML file selection
        kml_layout = QVBoxLayout()
        kml_label = QLabel("<b>2. Select KML File (optional):</b>")
        self.kml_edit = QLineEdit()
        self.kml_edit.setPlaceholderText("Path to KML basemap file")
        kml_btn = QPushButton("Browse...")
        kml_btn.clicked.connect(self.select_kml)
        
        kml_layout.addWidget(kml_label)
        kml_layout.addWidget(self.kml_edit)
        kml_layout.addWidget(kml_btn)
        layout.addLayout(kml_layout)
        
        # Button box (using QHBoxLayout)
        btn_box = QHBoxLayout()  # Now properly imported
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_box.addWidget(import_btn)
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
    
    def select_kml(self):
        kml, _ = QFileDialog.getOpenFileName(
            self,
            "Select KML File",
            "",
            "KML Files (*.kml *.kmz)"
        )
        if kml:
            self.kml_edit.setText(kml)
    
    def get_paths(self):
        return {
            'project_dir': self.folder_edit.text(),
            'kml_path': self.kml_edit.text() if self.kml_edit.text() else None
        }
    
class FieldMoveProjectImporter:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.svg_dir = os.path.join(self.plugin_dir, 'SVG')
        self.actions = []
        self.menu = "&FieldMove Project Importer"
        
        # List of CSV files that should be treated as point layers
        self.point_csvs = [
            "image.csv", 
            "note.csv", 
            "localities.csv", 
            "plane.csv", 
            "line.csv"#, 
            #"sighting.csv"
        ]

    def initGui(self):
        # Add SVG path to QGIS
        self._add_svg_path_to_qgis()
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.action = QAction(
            QIcon(icon_path),
            "Import FieldMove Project",
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)  
        self.action.setWhatsThis("Import FieldMove project data (CSV and KML files)")
        
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.menu, self.action)
        
        self.actions.append(self.action)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        """Cleanup when plugin is unloaded"""
        # Remove SVG path from QGIS
        self._remove_svg_path_from_qgis()

    def run(self):
        dlg = FieldMoveImportDialog(self.plugin_dir, self.iface.mainWindow())
        if not dlg.exec_():  # User cancelled
            return
            
        paths = dlg.get_paths()
        if not paths['project_dir'] or not os.path.exists(paths['project_dir']):
            QMessageBox.warning(self.iface.mainWindow(), "Error", "Invalid project folder")
            return
            
        self.import_project(project_dir=paths['project_dir'], kml_path=paths['kml_path'])
    
    def import_project(self, project_dir, kml_path=None):
        try:
            # Input validation
            if not isinstance(project_dir, str) or not os.path.isdir(project_dir):
                raise ValueError("Invalid project directory")
                
            # Create group
            group_name = f"FieldMoveImport_{os.path.basename(project_dir)}"
            root = QgsProject.instance().layerTreeRoot()
            if existing := root.findGroup(group_name):
                root.removeChildNode(existing)
            group = root.insertGroup(0, group_name)
            group2 = group.insertGroup(-1, 'basemaps')
            

            # Process files with type checking
            for root_dir, _, files in os.walk(project_dir):
                for file in files:
                    if not isinstance(file, str):
                        continue
                        
                    file_path = os.path.join(root_dir, file)
                    file_lower = file.lower()
                    
                    if file_lower.endswith('.csv'):
                        if file_lower in [f.lower() for f in self.point_csvs]:
                            self._process_point_csv(file_path, group)
                        else:
                            continue #self._process_csv(file_path, group)
                    elif file_lower.endswith(('.tif', '.tiff')):
                        self._process_geotiff(file_path, group2)

            # Process KML if provided and valid
            if kml_path and isinstance(kml_path, str) and os.path.exists(kml_path):
                self._process_kml(kml_path, group)

        except Exception as e:
            QgsMessageLog.logMessage(f"Import error: {e}", 'FieldMove', Qgis.Critical)
            QMessageBox.warning(None, "Error", f"Import failed: {str(e)}")
    
    def _is_valid_project(self, project_dir):
        """Check if directory contains FieldMove project files"""
        # Check for .fm extension or presence of CSV/KML files
        if project_dir.endswith('.fm'):
            return True
            
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.lower().endswith('.csv'):
                    return True
        return False
    
    def _process_point_csv(self, csv_path, group):
        """Process CSV files that should be point layers with X/Y/Z coordinates"""
        try:
            layer_name = os.path.splitext(os.path.basename(csv_path))[0]
            
            # Read CSV file to check for coordinate columns
            with open(csv_path, 'r') as f:
                # Read CSV with stripped whitespace from headers
                reader = csv.DictReader(f, skipinitialspace=True)
                fieldnames = [name.strip() for name in reader.fieldnames]  # Clean column names
                # Check for required columns (case insensitive)
                x_col = next((col for col in fieldnames if col.lower() in ['longitude', ' longitude', 'lon']), None)
                y_col = next((col for col in fieldnames if col.lower() in ['latitude', ' latitude', 'lat']), None)
                z_col = next((col for col in fieldnames if col.lower() in ['altitude', ' altitude', 'elevation']), None)
                
                if not x_col or not y_col:
                    QMessageBox.warning(None, "Error", f"CSV file {csv_path} is missing required coordinate columns (longitude/x and latitude/y)")
                    return
                
                # Create a point layer with Z dimension if altitude is available
                vlayer = QgsVectorLayer(f"Point?crs=EPSG:4326", layer_name, "memory")
                provider = vlayer.dataProvider()
                
                # Add fields (excluding coordinate columns)
                fields = QgsFields()
                for field in fieldnames:
                    if field.lower() not in [x_col.lower(), y_col.lower(), z_col.lower() if z_col else '']:
                        fields.append(QgsField(field, QVariant.String))
                
                provider.addAttributes(fields)
                vlayer.updateFields()
                
                # Add features
                features = []
                f.seek(0)  # Rewind file
                next(reader)  # Skip header again
                
                for row in reader:
                    try:
                        x = float(row[x_col])
                        y = float(row[y_col])
                        z = float(row[z_col]) if z_col and row.get(z_col) else None
                        
                        if z is not None:
                            point = QgsPoint(x, y, z)
                            geom = QgsGeometry(point)
                        else:
                            point = QgsPointXY(x, y)
                            geom = QgsGeometry.fromPointXY(point)
                        
                        feat = QgsFeature()
                        feat.setGeometry(geom)
                        
                        # Set attributes (excluding coordinate columns)
                        attributes = []
                        for field in fieldnames:
                            if field.lower() not in [x_col.lower(), y_col.lower(), z_col.lower() if z_col else '']:
                                attributes.append(row[field])
                        feat.setAttributes(attributes)
                        
                        features.append(feat)
                    except (ValueError, KeyError) as e:
                        continue
                
                provider.addFeatures(features)
                vlayer.updateExtents()
                
                # Save to GeoPackage
                gpkg_path = os.path.join(os.path.dirname(csv_path), f"{layer_name}.gpkg")
                options = QgsVectorFileWriter.SaveVectorOptions()
                options.driverName = "GPKG"
                options.layerName = layer_name
                error = QgsVectorFileWriter.writeAsVectorFormatV3(
                    vlayer,
                    gpkg_path,
                    QgsProject.instance().transformContext(),
                    options
                )
                
                if error[0] != QgsVectorFileWriter.NoError:
                    QMessageBox.warning(None, "Error", f"Could not save GeoPackage: {gpkg_path}")
                    return
                
                # Load the GeoPackage
                gpkg_layer = QgsVectorLayer(f"{gpkg_path}|layername={layer_name}", layer_name, "ogr")
                if gpkg_layer.isValid():
                    # For line and plane layers, try to join with rock-units.csv
                    if layer_name.lower() in ['line', 'plane']:
                        self._join_rock_units(gpkg_layer, os.path.dirname(csv_path))
                    
                    self._style_layer(gpkg_layer, layer_name)
                    QgsProject.instance().addMapLayer(gpkg_layer, False)

                # After creating gpkg_layer:
                if gpkg_layer.isValid():
                    self._style_layer(gpkg_layer, layer_name)
                    QgsProject.instance().addMapLayer(gpkg_layer, False)
                    group.addLayer(gpkg_layer)
                    # Configure map tips
                    if layer_name == 'image':
                        self._configure_image_map_tips(gpkg_layer,csv_path)
                    else:
                        self._configure_map_tips(gpkg_layer)
            
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error processing point CSV: {str(e)}")

    def _join_rock_units(self, layer, project_dir):
        """Join rock units information from rock-units.csv to the layer and transfer color to new field"""
        try:
            rock_units_path = os.path.join(project_dir, "rock-units.csv")
            if not os.path.exists(rock_units_path):
                return False

            # Read rock-units.csv to create a mapping dictionary
            rock_unit_colors = {}
            with open(rock_units_path, 'r') as f:
                # Read CSV with stripped whitespace from headers
                reader = csv.DictReader(f, skipinitialspace=True)
                for row in reader:
                    if 'name' in row and 'color' in row:
                        rock_unit_colors[row['name'].strip().lower()] = row['color'].strip()

            if not rock_unit_colors:
                return False

            # Find the rockunit field in our layer (case insensitive)
            rockunit_field = None
            for field in layer.fields():
                if field.name().lower() in ['rockunit', ' rockunit']:
                    rockunit_field = field.name()
                    break

            if not rockunit_field:
                return False

            # Start editing the layer to add color field
            layer.startEditing()
            
            # Add color field if it doesn't exist
            if layer.fields().indexFromName('color') == -1:
                layer.addAttribute(QgsField('color', QVariant.String))
            
            # Update features with color values
            for feature in layer.getFeatures():
                rockunit_value = feature[rockunit_field]
                if rockunit_value:
                    rockunit_key = str(rockunit_value).strip().lower()
                    color = rock_unit_colors.get(rockunit_key, '')
                    if color:
                        layer.changeAttributeValue(feature.id(), 
                                            layer.fields().indexFromName('color'), 
                                            color)
            
            layer.commitChanges()
            return True

        except Exception as e:
            QMessageBox.warning(None, "Warning", f"Could not join rock units: {str(e)}")
            if layer.isEditable():
                layer.rollBack()
            return False

    def _process_csv(self, csv_path, group):
        """Convert regular CSV to GeoPackage (non-spatial)"""
        try:
            layer_name = os.path.splitext(os.path.basename(csv_path))[0]
            
            # Create a temporary memory layer to read CSV
            uri = f'file://{csv_path}?delimiter=,'
            csv_layer = QgsVectorLayer(uri, layer_name, 'delimitedtext')
            
            if not csv_layer.isValid():
                QMessageBox.warning(None, "Error", f"Could not load CSV file: {csv_path}")
                return
                
            # Save to GeoPackage
            gpkg_path = os.path.join(os.path.dirname(csv_path), f"{layer_name}.gpkg")
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "GPKG"
            options.layerName = layer_name
            error = QgsVectorFileWriter.writeAsVectorFormatV3(
                csv_layer,
                gpkg_path,
                QgsProject.instance().transformContext(),
                options
            )
            
            if error[0] != QgsVectorFileWriter.NoError:
                QMessageBox.warning(None, "Error", f"Could not save GeoPackage: {gpkg_path}")
                return
                
            # Load the GeoPackage and style it
            gpkg_layer = QgsVectorLayer(f"{gpkg_path}|layername={layer_name}", layer_name, "ogr")
            if gpkg_layer.isValid():
                self._style_layer(gpkg_layer, layer_name)
                QgsProject.instance().addMapLayer(gpkg_layer, False)

            # After creating gpkg_layer:
            if gpkg_layer.isValid():
                self._style_layer(gpkg_layer, layer_name)
                QgsProject.instance().addMapLayer(gpkg_layer, False)
                group.addLayer(gpkg_layer)
            
                # Configure map tips
                self._configure_map_tips(gpkg_layer)
                
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error processing CSV: {str(e)}")

    def _process_kml(self, kml_path):
        """Convert KML to GeoPackage"""
        try:
            layer_name = os.path.splitext(os.path.basename(kml_path))[0]
            gpkg_path = os.path.join(os.path.dirname(kml_path), f"{layer_name}.gpkg")
            
            # Convert KML to GeoPackage
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "GPKG"
            options.layerName = layer_name
            kml_layer = QgsVectorLayer(kml_path, layer_name, "ogr")
            
            if not kml_layer.isValid():
                QMessageBox.warning(None, "Error", f"Could not load KML file: {kml_path}")
                return
                
            error = QgsVectorFileWriter.writeAsVectorFormatV3(
                kml_layer,
                gpkg_path,
                QgsProject.instance().transformContext(),
                options
            )
            
            if error[0] != QgsVectorFileWriter.NoError:
                QMessageBox.warning(None, "Error", f"Could not save GeoPackage: {gpkg_path}")
                return
                
            # Load the GeoPackage
            gpkg_layer = QgsVectorLayer(f"{gpkg_path}|layername={layer_name}", layer_name, "ogr")
            if gpkg_layer.isValid():
                QgsProject.instance().addMapLayer(gpkg_layer, False)

            # the  group layers:
            if gpkg_layer.isValid():
                QgsProject.instance().addMapLayer(gpkg_layer, False)
                group.addLayer(gpkg_layer)
                
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error processing KML: {str(e)}")

    def _process_geotiff(self, geotif_path, group):
        """Load and style a GeoTIFF file"""
        try:
            # Create layer name from filename
            layer_name = os.path.splitext(os.path.basename(geotif_path))[0]
            
            # Create raster layer
            raster_layer = QgsRasterLayer(geotif_path, layer_name)
            
            if raster_layer.isValid():
                # Add to project and group
                QgsProject.instance().addMapLayer(raster_layer, False)
                group.addLayer(raster_layer)
                
                # Apply basic styling
                raster_layer.setContrastEnhancement(QgsContrastEnhancement.StretchToMinimumMaximum)
                raster_layer.triggerRepaint()
                
                return raster_layer
            else:
                QgsMessageLog.logMessage(
                    f"Failed to load GeoTIFF: {geotif_path}",
                    'FieldMovePlugin',
                    Qgis.Warning
                )
                return None
                
        except Exception as e:
            QgsMessageLog.logMessage(
                f"Error processing GeoTIFF {geotif_path}: {str(e)}",
                'FieldMovePlugin',
                Qgis.Critical
            )
            return None

    def _style_layer(self, layer, layer_name):
        """Apply rule-based styling with SVG symbols, colored strokes, rotation, and custom labels"""
        try:
            # Special handling for plane layer
            if layer_name.lower() == 'plane':
                # Find required fields (case-insensitive with whitespace handling)
                color_field = next((f.name() for f in layer.fields() 
                                if f.name().strip().lower() == 'color'), None)
                rockunit_field = next((f.name() for f in layer.fields() 
                                    if f.name().strip().lower() in ['rockunit', 'rock-unit']), None)
                planetype_field = next((f.name() for f in layer.fields() 
                                    if f.name().strip().lower() in ['planetype', 'type']), None)
                strike_field = next((f.name() for f in layer.fields() 
                                if f.name().strip().lower() == 'strike'), None)
                dip_field = next((f.name() for f in layer.fields() 
                                if f.name().strip().lower() == 'dip'), None)

                if all([color_field, rockunit_field, planetype_field, strike_field]):
                    # Get SVG symbol path
                    svg_dir = os.path.join(self.plugin_dir, 'SVG', 'RHRule_strike')
                    # SVG symbol mapping - customize these paths
                    svg_mapping = {
                        'bedding': next((f for f in os.listdir(svg_dir) if f.startswith('201') and f.endswith('.svg')), None),
                        'fault': next((f for f in os.listdir(svg_dir) if f.startswith('261') and f.endswith('.svg')), None),
                        'joint': next((f for f in os.listdir(svg_dir) if f.startswith('263') and f.endswith('.svg')), None),
                        'cleavage': next((f for f in os.listdir(svg_dir) if f.startswith('207') and f.endswith('.svg')), None)
                        # Add more as needed
                    }
                    
                    # Create rule-based renderer
                    renderer = QgsRuleBasedRenderer(QgsMarkerSymbol())
                    root_rule = renderer.rootRule()
                    
                    # Get unique combinations of rockunit and planetype
                    unique_combos = {}
                    for feature in layer.getFeatures():
                        rockunit = str(feature[rockunit_field])#.strip()
                        planetype = str(feature[planetype_field]).strip()
                        color = str(feature[color_field]).strip()
                        strike = float(feature[strike_field]) if feature[strike_field] else 0
                        
                        if all([rockunit, planetype, color]):
                            unique_combos[(rockunit, planetype)] = (color, strike)

                    # Create one rule per combination
                    for (rockunit, planetype), (color, strike) in unique_combos.items():
                        # Get appropriate SVG
                        svg_file = svg_mapping.get(planetype.lower(), next((f for f in os.listdir(svg_dir) if f.startswith('201') and f.endswith('.svg')), None))
                        svg_path = os.path.join(self.plugin_dir, 'SVG', 'RHRule_strike', svg_file)

                        # Create rule
                        rule = root_rule.children()[0].clone()
                        rule.setLabel(f"{rockunit} - {planetype}")
                        rule.setFilterExpression(
                            f'"{rockunit_field}" = \'{rockunit}\' AND '
                            f'"{planetype_field}" = \'{planetype}\''
                        )

                        # Configure symbol
                        symbol = QgsMarkerSymbol()
                        svg_layer = QgsSvgMarkerSymbolLayer(svg_path)
                        svg_layer.setSize(10)
                        
                        # Set color from rockunit's color
                        svg_layer.setStrokeColor(QColor(color))
                        svg_layer.setStrokeWidth(0.5)
                        svg_layer.setFillColor(QColor(color))
                        
                        # Set rotation from strike
                        svg_layer.setAngle(325) #in the legend
                        svg_layer.setDataDefinedProperty(
                            QgsSymbolLayer.PropertyAngle,
                            QgsProperty.fromExpression(f'"{strike_field}"')
                        )
                        
                        symbol.changeSymbolLayer(0, svg_layer)
                        rule.setSymbol(symbol)
                        root_rule.appendChild(rule)
                            
                    # Remove the default rule
                    root_rule.removeChildAt(0)
                    
                    # Apply label styling after symbol styling
                    self._apply_label_style_plane(layer)
                    # Apply the renderer
                    layer.setRenderer(renderer)
                    layer.triggerRepaint()
                    return
                    
            # Special handling for lineation layer
            elif layer_name.lower() == 'line':
                # Find required fields (case-insensitive with whitespace handling)
                color_field = next((f.name() for f in layer.fields() 
                                if f.name().strip().lower() == 'color'), None)
                rockunit_field = next((f.name() for f in layer.fields() 
                                    if f.name().strip().lower() in ['rockunit', 'rock-unit']), None)
                lineationtype_field = next((f.name() for f in layer.fields() 
                                    if f.name().strip().lower() in ['lineationtype', 'type']), None)
                plungeazimuth_field = next((f.name() for f in layer.fields() 
                                if f.name().strip().lower() == 'plungeazimuth'), None)

                if all([color_field, rockunit_field, lineationtype_field, plungeazimuth_field]):
                    # Get SVG symbol path
                    svg_dir = os.path.join(self.plugin_dir, 'SVG', 'Arrows')
                    svg_file = next((f for f in os.listdir(svg_dir) 
                                if f.startswith('102') and f.endswith('.svg')), None)
                    
                    if svg_file:
                        svg_path = os.path.join(svg_dir, svg_file)

                        # Create base symbol with data-defined rotation
                        base_symbol = QgsMarkerSymbol()
                        svg_layer = QgsSvgMarkerSymbolLayer(svg_path)
                        svg_layer.setSize(22)
                        svg_layer.setStrokeWidth(0.5)
                        
                        # SET ROTATION EXPRESSION HERE
                        svg_layer.setDataDefinedProperty(
                            QgsSymbolLayer.PropertyAngle,
                            QgsProperty.fromExpression(f'"{plungeazimuth_field}"')
                        )
                        
                        base_symbol.changeSymbolLayer(0, svg_layer)
                    
                        # Create rule-based renderer
                        renderer = QgsRuleBasedRenderer(base_symbol.clone())
                        root_rule = renderer.rootRule()

                        # Get unique combinations for rules
                        unique_data = {}
                        for feature in layer.getFeatures():
                            rockunit = str(feature[rockunit_field]).strip()
                            lineationtype = str(feature[lineationtype_field]).strip()
                            color = str(feature[color_field]).strip()
                            if all([rockunit, lineationtype, color]):
                                unique_data[(rockunit, lineationtype)] = color

                        # Create rules
                        for (rockunit, lineationtype), color in unique_data.items():
                            rule = root_rule.children()[0].clone()
                            rule.setLabel(f"{rockunit} - {lineationtype}")
                            rule.setFilterExpression(
                                f'"{rockunit_field}" = \'{rockunit}\' AND '
                                f'"{lineationtype_field}" = \'{lineationtype}\''
                            )
                            
                            # Set stroke color per rule
                            symbol = rule.symbol().clone()
                            symbol.symbolLayer(0).setStrokeColor(QColor(color))
                            symbol.symbolLayer(0).setFillColor(QColor(color))
                            rule.setSymbol(symbol)
                            
                            root_rule.appendChild(rule)
                            
                        # Remove the default rule
                        root_rule.removeChildAt(0)
                        # Apply label styling after symbol styling
                        self._apply_label_style_line(layer)
                        # Apply the renderer
                        layer.setRenderer(renderer)
                        layer.triggerRepaint()
                        return
                    
            # Special handling for notes
            elif layer_name.lower() == 'note':
                # Get SVG symbol path
                svg_dir = os.path.join(self.plugin_dir, 'SVG')
                svg_file = next((f for f in os.listdir(svg_dir) 
                            if f.startswith('note') and f.endswith('.svg')), None)
                
                if svg_file:
                    svg_path = os.path.join(svg_dir, svg_file)
                    # Create base symbol
                    base_symbol = QgsMarkerSymbol()
                    svg_layer = QgsSvgMarkerSymbolLayer(svg_path)
                    svg_layer.setSize(10)
                    svg_layer.setStrokeWidth(0.8)
                    base_symbol.changeSymbolLayer(0, svg_layer)
                    # Create rule-based renderer
                    renderer = QgsRuleBasedRenderer(base_symbol.clone())
                    root_rule = renderer.rootRule()
                    
                    # Apply the renderer
                    layer.setRenderer(renderer)
                    layer.triggerRepaint()
                    return                
                
            # Special handling for localities
            elif layer_name.lower() == 'localities':
                # Get SVG symbol path
                svg_dir = os.path.join(self.plugin_dir, 'SVG')
                svg_file = next((f for f in os.listdir(svg_dir) 
                            if f.startswith('locality2') and f.endswith('.svg')), None)
                
                if svg_file:
                    svg_path = os.path.join(svg_dir, svg_file)
                    # Create base symbol
                    base_symbol = QgsMarkerSymbol()
                    svg_layer = QgsSvgMarkerSymbolLayer(svg_path)
                    svg_layer.setSize(15)
                    svg_layer.setStrokeWidth(0.5)
                    base_symbol.changeSymbolLayer(0, svg_layer)
                    # Create rule-based renderer
                    renderer = QgsRuleBasedRenderer(base_symbol.clone())
                    root_rule = renderer.rootRule()

                    # Apply the renderer
                    layer.setRenderer(renderer)
                    layer.triggerRepaint()
                    return                
            
            # Special handling for images
            elif layer_name.lower() == 'image':
                heading_field = next((f.name() for f in layer.fields() 
                                if f.name().strip().lower() == 'heading'), None)
                # Get SVG symbol path
                svg_dir = os.path.join(self.plugin_dir, 'SVG')
                svg_file = next((f for f in os.listdir(svg_dir) 
                            if f.startswith('photo') and f.endswith('.svg')), None)
                
                if svg_file:
                    svg_path = os.path.join(svg_dir, svg_file)
                    # Create base symbol
                    base_symbol = QgsMarkerSymbol()
                    svg_layer = QgsSvgMarkerSymbolLayer(svg_path)
                    svg_layer.setSize(6)
                    svg_layer.setStrokeWidth(0.5)
                    svg_layer.setDataDefinedProperty(
                            QgsSymbolLayer.PropertyAngle,
                            QgsProperty.fromExpression(f'"{heading_field}"+180')
                        )
                    base_symbol.changeSymbolLayer(0, svg_layer)
                    # Create rule-based renderer
                    renderer = QgsRuleBasedRenderer(base_symbol.clone())
                    root_rule = renderer.rootRule()

                    # Apply the renderer
                    layer.setRenderer(renderer)
                    layer.triggerRepaint()
                    return         


            # Default styling for other layers
            default_symbol = QgsMarkerSymbol.createSimple({
                'name': 'square',
                'color': 'red',
                'size': '4'
            })
            layer.setRenderer(QgsSingleSymbolRenderer(default_symbol))
            layer.triggerRepaint()

        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error styling layer: {str(e)}")
    
    def _find_svg_for_color(self, color):
        """Find an SVG symbol that matches the color (optional)"""
        if not os.path.exists(self.svg_dir):
            return None
        
        try:
            # Convert color to a string we can match in filenames
            color_str = QColor(color).name().lower().replace('#', '')
            
            # Look for SVG files containing the color code
            for svg_file in os.listdir(self.svg_dir):
                if svg_file.endswith('.svg') and color_str in svg_file.lower():
                    return os.path.join(self.svg_dir, svg_file)
        except:
            return None
        return None

    def _configure_map_tips(self, layer, notes_field="notes"):
        """Configure map tips to show notes attribute"""
        try:
            # Check if layer has notes field
            fields = layer.fields()
            notes_idx = fields.indexFromName(notes_field)
            
            if notes_idx >= 0:
                # Enable map tips and set to show notes
                layer.setMapTipTemplate(f"[% \"{notes_field}\" %]")
                layer.setDisplayExpression(f"\"{notes_field}\"")
                
                # Optional: Configure nicer display
                layer.setMapTipTemplate(
                    f"<b>Notes:</b><br>"
                    f"[% \"{notes_field}\" %]<br>"
                )
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error configuring Map tips: {str(e)}")

    def _configure_image_map_tips(self, layer, csv_path):
        """Configure map tips to show photo preview and notes"""
        try:
            # define the images folder path (within the project)
            imageFolder = "'"+csv_path[:-4]+"s/'"            
            # Configure nice display
            layer.setMapTipTemplate(
                f"<table>"
                f"<tr>"
                f"<th>heading:N[%round(heading,0)%]</th>"
                f"</tr>"
                f"<tr>"
                f"<th>"
                f'<img src="file:///[%concat({imageFolder},ltrim("image name"))%]" width="350" height="250";">'
                f"</th>"
                f"</tr>"
                f"<tr>"
                f"<th>[%notes%]</th>"
                f"</tr>"
                f"</table>"
            )    
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error configuring images Map tips: {str(e)}")

    def _apply_label_style_plane(self, layer):
        """Apply label style from QML file to plane layer"""
        try:
            # Path to your pre-made QML style file
            style_path = os.path.join(self.plugin_dir, 'styles', 'labelsPlanes.qml')
            
            # Check if style exists and apply
            if os.path.exists(style_path):
                layer.loadNamedStyle(style_path)
                layer.triggerRepaint()
                return True
            return False
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error loading label style: {str(e)}")

    def _apply_label_style_line(self, layer):
        """Apply label style from QML file to plane layer"""
        try:
            # Path to your pre-made QML style file
            style_path = os.path.join(self.plugin_dir, 'styles', 'labelsLines.qml')
            
            # Check if style exists and apply
            if os.path.exists(style_path):
                layer.loadNamedStyle(style_path)
                layer.triggerRepaint()
                return True
            return False
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Error loading label style: {str(e)}")

    def _add_svg_path_to_qgis(self):
        """Add plugin's SVG directory to QGIS SVG paths if not already present"""
        svg_path = os.path.join(self.plugin_dir, 'SVG')
        
        # Create the SVG directory if it doesn't exist
        if not os.path.exists(svg_path):
            os.makedirs(svg_path)
        
        # Get current QGIS SVG paths
        settings = QgsSettings()
        current_paths = settings.value('svg/searchPathsForSVG', [], type=list)
        
        # Convert to standardized path format for comparison
        normalized_svg_path = os.path.normpath(svg_path)
        normalized_current_paths = [os.path.normpath(p) for p in current_paths]
        
        # Add if not already present
        if normalized_svg_path not in normalized_current_paths:
            current_paths.append(svg_path)
            settings.setValue('svg/searchPathsForSVG', current_paths)
            
            # Refresh SVG cache - version compatible approach
            try:
                # Try QGIS 3.x method first
                svg_cache = QgsApplication.svgCache()
                if hasattr(svg_cache, 'clearCache'):
                    svg_cache.clearCache()
                elif hasattr(svg_cache, 'rebuild'):
                    svg_cache.rebuild()
            except:
                pass

    def _remove_svg_path_from_qgis(self):
        """Remove plugin's SVG directory from QGIS SVG paths"""
        svg_path = os.path.join(self.plugin_dir, 'SVG')
        
        settings = QgsSettings()
        current_paths = settings.value('svg/searchPathsForSVG', [], type=list)
        
        # Remove our path if present
        normalized_svg_path = os.path.normpath(svg_path)
        current_paths = [p for p in current_paths if os.path.normpath(p) != normalized_svg_path]
        
        settings.setValue('svg/searchPathsForSVG', current_paths)
        
        # Refresh SVG cache - version compatible approach
        try:
            # Try QGIS 3.x method first
            svg_cache = QgsApplication.svgCache()
            if hasattr(svg_cache, 'clearCache'):
                svg_cache.clearCache()
            elif hasattr(svg_cache, 'rebuild'):
                svg_cache.rebuild()
        except:
            pass

   
