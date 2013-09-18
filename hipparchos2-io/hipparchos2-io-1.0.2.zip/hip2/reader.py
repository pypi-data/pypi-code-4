from star import Star


def get_stars_generator(filename):
    """Read Hipparcos new reduction .dat file and return a generator of Star instances."""
    with open(filename, "rb") as f:
        row = f.read(277)
        while row != "":
            hipparcos_id = int(row[0:6])
            solution_type_new = int(row[7:10])
            solution_type_old = int(row[11])
            number_of_components = int(row[13])
            ra_radians = float(row[15:28])
            dec_radians = float(row[29:42])
            parallax_mas = float(row[43:50])
            proper_motion_ra_mas_per_year = float(row[51:59])
            proper_motion_dec_mas_per_year = float(row[60:68])
            ra_error_mas = float(row[69:75])
            dec_error_mas = float(row[76:82])
            parallax_error_mas = float(row[83:89])
            proper_motion_ra_error_mas_per_year = float(row[90:96])
            proper_motion_dec_error_mas_per_year = float(row[97:103])
            number_of_field_transits = int(row[104:107])
            goodness_of_fit = float(row[108:113])
            percentage_rejected_data = int(row[114:116])
            cosmic_dispersion_added = float(row[117:123])
            entry_in_supplemental_catalog = int(row[124:128])
            magnitude = float(row[129:136])
            magnitude_error = float(row[137:143])
            magnitude_scatter = float(row[144:149])
            variability_annex = int(row[150])
            color_index = float(row[152:158])
            color_index_error = float(row[159:164])
            VI_color_index = float(row[165:171])
            upper_triangular_weight_matrix = [[float(row[171:178]), float(row[178:185]), float(row[185:192]), float(row[192:199]), float(row[199:206])],
                                             [0.0, float(row[206:213]), float(row[213:220]), float(row[220:227]), float(row[227:234])],
                                             [0.0, 0.0, float(row[234:241]), float(row[241:248]), float(row[248:255])],
                                             [0.0, 0.0, 0.0, float(row[255:262]), float(row[262:269])],
                                             [0.0, 0.0, 0.0, 0.0, float(row[269:276])]]

            star = Star(hipparcos_id,
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
                        upper_triangular_weight_matrix)
            row = f.read(277)
            yield star


def get_stars_list(filename):
    """Read Hipparcos new reduction .dat file and return a list of Star instances."""
    return list(get_stars_generator(filename))
