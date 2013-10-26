"""
Script plotting source model using GMT.
"""
from oqtoolsui.converters import gmt, nrml04

if __name__=='__main__':

    gmt.MAP_WIDTH = 25.0
    gmt.FRAME_ANNOTATION_SPACING = 5.0
    plot_file = open("CanadaR.ps",'w')
    src_model = nrml04._parse_source_model_file('CanadaR.xml')
    gmt._plot_area_srcs_polygons(src_model, 'Equidistant Conic', plot_file)

    #gmt.MAP_WIDTH = 15.0
    #gmt.CPT_INCREMENT = 1e-4
    #plot_file = open("NSHMP2007AlaskaSSDeepest.ps",'w')
    #gmt._plot_point_srcs_occ_rates(src_model, 'Equidistant Conic', plot_file)
    #plot_file.close()
    