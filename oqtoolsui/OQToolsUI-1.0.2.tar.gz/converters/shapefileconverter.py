__author__ = 'orhan'


from openquake.nrmllib.models import *
import shapefile as shp


class ShapeFileConverter:

    __nodal_plane_properties = (('SS', 0.0), ('TF', 90.0), ('NF', -90.0))
    __tecRegionProperties = {'Active': 'Active Shallow Crust', 'Interface': 'Subduction Interface',
                             'Inslab': 'Subduction IntraSlab'}

    def __init__(self, sourceFileName, targetFileName, nameMappings):
        self.__sourceFileName = sourceFileName
        self.__targetFileName = targetFileName
        self.__nameMappings = nameMappings

    def getPrmName(self, name):
        if self.__nameMappings.has_key(name):
            return self.__nameMappings[name]

        return name

    def parse(self, sourceType, minMag=5.0):
        sf = shp.Reader(self.__sourceFileName)
        shape_records = sf.shapeRecords()

        source_model = SourceModel()
        source_model.name = 'Source Model'
        source_model.sources = []

        for maxMagInd in xrange(1, 6):
            mMaxName = 'MMAXMAG0' + str(maxMagInd)
            wMaxName = 'WMAXMAG0' + str(maxMagInd)

            found = False
            ind = -1
            ind2 = -1
            for i in xrange(len(sf.fields)):
                if sf.fields[i][0] == mMaxName:
                    found = True
                    ind = i
                elif sf.fields[i][0] == wMaxName:
                    ind2 = i

            if found and float(shape_records[0].record[ind-1]) != 0.0:
                self.__getSourceModelWithMMax(source_model, sf, shape_records, minMag, mMaxName, maxMagInd, sourceType)

        return source_model

    def __getSourceModelWithMMax(self, sourceModel, sf, shaperecords, minMag, mMaxPrmName, maxMagInd, sourceType):

        for shaperecord in shaperecords:
            area = self.__getAreaSource(sourceType)
            record = dict()

            for i in xrange(1, len(sf.fields)):
                record[sf.fields[i][0]] = shaperecord.record[i-1]

            area.trt = self.__tecRegionProperties[record['TECREG']]
            area.id = record[self.getPrmName('ID')] + "_" + str(maxMagInd)
            area.name = record[self.getPrmName('NAME')]

            area.geometry = PointGeometry()

            area.geometry.wkt = 'POLYGON(('
            first = True
            for point in shaperecord.shape.points:
                lon = point[0]
                lat = point[1]
                if not first:
                    area.geometry.wkt += ', '
                area.geometry.wkt += str(lon) + " " + str(lat)
                first = False

            area.geometry.wkt += '))'
            area.geometry.lower_seismo_depth = record['MAXDEPTH']
            area.geometry.upper_seismo_depth = record['MINDEPTH']
            area.mag_scale_rel = 'WC1994'
            area.rupt_aspect_ratio = 1.0

            area.mfd = TGRMFD(a_val=float(record[self.getPrmName('A')]), b_val=float(record[self.getPrmName('B')]),
                              min_mag=minMag, max_mag=float(record[mMaxPrmName]))
            # occur rates

            area.nodal_plane_dist = []
            for nodal_plane_property in self.__nodal_plane_properties:
                if record.has_key(nodal_plane_property[0]):
                    #sum of these columns should always be equal to 1
                    nodal_plane_val = float(record[nodal_plane_property[0]]) / 100.0

                    if nodal_plane_val > 0.0:
                        nodal_plane = NodalPlane()
                        nodal_plane.probability = nodal_plane_val
                        nodal_plane.strike = record['AZIMUTH'] % 360
                        nodal_plane.dip = record['PREF_DIP']
                        nodal_plane.rake = nodal_plane_property[1]

                        area.nodal_plane_dist.append(nodal_plane)

            if len(area.nodal_plane_dist) == 0:
                continue

            area.hypo_depth_dist = []
            ind = 1

            total_weight = 0.0
            while True:
                key = 'HYPODEPTH' + str(ind)
                if record.has_key(key) and float(record[key]) > 0.0:
                    hypo_depth = HypocentralDepth()
                    hypo_depth.probability = float(record['WHDEPTH' + str(ind)])
                    hypo_depth.depth = float(record['HYPODEPTH' + str(ind)])
                    total_weight += hypo_depth.probability

                    area.hypo_depth_dist.append(hypo_depth)
                    ind += 1
                else:
                    break

            if total_weight == 1.0:
                sourceModel.sources.append(area)
            else:
                raise Exception('Invalid hypo depth weights in area: %(id)d' % {'id': area.id})

        return sourceModel

    def __getAreaSource(self, sourceType):
        if sourceType == 'Area':
            return AreaSource()

        if sourceType == 'Point':
            return PointSource()

        if sourceType == 'Simple Fault':
            return SimpleFaultSource()

        if sourceType == 'Complex Fault':
            return ComplexFaultSource()

        raise Exception('Invalid source type')