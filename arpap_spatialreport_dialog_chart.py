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



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'arpap_spatialreport_dialog_chart.ui'))


class ARPAP_SpatialReportDialogChart(QtGui.QDialog, FORM_CLASS):

    webview = None
    chartTypes = dict()
    algorithm = None
    reslayer = list()
    
    def __init__(self, parent=None):
        super(ARPAP_SpatialReportDialogChart, self).__init__(parent)
        self.parent = parent
        self.algorithm = parent.algorithm
        self.reslayer = parent.reslayer
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
                           'Bar':self.tr('Bar (occurrences)'),
                           'Pie':self.tr('Pie (distribution)'),
                           }
        for type in self.chartTypes.keys():
            self.selectChartType.addItem(self.chartTypes[type],type)

    def populateCombosField(self):
        layer = self.reslayer[0]
        #populate category listview
        modelCategory = QtGui.QStandardItemModel(self.categoryFieldListView)
        modelValue = QtGui.QStandardItemModel(self.valueFieldListView) 
        self.categoryFieldListView.setModel(modelCategory)
        self.valueFieldListView.setModel(modelValue)
        for field in layer.pendingFields():
            itemCategory = QtGui.QStandardItem(field.name())
            itemValue = QtGui.QStandardItem(field.name())
            modelCategory.appendRow(itemCategory)
            modelValue.appendRow(itemValue)
        


    def generateChart(self):
        scene = QtGui.QGraphicsScene()
        self.graphicsView.setScene(scene)
        
        
        chart = pygal.StackedLine(fill=True, interpolate='cubic', style=pygal.style.BlueStyle)
        chart.add('A', [1, 3,  5, 16, 13, 3,  7])
        chart.add('B', [5, 2,  3,  2,  5, 7, 17])
        chart.add('C', [6, 10, 9,  7,  3, 1,  0])
        chart.add('D', [2,  3, 5,  9, 12, 9,  5])
        chart.add('E', [7,  4, 2,  1,  2, 10, 0])
        
        line_chart = pygal.Line(style=pygal.style.BlueStyle)
        line_chart.title = 'Browser usage evolution (in %)'
        line_chart.x_labels = map(str, range(2002, 2013))
        line_chart.add('Firefox', [None, None, 0, 16.6,   25,   31, 36.4, 45.5, 46.3, 42.8, 37.1])
        line_chart.add('Chrome',  [None, None, None, None, None, None,    0,  3.9, 10.8, 23.8, 35.3])
        line_chart.add('IE',      [85.8, 84.6, 84.7, 74.5,   66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
        line_chart.add('Others',  [14.2, 15.4, 15.3,  8.9,    9, 10.4,  8.9,  5.8,  6.7,  6.8,  7.5])
        
        self.webview = QGraphicsWebView()
        self.webview.resize(self.graphicsView.width()-20,self.graphicsView.height()-20)
        path = os.path.dirname(__file__)+'/js/'
        html = '''
        <script type="text/javascript" src="svg.jquery.js"></script>
        <script type="text/javascript" src="pygal-tooltips.js"></script>
        '''+line_chart.render()
        
        self.webview.setHtml(html,baseUrl=QUrl().fromLocalFile(path))
        self.webview.setFlags(QtGui.QGraphicsItem.ItemClipsToShape)
        self.webview.setCacheMode(QtGui.QGraphicsItem.NoCache)
        frame = self.webview.page().mainFrame()
        frame.setScrollBarPolicy(Qt.Vertical,Qt.ScrollBarAlwaysOff)
        frame.setScrollBarPolicy(Qt.Horizontal,Qt.ScrollBarAlwaysOff)
        
        
        
        scene.addItem(self.webview)
        self.graphicsView.show()
        
    def savepng(self):
        p = QtGui.QPixmap.grabWidget(self.graphicsView)
        out = p.scaled(QSize(1000,1000))
        res = out.save('/home/walter/chart.png')
        
        

        
    
    
   
        
            
    
        

        