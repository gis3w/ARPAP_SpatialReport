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
from qgis.utils import iface
from processing.algs.qgis.Intersection import Intersection as ProcessingIntersection, wkbTypeGroups
from processing.gui.RenderingStyles import RenderingStyles
from processing.core.parameters import ParameterVector, Parameter
from processing.core.outputs import OutputVector
from processing.core.ProcessingLog import ProcessingLog
from processing.core.ProcessingConfig import ProcessingConfig
from processing.core.GeoAlgorithmExecutionException import \
        GeoAlgorithmExecutionException
from processing.tools import dataobjects, vector
from processing.tools.vector import _toQgsField
from psql.arpap_psql import arpap_spatialreport_psql


TYPE_NAMES = ['Float', 'Integer', 'String', 'Date']
TYPES = [QVariant.Double, QVariant.Int, QVariant.String, QVariant.Date]

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
'''
class PostgisWriter(vector.VectorWriter):

    def __init__(self, dbData, encoding, fields, geometryType,
                 crs, options=None):
        self.dbData = dbData
        self.isMemory = False
        self.memLayer = None
        self.writer = None
        self.crs = crs
        
        class PGWriter():
            
            fromWKBType = {
                           QGis.WKBPoint : "Point",
                           QGis.WKBLineString: "LineString",
                           QGis.WKBPolygon: "Polygon", 
                           QGis.WKBMultiPoint: "MultiPoint", 
                           QGis.WKBMultiLineString: "MultiLineString",
                           QGis.WKBMultiPolygon: "MultiPolygon"
                           }
            
            lmemory = None
            dp = None
            dbData = None
            
            def __init__(self,dbData,fields,geometryType,crs,encoding):
                self.dbData = dbData
                uri = self.fromWKBType[geometryType]+'?crs='+str(crs.authid()).lower()
                #del self.lmemory
                self.lmemory = QgsVectorLayer(uri,'postgis_temporary','memory')
                self.lmemory.setProviderEncoding(encoding)
                self.dp = self.lmemory.dataProvider()
                self.dp.addAttributes(fields)
                
            def addFeature(self,f):
                self.dp.addFeatures([f])
                #self.lmemory.addFeature(f)
                self.lmemory.updateExtents()

        self.writer = PGWriter(self.dbData,fields, geometryType, crs,encoding)
        
    def importDB(self):
        #instance URI
        outUri = QgsDataSourceURI()
        psql = self.dbData['PSQL']
        outUri.setConnection(psql.PSQLHost, psql.PSQLPort, psql.PSQLDatabase, psql.PSQLUsername, psql.PSQLPassword)
        outUri.setDataSource(self.dbData['schema'],self.dbData['table'],self.dbData['geoColumn'])
        uri = outUri.uri()
        
        options = {}
        if self.dbData['overwrite']:
            options['overwrite'] = True
        
               
        ret, errMsg = QgsVectorLayerImport.importLayer( self.writer.lmemory, uri, "postgres", self.crs, False, False)
        if errMsg:
            raise GeoAlgorithmExecutionException(str(errMsg))
        
        #if self.dbData['spatialIndex']:
            #psql.createSpatialIndex( (self.dbData['schema'], self.dbData['table']), self.dbData['geoColumn'] )
'''
        
                    
class PostgisWriter(vector.VectorWriter):

    def __init__(self, dbData, encoding, fields, geometryType,
                 crs, options=None):
        
        self.dbData = dbData
        self.isMemory = False
        self.memLayer = None
        self.writer = None
        self.fileName = 'tempImportDB'
        self.crs = crs
        self.uri = None

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

        extension = 'shp'
        self.fileName = ProcessingConfig.getSetting(ProcessingConfig.OUTPUT_FOLDER)+'/'+ self.fileName + '.'+extension
    

        qgsfields = QgsFields()
        for field in fields:
            qgsfields.append(_toQgsField(field))

        self.writer = QgsVectorFileWriter(self.fileName, encoding,
            qgsfields, geometryType, crs, OGRCodes['shp'])
        
        
    def importDB(self):
        #instance URI
        outUri = QgsDataSourceURI()
        psql = self.dbData['PSQL']
        outUri.setConnection(psql.PSQLHost, psql.PSQLPort, psql.PSQLDatabase, psql.PSQLUsername, psql.PSQLPassword)
        outUri.setDataSource(self.dbData['schema'],self.dbData['table'],self.dbData['geoColumn'])
        uri = outUri.uri()
        
        options = {}
        if self.dbData['overwrite']:
            options['overwrite'] = True
        del self.writer
        vlayer = QgsVectorLayer(self.fileName, "layer_name_you_like", "ogr")       
        ret, errMsg = QgsVectorLayerImport.importLayer(vlayer, uri, "postgres", self.crs, False, False,options)
        if errMsg:
            raise GeoAlgorithmExecutionException(str(errMsg))

        if self.dbData['spatialIndex']:
            psql.createSpatialIndex( (self.dbData['schema'], self.dbData['table']), self.dbData['geoColumn'] )
        

