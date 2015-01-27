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
from arpap_spatialreport_dialog_chart import ARPAP_SpatialReportDialogChart
from arpap_geoprocessing import TYPE_NAMES, TYPES
from psql.arpap_psql import arpap_spatialreport_psql


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'arpap_spatialreport_dialog_base.ui'))


class ARPAP_SpatialReportDialog(QtGui.QDialog, FORM_CLASS):
    
    validation = None
    radioGeoprocessingSelectionButtons = ['Intersect','Touch','Contain']
    outputItemsSelect = ['Shape File','Spatialite','Postgis']
    headersFieldsTable = ['Field name','Data type','Length','Precision','Actions']
    algorithm = None
    reslayer = list()
    
    def __init__(self, parent=None,iface=None):
        super(ARPAP_SpatialReportDialog, self).__init__(parent)
        self.iface = iface
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
        self.openChartDialogButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/histogram.png'))
        self.risbaLogo.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/risba_logo.jpg'))
        self.arpaLogo.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/arpa_low_logo.tif'))
        self.alcotraLogo.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/alcotra_logo.png'))
        self.unioneEuropeaLogo.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/unione_europea_logo.jpg'))
        self.labelDescriptionGeoprocessingIntersection.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/intersection.png'))
        self.labelDescriptionGeoprocessingTouch.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/touch.png'))
        self.labelDescriptionGeoprocessingContain.setPixmap(QtGui.QPixmap(':/plugins/ARPAP_SpatialReport/icons/contain.png'))
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
        QObject.connect(self.outputShapeFileButton, SIGNAL('clicked()'),self.openOutputShapeFileDialog)
        QObject.connect(self.outputSpatialiteButton, SIGNAL('clicked()'),self.openOutputSpatialiteDialog)
        self.populateCombosOutputType()
        self.populateCombosDbConnection()
        QObject.connect(self.dbConnectionSelect, SIGNAL('currentIndexChanged(int)'),self.populateDbSchema)
        QObject.connect(self.selectOutputType, SIGNAL('currentIndexChanged(int)'),self.showOutputForm)
        QObject.connect(self.openChartDialogButton, SIGNAL('clicked()'),self.openChartDialog)
        
    
    def changeIndex(self,incrementValue):
        """
        Change step manager
        """
        if (self.getValidationStep(self.stackedWidget.currentIndex()) and incrementValue >= 0) or incrementValue < 0:
            self.stackedWidget.setCurrentIndex(self.stackedWidget.currentIndex() + incrementValue)
            self.setButtonNavigationStatus()
            if self.stackedWidget.currentIndex() == 1:
                self.doValidationGeoprocessingDataType()
            elif self.stackedWidget.currentIndex() == 3:
                self.showOutputForm(self.selectOutputType.currentIndex())
            elif self.stackedWidget.currentIndex() == 4:
                self.manageReportButton()
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
        conn = self.PSQL.getConnections()
        for c in conn:
            self.dbConnectionSelect.addItem(c)
        self.populateDbSchema()
        
    def populateDbSchema(self):
        self.PSQL.setConnection(self.dbConnectionSelect.currentText())
        schemas = self.PSQL.getSchemas()
        for s in schemas:
            self.dbSchemaSelect.addItem(s)
            
    def showOutputForm(self,index):
        self.stackedWidgetOutput.setCurrentIndex(index)
        
    def getOutputType(self):
        return self.outputItemsSelect[self.selectOutputType.currentIndex()]
            
    def populateOriginFieldsLists(self):
        if hasattr(self.getComboboxData('originLayerSelect'),'dataProvider'):
            self._populateTableFieldsList('originLayerSelect', self.tableViewOriginLayerFields)
    
    def populateTargetFieldsLists(self):
        if hasattr(self.getComboboxData('targetLayerSelect'),'dataProvider'):
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
        
    def getCurrentInputValues(self):
        toRet = {}
        #get stpe0 values
        toRet['step0']={
                        'title':self.tr('Selection Origin -> Target'),
                        'originLayerSelect':self.getComboboxData('originLayerSelect'),
                        'targetLayerSelect':self.getComboboxData('targetLayerSelect'),
                        }
        #get stpe1 values
        toRet['step1']={
                        'title':self.tr('Selection Geometry operation'),
                        'geoprocessingTypeData':self.getGeoprocessingTypeData()
                        }
        #get stpe2 values
        toRet['step2']={
                        'title':self.tr('Selection fields'),
                        'originLayerFields':self.getSelectedFields('tableViewOriginLayerFields'),
                        'targetLayerFields':self.getSelectedFields('tableViewTargetLayerFields'),
                        }
         #get stpe3 values
        toRet['step3']={
                        'title':self.tr('Selection Output'),
                        'selectOutputType':self.getOutputType(),
                        'outputShapeFile':self.outputShapeFile.text(),
                        'outputSpatialite':self.outputSpatialite.text(),
                        'outputPostgis':self.getPostgisOutputValues()
                        }
        return toRet
    
    def getPostgisOutputValues(self):
        return {
                 'connection':self.getComboboxText('dbConnectionSelect'),
                 'schema':self.getComboboxText('dbSchemaSelect'),
                 'table': self.tableName.text(),
                 'geoColumn':self.geoColumnName.text(),
                 }
        
    def createRuntimeStepLog(self):
        #take current inputs values
        currentInputValues = self.getCurrentInputValues()
        self.runtimeStepBrowser.clear()
        self.addRuntimeStepLog("<h3 style='border-style:dotted; border-color:red;'><u>1) %s:</u></h3>" % currentInputValues['step0']['title'])
        self.addRuntimeStepLog("<span>ORIGIN LAYER: %s (<b>%s</b>)[Provider:%s, Epsg:%s] </span>" % (currentInputValues['step0']['originLayerSelect'].name(),getVectorTypeAsString(currentInputValues['step0']['originLayerSelect']),currentInputValues['step0']['originLayerSelect'].dataProvider().storageType(),str(currentInputValues['step0']['originLayerSelect'].crs().postgisSrid())))
        self.addRuntimeStepLog("<span>TARGET LAYER: %s (<b>%s</b>)[Provider:%s, Epsg:%s] </span>" % (currentInputValues['step0']['targetLayerSelect'].name(),getVectorTypeAsString(currentInputValues['step0']['targetLayerSelect']),currentInputValues['step0']['targetLayerSelect'].dataProvider().storageType(),str(currentInputValues['step0']['targetLayerSelect'].crs().postgisSrid())))
        self.addRuntimeStepLog("<h3><u>2) %s:</u></h3>" % currentInputValues['step1']['title'])
        self.addRuntimeStepLog("<span>GEOPORCESSING TYPE: <b>%s</b> </span>" % (currentInputValues['step1']['geoprocessingTypeData']))
        self.addRuntimeStepLog("<h3><u>3) %s:</u></h3>" % currentInputValues['step2']['title'])
        self.addRuntimeStepLog("<h4>Origin Layer Fields:</h4>")
        for f in currentInputValues['step2']['originLayerFields'].values():
            self.addRuntimeStepLog("%s" % f.name())
        self.addRuntimeStepLog("<h4>Target Layer Fields:</h4>")
        for f in currentInputValues['step2']['targetLayerFields'].values():
            self.addRuntimeStepLog("%s" % f.name())
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
                #print fieldCalculatorDialog.mExistingFieldComboBox.currentText()
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
                itemName = QtGui.QStandardItem(fieldCalculatorDialog.mOutputFieldNameLineEdit.text())
                itemName.setData(QgsField(data['name'],TYPES[fieldCalculatorDialog.mOutputFieldTypeComboBox.currentIndex()],'',int(data['length']),int(data['precision'])))
                itemName.setCheckable(True)
                itemName.setCheckState(Qt.Checked)
                itemName.setSelectable(False)
                itemName.setEditable(False)
                itemType = QtGui.QStandardItem(data['type'])
                itemLength = QtGui.QStandardItem(str(data['length']))
                itemPrecision = QtGui.QStandardItem(str(data['precision']))
                itemExpression = QtGui.QStandardItem(data['expression'])
                #actions = QtGui.QStandardItem('actions')
                model = tableView.model()
                model.appendRow([itemName,itemType,itemLength,itemPrecision,itemExpression])
                #removeButton = QtGui.QPushButton(self.tr('Remove'),clicked=self.removeTableFieldsRow)
                #tableView.setIndexWidget(actions.index(),removeButton)
    
    def removeTableFieldsRow(self):
        print self.sender().parent()
            
    def openOutputShapeFileDialog(self):
        self.outputShapeFile.clear()
        ( outputShapeFile, encoding ) = self._openSaveDialog(self,'save')
        if outputShapeFile is None or encoding is None:
          return
        self.outputShapeFile.setText( outputShapeFile )
    
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
            fileDialog.setFileMode( QFileDialog.AnyFile )
        else:
            fileDialog.setFileMode( QFileDialog.ExistingFiles )
            fileDialog.setAcceptMode( QFileDialog.AcceptOpen )
                
        if not fileDialog.exec_() == QDialog.Accepted:
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
        
