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
from PyQt4.QtCore import QObject,SIGNAL, Qt
from arpap_validation_inputdata import ValidationInputdata
from __builtin__ import hasattr, getattr
from processing.tools.dataobjects import *
import fTools
if os.path.abspath(os.path.dirname(fTools.__file__) + '/tools') not in sys.path:
    sys.path.append(os.path.abspath(os.path.dirname(fTools.__file__) + '/tools')) 
from ftools_utils  import getVectorTypeAsString
from qgis.core import *
from qgis.gui import *
import resources_rc

from arpap_spatialreport_fieldcalculator_dialog import ARPAP_SpatialReportFieldCalculatorDialog


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'arpap_spatialreport_dialog_base.ui'))


class ARPAP_SpatialReportDialog(QtGui.QDialog, FORM_CLASS):
    
    validation = None
    headersFieldsTable = ['Field name','Data type','Length','Precision','Actions']
    
    def __init__(self, parent=None):
        """Constructor."""
        super(ARPAP_SpatialReportDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.fieldCalculatorOriginButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/mActionCalculateField.png'))
        self.fieldCalculatorTargetButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/mActionCalculateField.png'))
        self.validation = ValidationInputdata(self,self.tr)
        QObject.connect(self.geoprocessingIntersectRadio, SIGNAL('released()'),self.doValidationGeoprocessingDataType)
        QObject.connect(self.geoprocessingTouchRadio, SIGNAL('released()'),self.doValidationGeoprocessingDataType)
        QObject.connect(self.geoprocessingContainRadio, SIGNAL('released()'),self.doValidationGeoprocessingDataType)
        QObject.connect(self.fieldCalculatorOriginButton, SIGNAL('clicked()'),self.openFieldCalculatorOrigin)
        QObject.connect(self.fieldCalculatorTargetButton, SIGNAL('clicked()'),self.openFieldCalculatorTarget)
        QObject.connect(self.originLayerSelect, SIGNAL('currentIndexChanged(int)'),self.populateOriginFieldsLists)
        QObject.connect(self.targetLayerSelect, SIGNAL('currentIndexChanged(int)'),self.populateTargetFieldsLists)
        QObject.connect(self.forwardButton, SIGNAL('clicked()'),self.oneForwardStep)
        QObject.connect(self.backButton, SIGNAL('clicked()'),self.oneBackStep)
        self.populateCombosOriginTarget()
    
    def changeIndex(self,incrementValue):
        if (self.getValidationStep(self.stackedWidget.currentIndex()) and incrementValue >= 0) or incrementValue < 0:
            self.stackedWidget.setCurrentIndex(self.stackedWidget.currentIndex() + incrementValue)
            self.setButtonNavigationStatus()
            if self.stackedWidget.currentIndex() == 1:
                self.doValidationGeoprocessingDataType()
        else:
            self.showValidateErrors()
    
    def oneForwardStep(self):
        self.changeIndex(1)
        
    def oneBackStep(self):
        self.changeIndex(-1)
            
    def populateCombosOriginTarget(self):
        layers = getVectorLayers()
        self.originLayerSelect.clear()
        self.targetLayerSelect.clear()
        for vlayer in layers:
            self.originLayerSelect.addItem(vlayer.name(),vlayer)
            self.targetLayerSelect.addItem(vlayer.name(),vlayer)
            
    def populateOriginFieldsLists(self):
        if hasattr(self.getComboboxData('originLayerSelect'),'dataProvider'):
            self._populateTableFieldsList('originLayerSelect', self.tableViewOriginLayerFields)
    
    def populateTargetFieldsLists(self):
        if hasattr(self.getComboboxData('targetLayerSelect'),'dataProvider'):
            self._populateTableFieldsList('targetLayerSelect', self.tableViewTargetLayerFields)
        
    def _populateTableFieldsList(self,comboName,tableView):
        headersFieldsTable = ['Field name','Data type','Length','Precision','Actions']
        fields = self.getComboboxData(comboName).dataProvider().fields()            
        model = QtGui.QStandardItemModel(tableView)
        for columnName in headersFieldsTable:
            model.setHorizontalHeaderItem(headersFieldsTable.index(columnName),QtGui.QStandardItem(columnName))
        tableView.setModel(model)
        for f in fields:
            itemName = QtGui.QStandardItem(f.name())
            itemName.setData(f)
            itemName.setCheckable(True)
            itemName.setCheckState(Qt.Checked)
            itemName.setSelectable(False)
            itemName.setEditable(False)
            itemType = QtGui.QStandardItem(f.typeName())
            itemLength = QtGui.QStandardItem(str(f.length()))
            itemPrecision = QtGui.QStandardItem(str(f.precision()))
            model.appendRow([itemName,itemType,itemLength,itemPrecision])
            
    def getSelectedFields(self,layer):
        tableView = getattr(self,layer)
        model = tableView.model()
        fieldsToRet = []
        for r in range(model.rowCount()):
            item = model.item(r,0)
            if item.checkState() == Qt.Checked:
                fieldsToRet.append(item.data())
        return fieldsToRet
            
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
    
    def openFieldCalculatorOrigin(self):
        self.openFieldCalculator('origin')
        #fieldCalculatorDialog.show()
    
    def openFieldCalculatorTarget(self):
        self.openFieldCalculator('target')
    
    def openFieldCalculator(self,source='origin'):
        fieldCalculatorDialog =  ARPAP_SpatialReportFieldCalculatorDialog(self.getComboboxData(source+'LayerSelect'))
        result = fieldCalculatorDialog.exec_()
        if result == QtGui.QDialog.Accepted:
            print fieldCalculatorDialog.mOutputFieldTypeComboBox.currentIndex()
        

        