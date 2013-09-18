import csv


def write_csv(stars, filename):
    '''
    Write values from Star instances to a new CSV file
    '''
    with open(filename, "wb") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['hipparcos_id',
                         'solution_type_new',
                         'solution_type_old',
                         'number_of_components',
                         'ra_radians',
                         'dec_radians',
                         'parallax_mas',
                         'proper_motion_ra_mas_per_year',
                         'proper_motion_dec_mas_per_year',
                         'ra_error_mas',
                         'dec_error_mas',
                         'parallax_error_mas',
                         'proper_motion_ra_error_mas_per_year',
                         'proper_motion_dec_error_mas_per_year',
                         'number_of_field_transits',
                         'goodness_of_fit',
                         'percentage_rejected_data',
                         'cosmic_dispersion_added',
                         'entry_in_supplemental_catalog',
                         'magnitude',
                         'magnitude_error',
                         'magnitude_scatter',
                         'variability_annex',
                         'color_index',
                         'color_index_error',
                         'VI_color_index',
                         'upper_triangular_weight_matrix'])

        for star in stars:
            writer.writerow([star.hipparcos_id,
                             star.solution_type_new,
                             star.solution_type_old,
                             star.number_of_components,
                             star.ra_radians,
                             star.dec_radians,
                             star.parallax_mas,
                             star.proper_motion_ra_mas_per_year,
                             star.proper_motion_dec_mas_per_year,
                             star.ra_error_mas,
                             star.dec_error_mas,
                             star.parallax_error_mas,
                             star.proper_motion_ra_error_mas_per_year,
                             star.proper_motion_dec_error_mas_per_year,
                             star.number_of_field_transits,
                             star.goodness_of_fit,
                             star.percentage_rejected_data,
                             star.cosmic_dispersion_added,
                             star.entry_in_supplemental_catalog,
                             star.magnitude,
                             star.magnitude_error,
                             star.magnitude_scatter,
                             star.variability_annex,
                             star.color_index,
                             star.color_index_error,
                             star.VI_color_index,
                             star.upper_triangular_weight_matrix])
