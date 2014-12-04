# -*- coding: utf-8 -*-
"""
***************************************************************************
    arpap_spatialreport_fieldcalculator_dialog.py
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
from PyQt4.QtCore import QObject,SIGNAL, Qt, QVariant
from qgis.core import *
from qgis.gui import *



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qgsfieldcalculatorbase.ui'))


class ARPAP_SpatialReportFieldCalculatorDialog(QtGui.QDialog, FORM_CLASS):
    
    TYPE_NAMES = ['Float', 'Integer', 'String', 'Date']
    TYPES = [QVariant.Double, QVariant.Int, QVariant.String, QVariant.Date]
    
    def __init__(self, layer):
        """Constructor."""
        QtGui.QDialog.__init__(self)
        self.layer = layer
        self.setupUi(self)
        QObject.connect(self.mButtonBox, SIGNAL('accepted()'),self.success)
        self.updateLayer()
        self.populateComboFieldType()
        
    def updateLayer(self):
        self.builder.setLayer(self.layer)
        self.builder.loadFieldNames()

        self.populateFields()
        #populateOutputFieldTypes()
    def populateComboFieldType(self):
        self.mOutputFieldTypeComboBox.blockSignals(True)
        for t in self.TYPE_NAMES:
            self.mOutputFieldTypeComboBox.addItem(t)
        self.mOutputFieldTypeComboBox.blockSignals(False)
                                                   
    def success(self):
        self.value = self.mOutputFieldTypeComboBox.itemData(self.mOutputFieldTypeComboBox.currentIndex())
    
    def populateFields(self):
        if self.layer is None:
            return

        fields = self.layer.pendingFields()
        for f in fields:
            self.mExistingFieldComboBox.addItem(f.name())
        
    
   
        
            
    
        

        