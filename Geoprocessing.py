from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from processing.algs.qgis.Intersection import Intersection as ProcessingIntersection
from processing.core.parameters import ParameterVector
from processing.core.outputs import OutputVector
from processing.core.ProcessingLog import ProcessingLog
from processing.tools import dataobjects, vector

class Intersection(ProcessingIntersection):
    INPUT = 'ORIGIN'
    INPUT2 = 'TARGET'
    OUTPUT = 'OUTPUT'

class Touch(Intersection):
    
    def processAlgorithm(self, progress):
        vlayerA = dataobjects.getObjectFromUri(
                self.getParameterValue(self.INPUT))
        vlayerB = dataobjects.getObjectFromUri(
                self.getParameterValue(self.INPUT2))
        vproviderA = vlayerA.dataProvider()

        fields = vector.combineVectorFields(vlayerA, vlayerB)
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
        self.addOutput(OutputVector(self.OUTPUT, 'Touch'))

class Contain(Intersection):
    
    def defineCharacteristics(self):
        self.name = 'Contain'
        self.group = 'Vector overlay tools'
        self.addParameter(ParameterVector(self.INPUT, 'Input layer',
                          [ParameterVector.VECTOR_TYPE_ANY]))
        self.addParameter(ParameterVector(self.INPUT2,
                          'Touch layer',
                          [ParameterVector.VECTOR_TYPE_ANY]))
        self.addOutput(OutputVector(self.OUTPUT, 'Contain'))