# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ARPAP_SpatialReport
                                 A QGIS plugin
 ARPAP Spatial Report
                              -------------------
        begin                : 2014-11-20
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Walter Lorenzetti GIS3W
        email                : lorenzetti at gis3w dot it
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject, SIGNAL
from PyQt4.QtGui import QAction, QIcon
from qgis.core import *
from qgis.gui import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from arpap_spatialreport_dialog import ARPAP_SpatialReportDialog
import os.path
from processing.tools.dataobjects import *
from processing.algs.qgis.QGISAlgorithmProvider import QGISAlgorithmProvider
from processing.gui.SilentProgress import SilentProgress
from processing.gui.Postprocessing import handleAlgorithmResults
from arpap_geoprocessing import Intersection, Touch, Contain


class ARPAP_SpatialReport:
    """QGIS Plugin Implementation."""
    
    GeoprocessingAlgorithms = {
                               'Intersection':Intersection,
                               'Touch':Touch,
                               'Contain':Contain
                               }

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ARPAP_SpatialReport_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = ARPAP_SpatialReportDialog()
        
        QObject.connect(self.dlg.testButton, SIGNAL('pressed()'),self.test)
        QObject.connect(self.dlg.browseConfigFileOutputButton, SIGNAL('clicked()'),self.outConfigFile)
        QObject.connect(self.dlg.browseConfigFileInputButton, SIGNAL('clicked()'),self.inConfigFile)
        QObject.connect(self.dlg.runButton, SIGNAL('clicked()'),self.runAlgorithm)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&ARPAP SpatialReport')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ARPAP_SpatialReport')
        self.toolbar.setObjectName(u'ARPAP_SpatialReport')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('ARPAP_SpatialReport', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the InaSAFE toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/ARPAP_SpatialReport/icons/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'ARPAP SpatialReport'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&ARPAP SpatialReport'),
                action)
            self.iface.removeToolBarIcon(action)

            
    def saveDialog( self,parent, filtering="JSON files (*.json *.JSON)"):
        settings = QSettings()
        dirName = settings.value( "/ARPAPGeoprocessing/lastConfigDir" )
        encode = settings.value( "/ARPAPGeoprocessing/encoding" )
        fileDialog = QgsEncodingFileDialog( parent, "Save config file", dirName, filtering, encode )
        fileDialog.setDefaultSuffix( "json" )
        fileDialog.setFileMode( QFileDialog.AnyFile )
        fileDialog.setAcceptMode( QFileDialog.AcceptSave )
        fileDialog.setConfirmOverwrite( True )
        if not fileDialog.exec_() == QDialog.Accepted:
                return None, None
        files = fileDialog.selectedFiles()
        settings.setValue("/ARPAPGeoprocessing/lastConfigDir", QFileInfo( unicode( files[0] ) ).absolutePath() )
        return ( unicode( files[0] ), unicode( fileDialog.encoding() ) )
    
    def openDialog( self,parent, filtering="JSON files (*.json *.JSON)", dialogMode="SingleFile"):
        settings = QSettings()
        dirName = settings.value( "/ARPAPGeoprocessing/lastConfigDir" )
        encode = settings.value( "/ARPAPGeoprocessing/encoding" )
        fileDialog = QgsEncodingFileDialog( parent, "Open config file", dirName, filtering, encode )
        fileDialog.setFileMode( QFileDialog.ExistingFiles )
        fileDialog.setAcceptMode( QFileDialog.AcceptOpen )
        if not fileDialog.exec_() == QDialog.Accepted:
                return None, None
        files = fileDialog.selectedFiles()
        settings.setValue("/ARPAPGeoprocessing/lastConfigDir", QFileInfo( unicode( files[0] ) ).absolutePath() )
        if dialogMode == "SingleFile":
          return ( unicode( files[0] ), unicode( fileDialog.encoding() ) )
        else:
          return ( files, unicode( fileDialog.encoding() ) )
    
    def outConfigFile( self ):
        self.dlg.configFileOutput.clear()
        ( self.jsonFileOutputConfigFile, self.encoding ) = self.saveDialog(self.dlg)
        if self.jsonFileOutputConfigFile is None or self.encoding is None:
          return
        self.dlg.configFileOutput.setText( self.jsonFileOutputConfigFile )
    
    def inConfigFile( self ):
        self.dlg.configFileInput.clear()
        ( self.jsonFileInputConfigFile, self.encoding ) = self.openDialog(self.dlg)
        if self.jsonFileInputConfigFile is None or self.encoding is None:
          return
        self.dlg.configFileInput.setText( self.jsonFileInputConfigFile )
    
    def runAlgorithm(self):
        algorithm = self.GeoprocessingAlgorithms[self.dlg.getGeoprocessingTypeData()]()
        algorithm.provider = QGISAlgorithmProvider()
        algorithm.setParameterValue('ORIGIN',self.dlg.getComboboxData('originLayerSelect'))
        algorithm.setParameterValue('TARGET',self.dlg.getComboboxData('targetLayerSelect'))
        algorithm.setParameterValue('FIELDSORIGIN',self.dlg.getSelectedFields('tableViewOriginLayerFields'))
        algorithm.setParameterValue('FIELDSTARGET',self.dlg.getSelectedFields('tableViewTargetLayerFields'))
        algorithm.execute(self.dlg)
        print algorithm.getOutputValue('OUTPUT')
        handleAlgorithmResults(algorithm,self.dlg)
        
        
        
    def test(self):
        fields = self.dlg.getSelectedFields('tableViewOriginLayerFields')
        print fields[0].name()
        
        

    def run(self):
        #self.dlg.forwardButton
        self.dlg.stackedWidget.setCurrentIndex(0)
        self.dlg.setButtonNavigationStatus()
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
