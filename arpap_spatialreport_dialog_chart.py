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
import pygal
from pygal import style
from arpap_validation_inputdata import ValidationInputdata



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
        QObject.connect(self.chartGeneratorButton, SIGNAL('clicked()'),self.generateChart)
        QObject.connect(self.savePngFile, SIGNAL('clicked()'),self.savepng)
        self.populateChartTypesCombo()
        self.populateCombosField()
        
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
            chart = getattr(self, chartType+'ChartGenerator')()
            
             
            self.webview = QGraphicsWebView()
            self.webview.resize(self.graphicsView.width()-20,self.graphicsView.height()-20)
            path = os.path.dirname(__file__)+'/js/'
            html = '''
            <script type="text/javascript" src="svg.jquery.js"></script>
            <script type="text/javascript" src="pygal-tooltips.js"></script>
            '''+chart.render()
            
            self.webview.setHtml(html,baseUrl=QUrl().fromLocalFile(path))
            self.webview.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
            self.webview.setCacheMode(QtGui.QGraphicsItem.NoCache)
            frame = self.webview.page().mainFrame()
            frame.setScrollBarPolicy(Qt.Vertical,Qt.ScrollBarAlwaysOff)
            frame.setScrollBarPolicy(Qt.Horizontal,Qt.ScrollBarAlwaysOff)        
            scene.addItem(self.webview)
            self.graphicsView.show()
        else:
            self.showValidateErrors()
        
    def barChartGenerator(self):
        categoryItem = self.getSelectedListViewItem('category')
        layer = self.reslayer[0]
        features = layer.getFeatures()
        occourences = dict()
        for f in features:
            value = f.attribute(categoryItem.text())
            if value not in occourences:
                occourences[value] = 0
            occourences[value] += 1 
            
        
        chart = pygal.Bar(fill=True, show_legend=False, style=style.BlueStyle)
        chart.x_labels = map(str, occourences.keys())
        chart.add(categoryItem.text(), occourences.values())
        
        return chart
    
    def pieChartGenerator(self):
        categoryItem = self.getSelectedListViewItem('category')
        valueItem = self.getSelectedListViewItem('value')
        layer = self.reslayer[0]
        features = layer.getFeatures()
        occourences = dict()
        totValue = 0
        for f in features:
            key = f.attribute(categoryItem.text()) 
            value = f.attribute(valueItem.text())
            if key not in occourences:
                occourences[key] = 0
            occourences[key] += value
            totValue += value
            
        
        chart = pygal.Pie(fill=True, show_legend=False, style=style.BlueStyle)
        print occourences
        for key in occourences:
            chart.add(key, float(float(occourences[key])/float(totValue)))
        
        return chart
        
    def savepng(self):
        p = QtGui.QPixmap.grabWidget(self.graphicsView)
        out = p.scaled(QSize(1000,1000))
        res = out.save('/home/walter/chart.png')
        
    def showValidateErrors(self):
        QtGui.QMessageBox.warning( self, self.tr("ARPA Spatial Report"), self.tr( "Validation error:\n" ) + ';\n'.join(self.validation.getErrors()) )

        
        

        
    
    
   
        
            
    
        

        