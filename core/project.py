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
    projectChanged = pyqtSignal(object)
    projectSaved = pyqtSignal()
    
    def __init__(self,compIface,filepath=None):
        super(SpatialreportProject,self).__init__()
        self.projectName = None
        self.filepath = None
        self.errors = {
           "missginItems":[]
        }
        if filepath:
            self.setFilePath(filepath)
        self.compIface = compIface
        self.dirty = False
    
    def open(self,filepath=None,composition=None):
        if filepath:
            self.setFilePath(filepath)
        if not self.filepath or not os.path.exists(self.filepath):
            raise Exception(self.tr("File %s does not exists" % self.filepath))
        with open(self.filepath,"r") as configFile:
            try:
                self.config = self.readConfig(configFile.read())
                # composition parameter is set in case the user overlads the composition set inside the project file
                # otherwise use the project file's composition
                if not composition:
                    composition = self.compIface.getCompositionFromTitle(self.config["composition"])
                self.setupItemsFromConfig(composition)
            except ReportProjectParseException,e:
                raise e
            else:
                self.setComposition(composition,self.config["composition"])
                self.save()
                

    def save(self,filepath=None):
        if filepath:
            self.setFilePath(filepath)
        self.config = {}
        self.writeConfig()
        data = unicode(json.dumps(self.config))
        
        with open(self.filepath,"w") as outfile:
            outfile.write(data.encode("utf-8"))
        
        # we do it here because we want to be sure the items are set not new only if file write completes
        for item in self.items.values():
            if item.isRendered():
                item.setNew(False)
        
        self.setDirty(False)
        self.projectSaved.emit()
            
    def readConfig(self,data):
        config = json.loads(data)
        if config.get(self.ROOTIDENT,None):
            return config[self.ROOTIDENT]
        else:
            raise ReportProjectParseException(self.tr("Could not load report project"))

    def setStep(self,stepNumber,params):
        if not self.ROOTIDENT in self.config:
            self.config[self.ROOTIDENT] = dict()
        self.config[self.ROOTIDENT]['step'+str(stepNumber)] = params

    def getConfig(self):
        return self.config[self.ROOTIDENT]
    
    def setFilePath(self,filepath):
        filepath_noext,ext = os.path.splitext(filepath)
        if ext != '' or ext != self.EXTENSION:
            ext = self.EXTENSION
        self.filepath = "%s.%s" % (filepath_noext,ext)
        self.projectName = os.path.basename(self.filepath)

    def forSerializeStep0(self):
        self._config = self.config.copy()
        self._config[self.ROOTIDENT]['step0']['originLayerSelect'] = self.config[self.ROOTIDENT]['step0']['originLayerSelect'].originalName()
        self._config[self.ROOTIDENT]['step0']['targetLayerSelect'] = self.config[self.ROOTIDENT]['step0']['targetLayerSelect'].originalName()

    def writeConfig(self):        
        #for serilize step1
        self.forSerializeStep0()
        print self._config

    def close(self):
        pass
        
        
