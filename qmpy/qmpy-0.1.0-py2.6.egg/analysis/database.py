from qmpy.data import elements

pressure_words = [
        'pressure',
        'anvil cell',
        'dac',
        'mpa', 'gpa',
        'mbar', 'kbar']


def is_likely_high_pressure(structure):
    if structure.pressure > 102:
        return True
    if structure.reference:
        if structure.reference.title:
            title = structure.reference.title.lower()
            for w in pressure_words:
                if w in title:
                    return True
    return False
