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
    
    @classmethod
    def getSchemaTableName(self, table):
        if not hasattr(table, '__iter__'):
            return (None, table)
        elif len(table) < 2:
            return (None, table[0])
        else:
            return (table[0], table[1])
        
    def getSchemas(self):
        sql="SELECT nspname FROM pg_namespace WHERE nspname !~ '^pg_' AND nspname != 'information_schema' ORDER BY nspname"
        query = self.db.exec_(sql)
        schemas=[]
        while (query.next()):
            schemas.append(query.value(0))
        return schemas

    
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
        sql += ");"

        return sql
    
    def createVectorTable(self, table, fields, geom, schema=None):
        """
        Derived from db_manager plugin
        """
        sql = self.createTable(table, fields, schema)

        createGeomCol = geom != None
        if createGeomCol:
            geomCol, geomType, geomSrid, geomDim = geom[:4]
            createSpatialIndex = geom[4] == True if len(geom) > 4 else False

            sql += self.addGeometryColumn( (schema, table), geomCol, geomType, geomSrid, geomDim )

            if createSpatialIndex:
                sql += self.createSpatialIndex( (schema, table), geomCol)

        return sql
    
    def addGeometryColumn(self, table, geom_column='geom', geom_type='POINT', srid=-1, dim=2):
        schema, tablename = self.getSchemaTableName(table)
        schema_part = u"%s, " % self.quoteString(schema) if schema else ""

        sql = u"SELECT AddGeometryColumn(%s%s, %s, %d, %s, %d);" % (schema_part, self.quoteString(tablename), self.quoteString(geom_column), srid, self.quoteString(geom_type), dim)
        return sql
    
    def createSpatialIndex(self, table, geom_column='geom'):
        schema, tablename = self.getSchemaTableName(table)
        idx_name = self.quoteId(u"sidx_%s_%s" % (tablename, geom_column))
        sql = u"CREATE INDEX %s ON %s USING GIST(%s);" % (idx_name, self.quoteId(table), self.quoteId(geom_column))
        self.submitCommand(sql)