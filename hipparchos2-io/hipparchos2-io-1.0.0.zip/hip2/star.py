class Star(object):

    """
    Represents a single star in the Hipparcos new reduction data.
    """

    def __init__(self,
                 hipparcos_id,
                 solution_type_new,
                 solution_type_old,
                 number_of_components,
                 ra_radians,
                 dec_radians,
                 parallax_mas,
                 proper_motion_ra_mas_per_year,
                 proper_motion_dec_mas_per_year,
                 ra_error_mas,
                 dec_error_mas,
                 parallax_error_mas,
                 proper_motion_ra_error_mas_per_year,
                 proper_motion_dec_error_mas_per_year,
                 number_of_field_transits,
                 goodness_of_fit,
                 percentage_rejected_data,
                 cosmic_dispersion_added,
                 entry_in_supplemental_catalog,
                 magnitude,
                 magnitude_error,
                 magnitude_scatter,
                 variability_annex,
                 color_index,
                 color_index_error,
                 VI_color_index,
                 upper_triangular_weight_matrix):

        self.hipparcos_id = hipparcos_id
        self.solution_type_new = solution_type_new
        self.solution_type_old = solution_type_old
        self.number_of_components = number_of_components
        self.ra_radians = ra_radians
        self.dec_radians = dec_radians
        self.parallax_mas = parallax_mas
        self.proper_motion_ra_mas_per_year = proper_motion_ra_mas_per_year
        self.proper_motion_dec_mas_per_year = proper_motion_dec_mas_per_year
        self.ra_error_mas = ra_error_mas
        self.dec_error_mas = dec_error_mas
        self.parallax_error_mas = parallax_error_mas
        self.proper_motion_ra_error_mas_per_year = proper_motion_ra_error_mas_per_year
        self.proper_motion_dec_error_mas_per_year = proper_motion_dec_error_mas_per_year
        self.number_of_field_transits = number_of_field_transits
        self.goodness_of_fit = goodness_of_fit
        self.percentage_rejected_data = percentage_rejected_data
        self.cosmic_dispersion_added = cosmic_dispersion_added
        self.entry_in_supplemental_catalog = entry_in_supplemental_catalog
        self.magnitude = magnitude
        self.magnitude_error = magnitude_error
        self.magnitude_scatter = magnitude_scatter
        self.variability_annex = variability_annex
        self.color_index = color_index
        self.color_index_error = color_index_error
        self.VI_color_index = VI_color_index
        self.upper_triangular_weight_matrix = upper_triangular_weight_matrix