class OutputSpatialite(OutputVector):
    def getVectorWriter(self, fields, geomType, crs, options=None):
        if self.encoding is None:
            settings = QSettings()
            self.encoding = settings.value('/Processing/encoding', 'System', str)
    
        w = SpatialiteWriter(self.value, self.encoding, fields, geomType,
                         crs, options)
        self.memoryLayer = w.memLayer
        return w
    
class OutputPostgis(OutputVector):
    def __init__(self,name='', description='', hidden=False):
        OutputVector.__init__(self, name, description,hidden)
        self.hidden = True

        
    def getVectorWriter(self, fields, geomType, crs, options=None):
        if self.encoding is None:
            settings = QSettings()
            self.encoding = settings.value('/Processing/encoding', 'System', str)
    
        w = PostgisWriter(self.value, self.encoding, fields, geomType,
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

def combineVectorFieldsQgisFields(fieldsA, fieldsB):
    resFields = QgsFields()
    resMapBFields = dict()
    for q in fieldsA.values():
        resFields.append(q)
    namesA = [unicode(f.name()).lower() for f in fieldsA.values()]
    for field in fieldsB.values():
        origName = field.name()
        name = unicode(field.name()).lower()
        if name in namesA:
            idx = 2
            newName = name + '_' + unicode(idx)
            while newName in namesA:
                idx += 1
                newName = name + '_' + unicode(idx)
            field = QgsField(newName, field.type(), field.typeName())
        resMapBFields[field.name()] = origName
        resFields.append(field)

    return (resFields,resMapBFields)

class Intersection(ProcessingIntersection):
    INPUT = 'ORIGIN'
    INPUT2 = 'TARGET'
    FIELDSINPUT1 = 'FIELDSORIGIN'
    FIELDSINPUT2 = 'FIELDSTARGET'
    EXPRESSIONSINPUT1 = 'EXPRESSIONSORIGIN'
    EXPRESSIONSINPUT2 = 'EXPRESSIONSTARGET'
    OUTPUT = 'OUTPUT'
    
    outputFormats = {
               'Shape File':OutputVector,
               'Spatialite':OutputSpatialite,
               'Postgis':OutputPostgis,
               }
    
    outputType = 'Shape File'
    
    name = 'Intersection'
    group = 'Vector overlay tools'
    
    vlayerA = None
    vlayerB = None
    fieldsLayerA = None
    fieldsLayerB = None
    vproviderA = None
    inFeatA = QgsFeature()
    inFeatB = QgsFeature()
    outFeat = QgsFeature()
    fields = None
    mapBFields = None
    writer = None
    
    
    def __init__(self,outputType):
        self.outputType = outputType
        ProcessingIntersection.__init__(self)
        
    def initAlgorithm(self,progress):
        self.vlayerA = dataobjects.getObjectFromUri(
                self.getParameterValue(self.INPUT))
        self.vlayerB = dataobjects.getObjectFromUri(
                self.getParameterValue(self.INPUT2))
        self.fieldsLayerA = self.getParameterValue(self.FIELDSINPUT1)
        self.fieldsLayerB = self.getParameterValue(self.FIELDSINPUT2)
        self.expressionLayerA = self.getParameterValue(self.EXPRESSIONSINPUT1)
        self.expressionLayerB = self.getParameterValue(self.EXPRESSIONSINPUT2)
        # postgis parameter
        
        self.vproviderA = self.vlayerA.dataProvider()
        progress.setText(QCoreApplication.translate('ArpaGeoprocessing', 'Combine fields...')) 
        self.fields, self.mapBFields = combineVectorFieldsQgisFields(self.fieldsLayerA, self.fieldsLayerB)
        progress.setText(QCoreApplication.translate('ArpaGeoprocessing', 'Set output...')) 
        self.writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(self.fields.toList(),
                self.vproviderA.geometryType(), self.vproviderA.crs())
        
    def setExpressionObj(self):
        #set expression calculator if not empty
        self.expA = dict()
        self.expB = dict()
        if bool(self.expressionLayerA) or bool(self.expressionLayerB):
            if bool(self.expressionLayerA):
                for field in self.expressionLayerA.keys():
                    tempDict = {'exp':None,'val':None}
                    tempDict['exp'] = QgsExpression(self.expressionLayerA[field])
    
                    da = QgsDistanceArea()
                    da.setSourceCrs(self.vproviderA.crs().srsid())
                    canvas = iface.mapCanvas()
                    da.setEllipsoidalMode(canvas.mapRenderer().hasCrsTransformEnabled())
                    da.setEllipsoid(QgsProject.instance().readEntry('Measure',
                                                                    '/Ellipsoid',
                                                                    GEO_NONE)[0])
                    tempDict['exp'].setGeomCalculator(da)
                    self.expA[field] = tempDict
            else:
                for field in self.expressionLayerB.keys():
                    tempDict = {'exp':None,'val':None}
                    tempDict['exp'] = QgsExpression(self.expressionLayerB[field])
    
                    da = QgsDistanceArea()
                    da.setSourceCrs(self.vproviderA.crs().srsid())
                    canvas = iface.mapCanvas()
                    da.setEllipsoidalMode(canvas.mapRenderer().hasCrsTransformEnabled())
                    da.setEllipsoid(QgsProject.instance().readEntry('Measure',
                                                                    '/Ellipsoid',
                                                                    GEO_NONE)[0])
                    tempDict['exp'].setGeomCalculator(da)
                    self.expB[self.mapBFields[field]] = tempDict
    
    def setOutFeat(self,geom):
        self.outFeat.setGeometry(geom)
        self.outFeat.initAttributes(len(self.fields))
        self.outFeat.setFields(self.fields)
        if bool(self.expA) or bool(self.expB):
            if bool(self.expA):
                for f in self.expressionLayerA.keys() :
                    self.expA[f]['val'] = self.expA[f]['exp'].evaluate(self.inFeatA)
            else:
                for f in self.expressionLayerB.keys() :
                    self.expB[f]['val'] = self.expB[f]['exp'].evaluate(self.inFeatB)
        
        for fld in self.fields:
            #check if in field a or field b                                    
            if self.inFeatA.fieldNameIndex(fld.name()) >= 0:
                self.outFeat[fld.name()] = self.inFeatA[fld.name()]
            
            if bool(self.expA) and fld.name() in self.expA.keys():
                self.outFeat[fld.name()] = self.expA[fld.name()]['val']
                
            if fld.name() in self.mapBFields.keys() and self.inFeatB.fieldNameIndex(self.mapBFields[fld.name()]) >= 0:
                self.outFeat[fld.name()] = self.inFeatB[self.mapBFields[fld.name()]]
                
            if bool(self.expB) and fld.name() in self.expB.keys():
                self.outFeat[fld.name()] = self.expB[fld.name()]['val']
        
        self.writer.addFeature(self.outFeat)
    
    def sendToDB(self):
        self.writer.importDB()
        
    def finalizeAlgorithm(self):
        #for postgis output
        if self.outputType == 'Postgis':
            self.sendToDB()
        else:
            del self.writer
    
    def processAlgorithm(self, progress):
        
        self.initAlgorithm(progress)
        self.setExpressionObj()
        
        index = vector.spatialindex(self.vlayerB)
        nElement = 0
        selectionA = vector.features(self.vlayerA)
        nFeat = len(selectionA)
        progress.setText(QCoreApplication.translate('ArpaGeoprocessing', 'Running algorithm...'))        
        for self.inFeatA in selectionA:
            nElement += 1
            progress.setPercentage(nElement / float(nFeat) * 100)
            geom = QgsGeometry(self.inFeatA.geometry())
            intersects = index.intersects(geom.boundingBox())
            for i in intersects:
                request = QgsFeatureRequest().setFilterFid(i)
                self.inFeatB = self.vlayerB.getFeatures(request).next()
                tmpGeom = QgsGeometry(self.inFeatB.geometry())
                try:
                    if geom.intersects(tmpGeom):
                        int_geom = QgsGeometry(geom.intersection(tmpGeom))
                        if int_geom.wkbType() == QGis.WKBUnknown:
                            int_com = geom.combine(tmpGeom)
                            int_sym = geom.symDifference(tmpGeom)
                            int_geom = QgsGeometry(int_com.difference(int_sym))
                        try:
                            if int_geom.wkbType() in wkbTypeGroups[wkbTypeGroups[int_geom.wkbType()]]:
                                self.setOutFeat(int_geom)
                        except Exception as e:
                            ProcessingLog.addToLog(ProcessingLog.LOG_INFO, 'Feature geometry error: One or more output features ignored due to invalid geometry.')
                            continue
                except:
                    break
                
        #finalize
        self.finalizeAlgorithm()
        
    
    def defineCharacteristics(self):
        self.addParameter(ParameterVector(self.INPUT, 'Origin layer',
                          [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterVector(self.INPUT2,
                          'Target layer',
                          [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterObject(self.FIELDSINPUT1,'Fields Origin Layer'))
        self.addParameter(ParameterObject(self.FIELDSINPUT2,'Fields Target Layer'))
        self.addParameter(ParameterObject(self.EXPRESSIONSINPUT1,'Fields with expression Origin Layer'))
        self.addParameter(ParameterObject(self.EXPRESSIONSINPUT2,'Fields with expression Target Layer'))
        #select the output
        self.addOutput(self.outputFormats[self.outputType](self.OUTPUT, self.name))
    
class Touch(Intersection):
    
    name = 'Touch'
    group = 'Vector overlay tools'
    
    def processAlgorithm(self, progress):
        
        self.initAlgorithm(progress)
        self.setExpressionObj()
        
        nElement = 0
        selectionA = vector.features(self.vlayerA)
        
        nFeat = len(selectionA)
        for self.inFeatA in selectionA:
            nElement += 1
            progress.setPercentage(nElement / float(nFeat) * 100)
            geom = QgsGeometry(self.inFeatA.geometry())
            selectionB = vector.features(self.vlayerB)
            for self.inFeatB in selectionB:
                geomTarget = QgsGeometry(self.inFeatB.geometry())
                try:
                    if geom.touches(geomTarget):
                        try:
                            self.setOutFeat(geom)
                        except:
                            ProcessingLog.addToLog(ProcessingLog.LOG_INFO, 'Feature geometry error: One or more output features ignored due to invalid geometry.')
                            continue
                except:
                    break
        #finalize
        self.finalizeAlgorithm()


class Contain(Touch):
    
    name = 'Contain'
    group = 'Vector overlay tools'
    
    def processAlgorithm(self, progress):
        
        self.initAlgorithm(progress)
        self.setExpressionObj()
      
        nElement = 0
        selectionA = vector.features(self.vlayerA)
        nFeat = len(selectionA)
        for self.inFeatA in selectionA:
            nElement += 1
            progress.setPercentage(nElement / float(nFeat) * 100)
            geom = QgsGeometry(self.inFeatA.geometry())
            selectionB = vector.features(self.vlayerB)
            for self.inFeatB in selectionB:
                geomTarget = QgsGeometry(self.inFeatB.geometry())
                try:
                    if geomTarget.contains(geom):
                        try:
                            self.setOutFeat(geom)
                        except:
                            ProcessingLog.addToLog(ProcessingLog.LOG_INFO, 'Feature geometry error: One or more output features ignored due to invalid geometry.')
                            continue
                except:
                    break
        #finalize
        self.finalizeAlgorithm()
    



def handleAlgorithmResults(alg, progress=None, showResults=True):
    wrongLayers = []
    reslayers = []
    if progress is None:
        progress = SilentProgress()
    progress.setText(QCoreApplication.translate('ArpaGeoprocessing', 'Loading resulting layer'))
    i = 0
    for out in alg.outputs:
        progress.setPercentage(100 * i / float(len(alg.outputs)))
        #if out.hidden or not out.open:
            #continue
        if isinstance(out, (OutputVector)):
            try:
                if alg.outputType == 'Postgis':
                    outUri = QgsDataSourceURI()
                    psql = out.value['PSQL']
                    outUri.setConnection(psql.PSQLHost, psql.PSQLPort, psql.PSQLDatabase, psql.PSQLUsername, psql.PSQLPassword)
                    outUri.setDataSource(out.value['schema'],out.value['table'],out.value['geoColumn'])
                    layer = QgsVectorLayer(outUri.uri(), out.value['table'], "postgres")
                    QgsMapLayerRegistry.instance().addMapLayers([layer])
                    
                else:
                    if ProcessingConfig.getSetting(
                            ProcessingConfig.USE_FILENAME_AS_LAYER_NAME):
                        name = os.path.basename(out.value)
                        name = name.split('.')[0]
                    else:
                        name = out.description
                        # removing .ext from name if exixst
                    layer = dataobjects.load(out.value, name, alg.crs,
                            RenderingStyles.getStyle(alg.commandLineName(),
                            out.name))
                        
                reslayers.append(layer)
            except Exception, e:
                wrongLayers.append(out)
            i += 1
    return reslayers
     