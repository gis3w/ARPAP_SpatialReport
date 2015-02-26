# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ARPAP_SpatialReport
                             -------------------
        begin                : 2014-11-20
        copyright        : (C) 2015 by gis3w.it
        email                : info@gis3w.it
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os,tempfile
import json
from PyQt4.QtCore import QObject,pyqtSignal


class CompAlreadyOpenException(Exception):
    pass

class ReportProjectParseException(Exception):
    pass

class SpatialreportProject(QObject):
    EXTENSION = "qrp"
    ROOTIDENT = "spatialreport"

    config = dict()
    _config = dict()
    full = False
    loadingError = False


    projectChanged = pyqtSignal(object)
    projectSaved = pyqtSignal()
    projectFull = pyqtSignal()
    
    def __init__(self,compIface,parent = None,filepath=None):
        super(SpatialreportProject,self).__init__()
        self.projectName = None
        self.filepath = None
        if filepath:
            self.setFilePath(filepath)
        self.compIface = compIface
        self.parent = parent
        self.dirty = False
    
    def open(self,filepath=None,composition=None):
        if filepath:
            self.setFilePath(filepath)
        if not self.filepath or not os.path.exists(self.filepath):
            raise Exception(self.tr("File %s does not exists" % self.filepath))
        with open(self.filepath,"r") as configFile:
            try:
                self._config = self.readConfig(configFile.read())
                self.loadConfigData()
            except ReportProjectParseException,e:
                raise e

                

    def save(self,filepath=None):
        self.parent.addProjectFileLog(self.tr('Starting save file ...'))
        if filepath:
            self.setFilePath(filepath)
        self.writeConfig()
        data = unicode(json.dumps(self._config,indent=4))
        
        with open(self.filepath,"w") as outfile:
            outfile.write(data.encode("utf-8"))

        self.projectSaved.emit()
        self.parent.addProjectFileLog(self.tr('Project file saved!'))
            
    def readConfig(self,data):
        config = json.loads(data)
        if config.get(self.ROOTIDENT,None):
            return config[self.ROOTIDENT]
        else:
            raise ReportProjectParseException(self.tr("Could not load report project"))

    def setStep(self,stepNumber,params):
        '''
        Set single spte in config file
        '''
        if not self.ROOTIDENT in self.config:
            self.config[self.ROOTIDENT] = dict()
        self.config[self.ROOTIDENT]['step'+str(stepNumber)] = params
        if stepNumber == 3:
            self.full = True
            self.projectFull.emit()

    def getConfig(self):
        return self.config[self.ROOTIDENT]

    def getWriteableConfig(self):
        return self._config

    def getWriteableConfigStep(self,stepNumber):
        return self.getWriteableConfig()['step'+stepNumber]

    def setFilePath(self,filepath):
        filepath_noext,ext = os.path.splitext(filepath)
        if ext != '' or ext != self.EXTENSION:
            ext = self.EXTENSION
        self.filepath = "%s.%s" % (filepath_noext,ext)
        self.projectName = os.path.basename(self.filepath)

    def forSerializeStepCommon(self,stepNumber):
        if not self.ROOTIDENT in self._config:
          self._config[self.ROOTIDENT] = dict()
        step = 'step'+str(stepNumber)
        if not step in self._config[self.ROOTIDENT]:
            self._config[self.ROOTIDENT][step] = dict()

    def forSerializeStep0(self):
        self.forSerializeStepCommon(0)
        self._config[self.ROOTIDENT]['step0']['title'] = self.config[self.ROOTIDENT]['step0']['title']
        self._config[self.ROOTIDENT]['step0']['originLayerSelect'] = self.config[self.ROOTIDENT]['step0']['originLayerSelect'].originalName()
        self._config[self.ROOTIDENT]['step0']['targetLayerSelect'] = self.config[self.ROOTIDENT]['step0']['targetLayerSelect'].originalName()

    def forSerializeStep1(self):
        self._config[self.ROOTIDENT]['step1'] = self.config[self.ROOTIDENT]['step1'].copy()

    def forSerializeStep2(self):
        self._config[self.ROOTIDENT]['step2'] = self.config[self.ROOTIDENT]['step2'].copy()
        for typeLayer in ('originLayerFields','targetLayerFields'):
            self._config[self.ROOTIDENT]['step2'][typeLayer] = list()
            for f in self.config[self.ROOTIDENT]['step2'][typeLayer].values():
                self._config[self.ROOTIDENT]['step2'][typeLayer].append({'name':f.name(),'typeName':f.typeName(),'length':f.length(),'precision':f.precision()})

    def forSerializeStep3(self):
        self._config[self.ROOTIDENT]['step3'] = self.config[self.ROOTIDENT]['step3'].copy()
        del(self._config[self.ROOTIDENT]['step3']['outputPostgis']['PSQL'])


    def loadConfigData(self):
        self.parent.projectFileStatusBrowser.clear()
        self.parent.addProjectFileLog(self.tr('<h2>Starting load file ...</h2>'))
        for stepNumber in range(0,4):
           if hasattr(self.parent,'loadStep'+str(stepNumber)):
                getattr(self.parent,'loadStep'+str(stepNumber))()
        if not self.loadingError:
            self.parent.addProjectFileLog(self.tr('<h2>File loaded with success!</h2>'))
        else:
            self.parent.addProjectFileLog(self.tr('<h2 style="color:#FF0000;">Some errors on loading file!</h2>'))



    def writeConfig(self):
        '''
        Put data in a dict(self._config) that can be serilized by json.dump method
        '''
        #serialize step
        for stepNumber in range(0,4):
            if hasattr(self,'forSerializeStep'+str(stepNumber)):
                getattr(self,'forSerializeStep'+str(stepNumber))()

    def close(self):
        pass

    def __getattr__(self, name):
        if name.startswith('getWriteableConfigStep'):
            return self.getWriteableConfigStep(name[-1])
        
        
