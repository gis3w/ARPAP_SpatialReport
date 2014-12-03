from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from processing.algs.qgis.Intersection import Intersection as ProcessingIntersection
from processing.core.parameters import ParameterVector, Parameter
from processing.core.outputs import OutputVector
from processing.core.ProcessingLog import ProcessingLog
from processing.tools import dataobjects, vector

class ParameterList(Parameter):

    def __init__(self, name='', description=''):
        Parameter.__init__(self, name, description)
        self.value = None

    def setValue(self, value):
        self.value = value
        return True

    def getValueAsCommandLineParameter(self):
        return '"' + unicode(self.value) + '"'

def combineVectorFields(fieldsA, fieldsB):
    fields = []
    fields.extend(fieldsA)
    namesA = [unicode(f.name()).lower() for f in fieldsA]
    for field in fieldsB:
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

class Touch(Intersection):
    
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
            for inFeatB in selectionB:
                geomTarget = QgsGeometry(inFeatB.geometry())
                try:
                    if geom.touches(geomTarget):
                        atMapB = inFeatB.attributes()
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
    
    def defineCharacteristics(self):
        self.name = 'Touch'
        self.group = 'Vector overlay tools'
        self.addParameter(ParameterVector(self.INPUT, 'Input layer',
                          [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterVector(self.INPUT2,
                          'Touch layer',
                          [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterList(self.FIELDSINPUT1,'Fields Input Layer'))
        self.addParameter(ParameterList(self.FIELDSINPUT2,'Fields Touch Layer'))
        self.addOutput(OutputVector(self.OUTPUT, 'Touch'))

class Contain(Touch):
    
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
            for inFeatB in selectionB:
                geomTarget = QgsGeometry(inFeatB.geometry())
                try:
                    if geomTarget.contains(geom):
                        atMapB = inFeatB.attributes()
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
    
    def defineCharacteristics(self):
        self.name = 'Contain'
        self.group = 'Vector overlay tools'
        self.addParameter(ParameterVector(self.INPUT, 'Input layer',
                          [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterVector(self.INPUT2,
                          'Touch layer',
                          [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterList(self.FIELDSINPUT1,'Fields Input Layer'))
        self.addParameter(ParameterList(self.FIELDSINPUT2,'Fields Touch Layer'))
        self.addOutput(OutputVector(self.OUTPUT, 'Contain'))