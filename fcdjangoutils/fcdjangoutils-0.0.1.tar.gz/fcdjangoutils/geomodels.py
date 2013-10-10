import django.contrib.gis.db.models
import django.db.models

# Hack to allow columns with no geom_type
import django.contrib.gis.db.backends.postgis.operations
def geo_db_type(self, f):
     """
     Return the database field type for the given geometry field.
     Typically this is `None` because geometry columns are added via
     the `AddGeometryColumn` stored procedure, unless the field
     has been specified to be of geography type instead.
     """
     if f.geography:
         if not self.geography:
             raise NotImplementedError('PostGIS 1.5 required for geography column support.')

         if f.srid != 4326:
             raise NotImplementedError('PostGIS 1.5 supports geography columns '
                                       'only with an SRID of 4326.')

         if f.geom_type:
             return 'geography(%s,%d)'% (f.geom_type, f.srid)
         else:
             return 'geography' # FIXME: How to handle srid?
     elif self.geometry:
         if not f.geom_type:
             return 'geometry' # FIXME: How to handle srid?

         # Postgis 2.0 supports type-based geometries.
         # TODO: Support 'M' extension.
         if f.dim == 3:
             geom_type = f.geom_type + 'Z'
         else:
             geom_type = f.geom_type
         return 'geometry(%s,%d)' % (geom_type, f.srid)
     else:
         return None
django.contrib.gis.db.backends.postgis.operations.PostGISOperations.geo_db_type = geo_db_type


class GeometryField(django.contrib.gis.db.models.GeometryField):
    geom_type = None
