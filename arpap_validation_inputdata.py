# -*- coding: utf-8 -*-
"""
***************************************************************************
    arpap_validation_input.py
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

import sys
import os.path
import fTools
if os.path.abspath(os.path.dirname(fTools.__file__) + '/tools') not in sys.path:
    sys.path.append(os.path.abspath(os.path.dirname(fTools.__file__) + '/tools')) 
from ftools_utils  import getVectorTypeAsString

class ValidationInputdata():
    
    dlg = None
    errorMessages = []
    matrixRulesGeoprocessing = {
                                'mapping':{'Polygon': 0,'LineString' : 1,'Point': 2},
                                'Intersection':[[True,False,False],[True,True,False],[True,True,True]], 
                                'Touch':[[True,True,True],[True,True,True],[True,True,True]],
                                'Contain':[[True,False,False],[True,True,False],[True,True,True]]
    }
    
    
    def __init__(self,dlg,transletor):
        self.dlg = dlg
        self.tr = transletor
    
    def getErrors(self):
        toRet = self.errorMessages
        self.resetErrors()
        return toRet
    
    def resetErrors(self):
        self.errorMessages = []

    def validateStep0(self):
        #check if comboBoxes are empties
        toRes = True
        if self.dlg.originLayerSelect.currentIndex() == -1:
            toRes = False
            self.errorMessages.append(self.tr('Origin Layer not to be empty'))
            
        if self.dlg.targetLayerSelect.currentIndex() == -1:
            toRes = False
            self.errorMessages.append(self.tr('Target Layer not to be empty'))

        #check SR between layers:
        if toRes:
            originSR = self.dlg.getComboboxData('originLayerSelect').crs().postgisSrid()
            targetSR = self.dlg.getComboboxData('targetLayerSelect').crs().postgisSrid()
            if originSR != targetSR:
                toRes = False
                self.errorMessages.append(self.tr('Origin and Target Layer have different SR'))

        return toRes
    
    #def validateStep1(self):
        #return self.geoprocessingDataType()
    
    def validateStep3(self):
        toRes = True
        if self.dlg.getOutputType() == 'Shape File':
            if not self.dlg.outputShapeFile.text():
                toRes = False
                self.errorMessages.append(self.tr('Output Shape File path not to be empty'))
        elif self.dlg.getOutputType() == 'Spatialite':
            if not self.dlg.outputSpatialite.text():
                toRes = False
                self.errorMessages.append(self.tr('Output Spatialite file path not to be empty'))
        else:
            if not self.dlg.tableName.text():
                toRes = False
                self.errorMessages.append(self.tr('Output Postgis Table name not to be empty'))
            if not self.dlg.geoColumnName.text():
                toRes = False
                self.errorMessages.append(self.tr('Output Postgis Geo column name not to be empty'))
        return toRes
    
    def validateChart(self,chartType):
        toRes = True
        if chartType == 'bar':
            if not self.dlg.getSelectedListViewItem('category'):
                toRes = False
                self.errorMessages.append(self.tr('For Bar chart type, you have to select a Category combobox item'))
        else:
            itemValue = self.dlg.getSelectedListViewItem('value')
            if not self.dlg.getSelectedListViewItem('category') or not itemValue:
                toRes = False
                self.errorMessages.append(self.tr('For Pie chart type, you have to select a Category combobox item and a Value combobox item'))
            if itemValue.data().typeName() not in ('Integer','Double','Real'):
                toRes = False
                self.errorMessages.append(self.tr('For Pie chart type, you have to select a numeric Value combobox item'))
        return toRes      
        
    def geoprocessingDataType(self):
        geoprocessingType = self.dlg.getGeoprocessingTypeData()
        originLayerType = getVectorTypeAsString(self.dlg.getComboboxData('originLayerSelect'))
        targetLayerType = getVectorTypeAsString(self.dlg.getComboboxData('targetLayerSelect'))
        return self.matrixRulesGeoprocessing[geoprocessingType][self.matrixRulesGeoprocessing['mapping'][originLayerType]][self.matrixRulesGeoprocessing['mapping'][targetLayerType]]
            