# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ARPAP_SpatialReportDialog
                                 A QGIS plugin
 ARPAP Spatial Report
                             -------------------
        begin                : 2014-11-20
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Walter Lorenzetti GIS3W
        email                : lorenzetti@gis3w.it
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
import sys
from PyQt4 import QtGui, uic
from PyQt4.QtCore import QObject,SIGNAL
from arpap_validation_inputdata import ValidationInputdata
from __builtin__ import hasattr
import fTools
from PySide.QtGui import QStandardItem
if os.path.abspath(os.path.dirname(fTools.__file__) + '/tools') not in sys.path:
    sys.path.append(os.path.abspath(os.path.dirname(fTools.__file__) + '/tools')) 
from ftools_utils  import getVectorTypeAsString



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'arpap_spatialreport_dialog_base.ui'))


class ARPAP_SpatialReportDialog(QtGui.QDialog, FORM_CLASS):
    
    validation = None
    
    def __init__(self, parent=None):
        """Constructor."""
        super(ARPAP_SpatialReportDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.validation = ValidationInputdata(self,self.tr)
        QObject.connect(self.geoprocessingIntersectRadio, SIGNAL('released()'),self.doValidationGeoprocessingDataType)
        QObject.connect(self.geoprocessingTouchRadio, SIGNAL('released()'),self.doValidationGeoprocessingDataType)
        QObject.connect(self.geoprocessingContainRadio, SIGNAL('released()'),self.doValidationGeoprocessingDataType)
    
    def changeIndex(self,incrementValue):
        if (self.getValidationStep(self.stackedWidget.currentIndex()) and incrementValue >= 0) or incrementValue < 0:
            self.stackedWidget.setCurrentIndex(self.stackedWidget.currentIndex() + incrementValue)
            self.setButtonNavigationStatus()
            if self.stackedWidget.currentIndex() == 1:
                self.doValidationGeoprocessingDataType()
            elif self.stackedWidget.currentIndex() == 2:
                self.populateFieldsLists()
        else:
            self.showValidateErrors()
            
    def populateFieldsLists(self):
        fields = self.getComboboxData('originLayerSelect').dataProvider().fields()
        for f in fields:
            item = QtGui.QListWidgetItem()
            #item.setCheckable(True)
            item.setText(f.name())
            self.listWidgetOriginLayerFields.addItem(item)
            
        
            
    def setButtonNavigationStatus(self):
        if self.stackedWidget.currentIndex() == 0:
            self.backButton.setEnabled(False)
        else:
            self.backButton.setEnabled(True)
        
        if self.stackedWidget.currentIndex() == self.stackedWidget.count() - 1:
            self.forwardButton.setEnabled(False)
            self.runButton.setEnabled(True)
            self.createRuntimeStepLog()
        else:
            self.forwardButton.setEnabled(True)
            self.runButton.setEnabled(False)
            
    def getValidationStep(self,index): 
        if hasattr(self.validation,'validateStep%s' % (index,)):
            return getattr(self.validation, 'validateStep%s' % (index,))()
        else:
            return True
    
    def doValidationGeoprocessingDataType(self): 
        if not self.validation.geoprocessingDataType():
            self.showValidateErrors()
        
    def addLogMessage(self,logMessage):
        self.logBrowser.clear()
        self.logBrowser.append(logMessage)
    
    def addRuntimeStepLog(self,runtimeStepLog):
        self.runtimeStepBrowser.append(runtimeStepLog)
        
    def showValidateErrors(self):
        QtGui.QMessageBox.warning( self, self.tr("ARPA Spatial Report"), self.tr( "Validation error:\n" ) + ';\n'.join(self.validation.getErrors()) )
            
    def getGeoprocessingType(self):
        rbuttonChecked = None
        radioGeoprocessingSelectionButtons = ['Intersect','Touch','Contain']
        for key in radioGeoprocessingSelectionButtons:
            rbutton = 'geoprocessing' + key + 'Radio'
            if getattr(self, rbutton).isChecked():
                return getattr(self, rbutton)
    
    def getGeoprocessingTypeData(self):
        rbutton = self.getGeoprocessingType()
        return rbutton.text()
    
    def getComboboxData(self,nameCombobox):
        combobox = getattr(self, nameCombobox)
        return combobox.itemData(combobox.currentIndex())
    
    def setPercentage(self,i):
        if self.progressBar.maximum() == 0:
            self.progressBar.setMaximum(100)
        self.progressBar.setValue(i)
        
    def setText(self,text):
        self.labelProgress.setText(text)
        
    def getCurrentInputValues(self):
        toRet = {}
        #get stpe1 values
        toRet['step0']={
                        'originLayerSelect':self.getComboboxData('originLayerSelect'),
                        'targetLayerSelect':self.getComboboxData('targetLayerSelect'),
                        }
        #get stpe2 values
        toRet['step1']={
                        'geoprocessingTypeData':self.getGeoprocessingTypeData()
                        }
        return toRet
        
    def createRuntimeStepLog(self):
        #take current inputs values
        currentInputValues = self.getCurrentInputValues()
        print currentInputValues
        self.runtimeStepBrowser.clear()
        self.addRuntimeStepLog("<h3>STEP1:</h3>")
        self.addRuntimeStepLog("<span>ORIGIN LAYER: %s (<b>%s</b>)[] </span>" % (currentInputValues['step0']['originLayerSelect'].name(),getVectorTypeAsString(currentInputValues['step0']['originLayerSelect'])))
        self.addRuntimeStepLog("<span>TARGET LAYER: %s (<b>%s</b>)[] </span>" % (currentInputValues['step0']['targetLayerSelect'].name(),getVectorTypeAsString(currentInputValues['step0']['targetLayerSelect'])))
        
        