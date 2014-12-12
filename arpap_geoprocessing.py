# -*- coding: utf-8 -*-
"""
***************************************************************************
    arpap_geoprocessing.py
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from processing.algs.qgis.Intersection import Intersection as ProcessingIntersection, wkbTypeGroups
from processing.gui.RenderingStyles import RenderingStyles
from processing.core.parameters import ParameterVector, Parameter
from processing.core.outputs import OutputVector
from processing.core.ProcessingLog import ProcessingLog
from processing.core.ProcessingConfig import ProcessingConfig
from processing.tools import dataobjects, vector
from processing.tools.vector import _toQgsField

class SpatialiteWriter(vector.VectorWriter):

    def __init__(self, fileName, encoding, fields, geometryType,
                 crs, options=None):
        self.fileName = fileName
        self.isMemory = False
        self.memLayer = None
        self.writer = None

        if encoding is None:
            settings = QSettings()
            encoding = settings.value('/Processing/encoding', 'System', type=str)

        formats = QgsVectorFileWriter.supportedFiltersAndFormats()
        OGRCodes = {}
        for (key, value) in formats.items():
            extension = unicode(key)
            extension = extension[extension.find('*.') + 2:]
            extension = extension[:extension.find(' ')]
            OGRCodes[extension] = value

        extension = self.fileName[self.fileName.rfind('.') + 1:]
        if extension not in OGRCodes:
            extension = 'sqlite'
            self.filename = self.filename + 'sqlite'

        qgsfields = QgsFields()
        for field in fields:
            qgsfields.append(_toQgsField(field))

        self.writer = QgsVectorFileWriter(self.fileName, encoding,
            qgsfields, geometryType, crs, OGRCodes[extension],["SPATIALITE=YES",])



class OutputSpatialite(OutputVector):
    def getVectorWriter(self, fields, geomType, crs, options=None):
        if self.encoding is None:
            settings = QSettings()
            self.encoding = settings.value('/Processing/encoding', 'System', str)
    
        w = SpatialiteWriter(self.value, self.encoding, fields, geomType,
                         crs, options)
        self.memoryLayer = w.memLayer
        return w
    

class ParameterList(Parameter):

    def __init__(self, name='', description=''):
        Parameter.__init__(self, name, description)
        self.value = None

    def setValue(self, value):
        self.value = value
        return True

    def getValueAsCommandLineParameter(self):
        return '"' + unicode(self.value) + '"'

class ParameterObject(ParameterList):
    pass

def combineVectorFields(fieldsA, fieldsB):
    fields = []
    fields.extend(fieldsA.values())
    namesA = [unicode(f.name()).lower() for f in fieldsA.values()]
    for field in fieldsB.values():
        name = unicode(field.name()).lower()
        if name in namesA:
            idx = 2
            newName = name + '_' + unicode(idx)
            while newName in namesA:
                idx += 1
                newName = name + '_' + unicode(idx)
            field = QgsField(newName, field.type(), field.typeName())
        fields.append(field)

    return fields

class Intersection(ProcessingIntersection):
    INPUT = 'ORIGIN'
    INPUT2 = 'TARGET'
    FIELDSINPUT1 = 'FIELDSORIGIN'
    FIELDSINPUT2 = 'FIELDSTARGET'
    OUTPUT = 'OUTPUT'
    
    outputFormats = {
               'Shape File':OutputVector,
               'Spatialite':OutputSpatialite,
               'Postgis':OutputVector,
               }
    
    outputType = 'Shape File'
    
    name = 'Intersection'
    group = 'Vector overlay tools'
    
    def __init__(self,outputType):
        self.outputType = outputType
        ProcessingIntersection.__init__(self)
    
    def processAlgorithm(self, progress):
        vlayerA = dataobjects.getObjectFromUri(
                self.getParameterValue(self.INPUT))
        vlayerB = dataobjects.getObjectFromUri(
                self.getParameterValue(self.INPUT2))
        fieldsLayerA = self.getParameterValue(self.FIELDSINPUT1)
        fieldsLayerB = self.getParameterValue(self.FIELDSINPUT2)
        
        vproviderA = vlayerA.dataProvider()
        fields = combineVectorFields(fieldsLayerA, fieldsLayerB)
        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(fields,
                vproviderA.geometryType(), vproviderA.crs())
        inFeatA = QgsFeature()
        inFeatB = QgsFeature()
        outFeat = QgsFeature()
        index = vector.spatialindex(vlayerB)
        nElement = 0
        selectionA = vector.features(vlayerA)
        nFeat = len(selectionA)
        progress.setText(QCoreApplication.translate('ArpaGeoprocessing', 'Running algorithm...'))
        for inFeatA in selectionA:
            nElement += 1
            progress.setPercentage(nElement / float(nFeat) * 100)
            geom = QgsGeometry(inFeatA.geometry())
            atMapA = inFeatA.attributes()
            atMapA = [atMapA[i] for i in fieldsLayerA.keys()]
            intersects = index.intersects(geom.boundingBox())
            for i in intersects:
                request = QgsFeatureRequest().setFilterFid(i)
                inFeatB = vlayerB.getFeatures(request).next()
                tmpGeom = QgsGeometry(inFeatB.geometry())
                try:
                    if geom.intersects(tmpGeom):
                        atMapB = inFeatB.attributes()
                        atMapB = [atMapB[i] for i in fieldsLayerB.keys()]
                        int_geom = QgsGeometry(geom.intersection(tmpGeom))
                        if int_geom.wkbType() == QGis.WKBUnknown:
                            int_com = geom.combine(tmpGeom)
                            int_sym = geom.symDifference(tmpGeom)
                            int_geom = QgsGeometry(int_com.difference(int_sym))
                        try:
                            if int_geom.wkbType() in wkbTypeGroups[wkbTypeGroups[int_geom.wkbType()]]:
                                outFeat.setGeometry(int_geom)
                                attrs = []
                                attrs.extend(atMapA)
                                attrs.extend(atMapB)
                                outFeat.setAttributes(attrs)
                                writer.addFeature(outFeat)
                        except:
                            ProcessingLog.addToLog(ProcessingLog.LOG_INFO, 'Feature geometry error: One or more output features ignored due to invalid geometry.')
                            continue
                except:
                    break


        del writer
    
    def defineCharacteristics(self):
        self.addParameter(ParameterVector(self.INPUT, 'Origin layer',
                          [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterVector(self.INPUT2,
                          'Target layer',
                          [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterObject(self.FIELDSINPUT1,'Fields Origin Layer'))
        self.addParameter(ParameterObject(self.FIELDSINPUT2,'Fields Target Layer'))
        #select the output
        self.addOutput(self.outputFormats[self.outputType](self.OUTPUT, self.name))
    
class Touch(Intersection):
    
    name = 'Touch'
    group = 'Vector overlay tools'
    
    def processAlgorithm(self, progress):
        vlayerA = dataobjects.getObjectFromUri(
                self.getParameterValue(self.INPUT))
        vlayerB = dataobjects.getObjectFromUri(
                self.getParameterValue(self.INPUT2))
        fieldsLayerA = self.getParameterValue(self.FIELDSINPUT1)
        fieldsLayerB = self.getParameterValue(self.FIELDSINPUT2)
        vproviderA = vlayerA.dataProvider()
        fields = combineVectorFields(fieldsLayerA, fieldsLayerB)
        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(fields,
                vproviderA.geometryType(), vproviderA.crs())
        inFeatA = QgsFeature()
        inFeatB = QgsFeature()
        outFeat = QgsFeature()
        nElement = 0
        selectionA = vector.features(vlayerA)
        selectionB = vector.features(vlayerB)
        nFeat = len(selectionA)
        for inFeatA in selectionA:
            nElement += 1
            progress.setPercentage(nElement / float(nFeat) * 100)
            geom = QgsGeometry(inFeatA.geometry())
            atMapA = inFeatA.attributes()
            atMapA = [atMapA[i] for i in fieldsLayerA.keys()]
            for inFeatB in selectionB:
                geomTarget = QgsGeometry(inFeatB.geometry())
                try:
                    if geom.touches(geomTarget):
                        atMapB = inFeatB.attributes()
                        atMapB = [atMapB[i] for i in fieldsLayerB.keys()]
                        try:
                            outFeat.setGeometry(geom)
                            attrs = []
                            attrs.extend(atMapA)
                            attrs.extend(atMapB)
                            outFeat.setAttributes(attrs)
                            writer.addFeature(outFeat)
                        except:
                            ProcessingLog.addToLog(ProcessingLog.LOG_INFO, 'Feature geometry error: One or more output features ignored due to invalid geometry.')
                            continue
                except:
                    break
        del writer


class Contain(Touch):
    
    name = 'Contain'
    group = 'Vector overlay tools'
    
    def processAlgorithm(self, progress):
        vlayerA = dataobjects.getObjectFromUri(
                self.getParameterValue(self.INPUT))
        vlayerB = dataobjects.getObjectFromUri(
                self.getParameterValue(self.INPUT2))
        fieldsLayerA = self.getParameterValue(self.FIELDSINPUT1)
        fieldsLayerB = self.getParameterValue(self.FIELDSINPUT2)
        vproviderA = vlayerA.dataProvider()

        fields = combineVectorFields(fieldsLayerA, fieldsLayerB)
        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(fields,
                vproviderA.geometryType(), vproviderA.crs())
        inFeatA = QgsFeature()
        inFeatB = QgsFeature()
        outFeat = QgsFeature()
        nElement = 0
        selectionA = vector.features(vlayerA)
        selectionB = vector.features(vlayerB)
        nFeat = len(selectionA)
        for inFeatA in selectionA:
            nElement += 1
            progress.setPercentage(nElement / float(nFeat) * 100)
            geom = QgsGeometry(inFeatA.geometry())
            atMapA = inFeatA.attributes()
            atMapA = [atMapA[i] for i in fieldsLayerA.keys()]
            for inFeatB in selectionB:
                geomTarget = QgsGeometry(inFeatB.geometry())
                try:
                    if geomTarget.contains(geom):
                        atMapB = inFeatB.attributes()
                        atMapA = [atMapB[i] for i in fieldsLayerB.keys()]
                        try:
                            outFeat.setGeometry(geom)
                            attrs = []
                            attrs.extend(atMapA)
                            attrs.extend(atMapB)
                            outFeat.setAttributes(attrs)
                            writer.addFeature(outFeat)
                        except:
                            ProcessingLog.addToLog(ProcessingLog.LOG_INFO, 'Feature geometry error: One or more output features ignored due to invalid geometry.')
                            continue
                except:
                    break
        del writer
    



def handleAlgorithmResults(alg, progress=None, showResults=True):
    wrongLayers = []
    reslayers = []
    if progress is None:
        progress = SilentProgress()
    progress.setText(QCoreApplication.translate('ArpaGeoprocessing', 'Loading resulting layer'))
    i = 0
    for out in alg.outputs:
        progress.setPercentage(100 * i / float(len(alg.outputs)))
        if out.hidden or not out.open:
            continue
        if isinstance(out, (OutputVector)):
            try:
                if ProcessingConfig.getSetting(
                        ProcessingConfig.USE_FILENAME_AS_LAYER_NAME):
                    name = os.path.basename(out.value)
                else:
                    name = out.description
                layer = dataobjects.load(out.value, name, alg.crs,
                        RenderingStyles.getStyle(alg.commandLineName(),
                        out.name))
                    
                reslayers.append(layer)
            except Exception, e:
                wrongLayers.append(out)
                print e
            i += 1
    return reslayers
     