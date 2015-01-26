from .PSQL import PSQL


class arpap_spatialreport_psql(PSQL):
    
    @classmethod
    def quoteId(self, identifier):
        if hasattr(identifier, '__iter__'):
            ids = list()
            for i in identifier:
                if i == None or i == "":
                    continue
                ids.append( self.quoteId(i) )
            return u'.'.join( ids )

        identifier = unicode(identifier) if identifier != None else unicode() # make sure it's python unicode string
        return u'"%s"' % identifier.replace('"', '""')

    @classmethod
    def quoteString(self, txt):
        """ make the string safe - replace ' with '' """
        if hasattr(txt, '__iter__'):
            txts = list()
            for i in txt:
                if i == None:
                    continue
                txts.append( self.quoteString(i) )
            return u'.'.join( txts )

        txt = unicode(txt) if txt != None else unicode() # make sure it's python unicode string
        return u"'%s'" % txt.replace("'", "''")

    
    def createTable(self, table, field_defs, pkey, schema=None):
        """
        Derived from db_manager plugin
        """
        """ create ordinary table
                'fields' is array containing field definitions
                'pkey' is the primary key name
        """
        if len(field_defs) == 0:
            return False

        sql = "CREATE TABLE %s (" % self.quoteId(table)
        sql += u", ".join( field_defs )
        if pkey != None and pkey != "":
            sql += u", PRIMARY KEY (%s)" % self.quoteId(pkey)
        sql += ")"
        
        print sql
        
        #error = self.submitCommand(sql)

        return True
    
    def createVectorTable(self, table, fields, geom, schema=None):
        """
        Derived from db_manager plugin
        """
        ret = self.createTable(table, fields, schema)
        if ret == False:
            return False

        createGeomCol = geom != None
        if createGeomCol:
            geomCol, geomType, geomSrid, geomDim = geom[:4]
            createSpatialIndex = geom[4] == True if len(geom) > 4 else False

            self.addGeometryColumn( (schema, table), geomCol, geomType, geomSrid, geomDim )

            if createSpatialIndex:
                # commit data definition changes, otherwise index can't be built
                error = self.submitCommand(sql)
                self.createSpatialIndex( (schema, table), geomCol)

        return True