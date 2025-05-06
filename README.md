# FieldMoveProjectImporter_QGIS
A QGIS plugin to help geologists importing [FieldMove](https://www.petex.com/pe-geology/move-suite/digital-field-mapping/) project features into QGIS. FieldMove is a free digital mapping app available for iPad and Android tablets. 

(ctrl + click on the link to access latest template): [![DOI](https://zenodo.org/badge/957117869.svg)](https://doi.org/10.5281/zenodo.15133449)


## Install

The **FieldMoveProjectImporter** plugin can be installed directly from *QGIS Plugins Manager*. Make sure _show also experimental plugins_ is selected in the Plugins Manager's settings. 

Alternatively, or if you'd like the latest version you can save this repository to disk as a [zip file](https://github.com/gduclaux/FieldMoveProjectImporter_QGIS/archive/refs/heads/main.zip). Use *QGIS Plugins Manager* to load directly the FieldMoveProjectImporter plugin from zip file. If in doudt about plugin installation from a zip file watch this [short video](https://www.youtube.com/watch?v=AUQouvFyt34). 

_NB: This plugin has been developed and tested on OSX and tested Windows 11 with QGIS 3.40(LTR), if you encounter any issues please report them in the issue tracker providing information about the OS system and the version of QGIS you have been using._


## Usage 

### Prerequisites
From your tablet you can extract a FieldMove project in various format. I recommend you export in CSV format and copy the whole folder from your tablet to a dekstop computer. Store the **CSV project folder** (typically projectX.fm) in a convenient location in your local machine. _It should also work for CSV folder generated and exported from FieldMove-Clino, the mobile phone app version of FieldMove._

### FieldMove Project Importer plugin
After installation the plugin is avaliable from the plugin menu, or directly in the toolbar if the *Plugins Toolbar* is activated. Simply press the plugin button and provide the path to the CSV project folder then click **import**.

<p align="center">
  <img width="420" alt="image" src="https://github.com/user-attachments/assets/c9343426-f786-4a8b-afb4-dbcf25be227c" />
</p>

The plugin converts the CSV files to individual GeoPackages (with a WGS84 assigned coordinate reference system) stored in the original CSV Projet foder.

The plugin will generate a new Group (the group name is concatenation of "FieldMoveImport_" and your CSV project folder name - also the project id in FieldMove) in QGIS LayersTree, and load and display the imported point layers as well as any basemap imagery you might have in your project. Polygons and line drawings are imported as polylines.

<p align="center">
  <img width="950" alt="image" src="https://github.com/user-attachments/assets/c6bb84dd-663e-40ca-a899-e0d5dea5c74b" />
</p>


### Map Tips for features and images
If you activate the **show Map Tips** <img width="120" alt="image" src="https://github.com/user-attachments/assets/08acd5ed-1586-4a81-8642-24436a3218b5"/>, then select a layer in the LayersTree and move you mouse over a feature (i.e. a plane, a line, a locality or a note) from this active layer QGIS will display the information available in a pop-up box. 

<p align="center">
  <img width="950" alt="image" src="https://github.com/user-attachments/assets/d8f8705b-661c-42e2-a169-729ce1a54b99" />
</p>

If you select **image** in the LayersTree you should see a preview of the photograph (including any annotations you might have drawn onto it) with its heading and notes.

<p align="center">
  <img width="950" alt="image" src="https://github.com/user-attachments/assets/6988792f-0006-49f1-98f2-b1abb600c3d2" />
</p>



### Dip/plunge labeling
Dip (or plunge) labeling is set for both plane and line features. Labels are displayed when the zoom level (_scale_) of the map Canvas is larger than 1:300,000. This can be changed in the layer properties panel (Control feature labeling > Rendering > Scale dependent visibility).

### Symbology limitations
   - Symbol colors are set to match those imposed in the original FieldMove project for the different rock units.
   - Planar structures symbologies are not as detailed as it might be in your project. Different symbologies are applied to _fault_, _joint_ and _cleavage_ plane types. All other planar measurements are represented with the defaut _bedding_ symbol. The bedding symbol isn't changing as a function of the dip angle either.
   - All lineation types are displayed using a simple arrow symbology with the arrow shaft base located on the spatial reference point of the measurement.
   - Symbology can be updated and improved using a rule-based method in QGIS.


## Stereonet tool
In addition to the Importer itself, the plugin now comes with an additional **Stereonet Tool** <img width="120" alt="Stereonet Tool launch" src="https://github.com/user-attachments/assets/0fb63f5c-5e37-40df-ba0d-27b5b7da3eb3" />. 


You can use this tool to quickly explore structural data imported from FieldMove and export selected data for further analyses in external packages such as Allmendinger' Stereonet software. 

Usage is simple, select the Plane or Line layer in the LayersTree, then select the features you would like to plot in the stereonet, launch the **Stereonet Tool** and select among the available plot options (contouring, great circles and/or poles, rose diagram) and plot the selected data in a Schmidt stereonet (lower hemisphere). 

<p align="center">
  <img width="800" alt="image" src="https://github.com/user-attachments/assets/78930b6e-6e91-4a50-b620-2afcd9f43d1e" />
</p>



## Roadmap
 
   - Develop a template for generating a fieldbook-like report from all digital data. 

## Credits
   - Plugin construction and manual: Guillaume Duclaux, using QGIS Plugin Builder Plugin & DeepSeek 
   - SVG symbols for geological fabrics are from Rod Holcombe [geoqsymbol page](https://www.holcombe.net.au/software/geoqsymbol.html#download)
   - Stereonet tool is based on the [SWAXI QFIELD stereonet plugin](https://github.com/swaxi/qgis-stereonet) from Mark Jessel, itself based on the hard work carried out by Joe Kington's [mplsteronet project](https://github.com/joferkington/mplstereonet) and Daniel Childs' [qgis-stereonet project](https://github.com/childsd3/qgis-stereonet)
   - If you find this plugin useful for your research please cite this plugin using its Zenodo DOI [![DOI](https://zenodo.org/badge/957117869.svg)](https://doi.org/10.5281/zenodo.15133449)
