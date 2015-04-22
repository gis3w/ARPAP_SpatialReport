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
from ARPAP_SpatialReport import arpap_geoprocessing


__author__ = 'Walter Lorenzetti'
__date__ = 'December 2014'
__copyright__ = '(C) 2014, Walter Lorenzetti Gis3w'

# This will get replaced with a git SHA1 when you do a git archive
 
__revision__ = '$Format:%H$'

import os
import sys
from PyQt4 import QtGui, uic
from PyQt4.QtCore import QObject,SIGNAL, Qt, QFileInfo
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
from arpap_spatialreport_dialog_chart import ARPAP_SpatialReportDialogChart
from arpap_geoprocessing import TYPE_NAMES, TYPES
from psql.arpap_psql import arpap_spatialreport_psql
from .core.project import SpatialreportProject
import json


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'arpap_spatialreport_dialog_base.ui'))


class ARPAP_SpatialReportDialog(QtGui.QDialog, FORM_CLASS):
    
    validation = None
    radioGeoprocessingSelectionButtons = ['Intersection','Touch','Contain']
    outputItemsSelect = ['Shape File','Spatialite','Postgis']
    headersFieldsTable = ['Field name','Data type','Length','Precision','Actions']
    algorithm = None
    reslayer = list()
    removeButtons = dict()
    originalOriginLayerFieldsName = []
    originalTargetLayerFieldsName = []
    
    def __init__(self, parent=None,iface=None):
        super(ARPAP_SpatialReportDialog, self).__init__(parent)
        self.iface = iface
        self.project = SpatialreportProject(self.iface,parent=self)
        self.PSQL = arpap_spatialreport_psql(self.iface)
        self.setupUi(self)
        self.manageGui()

        
    def manageGui(self):
        """
        Finalize gui
        """
        self.fieldCalculatorOriginButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/mActionCalculateField.png'))
        self.fieldCalculatorTargetButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/mActionCalculateField.png'))
        self.forwardButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/forward.png'))
        self.backButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/back.png'))
        self.runButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/run.png'))
        self.projectFileButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/mActionFileOpen.svg'))
        self.saveProjectFileButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/mActionFileSave.png'))
        self.loadProjectFileButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/upload.svg'))
        self.openChartDialogButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/histogram.png'))
        self.risbaLogo.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/risba_logo.jpg'))
        self.arpaLogo.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/arpa_low_logo.tif'))
        self.alcotraLogo.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/alcotra_logo.png'))
        self.unioneEuropeaLogo.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/unione_europea_logo.jpg'))
        self.labelDescriptionGeoprocessingIntersection.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/intersection.png'))
        self.labelDescriptionGeoprocessingTouch.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/touch.png'))
        self.labelDescriptionGeoprocessingContain.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/contain.png'))
        self.validation = ValidationInputdata(self,self.tr)
        QObject.connect(self.geoprocessingIntersectionRadio, SIGNAL('released()'),self.doValidationGeoprocessingDataType)
        QObject.connect(self.geoprocessingTouchRadio, SIGNAL('released()'),self.doValidationGeoprocessingDataType)
        QObject.connect(self.geoprocessingContainRadio, SIGNAL('released()'),self.doValidationGeoprocessingDataType)
        QObject.connect(self.fieldCalculatorOriginButton, SIGNAL('clicked()'),self.openFieldCalculatorOrigin)
        QObject.connect(self.fieldCalculatorTargetButton, SIGNAL('clicked()'),self.openFieldCalculatorTarget)
        QObject.connect(self.originLayerSelect, SIGNAL('currentIndexChanged(int)'),self.populateOriginFieldsLists)
        QObject.connect(self.targetLayerSelect, SIGNAL('currentIndexChanged(int)'),self.populateTargetFieldsLists)
        QObject.connect(self.forwardButton, SIGNAL('clicked()'),self.oneForwardStep)
        QObject.connect(self.backButton, SIGNAL('clicked()'),self.oneBackStep)
        QObject.connect(self.outputShapeFileButton, SIGNAL('clicked()'),self.openOutputShapeFileDialog)
        QObject.connect(self.outputSpatialiteButton, SIGNAL('clicked()'),self.openOutputSpatialiteDialog)
        QObject.connect(self.dbConnectionSelect, SIGNAL('currentIndexChanged(int)'),self.populateDbSchema)
        QObject.connect(self.saveProjectFileButton, SIGNAL('clicked()'),self.saveProject)
        QObject.connect(self.loadProjectFileButton, SIGNAL('clicked()'),self.loadProject)
        QObject.connect(self.projectFile, SIGNAL('textChanged(QString)'),self.setEnableButtonIO)
        self.populateCombosOutputType()
        self.populateCombosDbConnection()
        QObject.connect(self.selectOutputType, SIGNAL('currentIndexChanged(int)'),self.showOutputForm)
        QObject.connect(self.projectFileButton, SIGNAL('clicked()'),self.openProjectFileDialog)
        QObject.connect(self.openChartDialogButton, SIGNAL('clicked()'),self.openChartDialog)
        QObject.connect(self.project, SIGNAL('projectFull()'),self.setEnableButtonIO)
        
    def setEnableButtonIO(self):
        if self.projectFile.text():
            if self.project.full:
                self.saveProjectFileButton.setEnabled(True)
            self.loadProjectFileButton.setEnabled(True)
        else:
            self.saveProjectFileButton.setEnabled(False)
            self.loadProjectFileButton.setEnabled(False)

    def saveProject(self):
        self.project.save(self.projectFile.text())

    def loadProject(self):
        self.project.loadingError = False
        self.project.open(self.projectFile.text())

    def changeIndex(self,incrementValue):
        """
        Change step manager
        """
        if (self.getValidationStep(self.stackedWidget.currentIndex()) and incrementValue >= 0) or incrementValue < 0:
            self.stackedWidget.setCurrentIndex(self.stackedWidget.currentIndex() + incrementValue)
            if self.stackedWidget.currentIndex() == 1:
                if not self.doValidationGeoprocessingDataType():
                    return False
            elif self.stackedWidget.currentIndex() == 3:
                self.showOutputForm(self.selectOutputType.currentIndex())
            elif self.stackedWidget.currentIndex() == 4:
                self.manageReportButton()
            #set project setp value
            if self.stackedWidget.currentIndex() < 5:
                self.project.setStep(self.stackedWidget.currentIndex() - incrementValue,self.getDataStep(self.stackedWidget.currentIndex() - incrementValue))
            self.setButtonNavigationStatus()
        else:
            self.showValidateErrors()
    
    def oneForwardStep(self):
        self.changeIndex(1)
        
    def oneBackStep(self):
        self.changeIndex(-1)
        
    def clearReslayer(self):
        if id(self.sender()) == id(self.reslayer[0]):
            self.reslayer = list()
        
    def manageReportButton(self):
        #if len(self.reslayer) and hasattr(self.reslayer[0],'name'):
            #self.labelProgress.setText(self.tr('Current output layer: '+self.reslayer[0].name()))
            #self.openChartDialogButton.setEnabled(True)
        #else:
        self.labelProgress.setText('')
            
        
    def populateCombosOriginTarget(self):
        layers = getVectorLayers()
        self.originLayerSelect.clear()
        self.targetLayerSelect.clear()
        for vlayer in layers:
            self.originLayerSelect.addItem('%s [Provider:%s, Epsg:%s]' % (vlayer.name(),vlayer.dataProvider().storageType(),vlayer.crs().postgisSrid()) ,vlayer)
            self.targetLayerSelect.addItem('%s [Provider:%s, Epsg:%s]' % (vlayer.name(),vlayer.dataProvider().storageType(),vlayer.crs().postgisSrid()),vlayer)
            
    def populateCombosOutputType(self):
        for type in self.outputItemsSelect:
            self.selectOutputType.addItem(type)
            
    def populateCombosDbConnection(self):
        self.dbConnectionSelect.clear()
        conn = self.PSQL.getConnections()
        for c in conn:
            self.dbConnectionSelect.addItem(c)
        
    def populateDbSchema(self):
        self.PSQL.setConnection(self.dbConnectionSelect.currentText())
        schemas = self.PSQL.getSchemas()
        self.dbSchemaSelect.clear()
        for s in schemas:
            self.dbSchemaSelect.addItem(s)
            
    def showOutputForm(self,index):
        self.stackedWidgetOutput.setCurrentIndex(index)
        
    def getOutputType(self):
        return self.outputItemsSelect[self.selectOutputType.currentIndex()]
            
    def populateOriginFieldsLists(self):
        if hasattr(self.getComboboxData('originLayerSelect'),'dataProvider'):
            fields = self.getComboboxData('originLayerSelect').dataProvider().fields()
            self.originalOriginLayerFieldsName = [f.name() for f in fields]
            self._populateTableFieldsList('originLayerSelect', self.tableViewOriginLayerFields)
    
    def populateTargetFieldsLists(self):
        if hasattr(self.getComboboxData('targetLayerSelect'),'dataProvider'):
            fields = self.getComboboxData('targetLayerSelect').dataProvider().fields()
            self.originalTargetLayerFieldsName = [f.name() for f in fields]
            self._populateTableFieldsList('targetLayerSelect', self.tableViewTargetLayerFields)
        
    def _populateTableFieldsList(self,comboName,tableView):
        headersFieldsTable = ['Field name','Data type','Length','Precision','Expression','Actions']
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
        fieldsToRet = dict()
        for r in range(model.rowCount()):
            item = model.item(r,0)
            if item.checkState() == Qt.Checked:
                fieldsToRet[r] = item.data()
                
        return fieldsToRet
    
    def getSelectedFieldsNameWithExpression(self,layer):
        '''
        Return a dict of field with expression
        '''
        tableView = getattr(self,layer)
        model = tableView.model()
        fieldsToRet = dict()
        for r in range(model.rowCount()):
            item = model.item(r,0)
            expressionItem = model.item(r,4)
            if item.checkState() == Qt.Checked and expressionItem:
                fieldsToRet[item.text()] = expressionItem.text()
                
        return fieldsToRet
            
    def setButtonNavigationStatus(self):
        self.openChartDialogButton.setEnabled(False)
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
        self.backButton.setEnabled(True)
        if not self.validation.geoprocessingDataType():
            self.forwardButton.setEnabled(False)
            self.showValidateErrors()
            return False
        else:
            self.forwardButton.setEnabled(True)
            return True
        
    def addLogMessage(self,logMessage):
        self.logBrowser.clear()
        self.logBrowser.append(logMessage)
    
    def addRuntimeStepLog(self,runtimeStepLog):
        self.runtimeStepBrowser.append(runtimeStepLog)

    def addProjectFileLog(self,logErrorMessage,type='log'):
        self.projectFileStatusBrowser.append(logErrorMessage)
        
    def showValidateErrors(self):
        QtGui.QMessageBox.warning( self, self.tr("ARPA Spatial Report"), self.tr( "Validation error:\n" ) + ';\n'.join(self.validation.getErrors()) )
            
    def getGeoprocessingType(self):
        rbuttonChecked = None
        for key in self.radioGeoprocessingSelectionButtons:
            rbutton = 'geoprocessing' + key + 'Radio'
            if getattr(self, rbutton).isChecked():
                return getattr(self, rbutton)
    
    def getGeoprocessingTypeData(self):
        rbutton = self.getGeoprocessingType()
        return rbutton.text()
    
    def getComboboxData(self,nameCombobox):
        combobox = getattr(self, nameCombobox)
        return combobox.itemData(combobox.currentIndex())
    
    def getComboboxText(self,nameCombobox):
        combobox = getattr(self, nameCombobox)
        return combobox.itemText(combobox.currentIndex())
    
    def setPercentage(self,i):
        if self.progressBar.maximum() == 0:
            self.progressBar.setMaximum(100)
        self.progressBar.setValue(i)
        
    def setText(self,text):
        self.labelProgress.setText(text)

    def getDataStep(self,stepNumber):
        data = {
            '0':{
                'title':self.tr('Selection Origin -> Target'),
                'originLayerSelect':self.getComboboxData('originLayerSelect'),
                'targetLayerSelect':self.getComboboxData('targetLayerSelect'),
            },
            '1':{
                'title':self.tr('Selection Geometry operation'),
                'geoprocessingTypeData':self.getGeoprocessingTypeData()
            },
            '2':{
                'title':self.tr('Selection fields'),
                'originLayerFields':self.getSelectedFields('tableViewOriginLayerFields'),
                'targetLayerFields':self.getSelectedFields('tableViewTargetLayerFields'),
            },
            '3':{
                'title':self.tr('Selection Output'),
                'selectOutputType':self.getOutputType(),
                'outputShapeFile':self.outputShapeFile.text(),
                'outputSpatialite':self.outputSpatialite.text(),
                'outputPostgis':self.getPostgisOutputValues()
            }
        }
        if str(stepNumber) in data:
            return data[str(stepNumber)]

    def loadStep0(self):
        #get data from _config
        self.addProjectFileLog(self.tr('<span style="color:#0000FF;"><b>Loading Step 0 data ...</b></span>  '))
        data = self.project.getWriteableConfigStep0
        layers = getVectorLayers()
        layersName = map(lambda l : l.originalName(),layers)
        modelOriginFields = self.tableViewOriginLayerFields.model()
        if not modelOriginFields == None:
            modelOriginFields.clear()
        if data['originLayerSelect'] in layersName:
            layer = layers[layersName.index(data['originLayerSelect'])]
            self.originLayerSelect.setCurrentIndex(self.originLayerSelect.findData(layer))
            self.addProjectFileLog(self.tr('Loaded Origin Layer')+': '+data['originLayerSelect'])
        else:
            self.project.loadingError = True
            self.addProjectFileLog(self.tr('<span style="color:#FF0000;"><b>Origin Layer(')+data['originLayerSelect']+self.tr(') not present in the current qgis project, please load the layer and load file project again</b></span>'))

        modelTargetFields = self.tableViewTargetLayerFields.model()
        if not modelTargetFields == None:
            modelTargetFields.clear()
        if data['targetLayerSelect'] in layersName:
            layer = layers[layersName.index(data['targetLayerSelect'])]
            self.targetLayerSelect.setCurrentIndex(self.targetLayerSelect.findData(layer))
            self.addProjectFileLog(self.tr('Loaded Target Layer')+': '+data['targetLayerSelect'])
        else:
            self.project.loadingError = True
            self.addProjectFileLog(self.tr('<span style="color:#FF0000;"><b>Target Layer(')+data['targetLayerSelect']+self.tr(') not present in the current qgis project, please load the layer and load file project again</b></span>'))

    def loadStep1(self):
        #get data from _config
        self.addProjectFileLog(self.tr('<span style="color:#0000FF;"><b>Loading Step 1 data ...</b></span>'))
        data = self.project.getWriteableConfigStep1
        if data['geoprocessingTypeData'] in self.radioGeoprocessingSelectionButtons:
            rbutton = 'geoprocessing' + data['geoprocessingTypeData'] + 'Radio'
            getattr(self,rbutton).setChecked(True)
            self.addProjectFileLog(self.tr('Loaded geometry type operation')+': '+data['geoprocessingTypeData'])
        else:
            self.project.loadingError = True
            self.addProjectFileLog(self.tr('<span style="color:#FF0000;"><b>Geoprocessing type not possible: </b></span>')+'<b>'+data['geoprocessingTypeData']+'</b>')

    def loadStep2(self):
        #get data from _config
        self.addProjectFileLog(self.tr('<span style="color:#0000FF;"><b>Loading Step 2 data ...</b></span>'))
        data = self.project.getWriteableConfigStep2
        for typeLayer in ['origin','target']:
            olfName = typeLayer+'LayerFields'
            table= 'tableView' + typeLayer[0].capitalize()+typeLayer[1:] + 'LayerFields'
            layerFieldsToCheck = [f['name'] for f in data[olfName] if f['origin'] == 'layer']
            layerFieldsToCheckExpression = [f['name'] for f in data[olfName] if f['origin'] == 'layer' and 'expression' in f]
            tableView = getattr(self,table)
            model = tableView.model()
            if model != None and model.rowCount() > 0:
                for r in range(model.rowCount()):
                    item = model.item(r,0)
                    if not item.text() in layerFieldsToCheck:
                        item.setCheckState(Qt.Unchecked)
                    elif item.text() in layerFieldsToCheckExpression:
                        expression = [f for f in data[olfName] if f['name'] == item.text()][0]['expression']
                        expressionItem = QtGui.QStandardItem(expression)
                        model.setItem(r,4,expressionItem)
                #add expression fields
                for f in [f for f in data[olfName] if f['origin'] == 'expression']:
                    f['type'] = f['typeName']
                    self.addExpressionField(tableView,f)
            else:
                self.addProjectFileLog(self.tr('<span style="color:#FF0000;"><b>Fields of ')+ typeLayer +self.tr(' not load</b></span>'))




    def loadStep3(self):
        #get data from _config
        self.addProjectFileLog(self.tr('<span style="color:#0000FF;"><b>Loading Step 3 data ...</b></span>'))
        data = self.project.getWriteableConfigStep3
        if data['selectOutputType'] == self.outputItemsSelect[2]:
            #POSTIGS
            #check if db connection is present
            conn = self.PSQL.getConnections()
            if data['outputPostgis']['connection'] in conn:
                #select the connection
                self.selectOutputType.setCurrentIndex(self.selectOutputType.findText(self.outputItemsSelect[2]))
                self.dbConnectionSelect.setCurrentIndex(self.dbConnectionSelect.findText(data['outputPostgis']['connection']))
                self.dbSchemaSelect.setCurrentIndex(self.dbSchemaSelect.findText(data['outputPostgis']['schema']))
                self.tableName.setText(data['outputPostgis']['table'])
                self.geoColumnName.setText(data['outputPostgis']['geoColumn'])
                if data['outputPostgis']['overwrite']:
                    self.overwriteTableCheckBox.setChecked(True)
                if data['outputPostgis']['spatialIndex']:
                    self.spatialIndexCheckBox.setChecked(True)
                self.addProjectFileLog(self.tr('Loaded Postgis output settings'))
            else:
                self.project.loadingError = True
                self.addProjectFileLog(self.tr('<span style="color:#FF0000;"><b>Database connection not present in yoour connections, please add connection e load config file again </b></span>')+'<b>'+data['outputPostgis']['connection']+'</b>')
                #show database connection details
                self.addProjectFileLog('<b>Connection:</b>' + data['outputPostgis']['connection'])
                self.addProjectFileLog('<b>Spatial index:</b>' + data['outputPostgis']['connection'])

        elif data['selectOutputType'] == self.outputItemsSelect[1]:
            #SPATIALLITE
            #check basename
            if os.path.exists(os.path.dirname(data['outputSpatialite'])):
                self.outputSpatialite.setText(data['outputSpatialite'])
                self.addProjectFileLog(self.tr('Loaded Spatialite output settings')+' - '+data['outputSpatialite'])
            else:
                self.project.loadingError = True
                self.addProjectFileLog(self.tr('<span style="color:#FF0000;"><b>Directory not exists: </b></span>')+'<b>'+os.path.dirname(data['outputSpatialite'])+'</b>')
        else:
            #SHAPE FILE
            #check basename
            if os.path.exists(os.path.dirname(data['outputShapeFile'])):
                self.outputShapeFile.setText(data['outputShapeFile'])
                self.addProjectFileLog(self.tr('Loaded Shape file output settings'))
            else:
                self.project.loadingError = True
                self.addProjectFileLog(self.tr('<span style="color:#FF0000;"><b>Directory not exists: </b></span>')+'<b>'+os.path.dirname(data['outputShapeFile'])+'</b>')

    
    def getPostgisOutputValues(self):
        return {
                 'connection':self.getComboboxText('dbConnectionSelect'),
                 'PSQL': self.PSQL,
                 'schema':self.getComboboxText('dbSchemaSelect'),
                 'table': self.tableName.text(),
                 'geoColumn':self.geoColumnName.text(),
                 'overwrite': self.overwriteTableCheckBox.isChecked(),
                 'spatialIndex': self.spatialIndexCheckbox.isChecked()
                 }
        
    def createRuntimeStepLog(self):
        #take current inputs values
        currentInputValues = self.project.getConfig()
        self.runtimeStepBrowser.clear()
        self.addRuntimeStepLog("<h3 style='border-style:dotted; border-color:red;'><u>1) %s:</u></h3>" % currentInputValues['step0']['title'])
        self.addRuntimeStepLog("<span>ORIGIN LAYER: %s (<b>%s</b>)[Provider:%s, Epsg:%s] </span>" % (currentInputValues['step0']['originLayerSelect'].name(),getVectorTypeAsString(currentInputValues['step0']['originLayerSelect']),currentInputValues['step0']['originLayerSelect'].dataProvider().storageType(),str(currentInputValues['step0']['originLayerSelect'].crs().postgisSrid())))
        self.addRuntimeStepLog("<span>TARGET LAYER: %s (<b>%s</b>)[Provider:%s, Epsg:%s] </span>" % (currentInputValues['step0']['targetLayerSelect'].name(),getVectorTypeAsString(currentInputValues['step0']['targetLayerSelect']),currentInputValues['step0']['targetLayerSelect'].dataProvider().storageType(),str(currentInputValues['step0']['targetLayerSelect'].crs().postgisSrid())))
        self.addRuntimeStepLog("<h3><u>2) %s:</u></h3>" % currentInputValues['step1']['title'])
        self.addRuntimeStepLog("<span>GEOPORCESSING TYPE: <b>%s</b> </span>" % (currentInputValues['step1']['geoprocessingTypeData']))
        self.addRuntimeStepLog("<h3><u>3) %s:</u></h3>" % currentInputValues['step2']['title'])
        self.addRuntimeStepLog("<h4>Origin Layer Fields:</h4>")
        for f in currentInputValues['step2']['originLayerFields'].values():
            self.addRuntimeStepLog(self.formatFieldToString(f))
        self.addRuntimeStepLog("<h4>Target Layer Fields:</h4>")
        for f in currentInputValues['step2']['targetLayerFields'].values():
            self.addRuntimeStepLog(self.formatFieldToString(f))
        self.addRuntimeStepLog("<h3><u>4) %s:</u></h3>" % currentInputValues['step3']['title'])
        self.addRuntimeStepLog("<span>OUTPUT TYPE: <b>%s</b> </span>" % (currentInputValues['step3']['selectOutputType']))
        if self.getOutputType() == 'Shape File':
            self.addRuntimeStepLog("<span>Shape File Path: <b>%s</b> </span>" % (currentInputValues['step3']['outputShapeFile']))
        elif self.getOutputType() == 'Spatialite':
            self.addRuntimeStepLog("<span>SQlite/Spatialite Path: <b>%s</b> </span>" % (currentInputValues['step3']['outputSpatialite']))
        else:
            self.addRuntimeStepLog("<span>Connection: <b>%s</b> </span>" % (currentInputValues['step3']['outputPostgis']['connection']))
            self.addRuntimeStepLog("<span>Schema: <b>%s</b> </span>" % (currentInputValues['step3']['outputPostgis']['schema']))
            self.addRuntimeStepLog("<span>Table: <b>%s</b> </span>" % (currentInputValues['step3']['outputPostgis']['table']))
            self.addRuntimeStepLog("<span>Geo column: <b>%s</b> </span>" % (currentInputValues['step3']['outputPostgis']['geoColumn']))
        
        
    def formatFieldToString(self,f):
        '''
        Format filed properties for human read
        '''
        return "%s (%s, %s, %s)" % (f.name(),f.typeName(),f.length(),f.precision())

    def openFieldCalculatorOrigin(self):
        self.openFieldCalculator('origin')
    
    def openFieldCalculatorTarget(self):
        self.openFieldCalculator('target')
        
    def getTebleViewRowNumberByFieldName(self,fieldName,tableViewName):
        tableView = getattr(self, tableViewName)
        model = tableView.model()
        for r in range(model.rowCount()):
            item = model.item(r,0)
            if item.text() == fieldName:
                return r
    
    def openFieldCalculator(self,source='origin'):
        tableViewName = 'tableView'+ source.capitalize() + 'LayerFields'
        tableView = getattr(self, tableViewName)
        fieldCalculatorDialog =  ARPAP_SpatialReportFieldCalculatorDialog(self.getComboboxData(source+'LayerSelect'))
        result = fieldCalculatorDialog.exec_()
        if result == QtGui.QDialog.Accepted:
            if fieldCalculatorDialog.mUpdateExistingGroupBox.isChecked():
                #find row field in tableview
                row = self.getTebleViewRowNumberByFieldName(fieldCalculatorDialog.mExistingFieldComboBox.currentText(),tableViewName)
                expressionItem = tableView.model().item(row,4)
                if expressionItem:
                    expressionItem.setText(fieldCalculatorDialog.builder.expressionText())
                else:
                    expressionItem = QtGui.QStandardItem(fieldCalculatorDialog.builder.expressionText())
                    tableView.model().setItem(row,4,expressionItem)
                #set expression
            else:
                data = {'objtype':'fieldCalculator',
                        'name':fieldCalculatorDialog.mOutputFieldNameLineEdit.text(),
                        'type':fieldCalculatorDialog.mOutputFieldTypeComboBox.currentText(),
                        'length':fieldCalculatorDialog.mOutputFieldWidthSpinBox.value(),
                        'precision':fieldCalculatorDialog.mOutputFieldPrecisionSpinBox.value(),
                        'expression':fieldCalculatorDialog.builder.expressionText()}
                self.addExpressionField(tableView,data)


    def addExpressionField(self,tableView,data):
        itemName = QtGui.QStandardItem(data['name'])
        itemName.setData(QgsField(data['name'],TYPES[TYPE_NAMES.index(data['type'])],data['type'],int(data['length']),int(data['precision'])))
        itemName.setCheckable(True)
        itemName.setCheckState(Qt.Checked)
        itemName.setSelectable(False)
        itemName.setEditable(False)
        itemType = QtGui.QStandardItem(data['type'])
        itemLength = QtGui.QStandardItem(str(data['length']))
        itemPrecision = QtGui.QStandardItem(str(data['precision']))
        itemExpression = QtGui.QStandardItem(data['expression'])
        actions = QtGui.QStandardItem('actions')
        model = tableView.model()
        model.appendRow([itemName,itemType,itemLength,itemPrecision,itemExpression,actions])
        removeButton = QtGui.QPushButton(self.tr('Remove'),clicked=self.removeTableFieldsRow)
        tableView.setIndexWidget(actions.index(),removeButton)
        self.removeButtons[id(removeButton)] = actions.index()
    
    def removeTableFieldsRow(self):
        index = self.removeButtons[id(self.sender())]
        model = self.sender().parent().parent().model()
        model.removeRow(index.row())
        
            
    def openOutputShapeFileDialog(self):
        self.outputShapeFile.clear()
        ( outputShapeFile, encoding ) = self._openSaveDialog(self,'save')
        if outputShapeFile is None or encoding is None:
          return
        self.outputShapeFile.setText( outputShapeFile )

    def openProjectFileDialog(self):
        self.projectFile.clear()
        ( projectFile, encoding ) = self._openSaveDialog(self,mode='save',saveDefaultSuffix=self.project.EXTENSION,filtering="Project files (*.qrp)")
        if projectFile is None or encoding is None:
          return
        self.projectFile.setText( projectFile )
    
    def openOutputSpatialiteDialog(self):
        self.outputSpatialite.clear()
        ( outputSpatialite, encoding ) = self._openSaveDialog(self,'save',filtering="Saptilite files (*.sqlite *.spatialite)")
        if outputSpatialite is None or encoding is None:
          return
        self.outputSpatialite.setText( outputSpatialite )
        
    def _openSaveDialog( self,parent,mode="open",saveDefaultSuffix="shp" ,filtering="Shape files (*.shp *.SHP)", dialogMode="SingleFile",dirNamePath="/ARPAPGeoprocessing/lastShapeDir",encode="/ARPAPGeoprocessing/encoding",titleDialog="/ARPAPGeoprocessing/encoding"):
        settings = QSettings()
        dirName = settings.value(dirNamePath)
        encode = settings.value(encode)
        fileDialog = QgsEncodingFileDialog( parent, titleDialog, dirName, filtering, encode )
        if mode == 'save':
            fileDialog.setDefaultSuffix( saveDefaultSuffix )
            fileDialog.setFileMode( QtGui.QFileDialog.AnyFile )
        else:
            fileDialog.setFileMode( QtGui.QFileDialog.ExistingFiles )
            fileDialog.setAcceptMode( QtGui.QFileDialog.AcceptOpen )
                
        if not fileDialog.exec_() == QtGui.QDialog.Accepted:
                return None, None
        files = fileDialog.selectedFiles()
        settings.setValue(dirNamePath, QFileInfo( unicode( files[0] ) ).absolutePath() )
        if dialogMode == "SingleFile" or mode == 'save':
          return ( unicode( files[0] ), unicode( fileDialog.encoding() ) )
        else:
          return ( files, unicode( fileDialog.encoding() ) )
        
    def openChartDialog(self):
        chartDialog = ARPAP_SpatialReportDialogChart(self)
        chartDialog.exec_()
        
