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
    
    
    def __init__(self,dlg):
        self.dlg = dlg
    
    def getErrors(self):
        return errorMessages

    def validateStep0(self):
        #check if comboBoxes are empties
        toRes = True
        if self.dlg.originLayerSelect.currentIndex() == -1:
            toRes = False
            self.errorMessages.append('Origin Leyer not to be empty')
            
        if self.dlg.targetLayerSelect.currentIndex() == -1:
            toRes = False
            self.errorMessages.append('Terget Leyer not to be empty')
        
        return toRes
    
    def geoprocessingDataType(self):
        geoprocessingType = self.dlg.getGeoprocessingTypeData()
        originLayerType = getVectorTypeAsString(self.dlg.getComboboxData('originLayerSelect'))
        targetLayerType = getVectorTypeAsString(self.dlg.getComboboxData('targetLayerSelect'))
        
        print originLayerType
        print targetLayerType
        print geoprocessingType
        print self.matrixRulesGeoprocessing[geoprocessingType]
        print self.matrixRulesGeoprocessing[geoprocessingType][self.matrixRulesGeoprocessing['mapping'][originLayerType]][self.matrixRulesGeoprocessing['mapping'][targetLayerType]]
            