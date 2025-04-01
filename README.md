# FieldMoveProjectImporter_QGIS
A QGIS plugin to help geologists importing [FieldMove](https://www.petex.com/pe-geology/move-suite/digital-field-mapping/) project features into QGIS. FieldMove free digital mapping app available for iPadOS and Android.

## Install

Save repository to disk as a [zip file](https://github.com/gduclaux/FieldMoveProjectImporter_QGIS/archive/refs/heads/main.zip). Use QGIS Plugin Manager to load directly the FieldMoveProjectImporter plugin from zip file. If in doudt about plugin installation from a zip file watch this [short video](https://www.youtube.com/watch?v=AUQouvFyt34). 


## Usage 

### Prerequisites
From your tablet you can extract a FieldMove project in various format. I recommend you export both in KML and as CSV formats and copy those from your tablet to a dekstop computer. Store  the **KMZ file** and the **CSV project folder** (typically projectX.fm) in a convenient location in your local machine. 

### FieldMove Project Importer plugin
After installation the plugin is avaliable from the plugin menu, or directly in the toolbar if the *Plugins Toolbar* is activated. Simply press the plugin button and provide the path to the CSV project folder and the KMZ file, then click **import**.

<p align="center">
  <img width="420" alt="image" src="https://github.com/user-attachments/assets/23293c38-8afa-4b5a-9795-de55a790e81a" />
</p>

The plugin converts the CSV files to individual GeoPackages stores in the CSV Projet foder.

The plugin will generate a new Group (the group name is concatenation of "FieldMoveImport_" and your CSV project folder name - also the project id in FieldMove) in QGIS LayersTree, and load and display the imported point layers as well as any basemap imagery you might have in your project. Polygons and line drawings are not yet supported. 

### Map Tips for features and images
If you activate the **show Map Tips** feature <img width="120" alt="image" src="https://github.com/user-attachments/assets/08acd5ed-1586-4a81-8642-24436a3218b5"/>, then select a layer in the LayersTree and move you mouse over a feature from this active layer QGIS will display the notes recorded in a text box. If you select **image** in the LayersTree you should see a preview of the photograph with any annotations you might have drawn on the image.
<p align="center">
  <img width="818" alt="image" src="https://github.com/user-attachments/assets/a76e5de3-1e52-4fc6-b9f8-ac6fcc76525e" />
</p>

### Dip labeling
Dip labeling is set for both plane and line features. Labels are displayed when the zoom level (_scale_) of the map Canvas is larger than 1:300,000.


## Roadmap

This has only been tested on OSX with QGIS 3.34 (LTR), other architecture support should come if it fails in your system. Add support for KMZ files (not working at this stage) to display line drawings and polygons.

## Credits
   - Plugin construction and manual - Guillaume Duclaux, using QGIS Plugin Builder Plugin & DeepSeek
   - SVG symbols for geological fabrics are from Rod Holcombe [geoqsymbol page](https://www.holcombe.net.au/software/geoqsymbol.html#download)
