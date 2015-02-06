# -*- coding: utf-8 -*-
"""
***************************************************************************
    arpap_spatialreport_chart_dialog.py
    ---------------------
    Date                 : December 2014
    Copyright            : (C) 2014 by Walter Lorenzetti Gis3W
    Email                : lorenzetti at gis3w dot it
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
__author__ = 'Walter Lorenzetti'
__date__ = 'December 2014'
__copyright__ = '(C) 2014, Walter Lorenzetti Gis3w'

# This will get replaced with a git SHA1 when you do a git archive
 
__revision__ = '$Format:%H$'

import os
import sys
from PyQt4 import QtGui, uic
from PyQt4.QtWebKit import QGraphicsWebView
from PyQt4.QtCore import QObject,SIGNAL, Qt, QVariant, QUrl, QSize
from qgis.core import *
from qgis.gui import *
from pygal import style
from arpap_validation_inputdata import ValidationInputdata
import numpy
import csv
from chart import bar,pie



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'arpap_spatialreport_dialog_chart.ui'))


class ARPAP_SpatialReportDialogChart(QtGui.QDialog, FORM_CLASS):

    webview = None
    chartTypes = dict()
    algorithm = None
    reslayer = list()
    modelCategory = None
    modelValue = None
    validation = None
    chartGenerated = False
    mapChartType = {'bar':bar,'pie':pie}
    
    def __init__(self, parent=None):
        super(ARPAP_SpatialReportDialogChart, self).__init__(parent)
        self.parent = parent
        self.algorithm = parent.algorithm
        self.reslayer = parent.reslayer
        self.validation = ValidationInputdata(self,self.tr)
        self.setupUi(self)
        self.manageGui()
    
    
        
        
    def manageGui(self):
        self.chartGeneratorButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/histogram.png'))
        self.statisticsGeneratorButton.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/mActionOpenTable.png'))
        self.savePngFile.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/mActionFileSave.png'))
        self.saveCSVFile.setIcon(QtGui.QIcon(':/plugins/ARPAP_SpatialReport/icons/mActionFileSave.png'))
        QObject.connect(self.chartGeneratorButton, SIGNAL('clicked()'),self.generateChart)
        QObject.connect(self.statisticsGeneratorButton, SIGNAL('clicked()'),self.generateStatistics)
        QObject.connect(self.savePngFile, SIGNAL('clicked()'),self.savepng)
        QObject.connect(self.saveCSVFile, SIGNAL('clicked()'),self.saveCSV)
        self.populateChartTypesCombo()
        self.populateCombosField()
        #manage resizeEvent QWebview
        def onResizeWebview(e):
            if self.chartGenerated:
                self.generateChart()
        self.graphicsView.resizeEvent = onResizeWebview 
        
    def populateChartTypesCombo(self):
        self.chartTypes = {
                           'bar':self.tr('Bar (occurrences)'),
                           'pie':self.tr('Pie (distribution)'),
                           }
        for type in self.chartTypes.keys():
            self.selectChartType.addItem(self.chartTypes[type],type)
            
    def getChartType(self):
        return self.selectChartType.itemData(self.selectChartType.currentIndex())
    
    def getSelectedListViewItem(self,listViewName):
        
        model_index = getattr(self,listViewName.lower()+'FieldListView').currentIndex()
        if model_index.row() != -1:
            return getattr(self,'model'+listViewName.capitalize()).itemFromIndex(model_index)

    def populateCombosField(self):
        layer = self.reslayer[0]
        #populate category listview
        self.modelCategory = QtGui.QStandardItemModel(self.categoryFieldListView)
        self.modelValue = QtGui.QStandardItemModel(self.valueFieldListView) 
        self.categoryFieldListView.setModel(self.modelCategory)
        self.valueFieldListView.setModel(self.modelValue)
        for field in layer.pendingFields():
            itemCategory = QtGui.QStandardItem(field.name())
            itemCategory.setData(field)
            itemValue = QtGui.QStandardItem(field.name())
            itemValue.setData(field)
            self.modelCategory.appendRow(itemCategory)
            self.modelValue.appendRow(itemValue)
        

    def generateChart(self):
        scene = QtGui.QGraphicsScene()
        self.graphicsView.setScene(scene)
        
        #select data adn chart type
        chartType = self.getChartType()
        if self.validation.validateChart(chartType):
            chart = self.mapChartType[chartType]()
            
             
            self.webview = QGraphicsWebView()
            self.webview.resize(self.graphicsView.width()-20,self.graphicsView.height()-20)
            path = os.path.dirname(__file__)+'/js/'
            chartData = getattr(self,chartType + 'ChartData' )()
            chart.setData(chartData)
            self.webview.setHtml(chart.getHTML(),baseUrl=QUrl().fromLocalFile(path))
            self.webview.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
            self.webview.setCacheMode(QtGui.QGraphicsItem.NoCache)
            frame = self.webview.page().mainFrame()
            frame.setScrollBarPolicy(Qt.Vertical,Qt.ScrollBarAlwaysOff)
            frame.setScrollBarPolicy(Qt.Horizontal,Qt.ScrollBarAlwaysOff)        
            scene.addItem(self.webview)
            self.graphicsView.show()
            self.savePngFile.setEnabled(True)
            self.chartGenerated = True
        else:
            self.showValidateErrors()
        
    def barChartData(self):
        categoryItem = self.getSelectedListViewItem('category')
        layer = self.reslayer[0]
        features = layer.getFeatures()
        occourences = dict()
        for f in features:
            value = f.attribute(categoryItem.text())
            if value not in occourences:
                occourences[value] = 0
            occourences[value] += 1 
            
        chartData = {'values':[{'label':k,'value':occourences[k]} for k in occourences.keys()]}    
        return [chartData]
    
    def pieChartData(self):
        categoryItem = self.getSelectedListViewItem('category')
        valueItem = self.getSelectedListViewItem('value')
        layer = self.reslayer[0]
        features = layer.getFeatures()
        occourences = dict()
        totValue = 0
        for f in features:
            key = f.attribute(categoryItem.text()) 
            if not key:
                key = self.tr('Unknown')
            value = f.attribute(valueItem.text())
            if key not in occourences:
                occourences[key] = 0
            if not value:
                value = 0
            occourences[key] += value
            totValue += value
            
        chartData = [{'key':k,'y':float(float(occourences[k])/float(totValue))} for k in occourences.keys()] 
        return chartData
    
    def generateStatistics(self):
        categoryItem = self.getSelectedListViewItem('category')
        valueItem = self.getSelectedListViewItem('value')
        layer = self.reslayer[0]
        features = layer.getFeatures()
        occourences = dict()
        for f in features:
            key = f.attribute(categoryItem.text()) 
            if not key:
                key = self.tr('Unknown')
            value = f.attribute(valueItem.text())
            if key not in occourences:
                occourences[key] = list()
            if not value:
                value = 0
            occourences[key].append(value)
        # statistics calcs
        self.statistics = dict()
        model = QtGui.QStandardItemModel(self.statisticsTableView)
        self.statisticsTableView.setModel(model)
        c = 0
        self.headersFieldsTableMethods = {
                                     self.tr('Sum'):sum,
                                     self.tr('Min'):min,
                                     self.tr('Max'):max,
                                     self.tr('Median'):numpy.median,
                                     self.tr('Mean'):numpy.mean,
                                     self.tr('Standard deviation'):numpy.std
                                     }
        print occourences
        for columnName in self.headersFieldsTableMethods:
            model.setHorizontalHeaderItem(self.headersFieldsTableMethods.keys().index(columnName),QtGui.QStandardItem(columnName))
        for key in occourences:
            if key not in self.statistics:
                self.statistics[key] = dict()
            rowToAppend = list()
            for func in self.headersFieldsTableMethods:
                self.statistics[key][func] = str(self.headersFieldsTableMethods[func](occourences[key]))
                rowToAppend.append(QtGui.QStandardItem(self.statistics[key][func]))
            model.appendRow(rowToAppend)
            model.setVerticalHeaderItem(c,QtGui.QStandardItem(str(key)))
            c += 1
        self.saveCSVFile.setEnabled(True)
    
    def sum(self,data):
        return sum(data)
    def min(self,data):
        return min(data)
    def max(self,data):
        return max(data)
        
    def savepng(self):
        dialog = QtGui.QFileDialog()                                              
        dialog.setAcceptMode(1)
        dialog.setDefaultSuffix("png")
        dialog.setNameFilters(["PNG files (*.png)", "All files (*)"])
        if dialog.exec_() == 0:                                            
            return
        pathFileToSave = dialog.selectedFiles()[0]
        p = QtGui.QPixmap.grabWidget(self.graphicsView)
        res = p.save(pathFileToSave)
        
    def saveCSV(self):
        dialog = QtGui.QFileDialog()                                              
        dialog.setAcceptMode(1)
        dialog.setDefaultSuffix("csv")
        dialog.setNameFilters(["CSV files (*.csv)", "All files (*)"])
        if dialog.exec_() == 0:                                             
            return
        pathFileToSave = dialog.selectedFiles()[0]
        fileCSV = open(pathFileToSave, 'wb')
        compilatorCSV = csv.writer( fileCSV, delimiter=';' )
        header = ['']
        header.extend(self.headersFieldsTableMethods.keys())
        compilatorCSV.writerow(header)
        for i in self.statistics:   
            row = [i]
            dataRow = [x.encode('utf-8') for x in self.statistics[i].values()]   
            row.extend(dataRow)                     
            compilatorCSV.writerow(row)
        fileCSV.close()
        
    def showValidateErrors(self):
        QtGui.QMessageBox.warning( self, self.tr("ARPA Spatial Report"), self.tr( "Validation error:\n" ) + ';\n'.join(self.validation.getErrors()) )

        
        

        
    
    
   
        
            
    
        

        